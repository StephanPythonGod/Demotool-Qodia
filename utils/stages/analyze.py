import os
from datetime import datetime
from io import BytesIO

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_paste_button import paste_image_button as pbutton

from utils.helpers.background import queue_document
from utils.helpers.distribution_store import DistributionStatus, get_distribution_store
from utils.helpers.document_store import (
    get_document_store,
    render_document_list_sidebar,
)
from utils.helpers.logger import logger
from utils.helpers.settings import settings_sidebar


def handle_clipboard_paste(paste_result) -> None:
    """Handle image pasted from clipboard."""
    if not paste_result.image_data:
        return

    try:
        # Convert PIL Image to bytes
        image = paste_result.image_data
        image_bytes_io = BytesIO()
        image.save(image_bytes_io, format="PNG")
        image_bytes = image_bytes_io.getvalue()

        # Create a unique filename for the pasted image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clipboard_{timestamp}.png"

        # Queue the document for processing
        queue_document(
            document_id=filename, file_data=image_bytes, file_type="image/png"
        )

        st.success(f"Bild '{filename}' wurde erfolgreich zur Verarbeitung hinzugefügt")

    except Exception as e:
        logger.error(f"Error processing clipboard image: {e}", exc_info=True)
        st.error("Fehler beim Verarbeiten des Bildes aus der Zwischenablage")


def handle_file_upload(
    uploaded_files: list[UploadedFile], from_sidebar: bool = False
) -> None:
    """Handle multiple file uploads."""
    if not uploaded_files:
        return

    # Initialize processed_files in session state if it doesn't exist
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()

    should_rerun = False

    for uploaded_file in uploaded_files:
        if uploaded_file.name in st.session_state.processed_files:
            continue

        try:
            # Get document store
            document_store = get_document_store(st.session_state.api_key)

            # Store the file
            document_store.store_document_file(
                document_id=uploaded_file.name,
                file_data=uploaded_file.getvalue(),
                file_type=uploaded_file.type,
            )

            # Add document to database
            document_store.add_document(uploaded_file.name)

            st.session_state.processed_files.add(uploaded_file.name)
            st.success(f"Dokument '{uploaded_file.name}' wurde erfolgreich hochgeladen")
            should_rerun = True

        except Exception as e:
            logger.error(
                f"Error storing document {uploaded_file.name}: {e}", exc_info=True
            )
            st.error(f"Fehler beim Hochladen von {uploaded_file.name}: {str(e)}")

    # Only trigger rerun for sidebar uploads and when files were actually processed
    if should_rerun and from_sidebar:
        if st.session_state.stage != "select_documents":
            st.session_state.stage = "select_documents"
        st.rerun()
    elif should_rerun:
        st.session_state.stage = "select_documents"
        st.rerun()


def handle_distribution_upload(uploaded_file: UploadedFile) -> None:
    """Handle distribution document upload."""
    if not uploaded_file:
        return

    try:
        # Get distribution store
        distribution_store = get_distribution_store()

        # Store the file
        distribution_store.store_document_file(
            document_id=uploaded_file.name, file_data=uploaded_file.getvalue()
        )

        # Add document to database
        distribution_store.add_document(uploaded_file.name)

        # Set session state for distribution document
        st.session_state.distribution_document_id = uploaded_file.name
        st.session_state.stage = "select_distribution_pages"
        st.rerun()

    except Exception as e:
        logger.error(
            f"Error storing distribution document {uploaded_file.name}: {e}",
            exc_info=True,
        )
        st.error(f"Fehler beim Hochladen von {uploaded_file.name}")


def analyze_stage() -> None:
    """Display the analyze stage in the Streamlit app."""
    settings_sidebar()

    # Render document list sidebar
    render_document_list_sidebar()

    # Main content area with two columns
    left_col, right_col = st.columns(2)

    with left_col:
        st.title("Dokumente analysieren")

        st.markdown(
            """
        Hier können Sie ein Dokument hochladen, dass Sie analysieren möchten.
        """
        )

        st.subheader("Dokumente hochladen")
        # Disable uploader if API key hasn't been tested successfully
        uploader_disabled = st.session_state.api_key_tested is False
        if uploader_disabled:
            st.warning(
                "⚠️ Bitte speichern Sie zuerst die API-Einstellungen, bevor Sie Dokumente hochladen."
            )

        uploaded_files = st.file_uploader(
            "Dokumente hochladen",
            type=["pdf", "png", "jpg"],
            accept_multiple_files=True,
            key="document_uploader",
            label_visibility="collapsed",
            disabled=uploader_disabled,
            help="Bitte speichern Sie die API-Einstellungen erst, bevor Sie Dokumente hochladen.",
        )

        if uploaded_files:
            handle_file_upload(uploaded_files, from_sidebar=False)

        if not uploader_disabled:
            st.subheader("Aus Zwischenablage einfügen")
            paste_result = pbutton(
                label="Aus Zwischenablage einfügen",
                text_color="#ffffff",
                background_color="#FF4B4B",
                hover_background_color="#FF3333",
            )

            if paste_result.image_data:
                handle_clipboard_paste(paste_result)

    logger.info("DEPLOYMENT_ENV: %s", os.environ.get("DEPLOYMENT_ENV"))

    if os.environ.get("DEPLOYMENT_ENV") == "local":
        with right_col:
            st.title("Dokument teilen")

            st.markdown(
                """
            Hier können Sie ein Dokument hochladen, dass Sie mit uns zu Trainingszwecken teilen möchten.
            Das Dokument wird automatisch anonymisiert und kann anschließend mit einer Rechnung kombiniert werden.
            """
            )

            distribution_file = st.file_uploader(
                "Dokument zum Verteilen hochladen",
                type=["pdf"],
                accept_multiple_files=False,
                key="distribution_uploader",
                help="Laden Sie hier das zu verteilende Dokument hoch (nur PDF Format).",
            )

            if distribution_file:
                handle_distribution_upload(distribution_file)

            # Show status of distribution document if one is being processed
            if "distribution_document_id" in st.session_state:
                distribution_store = get_distribution_store()
                doc = distribution_store.get_document(
                    st.session_state.distribution_document_id
                )

                if doc:
                    status = doc["status"]
                    if status == DistributionStatus.PROCESSING.value:
                        st.info("Dokument wird verarbeitet... ⏳")
                    elif status == DistributionStatus.COMPLETED.value:
                        st.success("Dokument wurde erfolgreich verarbeitet ✅")
                    elif status == DistributionStatus.FAILED.value:
                        st.error(
                            f"Fehler bei der Verarbeitung: {doc.get('error_message', 'Unbekannter Fehler')} ❌"
                        )
                        if st.button("Erneut versuchen"):
                            # Clear session state and let user upload again
                            del st.session_state.distribution_document_id
                            st.rerun()


def analyze_text(text: str) -> bool:
    """
    Analyze the provided text and update session state.

    Args:
        text (str): The text to analyze

    Returns:
        bool: True if analysis was successful, False otherwise
    """
    try:
        # Store the text in session state
        st.session_state.text = text
        st.session_state.stage = "anonymize"
        return True
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}", exc_info=True)
        st.error(f"Fehler bei der Textanalyse: {str(e)}")
        return False
