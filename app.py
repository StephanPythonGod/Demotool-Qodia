import streamlit as st
from dotenv import load_dotenv

from utils.helpers.logger import logger
from utils.helpers.settings import load_settings_from_cookies, settings_sidebar
from utils.session import initialize_session_state
from utils.stages.analyze import analyze_stage
from utils.stages.anonymize import anonymize_stage
from utils.stages.edit_anonymized import edit_anonymized_stage
from utils.stages.result import result_stage

# Load env variables from .env file
load_dotenv()

# Load settings from cookies before initializing session state
settings = load_settings_from_cookies()

# Now initialize the session state using the loaded settings
initialize_session_state(settings)

st.set_page_config(
    page_title="Qodia",
    page_icon="🔍🤖📚",
    layout="wide",  # Set the page layout to wide
    initial_sidebar_state="collapsed",
)


def main() -> None:
    """Main function to control the app stages based on session state."""
    st.title("Qodia")

    # Display the settings sidebar
    settings_sidebar()

    # Define stage-to-function mapping
    stage_functions = {
        "analyze": analyze_stage,
        "anonymize": anonymize_stage,
        "edit_anonymized": edit_anonymized_stage,
        "result": result_stage,
    }

    # Retrieve the current stage
    current_stage = st.session_state.stage

    # Call the appropriate stage function based on session state
    stage_function = stage_functions.get(current_stage)
    if stage_function:
        stage_function()
    else:
        logger.warning(f"Unknown stage: {current_stage}")


if __name__ == "__main__":
    main()
