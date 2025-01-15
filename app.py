import os

import streamlit as st
from dotenv import load_dotenv

from utils.helpers.api import get_workflows, test_api
from utils.helpers.document_store import get_document_store
from utils.helpers.logger import logger
from utils.helpers.settings import load_settings_from_cookies
from utils.session import initialize_session_state
from utils.stages.analyze import analyze_stage
from utils.stages.generate_result_modal import rechnung_erstellen_modal
from utils.stages.result import result_stage
from utils.stages.select_bill import select_bill_stage
from utils.stages.select_distribution_pages import select_distribution_pages_stage
from utils.stages.select_documents import select_documents_stage

st.set_page_config(
    page_title="Qodia",
    page_icon="🔍🤖📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def init_app():
    """Initialize app state and configuration"""
    if "initialized" not in st.session_state:
        load_dotenv()
        settings = load_settings_from_cookies()
        initialize_session_state(settings)
        if (
            os.getenv("DEPLOYMENT_ENV") == "local"
            or os.getenv("DEPLOYMENT_ENV") == "production"
        ):
            if test_api():
                st.sidebar.success("API-Test erfolgreich. API Key ist korrekt.")
                with st.spinner("🔍 Lade Workflows..."):
                    workflows = get_workflows()
                    if workflows:
                        st.session_state.workflows = workflows
                    else:
                        st.error(
                            "Keine Kategorien verfügbar. Bitte überprüfen Sie den API Key."
                        )
                        st.session_state.workflows = None
            else:
                st.sidebar.error(
                    "API-Test fehlgeschlagen. Bitte überprüfen Sie die API-Einstellungen."
                )
                st.session_state.workflows = None

        # Register cleanup handler for app shutdown
        if "cleanup_registered" not in st.session_state:
            st.session_state.cleanup_registered = True

        # Perform cleanup of document store
        document_store = get_document_store(st.session_state.api_key)
        document_store.cleanup()

        st.session_state.initialized = True


def main() -> None:
    """Main function to control the app stages"""
    init_app()

    st.image("data/logo.png")

    stage_functions = {
        "analyze": analyze_stage,
        "select_documents": select_documents_stage,
        "select_distribution_pages": select_distribution_pages_stage,
        "select_bill": select_bill_stage,
        "result": result_stage,
    }

    current_stage = st.session_state.stage
    if stage_function := stage_functions.get(current_stage):
        stage_function()
    else:
        logger.warning(f"Unknown stage: {current_stage}")

    if (
        "show_minderung_modal" in st.session_state
        and st.session_state.show_minderung_modal
    ):
        rechnung_erstellen_modal(
            df=st.session_state.generate_df, generate=st.session_state.generate_type
        )
        # Reset the state after showing the modal
        st.session_state.show_minderung_modal = False
        st.session_state.generate_type = None
        st.session_state.generate_df = None


if __name__ == "__main__":
    main()
