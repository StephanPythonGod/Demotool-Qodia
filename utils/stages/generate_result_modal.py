from typing import Optional

import pandas as pd
import streamlit as st

from utils.helpers.api import generate_pdf
from utils.helpers.padnext import generate_pad, generate_padnext

# Define options for 'Minderung Prozentsatz'
MINDERUNG_OPTIONS = ["keine", "15%", "25%"]


@st.dialog("Rechnung erstellen")
def rechnung_erstellen_modal(df: pd.DataFrame, generate: Optional[str] = None) -> None:
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
    if "minderung_data" not in st.session_state:
        st.session_state["minderung_data"] = {}
    st.session_state["minderung_data"]["prozentsatz"] = prozentsatz
    st.session_state["minderung_data"]["begruendung"] = begruendung

    # Disable button until mandatory fields are filled
    if not prozentsatz:
        st.button(
            "Generieren",
            disabled=True,
            help="Bitte wählen Sie einen Minderung Prozentsatz und geben Sie eine Begründung an.",
            type="primary",
        )
    else:
        if st.button("Generieren", type="primary"):
            with st.spinner("Generiere Dokument..."):
                try:
                    if generate == "pdf":
                        st.session_state.pdf_data = generate_pdf(df)
                        st.session_state.pdf_ready = True
                        st.success("PDF wurde erfolgreich generiert!")
                    elif generate == "pad_positionen":
                        st.session_state.pad_data = generate_pad(df)
                        st.session_state.pad_ready = True
                        st.success("PAD Positionen wurden erfolgreich generiert!")
                    elif generate == "pad_next":
                        st.session_state.pad_data_ready = generate_padnext(df)
                        st.success("PADnext Datei wurde erfolgreich generiert!")
                except Exception as e:
                    st.error(f"Fehler beim Generieren: {str(e)}")
                    return

            # Show download button based on generated content
            if generate == "pdf" and st.session_state.pdf_ready:
                st.download_button(
                    label="Download PDF",
                    data=st.session_state.pdf_data,
                    file_name="generated_pdf.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            elif generate == "pad_positionen" and st.session_state.pad_ready:
                st.download_button(
                    label="Download PAD Positionen",
                    data=st.session_state.pad_data,
                    file_name="pad_positionen.xml",
                    mime="application/xml",
                    use_container_width=True,
                )
            elif generate == "pad_next" and st.session_state.pad_data_ready:
                with open(st.session_state.pad_data_ready, "rb") as f:
                    padnext_file_data = f.read()
                st.download_button(
                    label="Download PADnext Datei",
                    data=padnext_file_data,
                    file_name=st.session_state.pad_data_ready.name,
                    mime="application/zip",
                    use_container_width=True,
                )
