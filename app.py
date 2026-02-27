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

        with open(DATA_FILE,"r") as f:

            return json.load(f)

    except:

        return []


# ====================================
# SAFE DATABASE SAVE
# ====================================

def save_artists(data):

    with open(DATA_FILE,"w") as f:

        json.dump(data,f,indent=4)


# ====================================
# LOGO
# ====================================

logo_path = "assets/blissful_logo.png"

if os.path.exists(logo_path):

    st.image(logo_path, width=150)

st.title("🌿 Blissful Gallery")
st.caption("Universal Spiritual Art Sanctuary")


# ====================================
# NAVIGATION
# ====================================

menu = st.sidebar.selectbox(

    "Menu",

    [

        "Gallery",

        "Apply as Artist",

        "Admin Panel"

    ]
)


# ====================================
# GALLERY PAGE
# ====================================

if menu == "Gallery":

    st.header("Art Gallery")

    artists = load_artists()

    approved_artists = [

        a for a in artists

        if a["status"] == "Approved"

    ]


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


                st.write("**Artist:**",artist["name"])

                st.write("**Title:**",artist["title"])

                st.write("**About:**",artist["bio"])

                st.caption(artist["date"])

            index += 1



# ====================================
# ARTIST APPLICATION
# ====================================

if menu == "Apply as Artist":

    st.header("Artist Application")

    name = st.text_input("Artist Name")

    title = st.text_input("Artwork Title")

    bio = st.text_area("Artist Bio")

    uploaded_file = st.file_uploader(

        "Upload Artwork",

        type=["png","jpg","jpeg"]

    )


    submit = st.button("Submit Application")


    if submit:

        if name == "" or title == "" or bio == "" or uploaded_file is None:

            st.error("Please fill all fields.")


        else:

            try:

                artists = load_artists()


                # Duplicate protection

                for artist in artists:

                    if artist["title"].lower() == title.lower():

                        st.error("Artwork title already exists.")

                        st.stop()


                # Safe filename

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                safe_name = name.replace(" ","_")

                filename = f"{safe_name}_{timestamp}.jpg"

                file_path = os.path.join(

                    UPLOAD_FOLDER,

                    filename

                )


                # Verify image

                image = Image.open(uploaded_file)

                image.save(file_path)


                # Artist record

                new_artist = {

                    "name":name,

                    "title":title,

                    "bio":bio,

                    "image_path":file_path,

                    "date":datetime.now().strftime("%Y-%m-%d"),

                    "status":"Pending"

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


    password = st.text_input(

        "Admin Password",

        type="password"

    )


    if password != "blissfuladmin":

        st.warning("Enter admin password")

        st.stop()


    artists = load_artists()

    pending = [

        a for a in artists

        if a["status"] == "Pending"

    ]


    if len(pending) == 0:

        st.success("No pending artists.")


    for artist in pending:

        st.divider()

        st.write("Artist:",artist["name"])

        st.write("Title:",artist["title"])

        st.write("Bio:",artist["bio"])


        if os.path.exists(artist["image_path"]):

            st.image(artist["image_path"])


        col1,col2 = st.columns(2)


        if col1.button(

            f"Approve {artist['title']}"

        ):

            artist["status"] = "Approved"

            save_artists(artists)

            st.rerun()


        if col2.button(

            f"Reject {artist['title']}"

        ):

            artists.remove(artist)

            save_artists(artists)

            st.rerun()