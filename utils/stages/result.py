import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from utils.helpers.document_store import DocumentStatus, get_document_store
from utils.helpers.feedback import handle_feedback_submission
from utils.helpers.logger import logger
from utils.helpers.transform import (
    analyze_add_data,
    format_ziffer_to_4digits,
    split_recognized_and_potential,
)
from utils.stages.export_modal import export_modal
from utils.stages.modal import add_new_ziffer, modal_dialog
from utils.utils import get_temp_dir, highlight_text_in_pdf


def set_selected_ziffer(index):
    """Update selected ziffer and highlight text in PDF."""
    if index is None:
        st.session_state.selected_ziffer = None
        st.session_state.current_highlighted_pdf = None
    else:
        st.session_state.selected_ziffer = index

        # Get document and OCR data
        document_store = get_document_store(st.session_state.api_key)
        document = document_store.get_document(st.session_state.selected_document_id)
        ocr_data = document_store.get_ocr_data(st.session_state.selected_document_id)

        if document and ocr_data:
            # Get the zitat for the selected ziffer
            selected_row = st.session_state.df.iloc[index]
            zitat = selected_row["zitat"]

            # Get PDF path
            pdf_path = document_store.get_document_path(
                st.session_state.selected_document_id
            )

            if pdf_path:
                # Create highlighted PDF
                temp_dir = get_temp_dir()
                highlighted_pdf = highlight_text_in_pdf(
                    pdf_path=pdf_path,
                    word_map=ocr_data["word_map"],
                    text_to_highlight=zitat,
                    temp_dir=temp_dir,
                )
                st.session_state.current_highlighted_pdf = highlighted_pdf


def add_to_recognized(index):
    st.session_state.df.loc[index, "confidence"] = 1.0
    st.rerun()


def delete_ziffer(index):
    """Delete a ziffer and update the UI state."""
    # Clear selected ziffer if we're deleting the currently selected one
    if st.session_state.selected_ziffer == index:
        st.session_state.selected_ziffer = None
        st.session_state.current_highlighted_pdf = None

    # Remove the ziffer only from the working DataFrame
    st.session_state.df = st.session_state.df[st.session_state.df.index != index]

    # Reset index for current DataFrame while preserving row_id
    st.session_state.df = st.session_state.df.reset_index(drop=True)

    # Force rerun to update the UI
    st.rerun()


def extract_numeric_value(ziffer):
    # Extract the numeric portion of the Ziffer and convert to int after removing leading zeros
    numeric_part = re.search(r"\d+", ziffer)
    return int(numeric_part.group()) if numeric_part else float("inf")


def sort_ziffer(ascending=True):
    # Sort based on the numeric values extracted from Ziffer strings
    st.session_state.df["numeric_ziffer"] = st.session_state.df["ziffer"].apply(
        extract_numeric_value
    )
    st.session_state.df = st.session_state.df.sort_values(
        by="numeric_ziffer", ascending=ascending
    )
    st.session_state.df.drop(columns=["numeric_ziffer"], inplace=True)


def reset_ziffer_order():
    st.session_state.df = st.session_state.df.sort_values(by="row_id")


def set_sort_mode():
    # Cycle through sorting modes: ask -> desc -> text
    modes = ["ask", "desc", "text"]
    current_mode = st.session_state.get("sort_mode", "text")
    next_mode = modes[(modes.index(current_mode) + 1) % len(modes)]
    st.session_state.selected_ziffer = None
    st.session_state.current_highlighted_pdf = None
    st.session_state.sort_mode = next_mode
    apply_sorting()  # Apply sorting whenever mode changes


def apply_sorting():
    # Apply sorting based on the current sort mode
    if st.session_state.sort_mode == "ask":
        sort_ziffer(ascending=True)
    elif st.session_state.sort_mode == "desc":
        sort_ziffer(ascending=False)
    elif st.session_state.sort_mode == "text":
        reset_ziffer_order()
    # Reset index and clear the selected ziffer
    st.session_state.df.reset_index(drop=True, inplace=True)


def cleanup_temp_files():
    """Clean up temporary highlighted PDFs."""
    temp_dir = get_temp_dir()
    for file in os.listdir(temp_dir):
        if file.startswith("highlighted_"):
            try:
                os.remove(os.path.join(temp_dir, file))
            except Exception as e:
                logger.error(
                    f"Error cleaning up temporary file {file}: {e}", exc_info=True
                )


def result_stage() -> None:
    """Display the result stage in the Streamlit app."""
    # Collapse sidebar when entering result stage
    if st.session_state.stage == "result":
        st.markdown(
            """
            <script>
                var elements = window.parent.document.getElementsByClassName("css-1544g2n e1fqkh3o4");
                if (elements.length > 0) {
                    elements[0].click();
                }
            </script>
            """,
            unsafe_allow_html=True,
        )

    # Render document list sidebar (reuse from analyze stage)
    from utils.stages.analyze import render_document_list_sidebar

    render_document_list_sidebar()

    # Get selected document
    if not st.session_state.selected_document_id:
        st.error("Kein Dokument ausgewählt")
        return

    document = get_document_store(st.session_state.api_key).get_document(
        st.session_state.selected_document_id
    )
    if not document:
        st.error("Ausgewähltes Dokument nicht gefunden")
        return
    if document["status"] == DocumentStatus.PROCESSING.value:
        update_time = datetime.fromisoformat(document["updated_at"])
        st.info(f"Dokument wird seit {datetime.now() - update_time} verarbeitet")
        return

    if document["status"] == DocumentStatus.FAILED.value:
        st.error("Dokument konnte nicht verarbeitet werden")
        error_message = document["error_message"]

        # Extract relevant parts from error message
        if "API error:" in error_message:
            # Split into main parts
            parts = error_message.split(", Message: ")
            if len(parts) > 1:
                # Extract the detail message from JSON-like string
                detail_start = parts[1].find('"detail":"') + 9
                detail_end = parts[1].find('"}')
                if detail_start > 8 and detail_end > 0:
                    error_detail = parts[1][detail_start:detail_end]
                    st.error(
                        f"""
                    Fehlerdetails:
                    {error_detail}
                    """
                    )
                else:
                    st.error(error_message)
            else:
                st.error(error_message)
        else:
            st.error(error_message)
        return

    # Update session state with document results
    if st.session_state.df is None or len(st.session_state.df) == 0:
        # Check for user modifications first
        if document.get("user_modifications"):
            st.session_state.df = pd.DataFrame(document["user_modifications"])
        else:
            # Fall back to original API result
            result = document["result"]
            processed_data = analyze_add_data(result)
            st.session_state.df = pd.DataFrame(processed_data)

    # Check if we need to clean up after adding a new ziffer
    if st.session_state.get("adding_new_ziffer", False):
        # If we're here, it means the modal was closed without saving
        if st.session_state.ziffer_to_edit is not None:
            st.session_state.df = st.session_state.df.drop(
                st.session_state.ziffer_to_edit
            )
            st.session_state.df = st.session_state.df.reset_index(drop=True)
        st.session_state.ziffer_to_edit = None
        st.session_state.selected_ziffer = None
        st.session_state.adding_new_ziffer = False

    # Save the original DataFrame
    if (
        "original_df" not in st.session_state
        or st.session_state.original_df is None
        or ("row_id" not in st.session_state.df)
    ):
        logger.info("Saving original DataFrame")
        st.session_state.original_df = st.session_state.df.copy()
        if "row_id" not in st.session_state.original_df.columns:
            st.session_state.original_df["row_id"] = range(
                len(st.session_state.original_df)
            )
        if "row_id" not in st.session_state.df.columns:
            st.session_state.df["row_id"] = st.session_state.original_df[
                "row_id"
            ].copy()
        if len(st.session_state.original_df) == 0:
            st.warning("Die KI hat keine Leistungsziffern erkannt.", icon="⚠️")

    if "sort_mode" in st.session_state:
        apply_sorting()

    recognized_df, potential_df = split_recognized_and_potential(st.session_state.df)

    # Create two main columns
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Erkannte Leistungsziffern")

        # Header row for recognized services
        header_cols = st.columns([1, 1, 1, 0.4, 0.4, 0.4])
        headers = ["Ziffer", "Anzahl", "Faktor", "", "️", "️"]

        for col, header in zip(header_cols, headers):
            if header == "Ziffer":
                col.button(
                    "Ziffer",
                    key="ziffer_header",
                    type="secondary",
                    use_container_width=False,
                    on_click=set_sort_mode,
                )
            else:
                col.markdown(f"**{header}**")

        # Display recognized services
        for index, row in recognized_df.iterrows():
            # Update columns to add space for delete button
            cols = st.columns([1, 1, 1, 0.4, 0.4, 0.4])

            if cols[0].button(
                format_ziffer_to_4digits(row["ziffer"]),
                key=f"ziffer_{row['row_id']}",
                type="secondary"
                if st.session_state.selected_ziffer != index
                else "primary",
            ):
                set_selected_ziffer(
                    None if st.session_state.selected_ziffer == index else index
                )
                st.rerun()

            cols[1].write(row["anzahl"])
            cols[2].write(row["faktor"])

            if cols[3].button("✏️", key=f"edit_{row['row_id']}"):
                st.session_state.ziffer_to_edit = index
                modal_dialog()

            if cols[4].button("🗑️", key=f"delete_{row['row_id']}"):
                delete_ziffer(index)

        # Add new Ziffer button
        if st.button(
            "➕ Ziffer hinzufügen",
            key="add_new_ziffer",
            type="secondary",
            use_container_width=True,
        ):
            add_new_ziffer()

        # Potential services section
        st.subheader("Potentielle Leistungsziffern")

        for index, row in potential_df.iterrows():
            # Update columns to add space for delete button
            cols = st.columns([1, 1, 1, 0.4, 0.4, 0.4])

            if cols[0].button(
                format_ziffer_to_4digits(row["ziffer"]),
                key=f"pot_ziffer_{row['row_id']}",
                type="secondary"
                if st.session_state.selected_ziffer != index
                else "primary",
            ):
                set_selected_ziffer(
                    None if st.session_state.selected_ziffer == index else index
                )
                st.rerun()

            cols[1].write(row["anzahl"])
            cols[2].write(row["faktor"])

            if cols[3].button("✏️", key=f"pot_edit_{row['row_id']}"):
                st.session_state.ziffer_to_edit = index
                modal_dialog()
            if cols[4].button("➕", key=f"pot_add_{row['row_id']}"):
                add_to_recognized(index)
            if cols[5].button("🗑️", key=f"pot_delete_{row['row_id']}"):
                delete_ziffer(index)

        # Remove the bottom_cols split and create a container for buttons at the bottom
        st.write("")  # Add some spacing
        st.write("")  # Add some spacing
        button_container = st.container()

    with right_col:
        document_store = get_document_store(st.session_state.api_key)
        pdf_path = st.session_state.get(
            "current_highlighted_pdf"
        ) or document_store.get_document_path(st.session_state.selected_document_id)

        if pdf_path:
            pdf_height = max(800, min(1400, 100 * len(st.session_state.original_df)))
            pdf_viewer(pdf_path, height=pdf_height)
        else:
            st.error("PDF konnte nicht geladen werden")
        st.write("")  # Add some spacing
        st.write("")  # Add some spacing

    # Create a full-width container for buttons
    button_container = st.container()
    with button_container:
        # Create three columns with the middle one taking most space
        left_btn, spacer, right_btn = st.columns([1, 5, 1])

        # Place Feedback button on the far left
        with left_btn:
            if st.button("Feedback geben", type="primary", use_container_width=True):
                with st.spinner("📝 Feedback wird geladen..."):
                    handle_feedback_submission(df=recognized_df)

        # Place Extrahieren button on the far right
        with right_btn:
            if st.button("Extrahieren", type="primary", use_container_width=True):
                export_modal(recognized_df)

    # Add to session state initialization
    if "current_highlighted_pdf" not in st.session_state:
        st.session_state.current_highlighted_pdf = None

    # Add cleanup when changing documents or stages
    if st.session_state.stage != "result":
        cleanup_temp_files()
