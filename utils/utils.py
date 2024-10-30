import io
import textwrap
from html import escape
from pathlib import Path
from typing import Any, List, Tuple, Union

import fitz
import pandas as pd
import streamlit as st
from Levenshtein import distance as levenshtein_distance
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus import Table as RLTable
from reportlab.platypus import TableStyle


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
            updated_annotated_text.append(original_text[last_end:])

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


def generate_pdf_report(
    df: pd.DataFrame, selected_columns=["ziffer", "analog", "zitat", "begruendung"]
):
    """
    Generates a comprehensive PDF report with:
        - A cover page
        - Embedded bill PDF (if available in session state)
        - OCR text section
        - Recognized services table using reportlab for better formatting

    Args:
        df (pd.DataFrame): DataFrame containing service data for the report.
        selected_columns (list): Optional list of DataFrame columns to display in the table.

    Returns:
        bytes: The generated PDF report as bytes.
    """
    # Define PDF output and styles
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # 1. Cover Page with Longer Intro Text in German
    title = Paragraph("Qodia Rechnungsbericht", styles["Title"])
    intro_text = Paragraph(
        "Dieser Bericht bietet eine umfassende Übersicht über die Ergebnisse der Analyse, "
        "die mit dem Qodia Kodierungstool durchgeführt wurde. Der Bericht enthält eine Kopie "
        "der abgeschlossenen Rechnung, den OCR-Textauszug, sowie eine detaillierte Übersicht "
        "der erkannten Leistungen. Verwenden Sie diesen Bericht als Referenz für die Abrechnung "
        "und Qualitätskontrolle der kodierten Dienstleistungen.",
        styles["Normal"],
    )
    toc = Paragraph(
        "<b>Inhaltsverzeichnis:</b><br/>"
        "1. Fertige Rechnung<br/>"
        "2. OP Text<br/>"
        "3. Übersicht erkannter Leistungen",
        styles["Normal"],
    )

    workflow = st.session_state.get("category", "Unbekannter Workflow")
    honorarvolumen = df["gesamtbetrag"].sum() if "gesamtbetrag" in df.columns else 0
    erkannte_leistungen = len(df)

    from utils.helpers.transform import format_euro

    summary_data = [
        ["Workflow", workflow],
        ["Honorarvolumen", f"{format_euro(honorarvolumen)}"],
        ["Anzahl erkannter Leistungen", erkannte_leistungen],
    ]

    summary_table = RLTable(summary_data, colWidths=[6 * cm, 10 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("BACKGROUND", (0, 0), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
            ]
        )
    )

    elements.extend(
        [
            title,
            Spacer(1, 0.5 * cm),
            intro_text,
            Spacer(1, 1 * cm),
            toc,
            Spacer(1, 1 * cm),
            summary_table,
            PageBreak(),
        ]
    )

    # 2. OCR Text Section
    op_text = st.session_state.get("text", "").replace("\n", "<br />")
    elements.append(Paragraph("OP Text", styles["Heading2"]))
    elements.append(Paragraph(op_text, styles["Normal"]))
    elements.append(PageBreak())

    # Build the first part of the PDF
    pdf.build(elements)
    first_part_data = buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)

    # 3. Create recognized services table using reportlab
    display_df = df[selected_columns].copy() if selected_columns else df.copy()

    # Adjustable wrap text function for consistent formatting
    def wrap_text(text, width=70):  # width can be adjusted as needed
        return "\n".join(textwrap.wrap(str(text), width=width))

    # Apply text wrapping with length restriction
    for col in display_df.columns:
        display_df[col] = display_df[col].apply(
            lambda x: wrap_text(
                textwrap.shorten(str(x), width=700, placeholder="... (Zitat gekürzt)")
            )
        )

    # Title for recognized services table
    elements = [
        Paragraph("Erkannte Leistungen", styles["Heading2"]),
        Spacer(1, 0.5 * cm),
    ]

    # Prepare dynamic table headers based on selected columns
    header_row = [
        Paragraph(f"<b>{col.capitalize()}</b>", styles["Heading4"])
        for col in display_df.columns
    ]
    data = [header_row]  # Start data with header row

    # Fill table data rows dynamically
    for _, row in display_df.iterrows():
        data.append(
            [Paragraph(str(row[col]), styles["Normal"]) for col in display_df.columns]
        )

    # Calculate dynamic column widths
    num_columns = len(display_df.columns)
    col_widths = [
        2 * cm if (col == "ziffer" or col == "analog") else (25 / num_columns) * cm
        for col in display_df.columns
    ]

    # Create and style the table with lighter colors and dynamic layout
    services_table = RLTable(data, colWidths=col_widths)
    services_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),  # Lighter header background color
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),  # Header text color
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold headers
                ("FONTSIZE", (0, 0), (-1, -1), 9),  # Font size for all cells
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.lightgrey,
                ),  # Lighter inner grid lines
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),  # Outer border
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.whitesmoke, colors.lightgrey],
                ),  # Alternating row colors
            ]
        )
    )

    elements.append(services_table)
    pdf.build(elements)
    table_data = buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)

    # 4. Merge all PDFs together
    final_pdf = fitz.open()

    # Add first part (cover and OCR text)
    first_part_pdf = fitz.open(stream=first_part_data, filetype="pdf")
    final_pdf.insert_pdf(first_part_pdf)

    # Add bill PDF if available
    if st.session_state.pdf_data is not None:
        bill_pdf_data = st.session_state.pdf_data
    else:
        from utils.helpers.api import generate_pdf

        bill_pdf_data = generate_pdf(df)
        st.session_state.pdf_data = bill_pdf_data

    bill_pdf = fitz.open(stream=bill_pdf_data, filetype="pdf")
    final_pdf.insert_pdf(bill_pdf, start_at=1)

    # Add recognized services table
    table_pdf = fitz.open(stream=table_data, filetype="pdf")
    final_pdf.insert_pdf(table_pdf)

    # Save the final merged PDF
    final_pdf_buffer = io.BytesIO()
    final_pdf.save(final_pdf_buffer)
    final_pdf_buffer.seek(0)
    return final_pdf_buffer.getvalue()


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
