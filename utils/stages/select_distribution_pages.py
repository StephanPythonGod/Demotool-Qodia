import fitz
import streamlit as st

from utils.helpers.background import process_distribution_document
from utils.helpers.distribution_store import get_distribution_store
from utils.helpers.logger import logger


def display_page_grid(document_path: str, total_pages: int):
    """Render a grid of page thumbnails with selection capability."""
    if "distribution_page_selections" not in st.session_state:
        st.session_state.distribution_page_selections = set()

    # Generate thumbnails
    cols = st.columns(5)
    for page_num in range(total_pages):
        col = cols[page_num % 5]
        with col:
            try:
                doc = fitz.open(document_path)
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))

                # Highlight if selected
                is_selected = page_num in st.session_state.distribution_page_selections
                border_color = "#FF4B4B" if is_selected else "#ddd"

                # Display thumbnail with border
                st.image(
                    pix.tobytes(),
                    caption=f"Seite {page_num + 1}",
                    use_column_width=True,
                )

                # Toggle button for selection
                if st.button(
                    f"{'Entfernen' if is_selected else 'Auswählen'} Seite {page_num + 1}",
                    key=f"page_{page_num}",
                ):
                    if is_selected:
                        st.session_state.distribution_page_selections.remove(page_num)
                    else:
                        st.session_state.distribution_page_selections.add(page_num)
                    st.rerun()

            except Exception as e:
                logger.error(f"Error displaying page {page_num}: {e}", exc_info=True)
                st.error(f"Fehler beim Anzeigen von Seite {page_num + 1}")
            finally:
                if "doc" in locals():
                    doc.close()


def select_distribution_pages_stage():
    """Handle the distribution document page selection stage."""
    st.title("Seiten für Verteilung auswählen")

    if "distribution_document_id" not in st.session_state:
        st.error("Kein Dokument zum Verteilen ausgewählt")
        if st.button("Zurück zum Hauptmenü"):
            st.session_state.stage = "analyze"
            st.rerun()
        return

    distribution_store = get_distribution_store()
    doc_id = st.session_state.distribution_document_id
    doc = distribution_store.get_document(doc_id)

    if not doc:
        st.error("Dokument nicht gefunden")
        return

    try:
        document_path = distribution_store.get_document_path(doc_id)
        pdf_doc = fitz.open(document_path)
        total_pages = len(pdf_doc)
        pdf_doc.close()

        st.markdown(
            """
        ### Anleitung
        1. Wählen Sie die Seiten aus, die Sie verteilen möchten
        2. Die ausgewählten Seiten werden automatisch anonymisiert
        3. Klicken Sie auf 'Weiter', um eine Rechnung hochzuladen
        """
        )

        display_page_grid(document_path, total_pages)

        if st.session_state.distribution_page_selections:
            selected_pages = sorted(list(st.session_state.distribution_page_selections))
            st.write(
                f"Ausgewählte Seiten: {', '.join(str(p + 1) for p in selected_pages)}"
            )

            if st.button("Weiter zur Rechnungsauswahl", type="primary"):
                # Start background processing
                process_distribution_document(
                    document_id=doc_id, selected_pages=selected_pages
                )

                # Move to bill selection stage
                st.session_state.stage = "select_bill"
                st.rerun()

        else:
            st.warning("Bitte wählen Sie mindestens eine Seite aus")

    except Exception as e:
        logger.error(f"Error in select_distribution_pages_stage: {e}", exc_info=True)
        st.error("Ein Fehler ist aufgetreten")
        if st.button("Zurück zum Hauptmenü"):
            st.session_state.stage = "analyze"
            st.rerun()
