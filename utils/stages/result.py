import streamlit as st
from annotated_text import annotated_text

from utils.helpers.api import generate_pdf
from utils.helpers.transform import annotate_text_update, format_ziffer_to_4digits
from utils.session import reset
from utils.utils import find_zitat_in_text


def set_selected_ziffer(index):
    st.session_state.selected_ziffer = index


def delete_ziffer(index):
    st.session_state.df.drop(index, inplace=True)
    st.session_state.selected_ziffer = None
    st.session_state.df.reset_index(drop=True, inplace=True)
    annotate_text_update()
    st.rerun()


def result_stage():
    "Display the result of the analysis."
    left_column, right_column = st.columns(2)
    left_outer_column, _, _, _, right_outer_column = st.columns([1, 2, 3, 2, 1])

    # Left Column: Display the text with highlighting
    with left_column:
        st.subheader("Ärztlicher Bericht:")

        # Highlight text based on selected Ziffer
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

        # Display column headers
        header_cols = right_column.columns([1, 1, 1, 3, 1])
        headers = ["Ziffer", "Häufigkeit", "Faktor", "Beschreibung", "Aktionen"]
        for col, header in zip(header_cols, headers):
            col.markdown(f"**{header}**")

        # Create a unique identifier for each row
        for index, row in st.session_state.df.iterrows():
            cols = right_column.columns([1, 1, 1, 3, 0.5, 0.5])
            if cols[0].button(
                format_ziffer_to_4digits(row["Ziffer"]),
                key=f"ziffer_{index}",
                type="secondary"
                if st.session_state.selected_ziffer != index
                else "primary",
            ):
                if st.session_state.selected_ziffer == index:
                    set_selected_ziffer(None)
                else:
                    set_selected_ziffer(index)
                st.rerun()
            # Use HTML and CSS for scrollable text field
            description_html = f"""
            <div style="overflow-x: auto; white-space: nowrap; padding: 5px;">
                {row['Beschreibung']}
            </div>
            """

            cols[1].write(row["Häufigkeit"])
            cols[2].write(row["Intensität"])
            cols[3].markdown(description_html, unsafe_allow_html=True)

            # Add a delete button for each row
            if cols[4].button("✏️", key=f"edit_{index}"):
                st.session_state.ziffer_to_edit = index
                st.session_state.stage = "modal"
                st.rerun()
            if cols[5].button("🗑️", key=f"delete_{index}"):
                delete_ziffer(index)

        _, middle_column_right_column, _ = st.columns([3, 1, 3])

        with middle_column_right_column:
            st.write("")
            # Add a button to add a new row
            if middle_column_right_column.button("➕", use_container_width=True):
                st.session_state.ziffer_to_edit = None
                st.session_state.stage = "modal"
                st.rerun()

    with left_outer_column:
        st.button(
            "Zurücksetzen", on_click=reset, type="primary", use_container_width=True
        )

    with right_outer_column:
        if st.button("PDF generieren", type="primary", use_container_width=True):
            with st.spinner("📄 Generiere PDF..."):
                st.session_state.pdf_data = generate_pdf(st.session_state.df)
                st.session_state.pdf_ready = True

        # If the PDF is ready, show the download button
        if st.session_state.pdf_ready:
            st.download_button(
                label="Download PDF",
                data=st.session_state.pdf_data,
                file_name="generated_pdf.pdf",
                mime="application/pdf",
            )
