import pandas as pd
import streamlit as st

from utils.helpers.api import send_feedback_api
from utils.helpers.logger import logger
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


def feedback_form(original_df: pd.DataFrame, df: pd.DataFrame) -> None:
    """Returns the Feedback Form."""
    changes = detect_changes(original_df, df)
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
        "Kommentar",
        key="user_comment",
        height=100,
        placeholder="(Optional) Fügen Sie hier Kommentare, Feedback oder Änderungswünsche hinzu ...",
        label_visibility="visible",
        help="Dieser Text geht direkt an Qodia und wir können Ihre Anmerkungen nutzen, um die KI und das Kodierungstool zu verbessern.",
    )


def process_and_send_feedback(df: pd.DataFrame) -> None:
    try:
        # Prepare feedback data for API call
        api_feedback_data = {}
        api_feedback_data["feedback_data"] = df_to_processdocumentresponse(
            df, st.session_state.text
        )
        api_feedback_data["user_comment"] = st.session_state.get("user_comment", None)
        send_feedback_api(api_feedback_data)
        st.success("Feedback erfolgreich gesendet 😊")
    except Exception as e:
        logger.error(f"Failed to generate bill: {e}")
        st.error("Fehler beim Erstellen der Rechnung")


@st.dialog("Feedback geben 🔨", width="large")
def feedback_modal(df: pd.DataFrame) -> None:
    feedback_form(st.session_state.original_df, df)

    if st.button("Feedback senden", type="primary"):
        process_and_send_feedback(df)
        st.rerun()
