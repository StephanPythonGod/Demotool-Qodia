import re
from pathlib import Path

import pandas as pd
import streamlit as st
from annotated_text import annotated_text

from utils.helpers.api import generate_pdf
from utils.helpers.logger import logger
from utils.helpers.padnext import (
    create_positionen_object,
    update_padnext_positionen,
    write_object_to_xml,
)
from utils.helpers.transform import (
    annotate_text_update,
    format_euro,
    format_ziffer_to_4digits,
    split_recognized_and_potential,
    transform_df_to_goziffertyp,
)
from utils.stages.feedback_modal import feedback_modal
from utils.stages.modal import create_new_data, modal_dialog
from utils.utils import create_tooltip, find_zitat_in_text, tooltip_css


def add_new_ziffer():
    # Create a temporary placeholder for the new ziffer
    new_row_id = (
        st.session_state.df["row_id"].max() + 1 if len(st.session_state.df) > 0 else 0
    )
    temp_index = len(st.session_state.df)

    # Add a temporary row to the dataframe
    temp_row = create_new_data(
        ziffer=None,
        analog=None,
        haufigkeit=0,
        intensitat=1.0,
        beschreibung=None,
        zitat=st.session_state.text,
        begruendung=None,
        einzelbetrag=0.0,
        gesamtbetrag=0.0,
        row_id=new_row_id,  # Add row_id to the new row
    )
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([temp_row])], ignore_index=True
    )
    # Set the temporary row as the selected index
    st.session_state.selected_ziffer = temp_index

    # Set a flag to indicate that we're adding a new ziffer
    st.session_state.adding_new_ziffer = True

    # Open the modal dialog for editing the new row
    st.session_state.ziffer_to_edit = temp_index
    modal_dialog()


def set_selected_ziffer(index):
    st.session_state.selected_ziffer = index


def add_to_recognized(index):
    st.session_state.df.loc[index, "confidence"] = 1.0
    st.rerun()


def delete_ziffer(index):
    st.session_state.df = st.session_state.df[st.session_state.df.index != index]
    st.session_state.selected_ziffer = None
    annotate_text_update()
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
    st.session_state.df.drop(
        columns=["numeric_ziffer"], inplace=True
    )  # Remove helper column


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


def generate_pad(df):
    # Generate PAD positions
    goziffern = transform_df_to_goziffertyp(df)
    positionen_obj = create_positionen_object(goziffern)
    output_path = "./data/pad_positionen.xml"
    output_path = write_object_to_xml(positionen_obj, output_path=output_path)
    with open(output_path, "r", encoding="iso-8859-15") as f:
        xml_object = f.read()
    return xml_object


def generate_padnext(df):
    with st.spinner("Generiere PADnext Datei..."):
        # Generate PADnext file based on uploaded PADnext file
        goziffern = transform_df_to_goziffertyp(df)
        positionen_obj = create_positionen_object(goziffern)
        pad_data_ready = update_padnext_positionen(
            padnext_folder=st.session_state.pad_data_path, positionen=positionen_obj
        )
        if isinstance(pad_data_ready, Path):
            return pad_data_ready
        else:
            return False


def handle_feedback_submission():
    # Open Feedback Modal
    feedback_modal(df=st.session_state.df)


def result_stage():
    "Display the result of the analysis."

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
    if "original_df" not in st.session_state or st.session_state.original_df is None:
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

    left_column, right_column = st.columns(2)
    left_outer_column, _, _, _, right_outer_column = st.columns([1, 2, 2, 2, 1])

    # Left Column: Display the text with highlighting
    with left_column:
        st.subheader("Ärztlicher Bericht:")
        if (
            "selected_ziffer" in st.session_state
            and st.session_state.selected_ziffer is not None
        ):
            selected_zitat = st.session_state.df.loc[
                st.session_state.selected_ziffer, "zitat"
            ]
            selected_ziffer = st.session_state.df.loc[
                st.session_state.selected_ziffer, "ziffer"
            ]
            annotated_text(
                find_zitat_in_text(
                    [(selected_zitat, selected_ziffer)], [st.session_state.text]
                )
            )
        else:
            st.write(st.session_state.text)

    with right_column:
        top_left, _, _, top_right = st.columns([2, 1, 1, 1])
        top_left.subheader("Erkannte Leistungsziffern:")

        # Displaying the Honorarsumme (Sum of "Gesamtbetrag" column) with thousand separators
        top_right.metric(
            label="Honorarsumme",
            value=format_euro(recognized_df["gesamtbetrag"].sum()),
        )

        # Header row
        header_cols = right_column.columns([0.5, 1, 1, 1, 1, 2, 1])
        headers = [
            "",
            "Ziffer",
            "Häufigkeit",
            "Faktor",
            "Gesamtbetrag",
            "Beschreibung",
            "Aktionen",
        ]

        for i, (col, header) in enumerate(zip(header_cols, headers)):
            if header == "Ziffer":
                # Set selected_ziffer to None

                # Set the button label based on the current sort_mode
                sort_label = {"ask": "Ziffer ⬆️", "desc": "Ziffer ⬇️"}

                # Initialize sort_mode in session_state if not set yet
                sort_mode = st.session_state.get("sort_mode", "text")

                # Display the button and set the sort mode accordingly
                col.button(
                    sort_label.get(sort_mode, "Ziffer 🔠"),
                    on_click=lambda: (set_selected_ziffer(None), set_sort_mode()),
                )
            elif header == "":
                pass
            else:
                col.markdown(f"**{header}**")

        # Display table rows, now including "Gesamtbetrag" in the table
        for index, row in recognized_df.iterrows():
            cols = right_column.columns([0.5, 1, 1, 1, 1, 2, 0.5, 0.5])

            # Ziffer button
            if cols[1].button(
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

            # Displaying each row's values
            cols[2].write(row["anzahl"])  # Häufigkeit
            cols[3].write(row["faktor"])  # Faktor

            # Format "Gesamtbetrag" with thousand separators
            formatted_gesamtbetrag = format_euro(row["gesamtbetrag"])
            cols[4].write(
                f"{formatted_gesamtbetrag}"
            )  # New "Gesamtbetrag" column displaying value

            description_html = f"<div style='overflow-x: auto; white-space: nowrap; padding: 5px;'>{row['text']}</div>"
            cols[5].markdown(description_html, unsafe_allow_html=True)  # Beschreibung

            # Actions: Edit and Delete
            if cols[6].button(
                "✏️", key=f"edit_{row['row_id']}"
            ):  # Use row_id in the key
                st.session_state.ziffer_to_edit = index
                modal_dialog()
            if cols[7].button(
                "🗑️", key=f"delete_{row['row_id']}"
            ):  # Use row_id in the key
                delete_ziffer(index)

        # Center the "Add New Ziffer" button
        button_col = right_column.columns([1, 1, 1, 1, 2, 1, 1, 1, 1])[4]
        if button_col.button("➕", key="add_new_ziffer", type="secondary"):
            add_new_ziffer()

        st.subheader("Potentielle Leistungsziffern:")

        # Display potential services
        for index, row in potential_df.iterrows():
            cols = right_column.columns([0.5, 1, 1, 1, 1, 2, 0.5, 0.5])

            cols[0].markdown(tooltip_css, unsafe_allow_html=True)
            cols[0].markdown(
                create_tooltip(row["confidence"], row["confidence_reason"]),
                unsafe_allow_html=True,
            )
            cols[1].button(
                format_ziffer_to_4digits(row["ziffer"]),
                key=f"pot_ziffer_{row['row_id']}",
            )
            cols[2].write(row["anzahl"])
            cols[3].write(row["faktor"])
            cols[4].write(format_euro(row["gesamtbetrag"]))
            cols[5].markdown(
                f"<div style='overflow-x: auto; white-space: nowrap; padding: 5px;'>{row['text']}</div>",
                unsafe_allow_html=True,
            )
            if cols[6].button("✏️", key=f"pot_edit_{row['row_id']}"):
                st.session_state.ziffer_to_edit = index
                modal_dialog()
            if cols[7].button("➕", key=f"pot_add_{row['row_id']}"):
                add_to_recognized(index)

    # Rest of the layout
    with left_outer_column:
        st.button(
            "Zurücksetzen",
            on_click=lambda: (handle_feedback_submission(),),
            type="primary",
            use_container_width=True,
        )
        with right_outer_column:
            if st.button("PDF generieren", type="primary", use_container_width=True):
                with st.spinner("📄 Generiere PDF..."):
                    try:
                        st.session_state.pdf_data = generate_pdf(recognized_df)
                        st.session_state.pdf_ready = True
                    except Exception as e:
                        st.error(f"Failed to generate PDF : {str(e)}")

                    handle_feedback_submission()

            if st.session_state.pdf_ready:
                st.download_button(
                    label="Download PDF",
                    data=st.session_state.pdf_data,
                    file_name="generated_pdf.pdf",
                    mime="application/pdf",
                )

            if st.button(
                "PAD Positionen generieren", type="primary", use_container_width=True
            ):
                st.session_state.pad_data = generate_pad(recognized_df)
                st.session_state.pad_ready = True
                handle_feedback_submission()

            if st.session_state.pad_ready:
                st.download_button(
                    label="Download PAD Positionen",
                    data=st.session_state.pad_data,
                    file_name="pad_positionen.xml",
                    mime="application/xml",
                )

            if st.button(
                "PADnext Datei generieren",
                type="primary",
                use_container_width=True,
                disabled=(st.session_state.pad_data_path is None),
                help="PADnext Datei kann nur generiert werden, wenn eine PADnext Datei hochgeladen wurde.",
            ):
                pad_data_ready = generate_padnext(recognized_df)
                st.session_state.pad_data_ready = pad_data_ready
                logger.info("PADnext Datei generiert")
                handle_feedback_submission()

            if st.session_state.pad_data_ready:
                # Read the .zip file as binary data
                with open(st.session_state.pad_data_ready, "rb") as f:
                    padnext_file_data = f.read()

                # Now, pass the binary data to the download button
                st.download_button(
                    label="Download PADnext Datei",
                    data=padnext_file_data,  # Binary data
                    file_name=st.session_state.pad_data_ready.name,  # Extract the filename from the Path object
                    mime="application/zip",  # Adjust MIME type for a .zip file
                )
