from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import streamlit as st

from utils.helpers.db import read_in_goa
from utils.helpers.logger import logger
from utils.helpers.transform import annotate_text_update
from utils.utils import ziffer_from_options


def update_ziffer(new_ziffer: Dict[str, Union[str, int, float, None]]) -> None:
    """
    Update the data in the result stage after editing.

    Args:
        new_ziffer (Dict[str, Union[str, int, float, None]]): The new or updated ziffer data.
    """
    try:
        if st.session_state.ziffer_to_edit is None:
            new_row = pd.DataFrame(new_ziffer, index=[0])
            new_row = new_row.apply(pd.to_numeric, errors="ignore", downcast="integer")
            st.session_state.df = pd.concat(
                [st.session_state.df, new_row], ignore_index=True
            )
        else:
            new_ziffer = {
                k: pd.to_numeric(v, errors="ignore", downcast="integer")
                if isinstance(v, (int, float))
                else v
                for k, v in new_ziffer.items()
            }
            st.session_state.df.iloc[st.session_state.ziffer_to_edit] = new_ziffer

        annotate_text_update()
        st.session_state.update(stage="result")
    except Exception as e:
        logger.error(f"Error updating ziffer: {str(e)}")
        st.error(
            "Ein Fehler ist beim Aktualisieren der Ziffer aufgetreten. Bitte versuchen Sie es erneut."
        )


def modal_stage() -> None:
    """
    Display the modal for editing a Ziffer.
    """
    try:
        ziffer_dataframe: pd.DataFrame = read_in_goa()
        ziffer_options: List[str] = ziffer_dataframe["Ziffern"].tolist()

        ziffer_data: Dict[str, Union[str, int, float, None]] = get_ziffer_data()
        ziffer_index: Optional[int] = get_ziffer_index(
            ziffer_options, ziffer_data["Ziffer"]
        )

        st.subheader("Leistungsziffer aktualisieren")

        ziffer, beschreibung = display_ziffer_selection(ziffer_options, ziffer_index)
        haufigkeit = display_haufigkeit_input(ziffer_data["Häufigkeit"])
        intensitat = display_intensitat_input(ziffer_data["Intensität"])
        zitat = display_zitat_input(ziffer_data["Zitat"])
        begrundung = display_begrundung_input(ziffer_data["Begründung"])

        new_data = create_new_data(
            ziffer, haufigkeit, intensitat, beschreibung, zitat, begrundung
        )
        display_buttons(new_data)

    except Exception as e:
        logger.error(f"Error in modal_stage: {str(e)}")
        st.error(
            "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut oder kontaktieren Sie den Support."
        )


def get_ziffer_data() -> Dict[str, Union[str, int, float, None]]:
    """
    Get the data for the ziffer to edit.

    Returns:
        Dict[str, Union[str, int, float, None]]: The ziffer data.
    """
    if st.session_state.get("ziffer_to_edit") is not None:
        return st.session_state.df.iloc[st.session_state.ziffer_to_edit].to_dict()
    else:
        return {
            "Ziffer": "",
            "Häufigkeit": None,
            "Intensität": None,
            "Beschreibung": None,
            "Zitat": st.session_state.text,
            "Begründung": None,
        }


def get_ziffer_index(ziffer_options: List[str], ziffer: str) -> Optional[int]:
    """
    Get the index of the selected ziffer.

    Args:
        ziffer_options (List[str]): List of available ziffer options.
        ziffer (str): The selected ziffer.

    Returns:
        Optional[int]: The index of the selected ziffer, or None if not found.
    """
    try:
        return ziffer_from_options(ziffer_options).index(ziffer)
    except ValueError:
        return None


def display_ziffer_selection(
    ziffer_options: List[str], ziffer_index: Optional[int]
) -> Tuple[str, Optional[str]]:
    """
    Display the ziffer selection dropdown.

    Args:
        ziffer_options (List[str]): List of available ziffer options.
        ziffer_index (Optional[int]): The index of the currently selected ziffer.

    Returns:
        Tuple[str, Optional[str]]: The selected ziffer and its description.
    """
    st.subheader("Ziffer")
    ziffer = st.selectbox(
        "Ziffer auswählen",
        options=ziffer_options,
        index=ziffer_index,
        placeholder="Bitte wählen Sie eine Ziffer aus ...",
    )

    if ziffer:
        beschreibung = "".join(ziffer.split(" - ")[1:])
        ziffer = ziffer.split(" - ")[0]
    else:
        beschreibung = None

    return ziffer, beschreibung


def display_haufigkeit_input(current_value: Optional[int]) -> int:
    """
    Display the häufigkeit input field.

    Args:
        current_value (Optional[int]): The current häufigkeit value.

    Returns:
        int: The selected häufigkeit value.
    """
    st.subheader("Häufigkeit")
    return st.number_input(
        "Häufigkeit setzen",
        value=current_value,
        placeholder="Bitte wählen Sie die Häufigkeit der Leistung ...",
        min_value=1,
        max_value=20,
    )


def display_intensitat_input(current_value: Optional[float]) -> float:
    """
    Display the intensität input field.

    Args:
        current_value (Optional[float]): The current intensität value.

    Returns:
        float: The selected intensität value.
    """
    st.subheader("Faktor")
    return st.number_input(
        "Faktor setzen",
        value=current_value,
        placeholder="Bitte wählen Sie die Intensität der Durchführung der Leistung ...",
        min_value=0.0,
        max_value=5.0,
        step=0.1,
        format="%.1f",
    )


def display_zitat_input(current_value: Optional[str]) -> str:
    """
    Display the zitat input field.

    Args:
        current_value (Optional[str]): The current zitat value.

    Returns:
        str: The entered zitat.
    """
    st.subheader("Textzitat")
    return st.text_area(
        "Textzitat einfügen",
        value=current_value,
        placeholder="Bitte hier das Textzitat einfügen ...",
        help="Hier soll ein Zitat aus dem ärztlichen Bericht eingefügt werden, welches die Leistungsziffer begründet.",
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
    begrundung = st.text_area(
        "Begründung eingeben",
        value=current_value,
        placeholder="Bitte hier die Begründung einfügen ...",
        help="Hier soll die Begründung für die Leistungsziffer eingefügt werden.",
    )
    return begrundung if begrundung else None


def create_new_data(
    ziffer: str,
    haufigkeit: int,
    intensitat: float,
    beschreibung: Optional[str],
    zitat: str,
    begrundung: Optional[str],
) -> Dict[str, Union[str, int, float, None]]:
    """
    Create a dictionary with the new ziffer data.

    Args:
        ziffer (str): The selected ziffer.
        haufigkeit (int): The selected häufigkeit.
        intensitat (float): The selected intensität.
        beschreibung (Optional[str]): The ziffer description.
        zitat (str): The entered zitat.
        begrundung (Optional[str]): The entered begründung.

    Returns:
        Dict[str, Union[str, int, float, None]]: The new ziffer data.
    """
    return {
        "Ziffer": ziffer,
        "Häufigkeit": haufigkeit,
        "Intensität": intensitat,
        "Beschreibung": beschreibung,
        "Zitat": zitat,
        "Begründung": begrundung,
    }


def display_buttons(new_data: Dict[str, Union[str, int, float, None]]) -> None:
    """
    Display the "Abbrechen" and "Aktualisieren" buttons.

    Args:
        new_data (Dict[str, Union[str, int, float, None]]): The new ziffer data.
    """
    left_outer_column, _, _, _, right_outer_column = st.columns([1, 2, 3, 2, 1])

    all_fields_filled = all(
        [
            new_data["Ziffer"],
            new_data["Häufigkeit"],
            new_data["Intensität"],
            new_data["Beschreibung"],
            new_data["Zitat"],
        ]
    )

    with left_outer_column:
        st.button(
            "Abbrechen",
            on_click=lambda: st.session_state.update(stage="result"),
            type="primary",
            use_container_width=True,
        )

    with right_outer_column:
        if all_fields_filled:
            if st.button(
                "Aktualisieren",
                on_click=lambda: update_ziffer(new_data),
                type="primary",
                use_container_width=True,
            ):
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
