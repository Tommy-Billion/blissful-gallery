import streamlit as st
import os
import json

# -----------------------------
# CONFIG
# -----------------------------
LOGO_HEADER = "assets/logo_header.png"
LOGO_ICON = "assets/logo_icon.png"
LOGO_FAVICON = "assets/logo_favicon.png"

DATA_DIR = "gallery_data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
ARTISTS_FILE = os.path.join(DATA_DIR, "creators.json")
ARTWORKS_FILE = os.path.join(DATA_DIR, "artworks.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(
    page_title="Blissful Gallery",
    page_icon=LOGO_FAVICON,
    layout="wide"
)

# -----------------------------
# STYLE
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family:'Montserrat',sans-serif;
        background: radial-gradient(circle at 15% 20%, rgba(255,215,180,0.25), transparent 45%),
                    radial-gradient(circle at 85% 25%, rgba(200,220,255,0.25), transparent 45%),
                    radial-gradient(circle at 50% 85%, rgba(220,255,220,0.25), transparent 45%),
                    url('https://www.transparenttextures.com/patterns/canvas.png'),
                    linear-gradient(180deg, #f6f7fb 0%, #eef1f6 100%);
        background-attachment: fixed;
    }

    h1,h2,h3{
        font-family:'Playfair Display',serif;
        letter-spacing:0.6px;
    }

    .card{
        background: rgba(255,255,255,0.82);
        backdrop-filter: blur(10px);
        padding: 18px;
        border-radius: 20px;
        box-shadow:0 8px 30px rgba(0,0,0,0.10);
        margin-bottom:20px;
        border:1px solid rgba(212,175,55,0.25);
        position:relative;
        overflow:hidden;
    }

    .card::before{
        content:"";
        position:absolute;
        inset:0;
        background: radial-gradient(circle at 30% 30%, rgba(212,175,55,0.18), transparent 60%);
        pointer-events:none;
    }

    .badge{
        background: linear-gradient(135deg,#d4af37,#8c6b1f);
        color:white;
        padding:4px 9px;
        border-radius:10px;
        font-size:11px;
        letter-spacing:0.4px;
    }

    body::after{
        content:"";
        position:fixed;
        inset:0;
        background-image: radial-gradient(circle at center, rgba(212,175,55,0.06) 1px, transparent 1px);
        background-size:120px 120px;
        pointer-events:none;
        opacity:0.4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# HEADER (STREAMLIT SAFE)
# -----------------------------
col1, col2 = st.columns([1,6])

with col1:
    st.image(LOGO_ICON, width=64)

with col2:
    st.markdown(
        "<h1 style='margin-top:10px;'>Blissful Gallery</h1>",
        unsafe_allow_html=True
    )

# -----------------------------
# DATA MANAGEMENT
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
artworks = load_json(ARTWORKS_FILE, [])

# -----------------------------
# NAVIGATION
# -----------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Explore", "Featured", "Collections", "Artist Profile", "Apply", "Admin"]
)

# -----------------------------
# EXPLORE
# -----------------------------
if page == "Explore":
    st.subheader("Explore Artworks")

    search = st.text_input("Search by artwork or artist")

    categories = sorted(list(set([a["category"] for a in artworks]))) if artworks else []
    category_filter = st.selectbox("Filter by category", ["All"] + categories)

    for art in artworks:
        if (
            (search.lower() in art["title"].lower() or search.lower() in art["artist"].lower())
            and (category_filter == "All" or art["category"] == category_filter)
        ):
            st.markdown(f"""
            <div class='card'>
                <img src="{art['image']}" style="width:100%;border-radius:10px;">
                <h3>{art['title']}</h3>
                <p>By {art['artist']}</p>
                <span class='badge'>{art['category']}</span>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# FEATURED
# -----------------------------
elif page == "Featured":
    st.subheader("Featured Artists")

    for artist in artists:
        if artist.get("featured"):
            st.markdown(f"""
            <div class='card'>
                <h3>{artist['name']}</h3>
                <p>{artist['bio']}</p>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# COLLECTIONS
# -----------------------------
elif page == "Collections":
    st.subheader("Collections")
    st.info("Collections feature coming soon")

# -----------------------------
# ARTIST PROFILE
# -----------------------------
elif page == "Artist Profile":
    st.subheader("Artist Profile")

    if artists:
        names = [a["name"] for a in artists]
        selected = st.selectbox("Select artist", names)

        profile = next((a for a in artists if a["name"] == selected), None)

        if profile:
            st.markdown(f"<h2>{profile['name']}</h2><p>{profile['bio']}</p>", unsafe_allow_html=True)

            artist_works = [a for a in artworks if a["artist"] == selected]
            for art in artist_works:
                st.image(art["image"], caption=art["title"], use_column_width=True)
    else:
        st.info("No artists yet")

# -----------------------------
# APPLY
# -----------------------------
elif page == "Apply":
    st.subheader("Apply as Artist")

    name = st.text_input("Full Name")
    bio = st.text_area("Short Bio")
    category = st.text_input("Category")

    uploads = st.file_uploader(
        "Upload Artwork Images",
        type=["png","jpg","jpeg"],
        accept_multiple_files=True
    )

    if st.button("Submit Application"):
        if name and uploads:
            artists.append({
                "name": name,
                "bio": bio,
                "featured": False,
                "verified": False
            })
            save_json(ARTISTS_FILE, artists)

            for file in uploads:
                save_path = os.path.join(UPLOAD_DIR, file.name)
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())

                artworks.append({
                    "title": file.name,
                    "artist": name,
                    "image": save_path,
                    "category": category
                })

            save_json(ARTWORKS_FILE, artworks)
            st.success("Application submitted")
        else:
            st.warning("Name and artworks required")

# -----------------------------
# ADMIN
# -----------------------------
elif page == "Admin":
    st.subheader("Admin Dashboard")

    for i, artist in enumerate(artists):
        c1, c2, c3 = st.columns([3,1,1])

        with c1:
            st.write(artist["name"])

        with c2:
            if st.button("Feature", key=f"f{i}"):
                artists[i]["featured"] = True
                save_json(ARTISTS_FILE, artists)

        with c3:
            if st.button("Verify", key=f"v{i}"):
                artists[i]["verified"] = True
                save_json(ARTISTS_FILE, artists)
