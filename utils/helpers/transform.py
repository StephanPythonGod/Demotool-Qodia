from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st
from xsdata.models.datatype import XmlDateTime  # Import the XmlDateTime class

from schemas.padnext_v2_py.padx_basis_v2_12 import GozifferTyp, LeistungspositionTyp
from utils.helpers.db import read_in_goa
from utils.helpers.logger import logger
from utils.utils import find_zitat_in_text


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
    st.session_state.df["order"] = st.session_state.df["order"].fillna(9999)
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
            "ziffer": row["ziffer"],
            "anzahl": row["anzahl"],
            "faktor": row["faktor"],
            "text": row["text"],
            "gesamtbetrag": row["gesamtbetrag"],
            "einzelbetrag": row["einzelbetrag"],
            "go": row["go"],
            "analog": row["analog"],
            "confidence": row["confidence"],
            "confidence_reason": row["confidence_reason"],
        }
        result_objekts.append(result_objekt)

    # Create the OCRResponse
    ocr_response = {"ocr_text": ocr_text}

    # Create the PredictionResponse
    prediction_response = {"ocr": ocr_response, "prediction": result_objekts}

    # Create the final ProcessDocumentResponse
    # process_document_response = {"result": prediction_response}

    return prediction_response


def format_ziffer_to_4digits(ziffer: str) -> str:
    """
    Format a billing code (ziffer) to a 4-digit format, preserving alphabetic characters and spaces.

    Args:
        ziffer (str): The billing code to format.

    Returns:
        str: The formatted billing code.
    """

    # Remove the initial 'z ' if it exists
    ziffer_parts = ziffer.split(" ", 1)[1] if ziffer.startswith("z ") else ziffer

    # Split numeric and alphabetic parts while preserving spaces
    numeric_part = ""
    alpha_part = ""
    space_between = ""

    # Traverse through ziffer_parts and separate numeric and alphabetic parts
    for i, char in enumerate(ziffer_parts):
        if char.isdigit():
            numeric_part += char
        elif char.isalpha():
            alpha_part = ziffer_parts[i:]
            break
        elif char == " " and not numeric_part:  # If space before numeric part
            continue
        elif char == " " and numeric_part:  # If space after numeric part
            space_between = " "
            alpha_part = ziffer_parts[i + 1 :]
            break

    # Format numeric part to be 4 digits
    if numeric_part:
        numeric_part = f"{int(numeric_part):04d}"

    # Return the formatted string, preserving the space between numeric and alpha part
    return f"{numeric_part}{space_between}{alpha_part}".strip()


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


def transform_df_to_goziffertyp(df: pd.DataFrame) -> List[GozifferTyp]:
    """
    Transforms a pandas DataFrame into a list of GozifferTyp objects.

    Each row of the DataFrame is converted into a GozifferTyp object, which represents
    a Leistungsposition nach jeweiliger Gebührenordnung. The function performs error handling
    to ensure that invalid rows are skipped and logs errors using the logger. A warning is
    also displayed in Streamlit for each invalid row.

    Args:
        df (pd.DataFrame): The input DataFrame containing GOZ data.

    Returns:
        List[GozifferTyp]: A list of successfully created GozifferTyp objects.
    """
    today = date.today().strftime("%Y-%m-%d")  # Format today's date as 'YYYY-MM-DD'
    goziffer_objects = []

    for idx, row in df.iterrows():
        try:
            # Extract mandatory fields
            positionsnr = idx  # The row index will be used as positionsnr
            go = row.get("go", None)
            ziffer = row.get("ziffer", None)
            anzahl = row.get("anzahl", None)
            text = row.get("text", None)
            gesamtbetrag = row.get("gesamtbetrag", None)
            faktor = row.get("faktor", None)
            einzelbetrag = row.get("einzelbetrag", None)

            # Check for missing mandatory fields
            missing_fields = [
                required_field
                for required_field in ["go", "ziffer", "anzahl", "text", "gesamtbetrag"]
                if row.get(required_field) is None
            ]
            if missing_fields:
                raise ValueError(
                    f"Missing mandatory fields in row {idx}: {', '.join(missing_fields)}"
                )

            # Ensure at least one of 'faktor' or 'einzelbetrag' is present
            if not (faktor or einzelbetrag):
                raise ValueError(
                    f"Missing both 'faktor' and 'einzelbetrag' in row {idx}"
                )

            # Convert 'gesamtbetrag' and 'einzelbetrag' to Decimal with two decimal places
            gesamtbetrag = Decimal(gesamtbetrag).quantize(
                Decimal("0.00"), rounding=ROUND_HALF_UP
            )

            if faktor:
                # 'faktor' should have one decimal place
                faktor = Decimal(faktor).quantize(
                    Decimal("0.0"), rounding=ROUND_HALF_UP
                )
                einzelbetrag = None
            elif einzelbetrag:
                # 'einzelbetrag' should have two decimal places
                einzelbetrag = Decimal(einzelbetrag).quantize(
                    Decimal("0.00"), rounding=ROUND_HALF_UP
                )

            # Create the GozifferTyp object
            goziffer_obj = GozifferTyp(
                faktor=faktor,
                einzelbetrag=einzelbetrag,
                gesamtbetrag=gesamtbetrag,
                beteiligung=[],  # Default to empty list
                anteil=None,  # Default as None
                begruendung=row.get("begruendung", None),
                mwstsatz=None,  # Set to None, could be populated if needed
                minderungssatz=None,  # Could be handled if provided
                ambo=None,  # Set to None as a placeholder
                punktwert=None,  # Set to None unless provided
                punktzahl=None,  # Set to None unless provided
                berechnung=None,  # Default to None
                go=go,  # Required field
                goversion=row.get("goversion", None),
                analog=row.get("analog", None),
                ziffer=ziffer,  # Required field
            )

            # Create the LeistungspositionTyp object, which is the parent class
            leistung_obj = LeistungspositionTyp(
                leistungserbringerid=row.get("leistungserbringerid", None),
                datum=today,  # Use today's date in the required format
                uhrzeit=None,  # Set to None unless time data is provided
                anzahl=int(anzahl),  # Convert 'anzahl' to integer
                text=text,  # Required field
                zusatztext=row.get("zusatztext", None),
                positionsnr=positionsnr,  # Use row index as positionsnr
                id=row.get("id", None),  # Optional unique identifier
                idref=row.get("idref", None),  # Optional reference to other positions
            )

            # Assign the LeistungspositionTyp fields to the GozifferTyp object
            goziffer_obj.datum = leistung_obj.datum
            goziffer_obj.anzahl = leistung_obj.anzahl
            goziffer_obj.text = leistung_obj.text
            goziffer_obj.positionsnr = leistung_obj.positionsnr

            # Append the valid GozifferTyp object
            goziffer_objects.append(goziffer_obj)

        except Exception as e:
            # Log the error using the provided logger and display a warning in Streamlit
            error_message = f"Error processing row {idx}: {str(e)}"
            logger.error(error_message)
            st.warning(f"Error in row {idx}: {str(e)}")
            continue

    return goziffer_objects


def format_erstellungsdatum(erstellungsdatum):
    """
    Converts the erstellungsdatum to the JJJJMMTT (YYYYMMDD) format.
    Handles both datetime objects and strings in ISO format.
    """
    try:
        # If erstellungsdatum is already a datetime object, format it
        if isinstance(erstellungsdatum, datetime):
            return erstellungsdatum.strftime("%Y%m%d")

        # If it's a string, attempt to parse it
        if isinstance(erstellungsdatum, str):
            # Try parsing the string in ISO 8601 format
            parsed_date = datetime.fromisoformat(erstellungsdatum)
            return parsed_date.strftime("%Y%m%d")

        # If erstellungsdatum is an instance of XmlDateTime, convert it to a Python datetime
        if isinstance(erstellungsdatum, XmlDateTime):
            # Convert XmlDateTime to a standard Python datetime object
            parsed_date = erstellungsdatum.to_datetime()
            return parsed_date.strftime("%Y%m%d")

        # If it's neither, raise an error (you could adjust to handle more formats if needed)
        raise ValueError(
            f"Unexpected type for erstellungsdatum: {type(erstellungsdatum)}"
        )

    except (ValueError, TypeError) as e:
        # Handle parsing or type errors
        logger.error(f"Error processing erstellungsdatum: {e}")
        # Optionally, you can return a default or error string in the file name if the date is invalid
        return "00000000"  # A fallback value, can be customized


def format_kundennummer(kundennummer):
    """
    Converts the kundennummer to a 8-digit format.
    The original kundennummer will be padded with zeros to the left.
    """

    # Convert the kundennummer to a string
    kundennummer_str = str(kundennummer)

    # Pad the kundennummer with zeros to the left
    kundennummer_padded = kundennummer_str.zfill(8)

    return kundennummer_padded


def format_transfernummer(transfernummer):
    """
    Converts the transfernummer to a 6-digit format.
    The original transfernummer will be padded with zeros to the left.
    """

    # Convert the transfernummer to a string
    transfernummer_str = str(transfernummer)

    # Pad the transfernummer with zeros to the left
    transfernummer_padded = transfernummer_str.zfill(6)

    return transfernummer_padded


def split_recognized_and_potential(df):
    recognized_df = df[df["confidence"] >= 0.9]
    potential_df = df[df["confidence"] < 0.9]
    return recognized_df, potential_df


def concatenate_labels(zitat):
    concatenated_text = []

    # Loop through all high-level keys in zitat
    for key, value in zitat.items():
        # Loop through all items in the list associated with the key
        for obj in value:
            # Extract the 'label' field
            concatenated_text.append(obj["label"].strip())

    # Join all the labels with " [...] " between them
    return " [...] ".join(concatenated_text)
