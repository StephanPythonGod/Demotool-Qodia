import os
from io import BytesIO
from typing import Union

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_paste_button import paste_image_button as pbutton

from utils.helpers.api import (
    analyze_api_call,
    check_if_default_credentials,
    ocr_pdf_to_text_api,
)
from utils.helpers.files import (
    create_uploaded_file_from_binary,
    list_files_by_extension,
)
from utils.helpers.logger import logger
from utils.helpers.padnext import handle_padnext_upload
from utils.helpers.telemetry import track_api_response
from utils.helpers.transform import annotate_text_update
from utils.stages.pad_modal import pad_file_modal

# Check for the environment variable DEPLOYMENT_ENV, default to 'local' if not set
DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "local")


def analyze_add_data(data: list[dict]) -> dict:
    """Add all necessary data for the frontend.

    Args:
        data (list[dict]): A list of dictionaries with 'zitat', 'begruendung', 'goa_ziffer'.

    Returns:
        dict: Dictionary with keys 'ziffer', 'anzahl', 'faktor', 'text', 'zitat', and 'begruendung'.
    """
    try:
        new_data = {
            "ziffer": [],
            "anzahl": [],
            "faktor": [],
            "text": [],
            "zitat": [],
            "begruendung": [],
            "erschwerende_bedingungen": [],
            "confidence": [],
            "analog": [],
            "einzelbetrag": [],
            "gesamtbetrag": [],
            "go": [],
            "confidence_reason": [],
        }

        for entry in data:
            new_data["ziffer"].append(entry.get("ziffer", ""))
            new_data["zitat"].append(entry.get("zitat", ""))
            new_data["begruendung"].append(entry.get("begruendung", ""))
            new_data["erschwerende_bedingungen"].append(
                entry.get("erschwerende_bedingungen", "")
            )
            new_data["anzahl"].append(entry.get("anzahl", 0))
            new_data["faktor"].append(entry.get("faktor", 0))
            new_data["text"].append(entry.get("text", ""))
            new_data["confidence"].append(entry.get("confidence", 1.0))
            new_data["analog"].append(entry.get("analog", ""))
            new_data["einzelbetrag"].append(entry.get("einzelbetrag", 0))
            new_data["gesamtbetrag"].append(entry.get("gesamtbetrag", 0))
            new_data["go"].append(entry.get("go", ""))
            new_data["confidence_reason"].append(entry.get("confidence_reason", ""))

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

            if data is not None:
                processed_data = analyze_add_data(data)
                st.session_state.df = pd.DataFrame(processed_data)
                annotate_text_update()
                st.session_state.update(session_id=track_api_response())
                st.session_state.update(stage="result")
                return True
            else:
                return False

    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        st.error("Fehler bei der Textanalyse. Bitte versuchen Sie es erneut.")


def perform_ocr(file: Union[Image.Image, UploadedFile]) -> bool:
    """
    Perform OCR on the uploaded file using Qodia API.

    Args:
        file (Union[Image.Image, UploadedFile]): Uploaded file object.

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
        st.error("Fehler bei der Textextraktion. Bitte versuchen Sie es erneut.")
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
        # If uploaded file exists in session state, it takes priority
        if st.session_state.uploaded_file and not st.session_state.new_file_uploaded:
            logger.info("Using uploaded file.")
            return st.session_state.uploaded_file

        # If pasted image exists, it takes priority
        if paste_result.image_data:
            logger.info("Using pasted image data.")

            # Convert the PngImageFile to bytes
            image = paste_result.image_data  # Assuming this is a PngImageFile object
            image_bytes_io = BytesIO()
            image.save(
                image_bytes_io, format="PNG"
            )  # Save image to BytesIO in PNG format
            image_bytes = image_bytes_io.getvalue()  # Get the raw bytes

            return create_uploaded_file_from_binary(
                binary_data=image_bytes,
                file_name="pasted_image.png",
                mime_type="image/png",
            )

        # If file upload exists, return the uploaded file
        if file_upload:
            logger.info("File uploaded successfully.")
            if st.session_state.new_file_uploaded:
                st.session_state.new_file_uploaded = False
            return file_upload

        return None
    except Exception as e:
        logger.error(f"Error processing file upload or paste: {e}")
        st.error("Fehler bei der Verarbeitung der Datei oder des Bildes.")
        return None


def handle_pad_file_selection():
    if st.session_state.get("file_selected"):
        st.session_state.file_selected = False  # Reset the flag
        return True
    return False


def file_upload_callback():
    if st.session_state.uploaded_file:
        st.session_state.new_file_uploaded = True


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
        if analyze_text(st.session_state.text):
            st.rerun()

    right_column.subheader("Dokument hochladen")
    right_column.markdown(
        "Laden Sie entweder ein PDF-Dokument, ein Bild oder eine PADnext Datei hoch oder fügen Sie ein Bild aus der Zwischenablage ein."
    )

    file_upload = right_column.file_uploader(
        "PDF Dokument auswählen",
        type=["pdf", "png", "jpg", "zip"],
        label_visibility="collapsed",
        on_change=file_upload_callback,
    )

    with right_column:
        paste_result = pbutton(
            label="Aus Zwischenablage einfügen",
            text_color="#ffffff",
            background_color="#FF4B4B",
            hover_background_color="#FF3333",
        )

    uploaded_file = handle_file_upload(file_upload, paste_result)

    if (
        uploaded_file
        and uploaded_file.name.split(".")[-1].lower() in ["zip"]
        and not st.session_state.uploaded_file
    ):
        try:
            padx_folder_path = handle_padnext_upload(uploaded_file)
            st.session_state.pad_data_path = padx_folder_path
            all_files = list_files_by_extension(padx_folder_path, ["pdf", "png", "jpg"])
            pad_file_modal(all_files)
        except Exception as e:
            logger.error(f"Error handling PADnext file: {e}")
            st.error(f"Fehler beim Verarbeiten der PADnext-Datei: {e}")

    if handle_pad_file_selection():
        st.rerun()

    def is_valid_file(file):
        return file and file.name.split(".")[-1].lower() in ["pdf", "png", "jpg"]

    if is_valid_file(uploaded_file) or is_valid_file(st.session_state.uploaded_file):
        st.session_state.uploaded_file = uploaded_file

        if st.session_state.uploaded_file:
            # Cloud environment logic
            if DEPLOYMENT_ENV == "cloud":
                right_column.warning(
                    "Dokument erfolgreich hochgeladen. Der Text wird automatisch extrahiert.",
                    icon="✅",
                )
                # Perform OCR only if text is not already extracted
                if not st.session_state.text:
                    if perform_ocr(uploaded_file):
                        st.rerun()

            # Local environment logic
            elif DEPLOYMENT_ENV == "local" or DEPLOYMENT_ENV == "development":
                right_column.warning(
                    "Dokument erfolgreich hochgeladen. Bitte wählen Sie eine der folgenden Optionen aus.",
                    icon="✅",
                )

                # Show anonymization options
                button_col1, _, button_col2 = right_column.columns([1, 1, 1])

                if button_col1.button("Anonymisieren", type="primary"):
                    st.session_state.stage = "anonymize"
                    st.rerun()

                if button_col2.button("Keine Anonymisierung Notwendig", type="primary"):
                    if perform_ocr(uploaded_file):
                        st.rerun()
