import base64
from typing import Optional

import fitz  # PyMuPDF
import streamlit as st

from utils.helpers.background import queue_document
from utils.helpers.document_store import (
    DocumentStatus,
    get_document_store,
    render_document_list_sidebar,
)
from utils.helpers.logger import logger


@st.cache_data
def get_page_thumbnail(document_path: str, page_number: int) -> Optional[str]:
    """Generate and cache a thumbnail for a specific page."""
    try:
        doc = fitz.open(document_path)
        page = doc[page_number]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))  # Scale down for thumbnail
        img_data = pix.tobytes("png")
        img_base64 = base64.b64encode(img_data).decode()
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        logger.error(
            f"Error generating thumbnail for page {page_number}: {e}", exc_info=True
        )
        return None
    finally:
        if "doc" in locals():
            doc.close()


def render_page_grid(document_path: str, total_pages: int):
    """Render a grid of page thumbnails with selection capability."""
    if "page_selections" not in st.session_state:
        st.session_state.page_selections = set()

    # Generate thumbnails
    thumbnails = []
    for page_num in range(total_pages):
        thumbnail = get_page_thumbnail(document_path, page_num)
        if thumbnail:
            thumbnails.append(thumbnail)
        else:
            thumbnails.append(None)  # Placeholder for failed thumbnails

    # Display thumbnails in a 5xN grid
    for row_start in range(0, total_pages, 5):
        cols = st.columns(5)
        for col, page_idx in zip(
            cols, range(row_start, min(row_start + 5, total_pages))
        ):
            if thumbnails[page_idx]:
                with col:
                    # Highlight if selected
                    is_selected = page_idx in st.session_state.page_selections
                    border_color = "#FF4B4B" if is_selected else "#ddd"

                    # Display thumbnail with a border
                    st.markdown(
                        f"""
                        <div style="border: 3px solid {border_color}; border-radius: 5px; padding: 5px;">
                            <img src="{thumbnails[page_idx]}" style="width: 100%;">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Toggle button for selection
                    if st.button(
                        f"{'Entfernen' if is_selected else 'Auswählen'} Seite {page_idx + 1}"
                    ):
                        if is_selected:
                            st.session_state.page_selections.remove(page_idx)
                        else:
                            st.session_state.page_selections.add(page_idx)
                        st.rerun()


def select_documents_stage():
    """Main function for the document selection stage."""

    render_document_list_sidebar()
    st.title("Dokument und Workflow auswählen")

    document_store = get_document_store()
    documents = [
        doc
        for doc in document_store.get_all_documents()
        if doc["status"] == DocumentStatus.UPLOADED.value
    ]
    if not documents:
        st.error("Keine Dokumente verfügbar. Bitte laden Sie zuerst Dokumente hoch.")
        return

    if not st.session_state.get("workflows"):
        st.error(
            "Keine Workflows verfügbar. Bitte überprüfen Sie Ihre API-Einstellungen."
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        selected_doc = st.selectbox(
            "Dokument auswählen",
            options=[doc["id"] for doc in documents],
            format_func=lambda x: x,
        )

    with col2:
        selected_workflow = st.selectbox(
            "Workflow auswählen",
            options=st.session_state.workflows,
            format_func=lambda x: x,
        )

    if selected_doc and selected_workflow:
        document_path = document_store.get_document_path(selected_doc)
        if document_path:
            try:
                doc = fitz.open(document_path)
                total_pages = len(doc)
                doc.close()

                st.subheader("Seiten auswählen")
                render_page_grid(document_path, total_pages)

                if st.session_state.page_selections:
                    selected_pages = sorted(list(st.session_state.page_selections))
                    st.write(
                        f"Ausgewählte Seiten: {', '.join(str(p + 1) for p in selected_pages)}"
                    )

                    if st.button("Ausgewählte Seiten verarbeiten", type="primary"):
                        try:
                            # Create new document ID with .pdf extension
                            pages_str = "-".join(str(p + 1) for p in selected_pages)
                            selected_doc = selected_doc.replace(".", "")
                            new_doc_id = (
                                f"{pages_str}_{selected_doc}_{selected_workflow}.pdf"
                            )

                            # Create new PDF with selected pages
                            new_doc = fitz.open()
                            doc = fitz.open(document_path)
                            for page_num in selected_pages:
                                new_doc.insert_pdf(
                                    doc, from_page=page_num, to_page=page_num
                                )

                            # Write to bytes
                            pdf_bytes = new_doc.write()
                            doc.close()
                            new_doc.close()

                            # Queue document for processing with explicit PDF MIME type
                            queue_document(
                                document_id=new_doc_id,
                                file_data=pdf_bytes,
                                file_type="application/pdf",
                                category=selected_workflow,
                                api_key=st.session_state.api_key,
                                api_url=st.session_state.api_url,
                                arzt_hash=st.session_state.arzt_hash,
                                kassenname_hash=st.session_state.kassenname_hash,
                            )

                            st.session_state.page_selections.clear()
                            st.success(
                                f"Dokument '{new_doc_id}' wurde zur Verarbeitung hinzugefügt"
                            )

                        except Exception as e:
                            logger.error(
                                f"Error processing selected pages: {e}", exc_info=True
                            )
                            st.error(
                                "Fehler bei der Verarbeitung der ausgewählten Seiten"
                            )

            except Exception as e:
                logger.error(
                    f"Error opening document {selected_doc}: {e}", exc_info=True
                )
                st.error("Fehler beim Öffnen des Dokuments")
