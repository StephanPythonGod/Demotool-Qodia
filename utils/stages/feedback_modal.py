from typing import Optional

import pandas as pd
import streamlit as st

from utils.helpers.api import generate_pdf, send_feedback_api
from utils.helpers.logger import logger
from utils.helpers.padnext import generate_pad, generate_padnext
from utils.helpers.transform import df_to_processdocumentresponse

# Define error types
ERROR_TYPES = [
    "Leistung nicht erbracht",
    "Leistung übersehen",
    "Falsche Textstelle als Zitat",
    "Häufigkeit falsch",
    "Faktor falsch",
    "Begründung falsch",
    "Falsche Analogziffer",
    "Analogziffer hat falschen Faktor",
    "Leistung wird bei dieser Krankenkasse nicht abgerechnet",
    "Leistung wird bei diesem Arzt nicht abgerechnet",
    "Anderer Grund",
]

# Define options for 'Minderung Prozentsatz'
MINDERUNG_OPTIONS = ["keine", "15%", "25%"]


def detect_changes(original_df: pd.DataFrame, modified_df: pd.DataFrame) -> list:
    changes = []

    # Columns to ignore
    ignore_columns = ["gesamtbetrag", "einzelbetrag", "confidence", "go"]

    # Add a unique identifier to each row if it doesn't exist
    if "row_id" not in original_df.columns:
        original_df["row_id"] = range(len(original_df))

    if "row_id" not in modified_df.columns:
        modified_df["row_id"] = range(len(modified_df))

    # Detect deleted rows
    deleted_rows = set(original_df["row_id"]) - set(modified_df["row_id"])
    for row_id in deleted_rows:
        original_row = original_df[original_df["row_id"] == row_id].iloc[0]
        changes.append(
            {
                "row_id": row_id,
                "type": "deletion",
                "details": f"Leistung gelöscht: Ziffer {original_row['ziffer']}",
            }
        )

    # Detect modified cells and added rows
    for _, mod_row in modified_df.iterrows():
        row_id = mod_row["row_id"]
        if row_id in set(original_df["row_id"]):
            # Modified row
            orig_row = original_df[original_df["row_id"] == row_id].iloc[0]
            for col in modified_df.columns:
                if (
                    col not in ignore_columns
                    and col != "row_id"
                    and mod_row[col] != orig_row[col]
                ):
                    changes.append(
                        {
                            "row_id": row_id,
                            "type": "modification",
                            "column": col,
                            "old_value": orig_row[col],
                            "new_value": mod_row[col],
                            "ziffer": mod_row["ziffer"],
                        }
                    )
        else:
            # New row
            changes.append(
                {
                    "row_id": row_id,
                    "type": "addition",
                    "details": f"Neue Leistung hinzugefügt: Ziffer {mod_row['ziffer']}",
                    "ziffer": mod_row["ziffer"],
                }
            )

    return changes


@st.dialog("Rechnung erstellen", width="large")
def rechnung_erstellen_modal(df: pd.DataFrame, generate: Optional[str] = None) -> None:
    original_df = st.session_state.original_df
    changes = detect_changes(original_df, df)

    st.write(
        "Bitte wählen Sie den Minderung Prozentsatz und geben Sie eine Begründung an:"
    )

    # Minderung Prozentsatz selection (mandatory)
    prozentsatz = st.selectbox(
        "Minderung Prozentsatz",
        MINDERUNG_OPTIONS,
        index=None,
        key="minderung_prozentsatz",
        placeholder="Bitte wählen ...",
    )

    # Dynamically set the Begründung based on selection
    if prozentsatz == "15%":
        begruendung_default = "Abzgl. 15% Minderung gem. §6a Abs.1 GOÄ"
    elif prozentsatz == "25%":
        begruendung_default = "Abzgl. 25% Minderung gem. §6a Abs.1 GOÄ"
    else:
        begruendung_default = ""

    begruendung = st.text_input(
        "Begründung",
        value=begruendung_default,
        key="minderung_begruendung",
        placeholder="Bitte geben Sie eine Begründung an ...",
    )

    # Store selected values in session state
    st.session_state["minderung_data"]["prozentsatz"] = prozentsatz
    st.session_state["minderung_data"]["begruendung"] = begruendung

    # Display changes and feedback section
    st.subheader("Hier können Sie Feedback an die KI geben.")
    feedback_data = []
    for change in changes:
        if change["type"] == "deletion":
            st.write(f"{change['details']}")
        elif change["type"] == "addition":
            st.write(f"{change['details']}")
        else:
            st.write(
                f"Ziffer {change['ziffer']}, Änderung an '{change['column']}': "
                f"{change['old_value']} -> {change['new_value']}"
            )

        error_type = st.selectbox(
            "Fehlertyp auswählen",
            ERROR_TYPES,
            key=f"error_type_{change['row_id']}_{change.get('column', change['type'])}",
            index=None,
            placeholder="Bitte wählen Sie den Fehlertyp ...",
        )

        if error_type == "Anderer Grund":
            st.info(
                "Bitte geben Sie zusätzliche Informationen im Kommentarfeld unten an."
            )

        feedback_data.append(
            {
                "row_id": change["row_id"],
                "type": change["type"],
                "column": change.get("column"),
                "old_value": change.get("old_value"),
                "new_value": change.get("new_value"),
                "error_type": error_type,
                "ziffer": change.get("ziffer"),
            }
        )

    # Optional feedback text area
    st.text_area(
        "Optional: Add any comments or feedback here",
        key="user_comment",
        height=100,
        placeholder="(Optional) Fügen Sie hier Kommentare oder Feedback hinzu ...",
        label_visibility="collapsed",
    )

    # Disable button until mandatory fields are filled
    if not prozentsatz:
        st.button(
            "Rechnung generieren",
            disabled=True,
            help="Bitte wählen Sie einen Minderung Prozentsatz und geben Sie eine Begründung an.",
        )
    else:
        if st.button("Rechnung generieren"):
            if generate == "pdf":
                try:
                    st.session_state.pdf_data = generate_pdf(df)
                    st.session_state.pdf_ready = True
                except Exception as e:
                    st.error(f"Failed to generate PDF : {str(e)}")
            elif generate == "pad_positionen":
                st.session_state.pad_data = generate_pad(df)
                st.session_state.pad_ready = True
            elif generate == "pad_next":
                pad_data_ready = generate_padnext(df)
                st.session_state.pad_data_ready = pad_data_ready

            try:
                # Prepare feedback data for API call
                api_feedback_data = {}
                api_feedback_data["feedback_data"] = df_to_processdocumentresponse(
                    df, st.session_state.text
                )
                api_feedback_data["user_comment"] = st.session_state.get(
                    "user_comment", None
                )
                send_feedback_api(api_feedback_data)
                st.success("Rechnung erfolgreich generiert!")
            except Exception as e:
                logger.error(f"Failed to generate bill: {e}")
                st.error("Fehler beim Erstellen der Rechnung")
            st.rerun()
