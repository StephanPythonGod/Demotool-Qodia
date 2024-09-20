import re

import streamlit as st
from annotated_text import annotated_text

from utils.helpers.api import generate_pdf, send_feedback_api
from utils.helpers.transform import (
    annotate_text_update,
    df_to_processdocumentresponse,
    format_ziffer_to_4digits,
)
from utils.session import reset
from utils.stages.modal import modal_dialog
from utils.utils import find_zitat_in_text


def set_selected_ziffer(index):
    st.session_state.selected_ziffer = index


def delete_ziffer(index):
    st.session_state.df.drop(index, inplace=True)
    st.session_state.selected_ziffer = None
    st.session_state.df.reset_index(drop=True, inplace=True)
    annotate_text_update()
    st.rerun()


def extract_numeric_value(ziffer):
    # Extract the numeric portion of the Ziffer and convert to int after removing leading zeros
    numeric_part = re.search(r"\d+", ziffer)
    return int(numeric_part.group()) if numeric_part else float("inf")


def sort_ziffer(ascending=True):
    # Sort based on the numeric values extracted from Ziffer strings
    st.session_state.df["numeric_ziffer"] = st.session_state.df["Ziffer"].apply(
        extract_numeric_value
    )
    st.session_state.df.sort_values(
        by="numeric_ziffer", ascending=ascending, inplace=True
    )
    st.session_state.df.drop(
        columns=["numeric_ziffer"], inplace=True
    )  # Remove helper column
    st.session_state.df.reset_index(drop=True, inplace=True)
    st.session_state.selected_ziffer = None  # Reset selection on sorting


def reset_ziffer_order():
    st.session_state.df = st.session_state.df.loc[st.session_state.original_order]
    st.session_state.df.reset_index(drop=True, inplace=True)
    st.session_state.selected_ziffer = None
    st.rerun()


def set_sort_mode():
    # Cycle through sorting modes: ask -> desc -> text
    modes = ["ask", "desc"]
    current_mode = st.session_state.get("sort_mode", "ask")
    next_mode = modes[(modes.index(current_mode) + 1) % len(modes)]
    st.session_state.sort_mode = next_mode
    apply_sorting()  # Apply sorting whenever mode changes


def apply_sorting():
    # Apply sorting based on the current sort mode
    if st.session_state.sort_mode == "ask":
        sort_ziffer(ascending=True)
    elif st.session_state.sort_mode == "desc":
        sort_ziffer(ascending=False)
    # Reset index and clear the selected ziffer
    st.session_state.df.reset_index(drop=True, inplace=True)
    st.session_state.selected_ziffer = None  # Reset selection


def result_stage():
    "Display the result of the analysis."
    left_column, right_column = st.columns(2)
    left_outer_column, _, _, _, right_outer_column = st.columns([1, 2, 3, 2, 1])

    # Left Column: Display the text with highlighting
    with left_column:
        st.subheader("Ärztlicher Bericht:")
        if (
            "selected_ziffer" in st.session_state
            and st.session_state.selected_ziffer is not None
        ):
            selected_zitat = st.session_state.df.loc[
                st.session_state.selected_ziffer, "Zitat"
            ]
            selected_ziffer = st.session_state.df.loc[
                st.session_state.selected_ziffer, "Ziffer"
            ]
            annotated_text(
                find_zitat_in_text(
                    [(selected_zitat, selected_ziffer)], [st.session_state.text]
                )
            )
        else:
            st.write(st.session_state.text)

    with right_column:
        st.subheader("Erkannte Leistungsziffern:")

        # Header row with the new Ziffer button
        header_cols = right_column.columns([1, 1, 1, 3, 1])
        headers = ["Ziffer", "Häufigkeit", "Faktor", "Beschreibung", "Aktionen"]
        for i, (col, header) in enumerate(zip(header_cols, headers)):
            if header == "Ziffer":
                # Set the button label based on the current sort_mode
                sort_label = {"ask": "Ziffer ⬆️", "desc": "Ziffer ⬇️"}

                # Initialize sort_mode in session_state if not set yet
                sort_mode = st.session_state.get("sort_mode", "text")

                # Display the button and set the sort mode accordingly
                col.button(
                    sort_label.get(sort_mode, "Ziffer 🔠"), on_click=set_sort_mode
                )
            else:
                col.markdown(f"**{header}**")

        # Display table rows
        for index, row in st.session_state.df.iterrows():
            cols = right_column.columns([1, 1, 1, 3, 0.5, 0.5])
            if cols[0].button(
                format_ziffer_to_4digits(row["Ziffer"]),
                key=f"ziffer_{index}",
                type="secondary"
                if st.session_state.selected_ziffer != index
                else "primary",
            ):
                set_selected_ziffer(
                    None if st.session_state.selected_ziffer == index else index
                )
                st.rerun()

            description_html = f"<div style='overflow-x: auto; white-space: nowrap; padding: 5px;'>{row['Beschreibung']}</div>"
            cols[1].write(row["Häufigkeit"])
            cols[2].write(row["Intensität"])
            cols[3].markdown(description_html, unsafe_allow_html=True)

            if cols[4].button("✏️", key=f"edit_{index}"):
                st.session_state.ziffer_to_edit = index
                modal_dialog()
            if cols[5].button("🗑️", key=f"delete_{index}"):
                delete_ziffer(index)

    # Rest of the layout
    with left_outer_column:
        st.button(
            "Zurücksetzen",
            on_click=lambda: (
                send_feedback_api(
                    df_to_processdocumentresponse(
                        st.session_state.df, st.session_state.text
                    )
                ),
                reset(),
            ),
            type="primary",
            use_container_width=True,
        )

    with right_outer_column:
        if st.button("PDF generieren", type="primary", use_container_width=True):
            with st.spinner("📄 Generiere PDF..."):
                st.session_state.pdf_data = generate_pdf(st.session_state.df)
                send_feedback_api(
                    response_object=df_to_processdocumentresponse(
                        df=st.session_state.df, ocr_text=st.session_state.text
                    )
                )
                st.session_state.pdf_ready = True

        if st.session_state.pdf_ready:
            st.download_button(
                label="Download PDF",
                data=st.session_state.pdf_data,
                file_name="generated_pdf.pdf",
                mime="application/pdf",
            )
