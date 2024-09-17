from io import BytesIO

import pandas as pd
import streamlit as st
from streamlit_paste_button import paste_image_button as pbutton

from utils.helpers.api import (
    analyze_api_call,
    check_if_default_credentials,
    ocr_pdf_to_text_api,
)
from utils.helpers.logger import logger
from utils.helpers.transform import annotate_text_update


def analyze_add_data(data: list[dict]) -> dict:
    """Add all necessary data for the frontend.

    Args:
        data (list[dict]): A list of dictionaries with 'zitat', 'begrundung', 'goa_ziffer'.

    Returns:
        dict: Dictionary with keys 'Ziffer', 'Häufigkeit', 'Intensität', 'Beschreibung', 'Zitat', and 'Begründung'.
    """
    try:
        new_data = {
            "Ziffer": [],
            "Häufigkeit": [],
            "Intensität": [],
            "Beschreibung": [],
            "Zitat": [],
            "Begründung": [],
        }

        for entry in data:
            new_data["Ziffer"].append(entry.get("goa_ziffer", ""))
            new_data["Zitat"].append(entry.get("zitat", ""))
            new_data["Begründung"].append(entry.get("begrundung", ""))
            new_data["Häufigkeit"].append(
                entry.get("quantitaet", 0)
            )  # Use default values if missing
            new_data["Intensität"].append(entry.get("faktor", 0))
            new_data["Beschreibung"].append(entry.get("beschreibung", ""))

        return new_data

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return {}


def analyze_text(text: str) -> None:
    """Analyze the text using the Qodia API.

    Args:
        text (str): Text to be analyzed.
    """
    try:
        with st.spinner("🤖 Analysiere den Bericht ..."):
            check_if_default_credentials()
            data = analyze_api_call(text)

            if data:
                processed_data = analyze_add_data(data)
                st.session_state.df = pd.DataFrame(processed_data)
                annotate_text_update()
                st.session_state.update(stage="result")

    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        st.error("Fehler bei der Textanalyse. Bitte versuchen Sie es erneut.")


def perform_ocr(file: BytesIO) -> bool:
    """Perform OCR on the uploaded file using Qodia API.

    Args:
        file (BytesIO): Uploaded file object.

    Returns:
        bool: True if OCR was successful, False otherwise.
    """
    try:
        with st.spinner("🔍 Extrahiere Text mittels OCR..."):
            check_if_default_credentials()
            text = ocr_pdf_to_text_api(file)
            if text:
                st.session_state.text = text
                return True
            else:
                return False
    except Exception as e:
        logger.error(f"Error performing OCR: {e}")
        st.error("Fehler bei der Textextraktion.")
        return False


def update_text() -> None:
    """Update the session state's text with the temporary text."""
    st.session_state.text = st.session_state.temp_text


def handle_file_upload(file_upload, paste_result) -> BytesIO:
    """Handle file uploads and clipboard image paste.

    Args:
        file_upload: Uploaded file via Streamlit's file uploader.
        paste_result: Pasted image data from clipboard.

    Returns:
        BytesIO: The uploaded or pasted file, if available.
    """
    try:
        # If pasted image exists, it takes priority
        if paste_result.image_data:
            logger.info("Using pasted image data.")
            return paste_result.image_data

        # If file upload exists, return the uploaded file
        if file_upload:
            logger.info("File uploaded successfully.")
            return file_upload

        return None
    except Exception as e:
        logger.error(f"Error processing file upload or paste: {e}")
        st.error("Fehler bei der Verarbeitung der Datei oder des Bildes.")
        return None


def analyze_stage() -> None:
    """Display the analyze stage in the Streamlit app."""
    left_column, right_column = st.columns(2)

    left_column.subheader("Ärztlicher Bericht:")

    # Initialize session state variables if missing
    st.session_state.setdefault("text", "")
    st.session_state.setdefault("temp_text", st.session_state.text)

    # Sync temp_text with text if needed
    if st.session_state.text != st.session_state.temp_text:
        st.session_state.temp_text = st.session_state.text

    logger.info(f"Length of text: {len(st.session_state.text)}")

    left_column.text_area(
        "Text des ärztlichen Berichts",
        key="temp_text",
        height=400,
        placeholder="Hier den Text des ärztlichen Berichts einfügen ...",
        on_change=update_text,
    )

    if left_column.button(
        "Analysieren", disabled=(not st.session_state.text), type="primary"
    ):
        analyze_text(st.session_state.text)
        st.rerun()

    right_column.subheader("Dokument hochladen")
    right_column.markdown(
        "Laden Sie entweder ein PDF-Dokument oder ein Bild hoch oder fügen Sie ein Bild aus der Zwischenablage ein."
    )

    file_upload = right_column.file_uploader(
        "PDF Dokument auswählen",
        type=["pdf", "png", "jpg"],
        label_visibility="collapsed",
    )

    with right_column:
        paste_result = pbutton(
            label="Aus Zwischenablage einfügen",
            text_color="#ffffff",
            background_color="#FF3333",
            hover_background_color="#FF4B4B",
        )

    uploaded_file = handle_file_upload(file_upload, paste_result)

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        right_column.markdown("### ✅ Dokument erfolgreich hochgeladen")
        right_column.markdown("Wählen Sie eine der folgenden Optionen aus:")
        st.warning(
            "Dokument erfolgreich hochgeladen. Bitte wählen Sie eine der folgenden Optionen aus.",
            icon="✅",
        )

        button_col1, _, button_col2 = right_column.columns([1, 1, 1])

        if button_col1.button("Anonymisieren", type="primary"):
            st.session_state.stage = "anonymize"
            st.rerun()

        if button_col2.button("Keine Anonymisierung Notwendig", type="primary"):
            if perform_ocr(uploaded_file):
                st.rerun()
