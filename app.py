import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image

# ====================================
# BLISSFUL GALLERY CONFIGURATION
# ====================================

st.set_page_config(
    page_title="Blissful Gallery",
    page_icon="assets/logo_favicon.png",
    layout="wide"
)

# ====================================
# AUTO CREATE FOLDERS
# ====================================

DATA_FOLDER = "data"
UPLOAD_FOLDER = "uploads"
ASSETS_FOLDER = "assets"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)

DATA_FILE = os.path.join(DATA_FOLDER, "artists.json")

# ====================================
# INITIALIZE DATABASE
# ====================================

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# ====================================
# SAFE DATABASE LOAD
# ====================================

def load_artists():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# ====================================
# SAFE DATABASE SAVE
# ====================================

def save_artists(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ====================================
# SESSION STATE
# ====================================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ====================================
# HEADER LOGO
# ====================================

logo_header_path = os.path.join(ASSETS_FOLDER, "logo_header.png")
if os.path.exists(logo_header_path):
    st.image(logo_header_path, width=150)

st.title("Blissful Gallery")
st.caption("Universal Art Gallery")

# ====================================
# NAVIGATION
# ====================================

menu = st.sidebar.selectbox(
    "Menu",
    ["Gallery", "Apply as Artist", "Admin Panel"]
)

# ====================================
# GALLERY PAGE
# ====================================

if menu == "Gallery":
    st.header("Art Gallery")
    artists = load_artists()
    approved_artists = [a for a in artists if a["status"] == "Approved"]

    if len(approved_artists) == 0:
        st.info("No approved artworks yet.")
    else:
        cols = st.columns(3)
        index = 0
        for artist in approved_artists:
            with cols[index % 3]:
                if os.path.exists(artist["image_path"]):
                    st.image(artist["image_path"])
                else:
                    st.warning("Image Missing")

                st.write("**Artist:**", artist["name"])
                st.write("**Title:**", artist["title"])
                st.write("**About:**", artist["bio"])
                st.caption(artist["date"])
            index += 1

# ====================================
# APPLY AS ARTIST
# ====================================

if menu == "Apply as Artist":
    st.header("Artist Application")

    name = st.text_input("Artist Name")
    title = st.text_input("Artwork Title")
    bio = st.text_area("Artist Bio")
    uploaded_file = st.file_uploader("Upload Artwork", type=["png", "jpg", "jpeg"])

    if st.button("Submit Application"):
        if not name or not title or not bio or uploaded_file is None:
            st.error("Please fill all fields.")
        else:
            try:
                artists = load_artists()

                for artist in artists:
                    if artist["title"].lower() == title.lower():
                        st.error("Artwork title already exists.")
                        st.stop()

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                safe_name = name.replace(" ", "_")
                filename = f"{safe_name}_{timestamp}.jpg"
                file_path = os.path.join(UPLOAD_FOLDER, filename)

                image = Image.open(uploaded_file)
                image.save(file_path)

                new_artist = {
                    "name": name,
                    "title": title,
                    "bio": bio,
                    "image_path": file_path,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "status": "Pending"
                }

                artists.append(new_artist)
                save_artists(artists)

                st.success("Application Submitted!")
                st.info("Awaiting Approval")
                st.image(file_path)

            except Exception as e:
                st.error("Upload Failed")
                st.write(e)

# ====================================
# ADMIN PANEL
# ====================================

if menu == "Admin Panel":

    st.header("Admin Panel")

    if not st.session_state.admin_logged_in:

        with st.form("admin_login_form"):
            password = st.text_input("Enter Admin Password", type="password")
            submitted = st.form_submit_button("Enter")

        if submitted:
            if password == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.admin_logged_in = True
                st.success("Access Granted")
                st.rerun()
            else:
                st.error("Incorrect Password")

    else:

        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

        artists = load_artists()
        pending = [a for a in artists if a["status"] == "Pending"]

        if len(pending) == 0:
            st.success("No pending artists.")

        for artist in pending:
            st.divider()
            st.write("Artist:", artist["name"])
            st.write("Title:", artist["title"])
            st.write("Bio:", artist["bio"])

            if os.path.exists(artist["image_path"]):
                st.image(artist["image_path"])

            col1, col2 = st.columns(2)

            if col1.button(f"Approve {artist['title']}"):
                artist["status"] = "Approved"
                save_artists(artists)
                st.rerun()

            if col2.button(f"Reject {artist['title']}"):
                artists.remove(artist)
                save_artists(artists)
                st.rerun()