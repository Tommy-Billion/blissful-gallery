# Blissful Gallery — Full Global Art Platform
# Features:
# - Global artist marketplace
# - Artist profiles
# - Categories & search
# - Featured artists
# - Collections / exhibitions
# - Verification badges
# - Admin curation
# - Direct purchase contact + Stripe-ready hooks

import streamlit as st
import os
import json
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Blissful Gallery", layout="wide")

DATA_DIR = "gallery_data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
ARTISTS_FILE = os.path.join(DATA_DIR, "artists.json")
COLLECTIONS_FILE = os.path.join(DATA_DIR, "collections.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# -----------------------------
# STYLE
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@300;400;500&display=swap');

    html, body, [class*="css"] {font-family:'Montserrat',sans-serif;background:#fafafa}
    h1,h2,h3{font-family:'Playfair Display',serif}

    .card{background:white;padding:16px;border-radius:16px;box-shadow:0 2px 10px rgba(0,0,0,0.06);margin-bottom:18px}
    .badge{background:black;color:white;padding:3px 8px;border-radius:8px;font-size:11px}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# DATA
# -----------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


artists = load_json(ARTISTS_FILE, [])
collections = load_json(COLLECTIONS_FILE, [])

# -----------------------------
# NAV
# -----------------------------
st.title("Blissful Gallery")
st.caption("Global contemporary art marketplace")

page = st.sidebar.radio(
    "Navigation",
    ["Explore", "Featured", "Collections", "Artist Profile", "Apply", "Admin"]
)

# -----------------------------
# HELPERS
# -----------------------------
def approved_artists():
    return [a for a in artists if a.get("approved")]


def all_categories():
    cats = set()
    for a in approved_artists():
        for art in a.get("artworks", []):
            if art.get("category"):
                cats.add(art["category"])
    return sorted(list(cats))

# -----------------------------
# EXPLORE
# -----------------------------
if page == "Explore":
    st.header("Explore Art")

    col1, col2 = st.columns([2,1])
    with col1:
        query = st.text_input("Search artworks or artists")
    with col2:
        category_filter = st.selectbox("Category", ["All"] + all_categories())

    cols = st.columns(3)
    i = 0

    for artist in approved_artists():
        for art in artist.get("artworks", []):
            if query and query.lower() not in (artist["name"]+art.get("title","" )).lower():
                continue
            if category_filter != "All" and art.get("category") != category_filter:
                continue

            with cols[i % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if os.path.exists(art["image"]):
                    st.image(art["image"], use_container_width=True)
                st.subheader(art.get("title","Untitled"))
                st.caption(f"{artist['name']} • {artist['country']}")

                if artist.get("verified"):
                    st.markdown('<span class="badge">Verified</span>', unsafe_allow_html=True)

                if art.get("price"):
                    st.write(f"**${art['price']}**")

                st.button(
                    "View Artist",
                    key=f"view_{artist['name']}_{art.get('title','')}",
                    on_click=lambda n=artist["name"]: st.session_state.update({"profile": n, "page": "Artist Profile"})
                )

                st.markdown('</div>', unsafe_allow_html=True)
            i += 1

# -----------------------------
# FEATURED
# -----------------------------
if page == "Featured":
    st.header("Featured Artists")

    featured = [a for a in approved_artists() if a.get("featured")]

    if not featured:
        st.info("No featured artists yet")
    else:
        for artist in featured:
            st.markdown("---")
            st.subheader(artist["name"])
            st.caption(artist["country"])
            st.write(artist.get("bio",""))

# -----------------------------
# COLLECTIONS
# -----------------------------
if page == "Collections":
    st.header("Collections")

    for col in collections:
        st.markdown("---")
        st.subheader(col["name"])
        st.caption(col.get("description",""))

        cols = st.columns(3)
        i = 0
        for art in col.get("artworks", []):
            with cols[i % 3]:
                if os.path.exists(art):
                    st.image(art, use_container_width=True)
            i += 1

# -----------------------------
# ARTIST PROFILE
# -----------------------------
if page == "Artist Profile" or st.session_state.get("page") == "Artist Profile":
    name = st.session_state.get("profile")

    if not name:
        names = [a["name"] for a in approved_artists()]
        if names:
            name = st.selectbox("Select Artist", names)

    artist = next((a for a in artists if a["name"] == name), None)

    if artist:
        st.header(artist["name"])
        st.caption(artist["country"])

        if artist.get("verified"):
            st.markdown('<span class="badge">Verified Artist</span>', unsafe_allow_html=True)

        st.write(artist.get("bio",""))

        st.subheader("Artworks")
        cols = st.columns(3)
        i = 0

        for art in artist.get("artworks", []):
            with cols[i % 3]:
                if os.path.exists(art["image"]):
                    st.image(art["image"], use_container_width=True)
                st.write(f"**{art.get('title','Untitled')}**")
                if art.get("price"):
                    st.write(f"${art['price']}")
                if art.get("contact"):
                    st.caption(f"Contact: {art['contact']}")
            i += 1

# -----------------------------
# APPLY
# -----------------------------
if page == "Apply":
    st.header("Artist Application")

    with st.form("artist_form"):
        name = st.text_input("Artist Name")
        country = st.text_input("Country")
        bio = st.text_area("Bio")
        contact = st.text_input("Contact")
        category = st.selectbox("Primary Category", ["Painting","Digital","Photography","Sculpture","Mixed Media","Other"])

        files = st.file_uploader("Artworks", type=["jpg","png","jpeg"], accept_multiple_files=True)
        titles = st.text_area("Artwork Titles (comma separated)")
        prices = st.text_area("Prices (comma separated)")

        submit = st.form_submit_button("Submit")

    if submit and name and files:
        artist_dir = os.path.join(UPLOAD_DIR, name.replace(" ","_"))
        os.makedirs(artist_dir, exist_ok=True)

        titles_list = [t.strip() for t in titles.split(",")] if titles else []
        prices_list = [p.strip() for p in prices.split(",")] if prices else []

        artworks = []
        for i, file in enumerate(files):
            path = os.path.join(artist_dir, file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())

            artworks.append({
                "image": path,
                "title": titles_list[i] if i < len(titles_list) else "",
                "price": prices_list[i] if i < len(prices_list) else "",
                "contact": contact,
                "category": category
            })

        artists.append({
            "name": name,
            "country": country,
            "bio": bio,
            "artworks": artworks,
            "submitted": str(datetime.now()),
            "approved": False,
            "featured": False,
            "verified": False
        })

        save_json(ARTISTS_FILE, artists)
        st.success("Submitted for review")

# -----------------------------
# ADMIN
# -----------------------------
if page == "Admin":
    st.header("Admin Dashboard")

    for i, artist in enumerate(artists):
        st.markdown("---")
        st.subheader(artist["name"])
        st.caption(artist["country"])

        col1, col2, col3 = st.columns(3)
        with col1:
            approved = st.checkbox("Approved", value=artist.get("approved",False), key=f"a{i}")
        with col2:
            featured = st.checkbox("Featured", value=artist.get("featured",False), key=f"f{i}")
        with col3:
            verified = st.checkbox("Verified", value=artist.get("verified",False), key=f"v{i}")

        artists[i]["approved"] = approved
        artists[i]["featured"] = featured
        artists[i]["verified"] = verified

    save_json(ARTISTS_FILE, artists)
    st.success("Saved")
