# utils/session.py
import pandas as pd
import streamlit as st


def reset():
    # Reset the app to the initial state
    st.session_state.stage = "analyze"
    st.session_state.text = ""
    st.session_state.annotated_text_object = []
    st.session_state.df = pd.DataFrame()
    st.rerun()


def initialize_session_state(settings=None):
    """Initialize session state with defaults or from provided settings."""
    if settings is None:
        settings = {}

    # Initialize default values for session state if they don't exist
    if "stage" not in st.session_state:
        st.session_state.stage = "analyze"

    if "text" not in st.session_state:
        st.session_state.text = ""

    if "annotated_text_object" not in st.session_state:
        st.session_state.annotated_text_object = []

    if "ziffer_to_edit" not in st.session_state:
        st.session_state.ziffer_to_edit = None

    if "pdf_ready" not in st.session_state:
        st.session_state.pdf_ready = False
        st.session_state.pdf_data = None

    # Initialize using the provided settings from cookies if available
    st.session_state.api_url = settings.get("api_url", "http://localhost:8080")
    st.session_state.api_key = settings.get(
        "api_key", "AIzaSyA7lclPCmJrWwUhcAsSaXrhmU3SL2rlOzc"
    )
    st.session_state.category = settings.get("category", "Hernien-OP")

    if "selected_ziffer" not in st.session_state:
        st.session_state.selected_ziffer = None

    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

    if "df" not in st.session_state:
        data = {
            "Ziffer": [],
            "Häufigkeit": [],
            "Intensität": [],
            "Beschreibung": [],
            "Zitat": [],
            "Begründung": [],
        }

        st.session_state.df = pd.DataFrame(data)

        st.session_state.df = st.session_state.df.astype(
            {"Häufigkeit": "int", "Intensität": "int"}, errors="ignore"
        )
