from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_drawable_canvas import st_canvas

from utils.helpers.anonymization import anonymize_text
from utils.helpers.logger import logger
from utils.helpers.ocr import perform_ocr_on_file


def display_file_selection_interface(
    uploaded_file: UploadedFile,
) -> Optional[List[List[Dict[str, float]]]]:
    """
    Display the file selection interface and handle user selections.

    Args:
        uploaded_file (st.UploadedFile): The uploaded file to process.

    Returns:
        Optional[List[List[Dict[str, float]]]]: A list of normalized selections for each page,
        or None if there was an error processing the file.
    """
    pages = []

    try:
        if isinstance(uploaded_file, Image.Image):
            pages.append(uploaded_file)
        else:
            uploaded_file.seek(0)
            if uploaded_file.type == "application/pdf":
                pages = convert_from_bytes(uploaded_file.read())
            elif uploaded_file.type.startswith("image"):
                image = Image.open(uploaded_file)
                pages.append(image)
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        st.error(f"Fehler beim Verarbeiten der Datei: {e}")
        return None

    all_selections = []
    left_column, right_column = st.columns([1, 1])

    with left_column:
        for i, page_image in enumerate(pages):
            st.subheader(f"Seite {i + 1}")
            display_width, display_height = _calculate_display_dimensions(page_image)

            canvas_result = st_canvas(
                fill_color=None,
                stroke_width=2,
                stroke_color="red",
                background_image=page_image,
                update_streamlit=True,
                height=display_height,
                width=display_width,
                drawing_mode="rect",
                key=f"canvas_{i}",
            )

            normalized_selections = _process_canvas_result(
                canvas_result, display_width, display_height
            )
            all_selections.append(normalized_selections)

    _display_instructions(right_column)

    return all_selections


def _calculate_display_dimensions(image: Image.Image) -> Tuple[int, int]:
    """
    Calculate the display dimensions for an image.

    Args:
        image (Image.Image): The image to calculate dimensions for.

    Returns:
        Tuple[int, int]: The calculated display width and height.
    """
    original_width, original_height = image.size
    max_display_height = max_display_width = 800
    aspect_ratio = original_width / original_height

    if original_height > max_display_height:
        display_height = max_display_height
        display_width = int(display_height * aspect_ratio)
    else:
        display_height = original_height
        display_width = original_width

    if display_width > max_display_width:
        display_width = max_display_width
        display_height = int(display_width / aspect_ratio)

    return display_width, display_height


def _process_canvas_result(
    canvas_result: Dict, display_width: int, display_height: int
) -> List[Dict[str, float]]:
    """
    Process the canvas result and return normalized selections.

    Args:
        canvas_result (Dict): The result from the st_canvas function.
        display_width (int): The display width of the image.
        display_height (int): The display height of the image.

    Returns:
        List[Dict[str, float]]: A list of normalized selections.
    """
    normalized_selections = []
    if canvas_result.json_data is not None:
        shapes = canvas_result.json_data["objects"]
        for shape in shapes:
            if shape["type"] == "rect":
                normalized_selections.append(
                    {
                        "left": shape["left"] / display_width,
                        "top": shape["top"] / display_height,
                        "width": shape["width"] / display_width,
                        "height": shape["height"] / display_height,
                    }
                )
    return normalized_selections


def _display_instructions(column: st.delta_generator.DeltaGenerator) -> None:
    """
    Display instructions for using the file selection interface.

    Args:
        column (st.delta_generator.DeltaGenerator): The Streamlit column to display instructions in.
    """
    column.markdown(
        """
        ## Anleitung zur Auswahl der Textpassagen

        Verwenden Sie das Tool auf der linken Seite, um **wichtige Textstellen** zu markieren, die extrahiert und anonymisiert werden sollen.

        ### Schritte zur Auswahl:
        1. Klicken Sie auf das Bild und ziehen Sie ein **rotes Rechteck** um den Bereich, den Sie markieren möchten.
        2. Sie können mehrere Bereiche auf einer Seite auswählen.
        3. Um einen Bereich zu löschen, verwenden Sie die **Rückgängig-Funktion** des Tools.
        4. Sobald Sie alle relevanten Bereiche markiert haben, klicken Sie auf **„Datei Anonymisieren"** unten.
        5. Danach erscheint der anonymisierte Text auf der rechten Seite und sie können ihn nochmals bearbeiten.

        ### Tipps:
        - Stellen Sie sicher, dass Sie alle relevanten Textstellen markieren.
        - Wenn Sie fertig sind, klicken Sie auf **„Datei Anonymisieren"** unten, um die markierten Bereiche für die OCR zu extrahieren und den Text zu anonymisieren.
        """
    )


def display_anonymized_text_editor(
    anonymized_text: str,
    detected_entities: List[Tuple[str, str]],
    st: st.delta_generator.DeltaGenerator,
) -> str:
    """
    Display the anonymized text editor and detected entities.

    Args:
        anonymized_text (str): The anonymized text to display and edit.
        detected_entities (List[Tuple[str, str]]): A list of detected entities and their types.
        st (st.delta_generator.DeltaGenerator): The Streamlit object to use for rendering.

    Returns:
        str: The edited anonymized text.
    """
    right_column = st.columns(2)[1]

    right_column.subheader("Anonymisierter Text")
    edited_text = right_column.text_area(
        "Bearbeiten Sie den anonymisierten Text:", value=anonymized_text, height=400
    )

    right_column.subheader("Ersetzte Wörter und zugehörige Entitäten:")
    if detected_entities:
        right_column.dataframe(
            pd.DataFrame(detected_entities, columns=["Ersetztes Wort", "Entitätstyp"]),
            hide_index=True,
        )
    else:
        right_column.warning("Keine ersetzten Entitäten gefunden.")

    return edited_text


def anonymize_stage() -> None:
    """
    Display the anonymize stage and handle the anonymization process.
    """
    selections = display_file_selection_interface(st.session_state.uploaded_file)

    if st.button("Datei Anonymisieren", type="primary"):
        with st.spinner("🔍 Extrahiere Text und anonymisiere..."):
            try:
                extracted_text = perform_ocr_on_file(
                    st.session_state.uploaded_file, selections
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
                st.rerun()
            except Exception as e:
                logger.error(f"Error during anonymization process: {e}")
                st.error(
                    f"Ein Fehler ist während des Anonymisierungsprozesses aufgetreten: {e}"
                )
