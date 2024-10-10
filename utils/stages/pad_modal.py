from pathlib import Path

import streamlit as st

from utils.helpers.files import load_file_from_path


@st.dialog("PADnext Anhang auswählen", width="large")
def pad_file_modal(files: list[Path]) -> Path:
    st.markdown(
        "Bitte wählen Sie den Anhang der PADnext Datei aus, der für die Analyse verwendet werden soll:"
    )
    for file in files:
        if st.button(file.name):
            try:
                uploaded_file = load_file_from_path(file)
                st.session_state.uploaded_file = uploaded_file
                st.session_state.file_selected = True
                st.rerun()
            except ValueError as e:
                st.error(f"Fehler beim Laden der Datei: {e}")
