from typing import Optional

import pandas as pd
import streamlit as st

from utils.helpers.api import generate_pdf
from utils.helpers.padnext import generate_pad, generate_padnext
from utils.stages.feedback_modal import feedback_form, process_and_send_feedback

# Define options for 'Minderung Prozentsatz'
MINDERUNG_OPTIONS = ["keine", "15%", "25%"]


@st.dialog("Rechnung erstellen", width="large")
def rechnung_erstellen_modal(df: pd.DataFrame, generate: Optional[str] = None) -> None:
    original_df = st.session_state.original_df

    st.write(
        "Bitte wählen Sie den Minderung Prozentsatz und geben Sie eine Begründung an:"
    )

    # Minderung Prozentsatz selection (mandatory)
    prozentsatz = st.selectbox(
        "Minderung Prozentsatz",
        MINDERUNG_OPTIONS,
        index=None,
        key="minderung_prozentsatz",
        placeholder="Bitte wählen ...",
    )

    # Dynamically set the Begründung based on selection
    if prozentsatz == "15%":
        begruendung_default = "Abzgl. 15% Minderung gem. §6a Abs.1 GOÄ"
    elif prozentsatz == "25%":
        begruendung_default = "Abzgl. 25% Minderung gem. §6a Abs.1 GOÄ"
    else:
        begruendung_default = ""

    begruendung = st.text_input(
        "Begründung",
        value=begruendung_default,
        key="minderung_begruendung",
        placeholder="Bitte geben Sie eine Begründung an ...",
    )

    # Store selected values in session state
    st.session_state["minderung_data"]["prozentsatz"] = prozentsatz
    st.session_state["minderung_data"]["begruendung"] = begruendung

    # Display Feedback section
    feedback_form(original_df, df)

    # Disable button until mandatory fields are filled
    if not prozentsatz:
        st.button(
            "Rechnung generieren",
            disabled=True,
            help="Bitte wählen Sie einen Minderung Prozentsatz und geben Sie eine Begründung an.",
            type="primary",
        )
    else:
        if st.button("Rechnung generieren", type="primary"):
            if generate == "pdf":
                try:
                    st.session_state.pdf_data = generate_pdf(df)
                    st.session_state.pdf_ready = True
                except Exception as e:
                    st.error(f"Failed to generate PDF : {str(e)}")
            elif generate == "pad_positionen":
                st.session_state.pad_data = generate_pad(df)
                st.session_state.pad_ready = True
            elif generate == "pad_next":
                pad_data_ready = generate_padnext(df)
                st.session_state.pad_data_ready = pad_data_ready

            process_and_send_feedback(df)

            st.rerun()
