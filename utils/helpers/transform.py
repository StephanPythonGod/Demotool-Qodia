import locale
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from utils.helpers.db import read_in_goa
from utils.helpers.logger import logger
from utils.utils import find_zitat_in_text

locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")  # German locale for formatting


def annotate_text_update() -> None:
    """
    Update the annotated text object in the Streamlit session state.
    This function finds and highlights medical billing codes in the text.
    """
    st.session_state.annotated_text_object = [st.session_state.text]

    zitate_to_find: List[Tuple[str, str]] = [
        (row["zitat"], row["ziffer"]) for _, row in st.session_state.df.iterrows()
    ]

    st.session_state.annotated_text_object = find_zitat_in_text(
        zitate_to_find, st.session_state.annotated_text_object
    )

    # Update st.session_state.df to be in the order as the labels are in the annotated_text_object
    ziffer_order = [
        i[1] for i in st.session_state.annotated_text_object if isinstance(i, tuple)
    ]
    ziffer_order = list(dict.fromkeys(ziffer_order))

    # Order the dataframe according to the order of the ziffer in the text
    ziffer_order_dict = {ziffer: order for order, ziffer in enumerate(ziffer_order)}
    st.session_state.df["order"] = st.session_state.df["ziffer"].map(ziffer_order_dict)
    st.session_state.df["order"].fillna(9999, inplace=True)
    st.session_state.df.sort_values("order", inplace=True)
    st.session_state.df.drop("order", axis=1, inplace=True)
    st.session_state.df.reset_index(drop=True, inplace=True)


def df_to_processdocumentresponse(df: pd.DataFrame, ocr_text: str) -> Dict[str, Any]:
    """
    Transform a DataFrame and OCR text into a ProcessDocumentResponse-compatible dictionary.

    Args:
        df (pd.DataFrame): DataFrame containing the prediction results.
        ocr_text (str): The OCR text to be included in the response.

    Returns:
        Dict[str, Any]: A dictionary compatible with the ProcessDocumentResponse schema.
    """
    # Transform DataFrame rows into ResultObjekt-compatible dictionaries
    result_objekts = []
    for _, row in df.iterrows():
        result_objekt = {
            "zitat": row["zitat"],
            "begruendung": row["begruendung"],
            "goa_ziffer": row["ziffer"],
            "quantitaet": int(row["anzahl"]),
            "faktor": float(row["faktor"]),
            "beschreibung": row["text"],
            "confidence": float(row["confidence"]),
        }
        result_objekts.append(result_objekt)

    # Create the OCRResponse
    ocr_response = {"ocr_text": ocr_text}

    # Create the PredictionResponse
    prediction_response = {"ocr": ocr_response, "prediction": result_objekts}

    # Create the final ProcessDocumentResponse
    process_document_response = {"result": prediction_response}

    return process_document_response


def format_ziffer_to_4digits(ziffer: str) -> str:
    """
    Format a billing code (ziffer) to a 4-digit format.

    Args:
        ziffer (str): The billing code to format.

    Returns:
        str: The formatted billing code.
    """
    ziffer_parts = ziffer.split(" ", 1)[1]
    numeric_part = "".join(filter(str.isdigit, ziffer_parts))
    alpha_part = "".join(filter(lambda x: not x.isdigit(), ziffer_parts))

    try:
        result = f"{int(numeric_part):04d}{alpha_part}"
    except ValueError:
        result = ziffer_parts
    return result


def df_to_items(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert a DataFrame of billing codes to a list of item dictionaries.

    Args:
        df (pd.DataFrame): The DataFrame containing billing code information.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a billing item.
    """
    items = []
    goa = read_in_goa(fully=True)

    for _, row in df.iterrows():
        goa_item = goa[goa["GOÄZiffer"] == row["ziffer"]]
        analog_ziffer = False

        if goa_item.empty:
            goa_analog_ziffer = row["ziffer"].replace(" A", "")
            goa_item = goa[goa["GOÄZiffer"] == goa_analog_ziffer]
            if goa_item.empty:
                logger.error(
                    f"No matching GOÄZiffer for analog Ziffer {goa_analog_ziffer}"
                )
                continue
            analog_ziffer = True

        intensity = row["faktor"]
        intensity_str_period = f"{intensity:.1f}"
        intensity_str_comma = intensity_str_period.replace(".", ",")

        matching_columns = goa_item.columns[
            goa_item.apply(
                lambda col: col.astype(str).str.contains(
                    f"(?:{intensity_str_period}|{intensity_str_comma})"
                )
            ).any()
        ]

        if matching_columns.empty:
            matching_columns = ["Regelhöchstfaktor"]

        column_name = matching_columns[0]
        faktor = intensity

        preis = _calculate_price(goa_item, column_name, faktor)

        item = {
            "ziffer": row["ziffer"],
            "anzahl": row["anzahl"],
            "intensitat": intensity,
            "beschreibung": row["text"],
            "Punktzahl": goa_item["Punktzahl"].values[0],
            "preis": preis,
            "faktor": faktor,
            "total": preis * int(row["anzahl"]),
            "auslagen": "",
            "date": "",
            "analog_ziffer": analog_ziffer,
        }

        items.append(item)

    if items:
        if not items[0]["date"]:
            items[0]["date"] = "25.05.24"
    else:
        logger.error("No items were created.")

    return items


def _calculate_price(goa_item: pd.DataFrame, column_name: str, faktor: float) -> float:
    """
    Calculate the price based on the GOÄ item and factor.

    Args:
        goa_item (pd.DataFrame): The GOÄ item DataFrame.
        column_name (str): The name of the column to use for price calculation.
        faktor (float): The intensity factor.

    Returns:
        float: The calculated price.
    """
    if column_name == "Einfachfaktor":
        return float(goa_item["Einfachsatz"].values[0].replace(",", "."))
    elif column_name == "Regelhöchstfaktor":
        return float(goa_item["Regelhöchstsatz"].values[0].replace(",", "."))
    elif column_name == "Höchstfaktor":
        return float(goa_item["Höchstsatz"].values[0].replace(",", "."))
    elif faktor < 2:
        return float(goa_item["Einfachsatz"].values[0].replace(",", "."))
    elif faktor < 3:
        return float(goa_item["Regelhöchstsatz"].values[0].replace(",", "."))
    else:
        return float(goa_item["Höchstsatz"].values[0].replace(",", "."))


def format_euro(value):
    """
    Manually formats a float value as a Euro string in German format.
    Thousands are separated by dots and decimals by commas.

    Args:
        value (float): The value to be formatted.

    Returns:
        str: The formatted Euro value.
    """
    # Split the value into whole and decimal parts
    whole_part, decimal_part = f"{value:.2f}".split(".")

    # Add dot as thousands separator to the whole part
    whole_part_with_dots = "{:,}".format(int(whole_part)).replace(",", ".")

    # Combine the whole part with the decimal part (replacing '.' with ',')
    formatted_value = f"{whole_part_with_dots},{decimal_part}"

    # Return the formatted value with Euro symbol
    return f"{formatted_value} €"
