import streamlit as st
from pgn_app.paths import IMAGES_DIR

def set_layout():
    favicon = IMAGES_DIR / "favicon.jpeg"
    st.set_page_config(
        layout="wide",
        page_title="ofiscal - PePE",
        page_icon=str(favicon) if favicon.exists() else "📊",
    )

def header():
    logo = IMAGES_DIR / "transp.png"
    if logo.exists():
        st.image(str(logo))
    st.divider()
