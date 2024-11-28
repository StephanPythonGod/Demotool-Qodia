import io
import zipfile
from typing import Dict, List, Optional, Tuple

import fitz
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.canvas import (
    base_display_file_selection_interface,
    cleanup_session_state,
)
from utils.helpers.logger import logger
from utils.session import reset


def display_file_selection_interface(
    uploaded_file: UploadedFile,
    left_column: st.delta_generator.DeltaGenerator,
    right_column: st.delta_generator.DeltaGenerator,
) -> Tuple[Optional[List[List[Dict[str, float]]]], bool]:
    """Rechnung-specific file selection interface."""
    _display_instructions(left_column)

    return base_display_file_selection_interface(
        uploaded_file=uploaded_file,
        overlay_text="Bitte die zu behaltenden Bereiche auswählen\n(Auswahl mehrerer Bereiche möglich)",
        file_types=["application/pdf"],
        layout_columns=(left_column, right_column),
    )


def _display_instructions(column: st.delta_generator.DeltaGenerator) -> None:
    """Display instructions for using the file selection interface."""
    column.markdown(
        """
        ## Anleitung zur Auswahl der relevanten Rechnungsbereiche

        Verwenden Sie das Tool auf der rechten Seite, um die **wichtigen Bereiche** der Rechnung auszuwählen.

        ### Schritte zur Auswahl:
        1. Klicken Sie auf die PDF-Seite und ziehen Sie ein **rotes Rechteck** um den Bereich, den Sie behalten möchten.
        2. Sie können mehrere Bereiche auf einer Seite auswählen.
        3. Um einen Bereich zu löschen, verwenden Sie die **Rückgängig-Funktion** des Tools.
        4. Die ausgewählten Bereiche werden in der neuen PDF an der gleichen Position erscheinen.
        5. Sobald Sie alle relevanten Bereiche markiert haben, klicken Sie auf **„Auswahl bestätigen"** unten.

        ### Tipps:
        - Stellen Sie sicher, dass Sie alle wichtigen Bereiche der Rechnung markiert haben.
        - Die Bereiche bleiben in der generierten PDF an der gleichen Position wie im Original.
        - Überprüfen Sie alle Seiten der Rechnung, bevor Sie die Auswahl bestätigen.
        """
    )


def process_selected_areas(
    pdf_data: bytes, selections: List[List[Dict[str, float]]]
) -> bytes:
    """Process the selected areas from the PDF and create a new PDF with only those areas."""
    if not selections:
        raise ValueError("No selections provided")

    try:
        input_pdf = fitz.open(stream=pdf_data, filetype="pdf")
    except Exception as e:
        logger.error(f"Failed to open PDF: {e}")
        raise ValueError("Failed to process PDF file")

    input_pdf = fitz.open(stream=pdf_data, filetype="pdf")
    output_pdf = fitz.open()

    try:
        for page_num, page_selections in enumerate(selections):
            if not page_selections:
                continue

            original_page = input_pdf[page_num]
            output_page = output_pdf.new_page(
                width=original_page.rect.width, height=original_page.rect.height
            )

            for selection in page_selections:
                x0 = selection["left"] * original_page.rect.width
                y0 = selection["top"] * original_page.rect.height
                x1 = x0 + (selection["width"] * original_page.rect.width)
                y1 = y0 + (selection["height"] * original_page.rect.height)

                rect = fitz.Rect(x0, y0, x1, y1)
                output_page.show_pdf_page(rect, input_pdf, page_num, clip=rect)

        output_buffer = io.BytesIO()
        output_pdf.save(output_buffer)
        return output_buffer.getvalue()

    finally:
        input_pdf.close()
        output_pdf.close()


def submit_processed_pdf(processed_pdf: bytes) -> None:
    """Submit the processed PDF for further processing."""
    if "text" not in st.session_state:
        st.error("No text content found in session state")
        return

    bericht_text = st.session_state.text
    bericht_file = io.BytesIO()
    bericht_file.write(bericht_text.encode("utf-8"))
    bericht_file.seek(0)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("bericht.txt", bericht_file.read())
        zip_file.writestr("rechnung.pdf", processed_pdf)
    zip_buffer.seek(0)

    st.download_button(
        label="Download Bericht und Rechnung",
        data=zip_buffer,
        file_name="bericht_rechnung.zip",
        mime="application/zip",
    )


def rechnung_anonymize_stage() -> None:
    """Handle the invoice anonymization stage."""
    left_column, right_column = st.columns([1, 1])

    with right_column:
        uploaded_file = st.file_uploader(
            "Laden Sie Ihre Rechnung hoch (PDF Format)",
            type=["pdf"],
            key="rechnung_file_uploader",
        )

    if uploaded_file is None:
        with left_column:
            st.markdown(
                """
                ## Willkommen beim Rechnungs-Bearbeitungstool

                Mit diesem Tool können Sie wichtige Bereiche Ihrer Rechnung auswählen
                und in eine neue PDF-Datei übernehmen. Die ausgewählten Bereiche
                bleiben dabei an ihrer ursprünglichen Position.

                Laden Sie zunächst eine Rechnung im PDF-Format hoch, um zu beginnen.
                """
            )
    else:
        with right_column:
            selections, has_selections = display_file_selection_interface(
                uploaded_file, left_column, right_column
            )

        second_left_column, second_right_column = st.columns([1, 1])
        with second_right_column:
            if st.button(
                "Auswahl bestätigen",
                type="primary",
                disabled=not has_selections,
                key="confirm_selection",
            ):
                try:
                    processed_pdf = process_selected_areas(
                        st.session_state.file_content, selections
                    )
                    submit_processed_pdf(processed_pdf)
                    cleanup_session_state()

                except Exception as e:
                    logger.error(f"Error processing selections: {e}")
                    st.error(
                        "Ein Fehler ist bei der Verarbeitung aufgetreten. Bitte versuchen Sie es erneut."
                    )

        with second_left_column:
            st.button(
                "Zurücksetzen",
                type="secondary",
                on_click=lambda: (reset()),
                key="reset_selection",
            )
