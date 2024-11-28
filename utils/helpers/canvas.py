import hashlib
import io
import os
from typing import Dict, List, Optional, Tuple

import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_drawable_canvas import st_canvas

from utils.helpers.logger import logger


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
        raise e


def sort_selections(
    selections: List[List[Dict[str, float]]]
) -> List[List[Dict[str, float]]]:
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
        sorted_page = sorted(page, key=lambda x: (x["top"], x["left"]))
        sorted_selections.append(sorted_page)

    return sorted_selections


def create_overlay_image(
    image: Image.Image, text: str, font_size: int = 100
) -> Image.Image:
    """Create an overlay on the image with semi-transparent gray background and rotated text."""
    overlay_image = image.copy().convert("RGBA")
    overlay = Image.new("RGBA", overlay_image.size, (128, 128, 128, 32))
    overlay_image = Image.alpha_composite(overlay_image, overlay)

    txt = Image.new("RGBA", overlay_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)

    try:
        REPO_PATH = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(REPO_PATH, "../../data/arial.ttf")
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    lines = text.split("\n")
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

    y_offset = (overlay_image.height - total_text_height) / 2

    for line, (left, top, right, bottom) in zip(lines, text_sizes):
        text_width = right - left
        x_position = (overlay_image.width - text_width) / 2
        draw.text((x_position, y_offset), line, font=font, fill=(255, 69, 0, 255))
        y_offset += bottom - top

    rotated_txt = txt.rotate(45, expand=1)
    paste_x = (overlay_image.width - rotated_txt.width) // 2
    paste_y = (overlay_image.height - rotated_txt.height) // 2
    overlay_image.paste(rotated_txt, (paste_x, paste_y), rotated_txt)

    return overlay_image


def _calculate_display_dimensions(image: Image.Image) -> Tuple[int, int]:
    """Calculate the display dimensions for an image."""
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
    """Process the canvas result and return normalized selections for a single page."""
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


def initialize_file_state(uploaded_file: UploadedFile) -> None:
    """Initialize file-related session state variables."""
    if "file_content" not in st.session_state or "file_hash" not in st.session_state:
        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        file_hash = hashlib.md5(file_content).hexdigest()
        st.session_state["file_content"] = file_content
        st.session_state["file_hash"] = file_hash
        st.session_state["loaded_pages"] = {}
        st.session_state["overlay_removed"] = False


def process_page(
    page_key: str, file_content: bytes, file_type: str, page_num: int, overlay_text: str
) -> Dict:
    """Process a single page and return its data."""
    page_image = load_image(file_content, file_type, page_num)
    display_width, display_height = _calculate_display_dimensions(page_image)
    overlay_image = create_overlay_image(page_image, overlay_text)

    return {
        "image": page_image,
        "overlay_image": overlay_image,
        "width": display_width,
        "height": display_height,
    }


def create_canvas(
    background_image: Image.Image, width: int, height: int, key: str
) -> Dict:
    """Create a drawable canvas with consistent settings."""
    return st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        stroke_color="#FF0000",
        background_image=background_image,
        height=height,
        width=width,
        drawing_mode="rect",
        key=key,
    )


def cleanup_session_state() -> None:
    """Clean up file-related session state variables."""
    keys_to_delete = ["file_content", "file_hash", "loaded_pages", "overlay_removed"]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]


def base_display_file_selection_interface(
    uploaded_file: UploadedFile,
    overlay_text: str,
    file_types: List[str],
    layout_columns: Optional[
        Tuple[st.delta_generator.DeltaGenerator, st.delta_generator.DeltaGenerator]
    ] = None,
) -> Tuple[Optional[List[List[Dict[str, float]]]], bool]:
    """
    Base implementation for file selection interface.

    Args:
        uploaded_file: The uploaded file to process
        overlay_text: Text to display on the overlay
        file_types: List of accepted file types
        layout_columns: Optional tuple of (left_column, right_column) for layout
    """
    if uploaded_file is None:
        return None, False

    if uploaded_file.type not in file_types:
        st.error(
            f"Unsupported file type. Please upload one of: {', '.join(file_types)}"
        )
        return None, False

    initialize_file_state(uploaded_file)

    file_content = st.session_state["file_content"]
    file_hash = st.session_state["file_hash"]
    all_selections = []
    has_selections = False

    try:
        # Determine number of pages
        if uploaded_file.type == "application/pdf":
            num_pages = len(convert_from_bytes(file_content))
        else:
            num_pages = 1

        display_column = layout_columns[1] if layout_columns else st

        with display_column:
            for i in range(num_pages):
                st.subheader(f"Seite {i + 1}")

                page_key = f"{file_hash}_page_{i}"
                if page_key not in st.session_state["loaded_pages"]:
                    with st.spinner(f"Lade Seite {i + 1}..."):
                        try:
                            page_data = process_page(
                                page_key,
                                file_content,
                                uploaded_file.type,
                                i,
                                overlay_text,
                            )
                            st.session_state["loaded_pages"][page_key] = page_data
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

                    canvas_result = create_canvas(
                        background_image,
                        page_data["width"],
                        page_data["height"],
                        f"canvas_{i}",
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
        logger.error(f"Error processing file for selection: {e}")
        st.error(f"Fehler beim Verarbeiten der Datei: {e}")
        return None, False

    return all_selections, has_selections
