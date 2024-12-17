import concurrent.futures
import hashlib
import io
import os
import threading
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union

import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_drawable_canvas import st_canvas

from utils.helpers.logger import logger

# Add a thread-safe cache for converted pages
page_conversion_lock = threading.Lock()
converted_pages_cache = {}


@lru_cache(maxsize=32)
def _convert_pdf_page(file_content: bytes, page_num: int) -> Image.Image:
    """Convert a single PDF page to image with caching."""
    return convert_from_bytes(file_content)[page_num]


def parallel_convert_pages(
    file_content: bytes, page_numbers: List[int]
) -> Dict[int, Image.Image]:
    """Convert multiple PDF pages in parallel."""
    converted_pages = {}

    def convert_single_page(page_num: int) -> Tuple[int, Image.Image]:
        try:
            with page_conversion_lock:
                if page_num in converted_pages_cache:
                    return page_num, converted_pages_cache[page_num]

                page_image = _convert_pdf_page(file_content, page_num)
                converted_pages_cache[page_num] = page_image
                return page_num, page_image
        except Exception as e:
            logger.error(f"Error converting page {page_num}: {e}")
            return page_num, None

    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_page = {
            executor.submit(convert_single_page, page_num): page_num
            for page_num in page_numbers
        }

        for future in concurrent.futures.as_completed(future_to_page):
            page_num, image = future.result()
            if image is not None:
                converted_pages[page_num] = image

    return converted_pages


def load_image(
    file_content: bytes, file_type: str, page_number: int
) -> Union[Image.Image, None]:
    """Load image from file content, with error handling."""
    try:
        if file_type == "application/pdf":
            with page_conversion_lock:
                if page_number in converted_pages_cache:
                    return converted_pages_cache[page_number]

                page_image = _convert_pdf_page(file_content, page_number)
                converted_pages_cache[page_number] = page_image
                return page_image
        elif file_type.startswith("image"):
            return Image.open(io.BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        logger.error(f"Failed to load image on page {page_number}: {e}")
        return None


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

        # Initialize all required session state variables
        st.session_state.setdefault("page_cache", {})
        st.session_state.setdefault("loaded_pages", {})
        st.session_state.setdefault("overlay_removed", False)
        st.session_state.setdefault("page_selections", {})
        st.session_state.setdefault("current_set", 0)
        st.session_state.setdefault("processing_started", False)
        st.session_state.setdefault("page_selection", [])
        st.session_state.setdefault("page_range", {"start": 1, "end": 1})


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
    """Create a drawable canvas with consistent settings and error handling."""
    try:
        # Ensure image is in correct format and mode
        if background_image.mode not in ["RGB", "RGBA"]:
            background_image = background_image.convert("RGBA")

        # Add minimal delay to ensure proper rendering
        import time

        time.sleep(0.1)

        return st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=2,
            stroke_color="#FF0000",
            background_image=background_image,
            height=height,
            width=width,
            drawing_mode="rect",
            key=key,
            update_streamlit=True,  # Force update
        )
    except Exception as e:
        logger.error(f"Canvas creation error for key {key}: {e}")
        raise e


def cleanup_session_state() -> None:
    """Clean up file-related session state variables."""
    # Clear the module-level cache
    global converted_pages_cache
    converted_pages_cache.clear()

    # Also clear the LRU cache for _convert_pdf_page
    _convert_pdf_page.cache_clear()

    keys_to_delete = [
        "file_content",
        "file_hash",
        "loaded_pages",
        "overlay_removed",
        "page_selections",
        "current_page_index",
        "page_cache",
        "current_set",
        "page_selection",
        "page_range",
        "processing_started",
        "pages_to_process",
    ]
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
    """Interface with hybrid page loading approach."""
    if uploaded_file is None:
        return None, False

    if uploaded_file.type not in file_types:
        st.error(
            f"Unsupported file type. Please upload one of: {', '.join(file_types)}"
        )
        return None, False

    initialize_file_state(uploaded_file)

    PAGES_PER_VIEW = 6
    if "current_set" not in st.session_state:
        st.session_state.current_set = 0

    display_column = layout_columns[1] if layout_columns else st
    control_column = layout_columns[0] if layout_columns else st

    try:
        num_pages = len(convert_from_bytes(st.session_state.file_content))
        use_page_selector = num_pages > PAGES_PER_VIEW * 3  # More than 18 pages
        use_pagination = num_pages > PAGES_PER_VIEW  # More than 6 pages

        if use_page_selector:
            # Page selection interface for large documents
            with control_column:
                selected_pages = display_page_selector(num_pages)

                if not selected_pages:
                    st.warning("Bitte wählen Sie mindestens eine Seite aus")
                    return None, False

                if st.button("Ausgewählte Seiten laden", type="primary"):
                    # Convert to 0-based indices and store
                    st.session_state.pages_to_process = [p - 1 for p in selected_pages]
                    st.session_state.processing_started = True

            if not st.session_state.get("processing_started"):
                return None, False

            # If more than 6 pages are selected, use pagination for selected pages
            if len(st.session_state.pages_to_process) > PAGES_PER_VIEW:
                start_idx = st.session_state.current_set * PAGES_PER_VIEW
                end_idx = min(
                    start_idx + PAGES_PER_VIEW, len(st.session_state.pages_to_process)
                )
                current_pages = st.session_state.pages_to_process[start_idx:end_idx]

                # Navigation controls for selected pages
                with control_column:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if st.button("⬅️", disabled=st.session_state.current_set == 0):
                            st.session_state.current_set -= 1
                            st.rerun()

                    with col2:
                        # Display 1-based page numbers
                        pages_to_show = [p + 1 for p in current_pages]
                        st.markdown(
                            f"### Seiten {pages_to_show[0]} - {pages_to_show[-1]}"
                        )

                    with col3:
                        max_sets = (
                            len(st.session_state.pages_to_process) - 1
                        ) // PAGES_PER_VIEW
                        if st.button(
                            "➡️", disabled=st.session_state.current_set >= max_sets
                        ):
                            st.session_state.current_set += 1
                            st.rerun()
            else:
                current_pages = st.session_state.pages_to_process

        else:
            # Standard pagination for medium-sized documents
            if use_pagination:
                # Initial loading of current set
                with st.spinner("Loading pages..."):
                    manage_page_cache(
                        st.session_state.current_set,
                        PAGES_PER_VIEW,
                        num_pages,
                        st.session_state.file_content,
                        uploaded_file.type,
                        overlay_text,
                    )

                # Navigation controls
                with control_column:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if st.button("⬅️", disabled=st.session_state.current_set == 0):
                            st.session_state.current_set -= 1
                            st.rerun()

                    with col2:
                        start_page = st.session_state.current_set * PAGES_PER_VIEW + 1
                        end_page = min(
                            (st.session_state.current_set + 1) * PAGES_PER_VIEW,
                            num_pages,
                        )
                        st.markdown(
                            f"### Pages {start_page} - {end_page} of {num_pages}"
                        )

                    with col3:
                        if st.button("➡️", disabled=end_page >= num_pages):
                            st.session_state.current_set += 1
                            st.rerun()

                current_start = st.session_state.current_set * PAGES_PER_VIEW
                current_pages = range(
                    current_start, min(current_start + PAGES_PER_VIEW, num_pages)
                )
            else:
                # Show all pages for small documents
                current_pages = range(num_pages)

        # Before processing pages, initialize all_selections from stored selections
        all_selections = [[] for _ in range(num_pages)]
        for page_idx, selections in st.session_state.page_selections.items():
            all_selections[page_idx] = selections

        # Process pages and handle selections
        with display_column:
            for page_idx in current_pages:
                try:
                    # Create a horizontal layout for the page title and reload button
                    col1, col2 = st.columns([10, 1])
                    with col1:
                        st.subheader(f"Seite {page_idx + 1}")
                    with col2:
                        # Add a reload button with an icon next to the page title
                        if st.button("🔄", key=f"reload_{page_idx}"):
                            # Clear the specific page cache to force reload
                            page_key = f"page_{page_idx}"
                            if page_key in st.session_state.page_cache:
                                del st.session_state.page_cache[page_key]
                            st.rerun()

                    page_key = f"page_{page_idx}"

                    # Process page if not in cache
                    if page_key not in st.session_state.page_cache:
                        with st.spinner(f"Lade Seite {page_idx + 1}..."):
                            page_data = process_page(
                                page_key,
                                st.session_state.file_content,
                                uploaded_file.type,
                                page_idx,
                                overlay_text,
                            )
                            st.session_state.page_cache[page_key] = page_data

                    page_data = st.session_state.page_cache[page_key]

                    # Verify image data
                    if page_data["image"] is None or page_data["overlay_image"] is None:
                        st.error(f"Fehler beim Laden der Seite {page_idx + 1}")
                        continue

                    # Select background image
                    background_image = (
                        page_data["image"]
                        if st.session_state.get("overlay_removed", False)
                        else page_data["overlay_image"]
                    )

                    # Add canvas creation with retries
                    MAX_RETRIES = 3
                    RETRY_DELAY = 0.5

                    for retry in range(MAX_RETRIES):
                        try:
                            # Create a unique key for each retry attempt
                            retry_key = f"canvas_{page_idx}_attempt_{retry}"

                            canvas_result = create_canvas(
                                background_image=background_image,
                                width=page_data["width"],
                                height=page_data["height"],
                                key=retry_key,
                            )

                            # Verify canvas was created successfully
                            if canvas_result is not None and hasattr(
                                canvas_result, "json_data"
                            ):
                                break

                            import time

                            time.sleep(RETRY_DELAY)

                        except Exception as e:
                            logger.error(
                                f"Canvas creation error on page {page_idx + 1}, attempt {retry + 1}: {e}"
                            )
                            if retry == MAX_RETRIES - 1:
                                st.error(
                                    f"Fehler beim Laden des Canvas für Seite {page_idx + 1}"
                                )
                                continue
                            time.sleep(RETRY_DELAY)

                    # Process selections if canvas was created successfully
                    if canvas_result is not None and hasattr(
                        canvas_result, "json_data"
                    ):
                        normalized_selections = _process_canvas_result(
                            canvas_result, page_data["width"], page_data["height"]
                        )
                        # Store in session state
                        st.session_state.page_selections[
                            page_idx
                        ] = normalized_selections
                        # Update all_selections
                        all_selections[page_idx] = normalized_selections
                    else:
                        st.error(
                            f"Canvas konnte nicht erstellt werden für Seite {page_idx + 1}"
                        )

                except Exception as e:
                    logger.error(f"Error processing page {page_idx + 1}: {e}")
                    st.error(f"Fehler bei der Verarbeitung von Seite {page_idx + 1}")
                    continue

        # Check for selections and handle overlay
        has_selections = any(len(sel) > 0 for sel in all_selections)
        if has_selections and not st.session_state.get("overlay_removed", False):
            st.session_state["overlay_removed"] = True
            st.rerun()

        return all_selections, has_selections

    except Exception as e:
        logger.error(f"Error in file selection interface: {e}")
        st.error(f"Error processing file: {e}")
        return None, False


def preprocess_page_set(
    file_content: bytes,
    file_type: str,
    start_page: int,
    end_page: int,
    overlay_text: str,
) -> Dict[str, Dict]:
    """Process a set of pages and store in cache."""
    processed_pages = {}

    # Convert all pages in parallel if it's a PDF
    if file_type == "application/pdf":
        # Convert all pages in the set at once
        page_numbers = list(range(start_page, end_page))
        with st.spinner(f"Lade Seiten {start_page + 1} bis {end_page}..."):
            converted_pages = parallel_convert_pages(file_content, page_numbers)

            # Process all conversions in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_page = {}
                for i, page_image in converted_pages.items():
                    if page_image is not None:
                        future = executor.submit(
                            process_single_page, page_image, overlay_text
                        )
                        future_to_page[future] = i

                # Collect results
                for future in concurrent.futures.as_completed(future_to_page):
                    i = future_to_page[future]
                    try:
                        page_data = future.result()
                        if page_data:
                            processed_pages[f"page_{i}"] = page_data
                    except Exception as e:
                        logger.error(f"Error processing page {i + 1}: {e}")

    return processed_pages


def process_single_page(page_image: Image.Image, overlay_text: str) -> Optional[Dict]:
    """Process a single page image with its overlay."""
    try:
        display_width, display_height = _calculate_display_dimensions(page_image)
        overlay_image = create_overlay_image(page_image, overlay_text)

        return {
            "image": page_image,
            "overlay_image": overlay_image,
            "width": display_width,
            "height": display_height,
        }
    except Exception as e:
        logger.error(f"Error in process_single_page: {e}")
        return None


def manage_page_cache(
    current_set: int,
    pages_per_view: int,
    total_pages: int,
    file_content: bytes,
    file_type: str,
    overlay_text: str,
) -> None:
    """Manage the rolling cache of page sets."""
    if "page_cache" not in st.session_state:
        st.session_state.page_cache = {}

    # Calculate set ranges with additional buffering
    current_start = current_set * pages_per_view
    buffer_size = pages_per_view
    prev_start = max(0, current_start - buffer_size)
    next_start = min(current_start + pages_per_view, total_pages)
    next_end = min(next_start + buffer_size, total_pages)

    # Determine which pages need processing
    cache_range = range(prev_start, next_end)
    missing_pages = [
        i for i in cache_range if f"page_{i}" not in st.session_state.page_cache
    ]

    # Process all missing pages at once if any are missing
    if missing_pages:
        new_pages = preprocess_page_set(
            file_content,
            file_type,
            min(missing_pages),
            max(missing_pages) + 1,
            overlay_text,
        )
        st.session_state.page_cache.update(new_pages)

    # Clean up cache for pages we don't need
    st.session_state.page_cache = {
        k: v
        for k, v in st.session_state.page_cache.items()
        if int(k.split("_")[1]) in cache_range
    }


def display_page_selector(num_pages: int) -> List[int]:
    """Display a page selection interface and return selected page numbers."""
    st.markdown("### Seitenauswahl")

    # Quick selection button
    if st.button("Alle Seiten auswählen"):
        st.session_state.page_selection = list(range(1, num_pages + 1))
        st.rerun()

    # Initialize page selection state
    if "page_selection" not in st.session_state:
        st.session_state.page_selection = []
    if "page_range" not in st.session_state:
        st.session_state.page_range = {"start": 1, "end": min(10, num_pages)}

    # Use a form to prevent recomputation on every input change
    with st.form(key="page_range_form"):
        col1, col2 = st.columns(2)
        with col1:
            range_start = st.number_input(
                "Von Seite",
                min_value=1,
                max_value=num_pages,
                value=st.session_state.page_range["start"],
            )
        with col2:
            range_end = st.number_input(
                "Bis Seite",
                min_value=st.session_state.page_range["start"],
                max_value=num_pages,
                value=st.session_state.page_range["end"],
            )

        # Form submit button
        submitted = st.form_submit_button("Seitenbereich hinzufügen")
        if submitted:
            # Add pages to selection
            new_pages = list(range(range_start, range_end + 1))
            st.session_state.page_selection = sorted(
                list(set(st.session_state.page_selection + new_pages))
            )

            # Update range for next selection
            # Ensure the next start is the next page after the current end
            next_start = min(range_end + 1, num_pages)
            # Ensure the next end is a valid page number
            next_end = min(next_start + (range_end - range_start), num_pages)
            st.session_state.page_range = {"start": next_start, "end": next_end}

            st.rerun()

    # Display and edit selected pages
    selected_pages = st.multiselect(
        "Ausgewählte Seiten",
        options=list(range(1, num_pages + 1)),
        default=st.session_state.page_selection,
        key="page_multiselect",
    )

    # Update page selection when multiselect changes
    if selected_pages != st.session_state.page_selection:
        st.session_state.page_selection = selected_pages

    return selected_pages
