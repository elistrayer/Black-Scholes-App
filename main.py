import streamlit as st
from st_pages import get_nav_from_toml

# Set the page configuration as well as page navigation settings

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav)
pg.run()