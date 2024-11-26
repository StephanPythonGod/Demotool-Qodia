import hashlib
import io
import os
from typing import Dict, List, Optional, Tuple

import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
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


def create_overlay_image(
    image: Image.Image, text: str, font_size: int = 100
) -> Image.Image:
    """
    Create an overlay on the image with semi-transparent gray background and rotated text.
    """
    # Create a copy of the image to avoid modifying the original
    overlay_image = image.copy().convert("RGBA")

    # Create a semi-transparent gray overlay
    overlay = Image.new("RGBA", overlay_image.size, (128, 128, 128, 32))

    # Combine the original image with the overlay
    overlay_image = Image.alpha_composite(overlay_image, overlay)

    # Create a transparent image for the text
    txt = Image.new("RGBA", overlay_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)

    # Load a font with a specified size
    try:
        REPO_PATH = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(REPO_PATH, "../../data/arial.ttf")
        font = ImageFont.truetype(
            font_path, font_size
        )  # You can change the path to another font if needed
    except IOError:
        font = (
            ImageFont.load_default()
        )  # Fallback to default font if the font is not found

    # Handle multi-line text by splitting on newline characters
    lines = text.split("\n")

    # Find the maximum width and height for the text
    max_width = overlay_image.width
    text_sizes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    total_text_height = sum(bottom - top for _, top, _, bottom in text_sizes)

    while True:
        max_line_width = max(right - left for left, top, right, bottom in text_sizes)
        if max_line_width <= max_width:
            break
        font_size -= 5
        font = ImageFont.truetype(font_path, font_size)
        text_sizes = [draw.textbbox((0, 0), line, font=font) for line in lines]
        total_text_height = sum(bottom - top for _, top, _, bottom in text_sizes)

    # Calculate vertical position for centering multiple lines
    y_offset = (overlay_image.height - total_text_height) / 2

    for line, (left, top, right, bottom) in zip(lines, text_sizes):
        text_width = right - left
        text_height = bottom - top

        # Calculate horizontal position for centering
        x_position = (overlay_image.width - text_width) / 2
        draw.text((x_position, y_offset), line, font=font, fill=(255, 69, 0, 255))

        # Move to the next line position
        y_offset += text_height

    # Rotate the text image
    rotated_txt = txt.rotate(45, expand=1)

    # Calculate the position to paste the rotated text
    paste_x = (overlay_image.width - rotated_txt.width) // 2
    paste_y = (overlay_image.height - rotated_txt.height) // 2

    # Paste the rotated text onto the overlay image
    overlay_image.paste(rotated_txt, (paste_x, paste_y), rotated_txt)

    return overlay_image


def sort_selections(selections: List[Dict[str, float]]) -> List[Dict[str, float]]:
    """
    Sort selections from top-left to bottom-right within each page.

    Args:
        selections (List[List[Dict[str, float]]]): A list of pages, where each page contains
            a list of selection dictionaries with 'top' and 'left' coordinates.

    Returns:
        List[List[Dict[str, float]]]: The sorted selections maintaining the page structure,
            with selections within each page sorted by vertical position first,
            then horizontal position.
    """
    if not selections:
        return selections

    sorted_selections = []

    for page in selections:
        # Use Python's built-in sorted function with a key function that creates a tuple
        # This is more efficient than manual insertion sort
        sorted_page = sorted(page, key=lambda x: (x["top"], x["left"]))
        sorted_selections.append(sorted_page)

    return sorted_selections


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
    Process the canvas result and return normalized selections for a single page.

    Args:
        canvas_result (Dict): The result from the st_canvas function.
        display_width (int): The display width of the image.
        display_height (int): The display height of the image.

    Returns:
        List[Dict[str, float]]: A list of normalized selections for the page, where each selection
            is a dictionary containing 'left', 'top', 'width', and 'height' as normalized coordinates
            (0.0 to 1.0).
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
    # Sort the selections for this page
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
        1. Klicken Sie auf das Bild und ziehen Sie ein **rotes Rechteck** um den Bereich, den Sie markieren möchten. **Nur markierte Bereiche** werden extrahiert.
        2. Sie können mehrere Bereiche auf einer Seite auswählen.
        3. Um einen Bereich zu löschen, verwenden Sie die **Rückgängig-Funktion** des Tools.
        4. Sobald Sie alle relevanten Bereiche markiert haben, klicken Sie auf **„Datei Anonymisieren"** unten.
        5. Danach erscheint der anonymisierte Text auf der rechten Seite und sie können ihn nochmals bearbeiten.

        ### Tipps:
        - Stellen Sie sicher, dass Sie alle relevanten Textstellen markieren.
        - Wenn Sie fertig sind, klicken Sie auf **„Datei Anonymisieren"** unten, um die markierten Bereiche für die OCR zu extrahieren und den Text zu anonymisieren.
        """
    )


def display_file_selection_interface(
    uploaded_file: UploadedFile,
) -> Tuple[Optional[List[List[Dict[str, float]]]], bool]:
    """
    Display the file selection interface and handle user selections.

    Args:
        uploaded_file (UploadedFile): The uploaded file to process.

    Returns:
        Tuple[Optional[List[List[Dict[str, float]]]], bool]: A tuple containing:
            - The selections organized by page, where each page contains a list of selection
              dictionaries with normalized coordinates ('left', 'top', 'width', 'height'),
              or None if there's an error
            - A boolean indicating whether any selections were made
    """

    if "file_content" not in st.session_state or "file_hash" not in st.session_state:
        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        file_hash = hashlib.md5(file_content).hexdigest()
        st.session_state["file_content"] = file_content
        st.session_state["file_hash"] = file_hash
        st.session_state["loaded_pages"] = {}

    file_content = st.session_state["file_content"]
    file_hash = st.session_state["file_hash"]

    if "overlay_removed" not in st.session_state:
        st.session_state["overlay_removed"] = False

    all_selections = []
    has_selections = False
    left_column, right_column = st.columns([1, 1])

    with right_column:
        if uploaded_file is None:
            st.warning("Please upload a file first.")
            return None, False

        try:
            if uploaded_file.type == "application/pdf":
                num_pages = len(convert_from_bytes(file_content))
            else:
                num_pages = 1

            for i in range(num_pages):
                st.subheader(f"Seite {i + 1}")

                page_key = f"{file_hash}_page_{i}"
                if page_key not in st.session_state["loaded_pages"]:
                    with st.spinner(f"Lade Seite {i + 1}..."):
                        try:
                            page_image = load_image(file_content, uploaded_file.type, i)
                            (
                                display_width,
                                display_height,
                            ) = _calculate_display_dimensions(page_image)

                            overlay_image = create_overlay_image(
                                page_image,
                                "Bitte die zu analysierenden Bereiche auswählen\n(Auswahl mehrerer Bereich möglich)",
                            )

                            st.session_state["loaded_pages"][page_key] = {
                                "image": page_image,
                                "overlay_image": overlay_image,
                                "width": display_width,
                                "height": display_height,
                            }
                        except Exception as e:
                            logger.error(f"Error loading page {i + 1}: {e}")
                            st.error(
                                f"Fehler beim Laden von Seite {i + 1}. Bitte laden Sie die Webseite neu."
                            )
                            continue

                if page_key in st.session_state["loaded_pages"]:
                    page_data = st.session_state["loaded_pages"][page_key]

                    background_image = (
                        page_data["image"]
                        if st.session_state["overlay_removed"]
                        else page_data["overlay_image"]
                    )

                    canvas_result = st_canvas(
                        fill_color="rgba(255, 0, 0, 0.3)",
                        stroke_width=2,
                        stroke_color="#FF0000",
                        background_image=background_image,
                        height=page_data["height"],
                        width=page_data["width"],
                        drawing_mode="rect",
                        key=f"canvas_{i}",
                    )

                    if (
                        canvas_result.json_data is not None
                        and len(canvas_result.json_data["objects"]) > 0
                    ):
                        has_selections = True
                        if not st.session_state["overlay_removed"]:
                            st.session_state["overlay_removed"] = True
                            st.rerun()

                    normalized_selections = _process_canvas_result(
                        canvas_result, page_data["width"], page_data["height"]
                    )
                    all_selections.append(normalized_selections)

        except Exception as e:
            st.error(f"Fehler beim Anonymisieren: {e}")
            logger.error(f"Error processing file for selection: {e}")
            return None, False

    _display_instructions(left_column)

    return sort_selections(all_selections), has_selections


def anonymize_stage() -> None:
    """
    Display the anonymize stage and handle the anonymization process.
    """
    selections, has_selections = display_file_selection_interface(
        st.session_state.uploaded_file
    )

    # Only enable the button if there are selections
    if st.button("Datei Anonymisieren", type="primary", disabled=not has_selections):
        with st.spinner("🔍 Extrahiere Text und anonymisiere..."):
            try:
                extracted_text = perform_ocr_on_file(
                    st.session_state.uploaded_file, selections=selections
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
