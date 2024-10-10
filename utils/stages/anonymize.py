import hashlib
import io
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


def load_image(
    file_content: bytes, file_type: str, page_number: int = 0
) -> Image.Image:
    """Load image from file content, with error handling."""
    try:
        if file_type == "application/pdf":
            return convert_from_bytes(file_content)[page_number]
        elif file_type.startswith("image"):
            return Image.open(io.BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        logger.error(f"Failed to load image on page {page_number}: {e}")
        raise e  # Re-raise to handle upstream


def display_file_selection_interface(
    uploaded_file: UploadedFile,
) -> Optional[List[List[Dict[str, float]]]]:
    """
    Display the file selection interface and handle user selections.
    """
    if "file_content" not in st.session_state or "file_hash" not in st.session_state:
        # Only read the file content if it hasn't been processed yet
        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        file_hash = hashlib.md5(file_content).hexdigest()
        st.session_state["file_content"] = file_content
        st.session_state["file_hash"] = file_hash
        st.session_state["loaded_pages"] = {}

    file_content = st.session_state["file_content"]
    file_hash = st.session_state["file_hash"]

    all_selections = []
    left_column, right_column = st.columns([1, 1])

    with left_column:
        if uploaded_file is None:
            st.warning("Please upload a file first.")
            return None

        try:
            if uploaded_file.type == "application/pdf":
                num_pages = len(convert_from_bytes(file_content))
            else:
                num_pages = 1

            for i in range(num_pages):
                st.subheader(f"Page {i + 1}")

                # Check if the page has already been loaded
                page_key = f"{file_hash}_page_{i}"
                if page_key not in st.session_state["loaded_pages"]:
                    with st.spinner(f"Lade Seite {i + 1}..."):
                        # Try loading the image
                        try:
                            page_image = load_image(file_content, uploaded_file.type, i)
                            (
                                display_width,
                                display_height,
                            ) = _calculate_display_dimensions(page_image)
                            st.session_state["loaded_pages"][page_key] = {
                                "image": page_image,
                                "width": display_width,
                                "height": display_height,
                            }
                        except Exception:
                            st.error(
                                f"Fehler beim Laden von Seite {i + 1}. Bitte einfach die Webseite neu laden."
                            )
                            continue  # Skip to the next page if loading fails

                if page_key in st.session_state["loaded_pages"]:
                    page_data = st.session_state["loaded_pages"][page_key]
                    canvas_result = st_canvas(
                        fill_color=None,
                        stroke_width=2,
                        stroke_color="red",
                        background_image=page_data["image"],
                        update_streamlit=True,
                        height=page_data["height"],
                        width=page_data["width"],
                        drawing_mode="rect",
                        key=f"canvas_{i}",
                    )

                    normalized_selections = _process_canvas_result(
                        canvas_result, page_data["width"], page_data["height"]
                    )
                    all_selections.append(normalized_selections)

        except Exception as e:
            st.error(f"Error processing the file: {e}")
            logger.error(f"Error processing file for selection: {e}")
            return None

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
