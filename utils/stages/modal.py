from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import streamlit as st

from utils.helpers.db import read_in_goa
from utils.helpers.logger import logger
from utils.helpers.transform import annotate_text_update
from utils.utils import ziffer_from_options


def determine_additional_fields(
    ziffer_data: Dict[str, Union[str, int, float, None]]
) -> Dict[str, Union[float, str, None]]:
    """
    Determine the additional fields like 'confidence', 'analog', 'einzelbetrag', 'gesamtbetrag', and 'go'.

    Args:
        ziffer_data (Dict[str, Union[str, int, float, None]]): The current ziffer data.
        ziffer_dataframe (pd.DataFrame): The DataFrame with GOÄ data for ziffer calculations.

    Returns:
        Dict[str, Union[float, str, None]]: A dictionary containing the additional field values.
    """
    ziffer_dataframe: pd.DataFrame = read_in_goa()  # Load ziffer data

    analog = ziffer_data.get("analog", None)
    ziffer_selected = analog if analog else ziffer_data["ziffer"]

    einzelbetrag = calculate_einzelbetrag(
        ziffer_data["faktor"], ziffer_selected, ziffer_dataframe
    )
    gesamtbetrag = calculate_gesamtbetrag(einzelbetrag, ziffer_data["anzahl"])

    return {
        "confidence": ziffer_data.get("confidence", 1.0),
        "analog": analog,
        "einzelbetrag": einzelbetrag,
        "gesamtbetrag": gesamtbetrag,
        "go": "GOAE",  # Default to GOAE
    }


def update_ziffer(new_ziffer: Dict[str, Union[str, int, float, None]]) -> None:
    try:
        # Determine additional fields
        additional_fields = determine_additional_fields(new_ziffer)
        new_ziffer.update(additional_fields)

        # Check if the ziffer is valid (you may want to adjust this condition)
        is_valid_ziffer = (
            new_ziffer["ziffer"] is not None and new_ziffer["ziffer"] != ""
        )

        if is_valid_ziffer:
            # Update the existing row or add a new one
            if st.session_state.ziffer_to_edit is not None:
                st.session_state.df.iloc[st.session_state.ziffer_to_edit] = new_ziffer
            else:
                new_row = pd.DataFrame(new_ziffer, index=[0])
                st.session_state.df = pd.concat(
                    [st.session_state.df, new_row], ignore_index=True
                )

            annotate_text_update()
        else:
            # Remove the temporary row if it's not valid
            if st.session_state.ziffer_to_edit is not None:
                st.session_state.df = st.session_state.df.drop(
                    st.session_state.ziffer_to_edit
                )
                st.session_state.df = st.session_state.df.reset_index(drop=True)

        # Reset the editing state
        st.session_state.ziffer_to_edit = None
        st.session_state.selected_ziffer = None
        st.session_state.adding_new_ziffer = False
        st.session_state.stage = "result"
    except Exception as e:
        logger.error(f"Error updating ziffer: {str(e)}")
        st.error(
            "Ein Fehler ist beim Aktualisieren der Ziffer aufgetreten. Bitte versuchen Sie es erneut."
        )


def display_update_button(new_data: Dict[str, Union[str, int, float, None]]) -> None:
    """
    Display the "Aktualisieren" button to save the new ziffer data.
    """
    all_fields_filled = all(
        [
            new_data["ziffer"],
            new_data["anzahl"],
            new_data["faktor"],
            new_data["text"],
            new_data["zitat"],
        ]
    )

    if all_fields_filled:
        if st.button(
            "Aktualisieren",
            type="primary",
            use_container_width=True,
        ):
            update_ziffer(new_data)
            st.rerun()
    else:
        st.button(
            "Aktualisieren",
            on_click=None,
            type="primary",
            use_container_width=True,
            disabled=True,
            help="Bitte füllen Sie alle erforderlichen Felder aus.",
        )


@st.dialog("Leistungsziffer aktualisieren", width="large")
def modal_dialog() -> None:
    try:
        ziffer_dataframe: pd.DataFrame = read_in_goa()
        ziffer_options: list = ziffer_dataframe["GOÄZiffer"].tolist()
        ziffer_beschreibung: list = ziffer_dataframe["Beschreibung"].tolist()

        ziffer_data: Dict[str, Union[str, int, float, None]] = get_ziffer_data()

        ziffer_index: Optional[int] = get_ziffer_index(
            ziffer_options, ziffer_data.get("ziffer")
        )

        st.subheader("Ziffer")
        ziffer, beschreibung = display_ziffer_selection(
            ziffer_options, ziffer_beschreibung, ziffer_index, ziffer_data.get("text")
        )

        st.subheader("Analog")
        analog = display_analog_selection(ziffer_options, ziffer_data.get("analog"))

        haufigkeit = display_haufigkeit_input(ziffer_data.get("anzahl"))
        intensitat = display_intensitat_input(ziffer_data.get("faktor"))
        zitat = display_zitat_input(ziffer_data.get("zitat"))
        begruendung = display_begrundung_input(ziffer_data.get("begruendung"))

        ziffer_selected = analog if analog else ziffer
        einzelbetrag = (
            calculate_einzelbetrag(intensitat, ziffer_selected, ziffer_dataframe)
            if ziffer_selected
            else 0.0
        )
        gesamtbetrag = calculate_gesamtbetrag(einzelbetrag, haufigkeit)

        st.subheader("Zusätzliche Informationen")
        st.markdown(
            f"Einzelbetrag: {einzelbetrag:,.2f} €".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        st.markdown(
            f"Gesamtbetrag: {gesamtbetrag:,.2f} €".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        st.markdown(f"Confidence: {ziffer_data.get('confidence', 1.0)}")
        st.markdown(
            f"GO: {'GOÄ' if ziffer_data.get('go') == 'GOAE' else ziffer_data.get('go', 'Nicht verfügbar')}"
        )

        # Prepare new data for update
        new_data = create_new_data(
            ziffer,
            analog,
            haufigkeit,
            intensitat,
            beschreibung,
            zitat,
            begruendung,
            einzelbetrag,
            gesamtbetrag,
        )

        # Display the "Aktualisieren" button
        display_update_button(new_data)

    except Exception as e:
        logger.error(f"Error in modal_stage: {str(e)}")
        st.error(
            "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
        )


# Helper functions:


def calculate_einzelbetrag(
    faktor: float, ziffer_selected: str, ziffer_dataframe: pd.DataFrame
) -> float:
    """
    Calculate the einzelbetrag based on intensität and häufigkeit.

    Args:
        faktor (float): The current intensität value.
        anzahl (int): The current häufigkeit value.

    Returns:
        float: The calculated einzelbetrag.
    """

    # get the row of the selected ziffer
    goa_item = ziffer_dataframe[ziffer_dataframe["GOÄZiffer"] == ziffer_selected]

    if goa_item.empty:
        logger.error(f"No matching GOÄZiffer for selected Ziffer {ziffer_selected}")
        return 0.0

    regelhoechstfaktor = goa_item["Regelhöchstfaktor"].values[0]
    regelhoechstsatz = goa_item["Regelhöchstsatz"].values[0]
    hoechstfaktor = goa_item["Höchstfaktor"].values[0]
    hoechstsatz = goa_item["Höchstsatz"].values[0]
    einfachsatz = goa_item["Einfachsatz"].values[0]

    if (
        isinstance(hoechstfaktor, float)
        and isinstance(hoechstsatz, float)
        and faktor >= hoechstfaktor
    ):
        return hoechstsatz
    elif (
        isinstance(regelhoechstfaktor, float)
        and isinstance(regelhoechstsatz, float)
        and faktor >= regelhoechstfaktor
    ):
        return regelhoechstsatz
    elif isinstance(einfachsatz, float):
        return einfachsatz
    else:
        logger.error(f"Invalid data for selected Ziffer {ziffer_selected}")
        return 0.0


def calculate_gesamtbetrag(einzelbetrag: float, anzahl: int) -> float:
    """
    Calculate the gesamtbetrag based on einzelbetrag and häufigkeit.

    Args:
        einzelbetrag (float): The einzelbetrag value.
        anzahl (int): The current häufigkeit value.

    Returns:
        float: The calculated gesamtbetrag.
    """
    return einzelbetrag * anzahl


def display_analog_selection(
    ziffer_options: list, current_value: Optional[str]
) -> Optional[str]:
    cleaned_ziffer_options = [ziffer.split(" - ")[0] for ziffer in ziffer_options]

    if current_value not in cleaned_ziffer_options:
        current_value = None

    analog = st.selectbox(
        "Analog auswählen",
        options=["Keine Auswahl"] + ziffer_options,
        index=0
        if current_value is None
        else (cleaned_ziffer_options.index(current_value) + 1),
        label_visibility="collapsed",
    )
    return analog if analog != "Keine Auswahl" else None


def get_ziffer_data() -> Dict[str, Union[str, int, float, None]]:
    if st.session_state.get("ziffer_to_edit") is not None:
        return st.session_state.df.iloc[st.session_state.ziffer_to_edit].to_dict()
    else:
        return {
            "ziffer": None,
            "anzahl": 0,
            "faktor": 1.0,
            "text": None,
            "zitat": st.session_state.text,
            "begruendung": None,
            "confidence": 1.0,
            "analog": None,
            "einzelbetrag": 0.0,
            "gesamtbetrag": 0.0,
            "go": None,
        }


def get_ziffer_index(ziffer_options: List[str], ziffer: Optional[str]) -> Optional[int]:
    if ziffer is None:
        return None
    try:
        return ziffer_from_options(ziffer_options).index(ziffer)
    except ValueError:
        return None


def display_ziffer_selection(
    ziffer_options: List[str],
    ziffer_beschreibung: List[str],
    ziffer_index: Optional[int],
    ziffer_text: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    ziffer_selections = [
        f"{ziffer} - {ziffer_text if ziffer_text and idx == ziffer_index else beschreibung}"
        for idx, (ziffer, beschreibung) in enumerate(
            zip(ziffer_options, ziffer_beschreibung)
        )
    ]

    ziffer_display = st.selectbox(
        "Ziffer auswählen",
        options=["Bitte wählen Sie eine Ziffer aus ..."] + ziffer_selections,
        index=0 if ziffer_index is None else ziffer_index + 1,
        label_visibility="collapsed",
    )

    if ziffer_display == "Bitte wählen Sie eine Ziffer aus ...":
        return None, None

    selected_ziffer, selected_beschreibung = ziffer_display.split(" - ", 1)
    return selected_ziffer, selected_beschreibung


def display_haufigkeit_input(current_value: Optional[int]) -> int:
    st.subheader("Häufigkeit")
    return st.number_input(
        "Häufigkeit setzen",
        value=current_value if current_value is not None else 0,
        placeholder="Bitte wählen Sie die Häufigkeit der Leistung ...",
        min_value=0,
        max_value=20,
        label_visibility="collapsed",
    )


def display_intensitat_input(current_value: Optional[float]) -> float:
    st.subheader("Faktor")
    intensitat = st.number_input(
        "Faktor setzen",
        value=current_value if current_value is not None else 1.0,
        placeholder="Bitte wählen Sie die Intensität der Durchführung der Leistung ...",
        min_value=0.0,
        max_value=5.0,
        step=0.1,
        format="%.1f",
        label_visibility="collapsed",
    )
    return round(intensitat, 1)


def display_zitat_input(current_value: Optional[str]) -> str:
    st.subheader("Textzitat")
    return st.text_area(
        "Textzitat einfügen",
        value=current_value if current_value is not None else "",
        placeholder="Bitte hier das Textzitat einfügen ...",
        help="Hier soll ein Zitat aus dem ärztlichen Bericht eingefügt werden, welches die Leistungsziffer begründet.",
        height=200,
    )


def display_begrundung_input(current_value: Optional[str]) -> Optional[str]:
    """
    Display the begründung input field.

    Args:
        current_value (Optional[str]): The current begründung value.

    Returns:
        Optional[str]: The entered begründung, or None if empty.
    """
    st.subheader("Begründung")
    begruendung = st.text_area(
        "Begründung eingeben",
        value=current_value,
        placeholder="Bitte hier die Begründung einfügen ...",
        help="Hier soll die Begründung für die Leistungsziffer eingefügt werden.",
        height=400,
    )
    return begruendung if begruendung else None


def create_new_data(
    ziffer: str,
    analog: Optional[str],
    haufigkeit: int,
    intensitat: float,
    beschreibung: Optional[str],
    zitat: str,
    begruendung: Optional[str],
    einzelbetrag: float,
    gesamtbetrag: float,
) -> Dict[str, Union[str, int, float, None]]:
    """
    Create a dictionary with the new ziffer data.

    Args:
        ziffer (str): The selected ziffer.
        analog (Optional[str]): The selected analog value.
        haufigkeit (int): The selected häufigkeit.
        intensitat (float): The selected intensität.
        beschreibung (Optional[str]): The ziffer description.
        zitat (str): The entered zitat.
        begruendung (Optional[str]): The entered begründung.
        einzelbetrag (float): The calculated einzelbetrag.
        gesamtbetrag (float): The calculated gesamtbetrag.

    Returns:
        Dict[str, Union[str, int, float, None]]: The new ziffer data.
    """
    new_data = {
        "ziffer": ziffer,
        "analog": analog,
        "anzahl": haufigkeit,
        "faktor": intensitat,
        "text": beschreibung,
        "zitat": zitat,
        "begruendung": begruendung,
        "einzelbetrag": einzelbetrag,
        "gesamtbetrag": gesamtbetrag,
    }

    # Add additional fields
    additional_fields = determine_additional_fields(new_data)
    new_data.update(additional_fields)

    return new_data
