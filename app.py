import streamlit as st
from dotenv import load_dotenv

from utils.helpers.logger import logger
from utils.helpers.settings import load_settings_from_cookies, settings_sidebar
from utils.session import configure_page, initialize_session_state
from utils.stages.analyze import analyze_stage
from utils.stages.anonymize import anonymize_stage
from utils.stages.edit_anonymized import edit_anonymized_stage
from utils.stages.rechnung_anonymize import rechnung_anonymize_stage
from utils.stages.result import result_stage


def init_app():
    """Initialize app state and configuration"""
    if "initialized" not in st.session_state:
        load_dotenv()
        settings = load_settings_from_cookies()
        initialize_session_state(settings)
        configure_page()
        st.session_state.initialized = True


def main() -> None:
    """Main function to control the app stages"""
    init_app()

    st.image("data/logo.png")
    settings_sidebar()

    stage_functions = {
        "analyze": analyze_stage,
        "anonymize": anonymize_stage,
        "edit_anonymized": edit_anonymized_stage,
        "result": result_stage,
        "rechnung_anonymize": rechnung_anonymize_stage,
    }

    current_stage = st.session_state.stage
    if stage_function := stage_functions.get(current_stage):
        stage_function()
    else:
        logger.warning(f"Unknown stage: {current_stage}")


if __name__ == "__main__":
    main()
