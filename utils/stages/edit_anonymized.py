import io
from typing import List, Tuple, Union

import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.logger import logger
from utils.stages.analyze import analyze_text


def display_anonymized_text_editor(
    anonymized_text: str,
    detected_entities: List[Tuple[str, str]],
    column: st.delta_generator.DeltaGenerator,
) -> str:
    """
    Display and allow editing of anonymized text.

    Args:
        anonymized_text (str): The anonymized text to display and edit.
        detected_entities (List[Tuple[str, str]]): List of detected entities.
        column (st.delta_generator.DeltaGenerator): Streamlit column to render in.

    Returns:
        str: The edited anonymized text.
    """
    column.subheader("Anonymisierter Text")
    edited_text = column.text_area(
        "Bearbeiten Sie den anonymisierten Text:", value=anonymized_text, height=400
    )
    return edited_text


def display_uploaded_file(
    uploaded_file: Union[Image.Image, UploadedFile], column: DeltaGenerator
) -> None:
    """
    Display the uploaded file in the specified column.

    Args:
        uploaded_file (Union[Image.Image, st.runtime.uploaded_file_manager.UploadedFile]): The uploaded file to display.
        column (st.delta_generator.DeltaGenerator): Streamlit column to render in.
    """
    column.subheader("Originaldokument")

    try:
        if isinstance(uploaded_file, Image.Image):
            column.image(uploaded_file, use_column_width=True)
        elif uploaded_file.type == "application/pdf":
            pdf_pages = convert_from_bytes(uploaded_file.getvalue())
            if pdf_pages:
                for pdf_image in pdf_pages:
                    img_byte_arr = io.BytesIO()
                    pdf_image.save(img_byte_arr, format="PNG")
                    column.image(img_byte_arr.getvalue(), use_column_width=True)
            else:
                column.warning("Konnte PDF nicht anzeigen.")
        elif uploaded_file.type.startswith("image"):
            column.image(uploaded_file, use_column_width=True)
        else:
            column.warning("Nicht unterstütztes Dateiformat.")
    except Exception as e:
        logger.error(f"Error displaying uploaded file: {str(e)}")
        column.error("Fehler beim Anzeigen der hochgeladenen Datei.")


def edit_anonymized_stage() -> None:
    """Display the edit anonymized stage."""
    left_column, right_column = st.columns(2)

    try:
        display_uploaded_file(st.session_state.uploaded_file, left_column)
        edited_text = display_anonymized_text_editor(
            st.session_state.anonymized_text,
            st.session_state.detected_entities,
            right_column,
        )

        # Confirm or go back buttons
        with right_column:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(
                    "Zurück zur Anonymisierung",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state.stage = "anonymize"
                    st.rerun()
            with col2:
                if st.button(
                    "Analyse starten", type="primary", use_container_width=True
                ):
                    st.session_state.text = edited_text
                    if analyze_text(st.session_state.text):
                        st.rerun()
            with col3:
                if st.button(
                    "Mit Rechnung kombinieren", type="primary", use_container_width=True
                ):
                    st.session_state.text = edited_text
                    st.session_state.stage = "rechnung_anonymize"
                    st.rerun()
    except Exception as e:
        logger.error(f"Error in edit_anonymized_stage: {str(e)}")
        st.error(f"Ein Fehler ist aufgetreten: {str(e)}")
