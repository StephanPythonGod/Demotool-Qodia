import streamlit as st

from utils.utils import generate_report_files_as_zip


@st.dialog("Export Optionen")
def export_modal(df):
    """Modal dialog for export options."""
    st.subheader("Wählen Sie eine Export-Option")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("PDF generieren", type="primary", use_container_width=True):
            # Close this modal before opening the next one
            st.session_state.show_minderung_modal = True
            st.session_state.generate_type = "pdf"
            st.session_state.generate_df = df
            st.rerun()

        if st.button(
            "PAD Positionen generieren", type="primary", use_container_width=True
        ):
            st.session_state.show_minderung_modal = True
            st.session_state.generate_type = "pad_positionen"
            st.session_state.generate_df = df
            st.rerun()

    with col2:
        if st.button("Bericht exportieren", type="primary", use_container_width=True):
            with st.spinner("📄 Generiere Bericht..."):
                st.session_state.pdf_report_data = generate_report_files_as_zip(df=df)

        if st.button(
            "PADnext Datei generieren",
            type="primary",
            use_container_width=True,
            disabled=(st.session_state.pad_data_path is None),
            help="PADnext Datei kann nur generiert werden, wenn eine PADnext Datei hochgeladen wurde.",
        ):
            st.session_state.show_minderung_modal = True
            st.session_state.generate_type = "pad_next"
            st.session_state.generate_df = df
            st.rerun()

    # Display download buttons if data is ready
    if st.session_state.pdf_ready:
        st.download_button(
            label="Download PDF",
            data=st.session_state.pdf_data,
            file_name="generated_pdf.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    if st.session_state.pad_ready:
        st.download_button(
            label="Download PAD Positionen",
            data=st.session_state.pad_data,
            file_name="pad_positionen.xml",
            mime="application/xml",
            use_container_width=True,
        )

    if st.session_state.pdf_report_data:
        st.download_button(
            label="Download Bericht",
            data=st.session_state.pdf_report_data,
            file_name="report.zip",
            mime="application/zip",
            use_container_width=True,
        )

    if st.session_state.pad_data_ready:
        with open(st.session_state.pad_data_ready, "rb") as f:
            padnext_file_data = f.read()
        st.download_button(
            label="Download PADnext Datei",
            data=padnext_file_data,
            file_name=st.session_state.pad_data_ready.name,
            mime="application/zip",
            use_container_width=True,
        )
