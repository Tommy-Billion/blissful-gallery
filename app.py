import streamlit as st
import os
import json
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Blissful Gallery", page_icon="assets/logo.png", layout="wide")

st.image("assets/logo.png", width=200)
st.title("Blissful Gallery")

DATA_DIR = "gallery_data"
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
ARTISTS_FILE = os.path.join(DATA_DIR, "creators.json")
ARTWORKS_FILE = os.path.join(DATA_DIR, "artworks.json")
LOGO_PATH = "assets/logo.png"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# -----------------------------
# STYLE & LOGO HEADER
# -----------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Montserrat:wght@300;400;500&display=swap');

    html, body, [class*="css"] {{
        font-family:'Montserrat',sans-serif;
        background: radial-gradient(circle at 15% 20%, rgba(255,215,180,0.25), transparent 45%),
                    radial-gradient(circle at 85% 25%, rgba(200,220,255,0.25), transparent 45%),
                    radial-gradient(circle at 50% 85%, rgba(220,255,220,0.25), transparent 45%),
                    url('https://www.transparenttextures.com/patterns/canvas.png'),
                    linear-gradient(180deg, #f6f7fb 0%, #eef1f6 100%);
        background-attachment: fixed;
    }}

    h1,h2,h3{{font-family:'Playfair Display',serif;letter-spacing:0.6px;}}

    .card{{
        background: rgba(255,255,255,0.82);
        backdrop-filter: blur(10px);
        padding: 18px;
        border-radius: 20px;
        box-shadow:0 8px 30px rgba(0,0,0,0.10);
        margin-bottom:20px;
        border:1px solid rgba(212,175,55,0.25);
        position:relative;
        overflow:hidden;
    }}

    .card::before{{content: "";position:absolute;inset:0;background: radial-gradient(circle at 30% 30%, rgba(212,175,55,0.18), transparent 60%);pointer-events:none;}}

    .badge{{background: linear-gradient(135deg,#d4af37,#8c6b1f);color:white;padding:4px 9px;border-radius:10px;font-size:11px;letter-spacing:0.4px;}}

    body::after{{content:"";position:fixed;inset:0;background-image: radial-gradient(circle at center, rgba(212,175,55,0.06) 1px, transparent 1px);background-size:120px 120px;pointer-events:none;opacity:0.4;}}

    .logo-header{{display:flex;align-items:center;margin-bottom:20px;}}
    .logo-header img{{height:64px;margin-right:15px;}}
    .logo-header h1{{margin:0;}}
    </style>

    <div class='logo-header'>
        <img src='{LOGO_PATH}' alt='Blissful Gallery Logo'>
        <h1>Blissful Gallery</h1>
    </div>
    """,
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
# EXPLORE PAGE
# -----------------------------
if page == "Explore":
    st.subheader("Explore Artworks")
    search = st.text_input("Search by artwork or artist")
    category_filter = st.selectbox("Filter by category", options=["All"] + list(set([a['category'] for a in artworks])))
    for art in artworks:
        if ((search.lower() in art['title'].lower() or search.lower() in art['artist'].lower())
            and (category_filter == "All" or art['category'] == category_filter)):
            st.markdown(f"""
            <div class='card'>
            <img src='{art['image']}' alt='{art['title']}' style='width:100%;border-radius:10px;'>
            <h3>{art['title']}</h3>
            <p>By {art['artist']}</p>
            <span class='badge'>{art['category']}</span>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# FEATURED PAGE
# -----------------------------
elif page == "Featured":
    st.subheader("Featured Artists")
    for artist in [a for a in artists if a.get('featured')]:
        st.markdown(f"""
        <div class='card'>
        <h3>{artist['name']}</h3>
        <p>{artist['bio']}</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# COLLECTIONS PAGE
# -----------------------------
elif page == "Collections":
    st.subheader("Collections")
    # Placeholder for collections, can render multiple artworks grouped by collection

# -----------------------------
# ARTIST PROFILE PAGE
# -----------------------------
elif page == "Artist Profile":
    st.subheader("Artist Profile")
    selected_artist = st.selectbox("Select an artist", [a['name'] for a in artists])
    profile = next((a for a in artists if a['name'] == selected_artist), None)
    if profile:
        st.markdown(f"<h2>{profile['name']}</h2><p>{profile['bio']}</p>", unsafe_allow_html=True)
        artist_artworks = [a for a in artworks if a['artist'] == selected_artist]
        for art in artist_artworks:
            st.image(art['image'], caption=art['title'], use_column_width=True)

# -----------------------------
# APPLY PAGE
# -----------------------------
elif page == "Apply":
    st.subheader("Apply as Artist")
    name = st.text_input("Full Name")
    bio = st.text_area("Short Bio")
    category = st.text_input("Category")
    uploaded_files = st.file_uploader("Upload Artwork Images", accept_multiple_files=True, type=['png','jpg','jpeg'])

    if st.button("Submit Application"):
        artist_entry = {'name': name, 'bio': bio, 'featured': False, 'verified': False}
        artists.append(artist_entry)
        save_json(ARTISTS_FILE, artists)

        for file in uploaded_files:
            save_path = os.path.join(UPLOAD_DIR, file.name)
            with open(save_path, 'wb') as f:
                f.write(file.getbuffer())
            artworks.append({'title': file.name, 'artist': name, 'image': save_path, 'category': category})
        save_json(ARTWORKS_FILE, artworks)
        st.success("Application submitted successfully!")

# -----------------------------
# ADMIN PAGE
# -----------------------------
elif page == "Admin":
    st.subheader("Admin Dashboard")
    st.write("Approve artists, mark Featured/Verified, manage artworks")
    for idx, artist in enumerate(artists):
        col1, col2, col3 = st.columns(3)
        with col1: st.text(artist['name'])
        with col2:
            if st.button(f"Feature {artist['name']}", key=f'feat_{idx}'):
                artists[idx]['featured'] = True
                save_json(ARTISTS_FILE, artists)
        with col3:
            if st.button(f"Verify {artist['name']}", key=f'ver_{idx}'):
                artists[idx]['verified'] = True
                save_json(ARTISTS_FILE, artists)
