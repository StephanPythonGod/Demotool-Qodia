import pandas as pd
import streamlit as st

from utils.helpers.api import send_feedback_api
from utils.helpers.logger import logger
from utils.helpers.transform import df_to_processdocumentresponse


def detect_changes(original_df: pd.DataFrame, modified_df: pd.DataFrame) -> list:
    """
    Silently detect changes between original and modified DataFrames.
    This function remains unchanged to maintain API compatibility.
    """
    changes = []
    ignore_columns = ["gesamtbetrag", "einzelbetrag", "confidence", "go"]

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
    """Simplified feedback form with only a comment box."""
    st.subheader("Hier können Sie Feedback an die KI geben.")

    # Silently detect changes for API
    changes = detect_changes(original_df, df)

    # Store changes in session state with empty error_type
    feedback_data = []
    for change in changes:
        feedback_data.append(
            {
                "row_id": change["row_id"],
                "type": change["type"],
                "column": change.get("column"),
                "old_value": change.get("old_value"),
                "new_value": change.get("new_value"),
                "error_type": None,
                "ziffer": change.get("ziffer"),
            }
        )

    # Use a form to enable submission via Enter key
    with st.form(key="feedback_form", border=False):
        st.text_area(
            "Kommentar",
            key="user_comment",
            height=100,
            placeholder="Fügen Sie hier Kommentare, Feedback oder Änderungswünsche hinzu ...",
            label_visibility="visible",
            help="Dieser Text geht direkt an Qodia und wir können Ihre Anmerkungen nutzen, um die KI und das Kodierungstool zu verbessern.",
        )

        submit = st.form_submit_button("Feedback senden", type="primary")
        return submit


def process_and_send_feedback(df: pd.DataFrame) -> None:
    """Process and send feedback to the API."""
    try:
        api_feedback_data = {}
        api_feedback_data["feedback_data"] = df_to_processdocumentresponse(
            df, st.session_state.text
        )
        api_feedback_data["user_comment"] = st.session_state.get("user_comment", None)
        send_feedback_api(api_feedback_data)
        st.success("Feedback erfolgreich gesendet 😊")
    except Exception as e:
        logger.error(f"Failed to send feedback: {e}")
        st.error("Fehler beim Senden des Feedbacks")


@st.dialog("Feedback geben 🔨", width="large")
def feedback_modal(df: pd.DataFrame) -> None:
    """Display the simplified feedback modal."""
    if feedback_form(st.session_state.original_df, df):
        process_and_send_feedback(df)
