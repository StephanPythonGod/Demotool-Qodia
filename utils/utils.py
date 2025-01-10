import io
import os
import tempfile
import zipfile
from html import escape
from pathlib import Path
from typing import Any, List, Tuple, Union

import fitz
import pandas as pd
import streamlit as st
from Levenshtein import distance as levenshtein_distance

from utils.helpers.document_store import get_document_store
from utils.helpers.logger import logger


def flatten(lst: Union[List[Any], str]) -> List[Any]:
    """
    Recursively flattens a nested list. If the input is a string, returns it as a single-element list.

    Args:
        lst (Union[List[Any], str]): The list to flatten or a string.

    Returns:
        List[Any]: A flattened list or a list containing the input string.
    """
    if isinstance(lst, str):
        return [lst]

    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def clean_zitat(zitat: str) -> List[str]:
    """
    Cleans and splits a zitat string into individual parts, removing unnecessary whitespace and placeholders.

    Args:
        zitat (str): The input zitat string, possibly containing newlines or '[...]' placeholders.

    Returns:
        List[str]: A list of cleaned parts of the zitat.
    """
    lines = zitat.split("\n")
    cleaned_lines = []

    for line in lines:
        parts = line.split("[...]")
        for part in parts:
            cleaned_part = part.strip()
            if cleaned_part:
                cleaned_lines.append(cleaned_part)

    return cleaned_lines


def find_zitat_in_text(
    zitate_to_find: List[Tuple[str, str]],
    annotated_text: List[Union[Tuple[str, str], str]],
    window_size: int = 50,
    distance_threshold: int = 10,
) -> List[Union[Tuple[str, str], str]]:
    """
    Finds and annotates 'zitate' in a given annotated text by matching it to the original text.

    Args:
        zitate_to_find (List[Tuple[str, str]]): List of tuples containing zitate and their associated labels.
        annotated_text (List[Union[Tuple[str, str], str]]): The original annotated text with zitate in it.
        window_size (int): The size of the sliding window in characters for potential matches.
        distance_threshold (int): Maximum Levenshtein distance to consider a match.

    Returns:
        List[Union[Tuple[str, str], str]]: The annotated text with zitate identified and labeled.
    """
    updated_annotated_text = []

    # Join the annotated text to create a single text string
    original_text = "".join(
        [item[0] if isinstance(item, tuple) else item for item in annotated_text]
    )

    # Clean text for matching (remove line breaks, normalize spaces)
    cleaned_text = original_text.replace("\n", " ").replace("  ", " ")

    # Process the quotes to find
    list_of_zitate_to_find = [(clean_zitat(z[0]), z[1]) for z in zitate_to_find]
    list_of_zitate_to_find = [
        (z, zitat_label)
        for zitate, zitat_label in list_of_zitate_to_find
        for z in zitate
    ]

    list_of_indices = []

    # Sliding window with Levenshtein distance for approximate matching
    for zitat, zitat_label in list_of_zitate_to_find:
        cleaned_zitat = zitat.replace("\n", " ").replace("  ", " ")

        # Set up sliding window mechanism
        zitat_len = len(cleaned_zitat)
        best_match = None
        best_distance = float("inf")
        best_match_indices = None

        # Slide over the text in windows of size 'window_size'
        for i in range(len(cleaned_text) - zitat_len + 1):
            window_text = cleaned_text[i : i + zitat_len]

            # Calculate Levenshtein distance between the quote and the window text
            current_distance = levenshtein_distance(cleaned_zitat, window_text)

            if (
                current_distance < best_distance
                and current_distance <= distance_threshold
            ):
                best_distance = current_distance
                best_match = window_text
                best_match_indices = (i, i + zitat_len)

        if best_match:
            start_idx, end_idx = best_match_indices

            # Extend the match to the next blank space if it ends in the middle of a word
            while end_idx < len(cleaned_text) and cleaned_text[end_idx] != " ":
                end_idx += 1

            # Add the match to the list with the adjusted end index
            adjusted_match_text = cleaned_text[start_idx:end_idx]
            list_of_indices.append(
                ((start_idx, end_idx), zitat_label, adjusted_match_text)
            )

    # Sort list of indices by the starting position in the text
    list_of_indices.sort(key=lambda x: x[0][0])

    # Build the annotated text with the found quotes
    if list_of_indices:
        zitat_start = list_of_indices[0][0][0]
        updated_annotated_text.append(original_text[:zitat_start])

    for i, (indices, label, zitat_text) in enumerate(list_of_indices):
        updated_annotated_text.append((zitat_text, label))

        if i < len(list_of_indices) - 1:
            next_start = list_of_indices[i + 1][0][0]
            updated_annotated_text.append(original_text[indices[1] + 1 : next_start])

    if list_of_indices:
        last_end = list_of_indices[-1][0][1]
        if last_end < len(original_text):
            updated_annotated_text.append(original_text[last_end + 1 :])

    return updated_annotated_text or annotated_text


def ziffer_from_options(ziffer_option: Union[List[str], str]) -> List[str]:
    """
    Extracts the ziffer (numeric part) from a string or list of strings.

    Args:
        ziffer_option (Union[List[str], str]): A string or list of strings containing ziffer options.

    Returns:
        List[str]: A list of extracted ziffer values.
    """
    if isinstance(ziffer_option, list):
        return [i.split(" - ")[0] for i in ziffer_option]
    elif isinstance(ziffer_option, str):
        return [ziffer_option.split(" - ")[0]]
    return []


def validate_filenames_match(auf_xml_path: Path, padx_xml_path: Path):
    """
    Validates that the filenames of the provided XML paths match after removing specific suffixes.

    This function checks if the filenames (excluding the '_auf' and '_padx' suffixes) of the provided
    `auf_xml_path` and `padx_xml_path` are identical. If they do not match, a ValueError is raised.

    Args:
        auf_xml_path (Path): The path to the '_auf' XML file.
        padx_xml_path (Path): The path to the '_padx' XML file.

    Raises:
        ValueError: If the filenames do not match after removing the '_auf' and '_padx' suffixes.
    """
    if auf_xml_path.stem.replace("_auf", "") != padx_xml_path.stem.replace("_padx", ""):
        raise ValueError("Mismatch between _auf.xml and _padx.xml filenames.")


def get_confidence_emoji(confidence):
    if 0.5 <= confidence:
        return "⚠️"  # Warning sign for moderate confidence
    else:
        return "❌"  # Red cross for low confidence


def create_tooltip(confidence, confidence_reason):
    emoji = get_confidence_emoji(confidence)
    if confidence_reason:
        escaped_reason = escape(confidence_reason)
        return f"""
            <span class="tooltip">
                {emoji}
                <span class="tooltiptext">{escaped_reason}</span>
            </span>
        """
    return emoji


def generate_report_files_as_zip(df: pd.DataFrame):
    """
    Generate a ZIP file containing Rechnung.pdf, Ziffern.xlsx, and the selected document PDF.
    """
    # Create a temporary directory for file storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Generate Rechnung.pdf (Use existing or generate if missing)
        rechnung_path = f"{temp_dir}/Rechnung.pdf"

        # Retrieve or generate the bill PDF data
        if st.session_state.pdf_data is not None:
            bill_pdf_data = st.session_state.pdf_data
        else:
            from utils.helpers.api import generate_pdf

            bill_pdf_data = generate_pdf(df)
            st.session_state.pdf_data = bill_pdf_data

        # Save the PDF data to the temporary directory
        with open(rechnung_path, "wb") as f:
            f.write(bill_pdf_data)

        # 2. Generate Ziffern.xlsx (Excel sheet of the DataFrame)
        ziffern_path = f"{temp_dir}/Ziffern.xlsx"
        df.to_excel(ziffern_path, index=False)

        # 3. Get the selected document's PDF
        document_store = get_document_store()
        selected_doc_path = document_store.get_document_path(
            st.session_state.selected_document_id
        )

        if not selected_doc_path or not os.path.exists(selected_doc_path):
            st.error("Selected document not found")
            return None

        # 4. Create a zip file containing all three documents
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.write(rechnung_path, "Rechnung.pdf")
            zip_file.write(ziffern_path, "Ziffern.xlsx")
            zip_file.write(selected_doc_path, "Bericht.pdf")

        # Return the ZIP file bytes for download
        zip_buffer.seek(0)
        return zip_buffer.getvalue()


def clean_word(word: str) -> str:
    """Clean a word by removing punctuation and converting to lowercase."""
    return "".join(c.lower() for c in word if c.isalnum())


def highlight_phrase(page, words_to_highlight, page_words, scale_factor):
    """Helper function to highlight a sequence of words."""
    # Clean the words to highlight
    clean_words_to_highlight = [clean_word(w) for w in words_to_highlight]

    if len(words_to_highlight) <= 2:
        # For short phrases, just find and highlight each word
        for ocr_word in page_words:
            # Clean the OCR word
            clean_ocr_word = clean_word(ocr_word["text"])
            if clean_ocr_word in clean_words_to_highlight:
                # Scale and highlight
                x0 = ocr_word["bbox"][0] * scale_factor
                x1 = ocr_word["bbox"][2] * scale_factor
                y0 = ocr_word["bbox"][1] * scale_factor
                y1 = ocr_word["bbox"][3] * scale_factor

                rect = fitz.Rect(x0, y0, x1, y1)
                highlight = page.add_highlight_annot(rect)
                if highlight:
                    highlight.set_colors(stroke=(1, 1, 0))
                    highlight.set_opacity(0.5)
                    highlight.update()
                    page.apply_redactions()
    else:
        # For longer phrases, use sequential matching
        potential_matches = []
        for i, ocr_word in enumerate(page_words):
            if clean_word(ocr_word["text"]) == clean_words_to_highlight[0]:
                potential_matches.append(i)

        # For each potential starting point
        for start_idx in potential_matches:
            matches = []
            max_distance = 5  # Maximum words to look ahead
            min_match_ratio = 0.7  # Minimum ratio of words that must match

            # Try to find words in sequence within max_distance
            current_idx = start_idx
            for search_word in clean_words_to_highlight:
                found = False
                for j in range(
                    current_idx, min(current_idx + max_distance, len(page_words))
                ):
                    if clean_word(page_words[j]["text"]) == search_word:
                        matches.append(page_words[j])
                        current_idx = j + 1
                        found = True
                        break
                if not found:
                    # Don't break immediately, continue looking for other words
                    current_idx += 1

            # Check if we found enough matching words
            match_ratio = len(matches) / len(words_to_highlight)
            if match_ratio >= min_match_ratio:
                logger.info(f"Found partial match with ratio {match_ratio:.2f}")
                for ocr_word in matches:
                    x0 = ocr_word["bbox"][0] * scale_factor
                    x1 = ocr_word["bbox"][2] * scale_factor
                    y0 = ocr_word["bbox"][1] * scale_factor
                    y1 = ocr_word["bbox"][3] * scale_factor

                    rect = fitz.Rect(x0, y0, x1, y1)
                    highlight = page.add_highlight_annot(rect)
                    if highlight:
                        highlight.set_colors(stroke=(1, 1, 0))
                        highlight.set_opacity(0.5)
                        highlight.update()
                        page.apply_redactions()


def highlight_text_in_pdf(
    pdf_path: str, word_map: list, text_to_highlight: str, temp_dir: str
) -> str:
    """
    Create a temporary PDF with highlighted text.
    """
    import os
    from datetime import datetime

    import fitz

    from utils.helpers.logger import logger

    # First check total word count
    total_words = len([w for w in text_to_highlight.split() if w.strip()])
    if total_words > 100:
        st.warning(
            f"Zitat ist zu lang ({total_words} Wörter). Aus Performance-Gründen werden Zitate mit mehr als 250 Wörtern nicht hervorgehoben. Bitte gucken Sie einfach in die Zifferndetails."
        )
        return pdf_path  # Return original PDF path without highlighting

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_pdf_path = os.path.join(temp_dir, f"highlighted_{timestamp}.pdf")

    logger.info(f"Original PDF path: {pdf_path}")
    logger.info(f"Temp PDF path: {temp_pdf_path}")

    doc = fitz.open(pdf_path)

    try:
        # Split text into separate quotes
        quotes = [
            quote.strip() for quote in text_to_highlight.split("[...]") if quote.strip()
        ]
        logger.info(f"Processing {len(quotes)} separate quotes")

        # Process each quote independently
        for quote in quotes:
            logger.info(f"Processing quote: {quote}")
            search_words = [w.strip().lower() for w in quote.split() if w.strip()]
            if not search_words:
                continue

            # Search through each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                scale_factor = 72.0 / 200.0

                # Get words for current page
                page_words = [w for w in word_map if w["page"] == page_num]
                logger.info(f"Page {page_num} has {len(page_words)} words")

                # Try to highlight this quote on this page
                highlight_phrase(page, search_words, page_words, scale_factor)

        doc.save(temp_pdf_path, garbage=4, deflate=True, clean=True)
        logger.info(f"Saved final PDF to: {temp_pdf_path}")

    except Exception as e:
        logger.error(f"Error highlighting PDF: {e}", exc_info=True)
        raise
    finally:
        doc.close()

    return temp_pdf_path


def get_temp_dir() -> str:
    """Get or create temporary directory for highlighted PDFs."""
    temp_dir = os.path.join(os.path.dirname(__file__), "../temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


tooltip_css = """
<style>
.tooltip {
    position: relative;
    display: inline-block;
    cursor: pointer;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 240px;
    background-color: black;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    bottom: 150%; /* Position tooltip above the emoji */
    left: 50%;
    margin-left: -70px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}
</style>
"""
