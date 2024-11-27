from typing import Dict, List, Optional, Tuple

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.anonymization import anonymize_text
from utils.helpers.canvas import (
    base_display_file_selection_interface,
    cleanup_session_state,
    sort_selections,
)
from utils.helpers.logger import logger
from utils.helpers.ocr import perform_ocr_on_file


def _display_instructions(column: st.delta_generator.DeltaGenerator) -> None:
    """Display instructions for using the file selection interface."""
    column.markdown(
        """
        ## Anleitung zur Auswahl der Textpassagen

        Verwenden Sie das Tool auf der linken Seite, um **wichtige Textstellen** zu markieren, die extrahiert und anonymisiert werden sollen.

        ### Schritte zur Auswahl:
        1. Klicken Sie auf das Bild und ziehen Sie ein **rotes Rechteck** um den Bereich, den Sie markieren möchten. **Nur markierte Bereiche** werden extrahiert.
        2. Sie können mehrere Bereiche auf einer Seite auswählen.
        3. Um einen Bereich zu löschen, verwenden Sie die **Rückgängig-Funktion** des Tools.
        4. Sobald Sie alle relevanten Bereiche markiert haben, klicken Sie auf **„Datei Anonymisieren"** unten.
        5. Danach erscheint der anonymisierte Text auf der rechten Seite und sie können ihn nochmals bearbeiten.
        """
    )


def display_file_selection_interface(
    uploaded_file: UploadedFile,
    left_column: st.delta_generator.DeltaGenerator,
    right_column: st.delta_generator.DeltaGenerator,
) -> Tuple[Optional[List[List[Dict[str, float]]]], bool]:
    """Anonymization-specific file selection interface."""
    _display_instructions(left_column)

    selections, has_selections = base_display_file_selection_interface(
        uploaded_file=uploaded_file,
        overlay_text="Bitte die zu analysierenden Bereiche auswählen\n(Auswahl mehrerer Bereich möglich)",
        file_types=["application/pdf", "image/png", "image/jpeg", "image/jpg"],
        layout_columns=(left_column, right_column),
    )

    if selections is not None:
        # Apply anonymization-specific sorting
        selections = sort_selections(selections)

    return selections, has_selections


def anonymize_stage() -> None:
    """Display the anonymize stage and handle the anonymization process."""
    if "uploaded_file" not in st.session_state:
        st.error("No file has been uploaded. Please upload a file first.")
        return

    left_column, right_column = st.columns([1, 1])

    selections, has_selections = display_file_selection_interface(
        st.session_state.uploaded_file, left_column, right_column
    )

    # Only enable the button if there are selections
    if st.button("Datei Anonymisieren", type="primary", disabled=not has_selections):
        with st.spinner("🔍 Extrahiere Text und anonymisiere..."):
            try:
                # Sort selections before OCR processing
                sorted_selections = sort_selections(selections)

                extracted_text = perform_ocr_on_file(
                    st.session_state.uploaded_file, selections=sorted_selections
                )
                anonymize_result = anonymize_text(extracted_text)

                st.session_state.anonymized_text = anonymize_result["anonymized_text"]

                detected_entities = [
                    (entity.get("original_word"), entity.get("entity_type"))
                    for entity in anonymize_result["detected_entities"]
                    if entity.get("original_word") and entity.get("entity_type")
                ]
                st.session_state.detected_entities = detected_entities

                st.session_state.stage = "edit_anonymized"

                cleanup_session_state()
                st.rerun()

            except Exception as e:
                logger.error(f"Error during anonymization process: {e}")
                st.error(
                    f"Ein Fehler ist während des Anonymisierungsprozesses aufgetreten: {e}"
                )
