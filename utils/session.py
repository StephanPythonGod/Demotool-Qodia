import os  # For accessing environment variables
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

from utils.helpers.background import get_thread_pool
from utils.helpers.document_store import get_document_store
from utils.helpers.logger import logger


def reset() -> None:
    """Reset the app to its initial state and rerun the script."""
    st.session_state.text = None
    st.session_state.annotated_text_object = []
    st.session_state.df = pd.DataFrame()
    st.session_state.analyze_api_response = None
    st.session_state.ocr_api_response = None
    st.session_state.pad_ready = False
    st.session_state.pad_data_path = None
    st.session_state.pad_data_ready = False
    st.session_state.ziffer_to_edit = None
    st.session_state.pdf_ready = False
    st.session_state.pdf_data = None
    st.session_state.selected_ziffer = None
    st.session_state.uploaded_file = None
    st.session_state.original_df = None

    if "current_highlighted_pdf" in st.session_state:
        del st.session_state.current_highlighted_pdf

    # Add these new resets

    # cleanup_session_state()


def cleanup_resources():
    """Clean up resources when the application exits."""
    try:
        # Clean up document store
        if "document_store" in st.session_state:
            st.session_state.document_store.cleanup()
            del st.session_state.document_store

        # Cancel any pending futures
        if "futures" in st.session_state:
            for future in st.session_state.futures:
                future.cancel()
            st.session_state.futures.clear()

        # Shutdown thread pool
        if "thread_pool" in st.session_state:
            st.session_state.thread_pool.shutdown(wait=True, cancel_futures=True)
            del st.session_state.thread_pool

        # Clear upload state
        if "document_uploader" in st.session_state:
            del st.session_state.document_uploader

    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)


def initialize_session_state(settings: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize Streamlit session state with default values or from provided settings.

    Args:
        settings (Optional[Dict[str, Any]]): Optional dictionary with keys like
        'api_url', 'api_key', and 'category'. Default values will be used if not provided.

    The session state fields initialized include:
        - stage: the current stage of the app, default is "analyze"
        - text: text to be analyzed, default is an empty string
        - annotated_text_object: holds annotated text, default is an empty list
        - ziffer_to_edit: an editable item in the app, default is None
        - pdf_ready: flag indicating if a PDF is ready for download, default is False
        - pdf_data: binary data for the PDF, default is None
        - api_url: API endpoint, default is "URL der API"
        - api_key: API key for authentication, default is "Ihr API Schlüssel"
        - category: default category, default is "Hernien-OP"
        - selected_ziffer: currently selected item, default is None
        - uploaded_file: file uploaded by the user, default is None
        - df: pandas DataFrame holding some default structured data, with specific column types
    """

    # Export environment variables to the current environment for Monitoring
    if settings is None:
        settings = {}

    # Initialize or reset session state variables if they do not exist
    st.session_state.setdefault("stage", "analyze")
    st.session_state.setdefault("text", None)
    st.session_state.setdefault("annotated_text_object", [])
    st.session_state.setdefault("ziffer_to_edit", None)
    st.session_state.setdefault("pdf_ready", False)
    st.session_state.setdefault("pdf_data", None)
    st.session_state.setdefault("pdf_report_data", None)
    st.session_state.setdefault("analyze_api_response", None)
    st.session_state.setdefault("ocr_api_response", None)
    st.session_state.setdefault("user_comment", None)
    st.session_state.setdefault("pad_ready", False)
    st.session_state.setdefault("pad_data_path", None)
    st.session_state.setdefault("pad_data_ready", False)
    st.session_state.setdefault("arzt_hash", None)
    st.session_state.setdefault("kassenname_hash", None)
    st.session_state.setdefault("session_id", None)
    st.session_state.setdefault(
        "minderung_data", {"prozentsatz": None, "begruendung": None}
    )
    st.session_state.setdefault("new_file_uploaded", False)

    # Initialize page selection related state
    st.session_state.setdefault("page_selection", [])
    st.session_state.setdefault("page_range", {"start": 1, "end": 1})
    st.session_state.setdefault("current_set", 0)
    st.session_state.setdefault("page_cache", {})
    st.session_state.setdefault("loaded_pages", {})
    st.session_state.setdefault("overlay_removed", False)
    st.session_state.setdefault("page_selections", {})
    st.session_state.setdefault("processing_started", False)

    # Load API URL and API Key with the following hierarchy: settings > environment variable > fallback
    st.session_state.api_url = settings.get("api_url") or os.getenv(
        "API_URL", "URL der API"
    )
    st.session_state.api_key = settings.get("api_key") or os.getenv(
        "API_KEY", "Ihr API Schlüssel"
    )

    # Default category if not in settings
    st.session_state.category = settings.get("category") or None

    st.session_state.setdefault("selected_ziffer", None)
    st.session_state.setdefault("uploaded_file", None)
    st.session_state.setdefault("sidebar_state", None)

    # Initialize an empty DataFrame with specific columns and types
    if "df" not in st.session_state:
        data = {
            "ziffer": [],
            "anzahl": [],
            "faktor": [],
            "text": [],
            "zitat": [],
            "begruendung": [],
            "confidence": [],
            "analog": [],
            "einzelbetrag": [],
            "gesamtbetrag": [],
            "go": [],
            "confidence_reason": [],
        }
        df = pd.DataFrame(data)
        st.session_state.df = df.astype(
            {
                "anzahl": "int",
                "faktor": "int",
                "einzelbetrag": "float",
                "gesamtbetrag": "float",
            },
            errors="ignore",
        )

    # Add new session state variables for document management
    st.session_state.setdefault("selected_document_id", None)
    st.session_state.setdefault(
        "show_document_list", True
    )  # Controls sidebar visibility

    # Initialize document store if API key is available
    if st.session_state.api_key != "Ihr API Schlüssel":
        get_document_store()
        get_thread_pool()

    # Initialize page_selections as a set
    if "page_selections" not in st.session_state or not isinstance(
        st.session_state.page_selections, set
    ):
        st.session_state.page_selections = set()
    st.session_state.setdefault("selected_workflow", None)
