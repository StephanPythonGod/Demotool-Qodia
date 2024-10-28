import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional

import streamlit as st
from streamlit_cookies_controller import CookieController

from utils.helpers.api import get_workflows, test_api

# Initialize the cookie controller
controller = CookieController()


def get_cookie(cookie_name: str) -> Optional[str]:
    return controller.get(cookie_name)


def set_cookie(cookie_name: str, value: str, secure: bool = True) -> None:
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
    return {
        "api_url": get_cookie("api_url") or None,
        "api_key": get_cookie("api_key") or None,
        "category": get_cookie("category") or None,
        "arzt_hash": get_cookie("arzt_hash") or None,
        "kassenname_hash": get_cookie("kassenname_hash") or None,
    }


def save_settings_to_cookies() -> None:
    set_cookie("api_url", st.session_state.api_url)
    set_cookie("api_key", st.session_state.api_key)
    set_cookie("category", st.session_state.category)
    if st.session_state.arzt_hash:
        set_cookie("arzt_hash", st.session_state.arzt_hash)
    if st.session_state.kassenname_hash:
        set_cookie("kassenname_hash", st.session_state.kassenname_hash)


def hash_input(input_string: str) -> str:
    return hashlib.sha256(input_string.encode()).hexdigest()


def settings_sidebar() -> None:
    """Display the settings sidebar in the Streamlit app."""
    with st.sidebar:
        # API URL and API Key inputs
        st.session_state.api_url = st.text_input(
            "API URL",
            value=st.session_state.get("api_url", ""),
            help="Hier kann die URL der API geändert werden, die für die Analyse des Textes verwendet wird.",
        ).strip()
        st.session_state.api_key = st.text_input(
            "API Key",
            value=st.session_state.get("api_key", ""),
            help="Hier kann der API Key geändert werden, der für die Authentifizierung bei der API verwendet wird.",
        ).strip()

        if st.button("Test API"):
            with st.spinner("🔍 Teste API Einstellungen..."):
                if test_api():
                    st.success("API-Test erfolgreich! Kategorien werden geladen...")
                    # Fetch workflows once API test passes
                    workflows = get_workflows()
                    if workflows:
                        st.session_state.workflows = workflows
                    else:
                        st.error(
                            "Keine Kategorien verfügbar. Bitte überprüfen Sie den API Key."
                        )
                        st.session_state.workflows = None
                else:
                    st.error(
                        "API-Test fehlgeschlagen. Bitte überprüfen Sie die Einstellungen."
                    )
                    st.session_state.workflows = None

        # Check if workflows are available to proceed
        if st.session_state.get("workflows"):
            # Workflow selection
            st.session_state.category = st.selectbox(
                "Kategorie",
                options=st.session_state.workflows,
                index=0,
                help="Hier kann die Kategorie der Leistungsziffern geändert werden, die für die Analyse des Textes verwendet wird.",
            )

            # Optional Arzt and Kassenname inputs
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
                with st.spinner("Speichern der Einstellungen..."):
                    save_settings_to_cookies()
                    st.success("Einstellungen erfolgreich gespeichert!")
