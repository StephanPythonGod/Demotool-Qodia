import io
import time
from typing import Dict, List, Optional, Tuple

import fitz
import streamlit as st
from PIL import Image, UnidentifiedImageError
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_drawable_canvas import st_canvas

from utils.helpers.logger import logger


def _calculate_display_dimensions(
    img_width: int, img_height: int, container_width: int
) -> Tuple[int, int]:
    """Calculate dimensions to fit image in container while maintaining aspect ratio."""
    aspect_ratio = img_width / img_height

    # Scale width to container
    new_width = container_width
    new_height = int(new_width / aspect_ratio)

    return new_width, new_height


def _create_canvas_with_retry(
    img: Image.Image,
    display_width: int,
    display_height: int,
    key: str,
    max_retries: int = 3,
    delay: float = 0.5,
) -> Optional[Dict]:
    """Create canvas with retry logic for reliability."""
    for attempt in range(max_retries):
        try:
            # Ensure image is in RGB mode
            if img.mode not in ["RGB", "RGBA"]:
                img = img.convert("RGBA")

            canvas_result = st_canvas(
                fill_color="rgba(255, 0, 0, 0.3)",
                stroke_width=2,
                stroke_color="#FF0000",
                background_image=img,
                height=display_height,
                width=display_width,
                drawing_mode="rect",
                key=f"{key}_attempt_{attempt}",
            )

            # Verify canvas was created successfully
            if canvas_result is not None and hasattr(canvas_result, "json_data"):
                return canvas_result

        except Exception as e:
            logger.error(
                f"Canvas creation attempt {attempt + 1} failed: {e}", exc_info=True
            )
            if attempt < max_retries - 1:
                time.sleep(delay)
            continue

    return None


def base_display_file_selection_interface(
    uploaded_file: UploadedFile,
    overlay_text: str,
    file_types: List[str],
    layout_columns: Tuple[
        st.delta_generator.DeltaGenerator, st.delta_generator.DeltaGenerator
    ],
    selection_key: str = "selections",
) -> Tuple[Optional[List[List[Dict[str, float]]]], bool]:
    """Base interface for file selection with canvas."""
    try:
        # Initialize selections if not exists
        if selection_key not in st.session_state:
            st.session_state[selection_key] = {}

        left_column, right_column = layout_columns

        # Store file content in session state if not already stored
        if "file_content" not in st.session_state:
            st.session_state.file_content = uploaded_file.getvalue()

        # Convert PDF to images
        pdf_document = fitz.open(stream=st.session_state.file_content, filetype="pdf")
        total_pages = len(pdf_document)

        with right_column:
            # Get container width
            container_width = (
                right_column._get_delta_path_str().startswith("columns") and 400 or 700
            )

            # Display all pages with canvas for each
            for page_num in range(total_pages):
                st.subheader(f"Seite {page_num + 1}")

                try:
                    # Get page and convert to image
                    page = pdf_document[page_num]
                    pix = page.get_pixmap(
                        matrix=fitz.Matrix(2, 2)
                    )  # Scale up for better quality
                    img_data = pix.tobytes("png")

                    # Create PIL Image for getting dimensions
                    try:
                        img = Image.open(io.BytesIO(img_data))
                    except UnidentifiedImageError:
                        st.error(f"Fehler beim Laden von Seite {page_num + 1}")
                        continue

                    img_width, img_height = img.size

                    # Calculate display dimensions to fit container
                    display_width, display_height = _calculate_display_dimensions(
                        img_width, img_height, container_width
                    )

                    # Create canvas with retry logic
                    canvas_result = _create_canvas_with_retry(
                        img=img,
                        display_width=display_width,
                        display_height=display_height,
                        key=f"canvas_{selection_key}_{page_num}",
                    )

                    if canvas_result is None:
                        st.error(
                            f"Fehler beim Erstellen des Canvas für Seite {page_num + 1}"
                        )
                        # Add retry button
                        if st.button("Seite neu laden", key=f"retry_page_{page_num}"):
                            st.rerun()
                        continue

                    # Process canvas results
                    if canvas_result.json_data is not None:
                        objects = canvas_result.json_data["objects"]
                        if objects:
                            # Convert canvas coordinates to normalized coordinates
                            selections = []
                            for obj in objects:
                                if obj["type"] == "rect":
                                    # Convert display coordinates back to original scale
                                    scale_x = img_width / display_width
                                    scale_y = img_height / display_height

                                    left = (obj["left"] * scale_x) / img_width
                                    top = (obj["top"] * scale_y) / img_height
                                    width = (obj["width"] * scale_x) / img_width
                                    height = (obj["height"] * scale_y) / img_height

                                    selections.append(
                                        {
                                            "left": left,
                                            "top": top,
                                            "width": width,
                                            "height": height,
                                        }
                                    )
                            # Store selections for current page
                            st.session_state[selection_key][str(page_num)] = selections
                        else:
                            # Clear selections if canvas is empty
                            if str(page_num) in st.session_state[selection_key]:
                                del st.session_state[selection_key][str(page_num)]

                except Exception as e:
                    logger.error(
                        f"Error processing page {page_num + 1}: {e}", exc_info=True
                    )
                    st.error(f"Fehler bei der Verarbeitung von Seite {page_num + 1}")
                    if st.button("Seite neu laden", key=f"retry_error_{page_num}"):
                        st.rerun()
                    continue

        # Get current selections from session state
        current_selections = st.session_state[selection_key]

        # Check if we have any valid selections
        has_selections = False
        if current_selections and isinstance(current_selections, dict):
            has_selections = any(
                isinstance(page_selections, list) and len(page_selections) > 0
                for page_selections in current_selections.values()
            )

        # Convert selections dict to list format
        selection_list = []
        if has_selections:
            selection_list = [[] for _ in range(total_pages)]
            for page_num_str, page_selections in current_selections.items():
                page_num = int(page_num_str)
                if isinstance(page_selections, list):
                    selection_list[page_num] = page_selections

        pdf_document.close()
        return selection_list, has_selections

    except Exception as e:
        logger.error(f"Error in file selection interface: {e}", exc_info=True)
        raise


def cleanup_session_state() -> None:
    """Clean up selection-related session state."""
    keys_to_remove = [
        "selections",
        "bill_selections",
        "file_content",
        "canvas_selections",
        "canvas_bill_selections",
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
