from typing import Optional

import pandas as pd
import streamlit as st

from utils.helpers.logger import logger
from utils.helpers.telemetry import track_user_feedback
from utils.stages.feedback_modal import feedback_modal
from utils.stages.generate_result_modal import rechnung_erstellen_modal


def handle_feedback_submission(df: pd.DataFrame, generate: Optional[str] = None):
    """Handle feedback submission and modal display."""
    # Track the duration taken by the user to provide feedback
    if st.session_state.get("session_id"):
        track_user_feedback(st.session_state.session_id)
    else:
        logger.warning("Session ID not found; feedback duration not tracked.")

    # Open appropriate modal based on generate parameter
    if generate is None:
        feedback_modal(df)
    else:
        rechnung_erstellen_modal(df=df, generate=generate)
