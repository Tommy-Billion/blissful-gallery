import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# -------------------------
# Setup
# -------------------------
load_dotenv(".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

st.set_page_config(page_title="Blissful Gallery", layout="wide")

DATA_CREATORS = "creators.json"
DATA_ARTWORKS = "artworks.json"

# -------------------------
# Data Helpers (SAFE)
# -------------------------
def load_data(file):
    if not os.path.exists(file):
        return []

    with open(file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)


def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------------------------
# AI Helper
# -------------------------
def ai_generate(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception:
        return "AI interpretation unavailable right now."


# -------------------------
# Load Data
# -------------------------
creators = load_data(DATA_CREATORS)
artworks = load_data(DATA_ARTWORKS)

# -------------------------
# Sidebar Navigation
# -------------------------
menu = st.sidebar.radio(
    "Navigation",
    ["Home", "Explore", "Apply as Creator", "Admin"]
)

# =========================
# HOME
# =========================
if menu == "Home":
    st.title("Blissful Gallery")
    st.subheader("A Sacred Digital Sanctuary for Spiritual Creators of All Paths")
    st.divider()

    featured = [art for art in artworks if art.get("approved")]

    if featured:
        for art in featured[-3:]:
            st.image(art["image"], use_container_width=True)
            st.markdown(f"### {art['title']}")
            st.write(art["description"])
            st.caption(f"By {art['artist']}")
            st.divider()
    else:
        st.info("No artworks featured yet.")

# =========================
# EXPLORE
# =========================
elif menu == "Explore":
    st.title("Explore Blissful Gallery")

    approved_art = [art for art in artworks if art.get("approved")]

    if approved_art:
        for i, art in enumerate(approved_art):
            st.image(art["image"], use_container_width=True)
            st.markdown(f"### {art['title']}")
            st.write(art["description"])
            st.caption(f"Artist: {art['artist']}")

            if st.button(f"🔮 Interpret", key=f"interpret_{i}"):
                interpretation = ai_generate(
                    f"Give a gentle spiritual interpretation of this artwork: {art['description']}"
                )
                st.info(interpretation)

            st.divider()
    else:
        st.warning("No approved artworks yet.")

# =========================
# APPLY AS CREATOR
# =========================
elif menu == "Apply as Creator":
    st.title("Apply as a Creator")

    name = st.text_input("Your Name / Spiritual Name")
    bio = st.text_area("Short Bio")
    intention = st.text_area("Why do you create spiritual art?")
    image = st.text_input("Artwork Image URL")
    title = st.text_input("Artwork Title")
    description = st.text_area("Artwork Description")

    if st.button("Submit Application"):
        if name and bio and image and title:
            new_creator = {
                "name": name,
                "bio": bio,
                "intention": intention,
                "approved": False,
                "joined": str(datetime.now())
            }

            creators.append(new_creator)
            save_data(DATA_CREATORS, creators)

            new_art = {
                "artist": name,
                "title": title,
                "description": description,
                "image": image,
                "approved": False,
                "date": str(datetime.now())
            }

            artworks.append(new_art)
            save_data(DATA_ARTWORKS, artworks)

            st.success("Application submitted 🌿 Awaiting approval.")
        else:
            st.error("Please complete all required fields.")

# =========================
# ADMIN
# =========================
elif menu == "Admin":
    st.title("Admin Access")

    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access Granted")

        # ---- Creators ----
        st.subheader("Pending Creators")
        pending_creators = [c for c in creators if not c.get("approved")]

        if pending_creators:
            for i, creator in enumerate(pending_creators):
                st.write(f"**{creator['name']}**")
                if st.button("Approve Creator", key=f"creator_{i}"):
                    creator["approved"] = True
                    save_data(DATA_CREATORS, creators)
                    st.success("Creator approved")
        else:
            st.info("No pending creators")

        st.divider()

        # ---- Artworks ----
        st.subheader("Pending Artworks")
        pending_art = [a for a in artworks if not a.get("approved")]

        if pending_art:
            for i, art in enumerate(pending_art):
                st.write(f"**{art['title']}** by {art['artist']}")
                if st.button("Approve Artwork", key=f"art_{i}"):
                    art["approved"] = True
                    save_data(DATA_ARTWORKS, artworks)
                    st.success("Artwork approved")
        else:
            st.info("No pending artworks")

    elif password != "":
        st.error("Incorrect password")