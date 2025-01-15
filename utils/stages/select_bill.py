import io
import os
import zipfile
from typing import Dict, List, Optional, Tuple

import fitz
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.canvas import base_display_file_selection_interface
from utils.helpers.distribution_store import DistributionStatus, get_distribution_store
from utils.helpers.logger import logger


def display_bill_selection_interface(
    uploaded_file: UploadedFile,
    left_column: st.delta_generator.DeltaGenerator,
    right_column: st.delta_generator.DeltaGenerator,
) -> Tuple[Optional[List[List[Dict[str, float]]]], bool]:
    """Bill-specific file selection interface."""
    # Initialize selections in session state if not exists
    if "bill_selections" not in st.session_state:
        st.session_state.bill_selections = {}

    _display_instructions(left_column)

    return base_display_file_selection_interface(
        uploaded_file=uploaded_file,
        overlay_text="Bitte die zu behaltenden Bereiche auswählen\n(Auswahl mehrerer Bereiche möglich)",
        file_types=["application/pdf"],
        layout_columns=(left_column, right_column),
        selection_key="bill_selections",  # Pass specific key for bill selections
    )


def _display_instructions(column: st.delta_generator.DeltaGenerator) -> None:
    """Display instructions for using the bill selection interface."""
    column.markdown(
        """
        ## Anleitung zur Auswahl der relevanten Rechnungsbereiche

        Verwenden Sie das Tool auf der rechten Seite, um die **wichtigen Bereiche** der Rechnung auszuwählen.

        ### Schritte zur Auswahl:
        1. Klicken Sie auf die PDF-Seite und ziehen Sie ein **rotes Rechteck** um den Bereich, den Sie behalten möchten
        2. Sie können mehrere Bereiche auf einer Seite auswählen
        3. Um einen Bereich zu löschen, verwenden Sie die **Rückgängig-Funktion** des Tools
        4. Die ausgewählten Bereiche werden in der neuen PDF an der gleichen Position erscheinen
        5. Sobald Sie alle relevanten Bereiche markiert haben, klicken Sie auf **„Export"** unten

        ### Tipps:
        - Stellen Sie sicher, dass Sie alle wichtigen Bereiche der Rechnung markiert haben
        - Die Bereiche bleiben in der generierten PDF an der gleichen Position wie im Original
        - Überprüfen Sie alle Seiten der Rechnung, bevor Sie exportieren
        """
    )


def process_bill_selections(
    pdf_data: bytes, selections: List[List[Dict[str, float]]]
) -> bytes:
    """Process the selected areas from the bill PDF and create a new PDF with only those areas."""
    if not selections:
        raise ValueError("No selections provided")

    try:
        input_pdf = fitz.open(stream=pdf_data, filetype="pdf")
        output_pdf = fitz.open()

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

    except Exception as e:
        logger.error(f"Error processing bill selections: {e}", exc_info=True)
        raise
    finally:
        if "input_pdf" in locals():
            input_pdf.close()
        if "output_pdf" in locals():
            output_pdf.close()


def create_export_zip(processed_bill: bytes) -> Optional[bytes]:
    """Create ZIP file with processed document and bill."""
    if "distribution_document_id" not in st.session_state:
        st.error("Kein Verteilungsdokument gefunden")
        return None

    distribution_store = get_distribution_store()
    doc = distribution_store.get_document(st.session_state.distribution_document_id)

    if not doc:
        st.error("Verteilungsdokument nicht gefunden")
        return None

    if doc["status"] != DistributionStatus.COMPLETED.value:
        if doc["status"] == DistributionStatus.PROCESSING.value:
            st.info(
                "Dokumentverarbeitung noch nicht fertig. Probieren Sie es in 10 Sekunden noch einmal."
            )
        else:
            st.error(f"Dokument Status: {doc['status']}")
        return None

    try:
        # Get path to redacted PDF
        redacted_pdf_path = distribution_store.get_redacted_pdf_path(
            st.session_state.distribution_document_id
        )
        if not redacted_pdf_path or not os.path.exists(redacted_pdf_path):
            st.error("Redacted PDF nicht gefunden")
            return None

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            # Add redacted PDF
            with open(redacted_pdf_path, "rb") as f:
                zip_file.writestr("bericht.pdf", f.read())
            # Add processed bill
            zip_file.writestr("rechnung.pdf", processed_bill)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    except Exception as e:
        logger.error(f"Error creating export zip: {e}", exc_info=True)
        st.error("Fehler beim Erstellen der Export-Datei")
        return None


def select_bill_stage() -> None:
    """Handle the bill selection stage."""
    st.title("Rechnung bearbeiten")

    left_column, right_column = st.columns([1, 1])

    with right_column:
        uploaded_file = st.file_uploader(
            "Laden Sie Ihre Rechnung hoch (PDF Format)",
            type=["pdf"],
            key="bill_file_uploader",
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
        selections, has_selections = display_bill_selection_interface(
            uploaded_file, left_column, right_column
        )

        if has_selections:
            try:
                # Create columns for buttons
                _, col1, col2 = st.columns([6, 1, 1])

                with col1:
                    if st.button("Export", type="primary", use_container_width=True):
                        processed_bill = process_bill_selections(
                            uploaded_file.getvalue(), selections
                        )
                        if processed_bill:
                            export_zip = create_export_zip(processed_bill)
                            if export_zip:
                                st.session_state.export_zip = export_zip
                                st.session_state.export_ready = True
                                st.rerun()

                with col2:
                    # Download button - disabled until export is ready
                    if st.session_state.get("export_ready", False):
                        st.download_button(
                            "Download",
                            data=st.session_state.export_zip,
                            file_name="bericht_rechnung.zip",
                            mime="application/zip",
                            use_container_width=True,
                            on_click=lambda: st.session_state.update(
                                {
                                    "stage": "analyze",
                                    "distribution_document_id": None,
                                    "distribution_page_selections": set(),
                                    "export_zip": None,
                                    "export_ready": False,
                                }
                            ),
                            type="primary",
                        )
                    else:
                        # Disabled download button
                        st.button(
                            "Download",
                            disabled=True,
                            use_container_width=True,
                            help="Klicken Sie zuerst auf 'Export', um den Download zu aktivieren",
                        )

            except Exception as e:
                logger.error(f"Error processing bill: {e}", exc_info=True)
                st.error("Ein Fehler ist bei der Verarbeitung aufgetreten")
        else:
            st.warning("Bitte wählen Sie zuerst Bereiche aus in den PDFs")

        with left_column:
            if st.button("Zurück zum Hauptmenü", type="secondary"):
                st.session_state.stage = "analyze"
                st.rerun()
