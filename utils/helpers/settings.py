# utils/settings.py
from datetime import datetime, timedelta

import streamlit as st
from streamlit_cookies_controller import CookieController

from utils.helpers.api import test_api

controller = CookieController()


def get_cookie(cookie_name):
    return controller.get(cookie_name)


def set_cookie(cookie_name, value, secure=True):
    expires = datetime.now() + timedelta(days=180)
    controller.set(
        cookie_name,
        value,
        expires=expires,
        path="/",  # Setting the path to root
        secure=secure,  # Set Secure attribute if using HTTPS
        same_site="lax",  # Adjusting SameSite to Lax for more flexibility
    )


def load_settings_from_cookies():
    """Load settings from cookies and return them as a dictionary."""
    settings = {
        "api_url": get_cookie("api_url") or "http://localhost:8080",
        "api_key": get_cookie("api_key") or "AIzaSyA7lclPCmJrWwUhcAsSaXrhmU3SL2rlOzc",
        "category": get_cookie("category") or "Hernien-OP",
    }

    return settings


def save_settings_to_cookies():
    """Save the current session state settings to cookies."""
    set_cookie("api_url", st.session_state.api_url)
    set_cookie("api_key", st.session_state.api_key)
    set_cookie("category", st.session_state.category)


def settings_sidebar():
    """Display the settings sidebar."""
    with st.sidebar:
        st.session_state.api_url = st.text_input(
            "API URL",
            value=st.session_state.api_url,
            help="Hier kann die URL der API geändert werden, die für die Analyse des Textes verwendet wird.",
        ).strip()
        st.session_state.api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            help="Hier kann der API Key geändert werden, der für die Authentifizierung bei der API verwendet wird.",
        ).strip()
        st.session_state.category = st.selectbox(
            "Kategorie",
            options=["Hernien-OP", "Knie-OP", "Zahn-OP"],
            index=["Hernien-OP", "Knie-OP", "Zahn-OP"].index(st.session_state.category),
            help="Hier kann die Kategorie der Leistungsziffern geändert werden, die für die Analyse des Textes verwendet wird.",
        )

        if st.button("Save Settings"):
            with st.spinner("🔍 Teste API Einstellungen..."):
                working = test_api()
                if working:
                    save_settings_to_cookies()
                    st.success("Einstellungen erfolgreich gespeichert!")
