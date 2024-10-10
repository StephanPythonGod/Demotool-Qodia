import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional

import streamlit as st
from streamlit_cookies_controller import CookieController

from utils.helpers.api import test_api

# Initialize the cookie controller
controller = CookieController()


def get_cookie(cookie_name: str) -> Optional[str]:
    """
    Retrieve a cookie value by name.
    Args:
        cookie_name (str): The name of the cookie to retrieve.
    Returns:
        Optional[str]: The value of the cookie if it exists, None otherwise.
    """
    return controller.get(cookie_name)


def set_cookie(cookie_name: str, value: str, secure: bool = True) -> None:
    """
    Set a cookie with the given name and value.
    Args:
        cookie_name (str): The name of the cookie to set.
        value (str): The value to store in the cookie.
        secure (bool, optional): Whether to set the Secure attribute. Defaults to True.
    """
    expires = datetime.now() + timedelta(days=180)
    controller.set(
        cookie_name,
        value,
        expires=expires,
        path="/",
        secure=secure,
        same_site="lax",
    )


def load_settings_from_cookies() -> Dict[str, str]:
    """
    Load settings from cookies and return them as a dictionary.
    Returns:
        Dict[str, str]: A dictionary containing the loaded settings.
    """
    return {
        "api_url": get_cookie("api_url") or None,
        "api_key": get_cookie("api_key") or None,
        "category": get_cookie("category") or None,
    }


def save_settings_to_cookies() -> None:
    """Save the current session state settings to cookies."""
    set_cookie("api_url", st.session_state.api_url)
    set_cookie("api_key", st.session_state.api_key)
    set_cookie("category", st.session_state.category)


def hash_input(input_string: str) -> str:
    """
    Hash the input string using SHA-256.
    Args:
        input_string (str): The string to be hashed.
    Returns:
        str: The hashed string.
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


def settings_sidebar() -> None:
    """Display the settings sidebar in the Streamlit app."""
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
        category_options = ["Hernien-OP", "Knie-OP", "Zahn-OP"]
        st.session_state.category = st.selectbox(
            "Kategorie",
            options=category_options,
            index=category_options.index(st.session_state.category),
            help="Hier kann die Kategorie der Leistungsziffern geändert werden, die für die Analyse des Textes verwendet wird.",
        )

        # New fields for Arzt and Kassenname
        arzt_input = st.text_input(
            "Arzt",
            value="",
            help="Optional: Geben Sie den Namen des Arztes ein.",
        ).strip()
        kassenname_input = st.text_input(
            "Kassenname",
            value="",
            help="Optional: Geben Sie den Namen der Krankenkasse ein.",
        ).strip()

        # Hash and store the new inputs if they are not empty
        if arzt_input:
            st.session_state.arzt_hash = hash_input(arzt_input)
        else:
            st.session_state.arzt_hash = None

        if kassenname_input:
            st.session_state.kassenname_hash = hash_input(kassenname_input)
        else:
            st.session_state.kassenname_hash = None

        if st.button("Save Settings"):
            with st.spinner("🔍 Teste API Einstellungen..."):
                if test_api():
                    save_settings_to_cookies()
                    st.success("Einstellungen erfolgreich gespeichert!")
                else:
                    st.error(
                        "API-Test fehlgeschlagen. Bitte überprüfen Sie die Einstellungen."
                    )
