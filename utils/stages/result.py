import re
from pathlib import Path

import pandas as pd
import streamlit as st
from annotated_text import annotated_text

from utils.helpers.api import generate_pdf, send_feedback_api
from utils.helpers.logger import logger
from utils.helpers.padnext import (
    create_positionen_object,
    update_padnext_positionen,
    write_object_to_xml,
)
from utils.helpers.transform import (
    annotate_text_update,
    df_to_processdocumentresponse,
    format_euro,
    format_ziffer_to_4digits,
    transform_df_to_goziffertyp,
)
from utils.session import reset
from utils.stages.modal import create_new_data, modal_dialog
from utils.utils import find_zitat_in_text


def add_new_ziffer():
    # Create a temporary placeholder for the new ziffer
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
    st.session_state.df["numeric_ziffer"] = st.session_state.df["ziffer"].apply(
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


def generate_pad():
    # Generate PAD positions
    goziffern = transform_df_to_goziffertyp(st.session_state.df)
    positionen_obj = create_positionen_object(goziffern)
    output_path = "./data/pad_positionen.xml"
    output_path = write_object_to_xml(positionen_obj, output_path=output_path)
    with open(output_path, "r", encoding="iso-8859-15") as f:
        xml_object = f.read()
    return xml_object


def generate_padnext():
    with st.spinner("Generiere PADnext Datei..."):
        # Generate PADnext file based on uploaded PADnext file
        goziffern = transform_df_to_goziffertyp(st.session_state.df)
        positionen_obj = create_positionen_object(goziffern)
        pad_data_ready = update_padnext_positionen(
            padnext_folder=st.session_state.pad_data_path, positionen=positionen_obj
        )
        if isinstance(pad_data_ready, Path):
            return pad_data_ready
        else:
            return False


def handle_feedback_submission():
    try:
        # Include the user comment from the text area in the feedback data
        feedback_data = df_to_processdocumentresponse(
            st.session_state.df, st.session_state.text
        )

        # Access the user comment from session state
        user_comment = st.session_state.get("user_comment", "")
        feedback_with_comment = {
            "feedback_data": feedback_data,
            "user_comment": user_comment,  # Include the comment if provided
        }

        send_feedback_api(feedback_with_comment)  # Pass the data to the API

        st.success("Feedback successfully sent!")
    except Exception as e:
        logger.error(f"Failed to send feedback: {e}")
        st.error("Failed to send feedback")


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
            value=format_euro(st.session_state.df["gesamtbetrag"].sum()),
        )

        # Header row with the new Ziffer button and the new "Gesamtbetrag" column
        header_cols = right_column.columns(
            [1, 1, 1, 1, 2, 1]
        )  # Adjusted column widths for the new column
        headers = [
            "Ziffer",
            "Häufigkeit",
            "Faktor",
            "Gesamtbetrag",
            "Beschreibung",
            "Aktionen",
        ]
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

        # Display table rows, now including "Gesamtbetrag" in the table
        for index, row in st.session_state.df.iterrows():
            cols = right_column.columns(
                [1, 1, 1, 1, 2, 0.5, 0.5]
            )  # Adjusted column widths for the new column

            # Ziffer button
            if cols[0].button(
                format_ziffer_to_4digits(row["ziffer"]),
                key=f"ziffer_{index}",
                type="secondary"
                if st.session_state.selected_ziffer != index
                else "primary",
            ):
                set_selected_ziffer(
                    None if st.session_state.selected_ziffer == index else index
                )
                st.rerun()

            # Displaying each row's values
            cols[1].write(row["anzahl"])  # Häufigkeit
            cols[2].write(row["faktor"])  # Faktor

            # Format "Gesamtbetrag" with thousand separators
            formatted_gesamtbetrag = format_euro(row["gesamtbetrag"])
            cols[3].write(
                f"{formatted_gesamtbetrag}"
            )  # New "Gesamtbetrag" column displaying value

            description_html = f"<div style='overflow-x: auto; white-space: nowrap; padding: 5px;'>{row['text']}</div>"
            cols[4].markdown(description_html, unsafe_allow_html=True)  # Beschreibung

            # Actions: Edit and Delete
            if cols[5].button("✏️", key=f"edit_{index}"):
                st.session_state.ziffer_to_edit = index
                modal_dialog()
            if cols[6].button("🗑️", key=f"delete_{index}"):
                delete_ziffer(index)

        # Center the "Add New Ziffer" button
        button_col = right_column.columns([1, 1, 1, 1, 2, 1, 1, 1, 1])[4]
        if button_col.button("➕", key="add_new_ziffer", type="secondary"):
            add_new_ziffer()

        # Add a text area for the user comment under the table
        st.text_area(
            "Optional: Add any comments or feedback here",
            key="user_comment",
            height=100,
            placeholder="(Optional) Fügen Sie hier Kommentare oder Feedback hinzu ...",
            label_visibility="collapsed",
        )

    # Rest of the layout
    with left_outer_column:
        st.button(
            "Zurücksetzen",
            on_click=lambda: (
                handle_feedback_submission(),
                reset(),
            ),
            type="primary",
            use_container_width=True,
        )

    with right_outer_column:
        if st.button("PDF generieren", type="primary", use_container_width=True):
            with st.spinner("📄 Generiere PDF..."):
                try:
                    st.session_state.pdf_data = generate_pdf(st.session_state.df)
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
            st.session_state.pad_data = generate_pad()
            st.session_state.pad_ready = True

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
            pad_data_ready = generate_padnext()
            st.session_state.pad_data_ready = pad_data_ready
            print("PADnext Datei generiert")
            print(pad_data_ready)

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
