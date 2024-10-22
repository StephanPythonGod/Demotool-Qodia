from typing import Optional

import pandas as pd
import streamlit as st

from utils.helpers.logger import logger


@st.cache_data
def read_in_goa(
    path: str = "./data/GOA_Ziffern.csv", fully: bool = False
) -> pd.DataFrame:
    """
    Read and process the GOA (Gebührenordnung für Ärzte) data from a CSV file.

    This function reads a CSV file containing GOA data, processes it based on the 'fully' parameter,
    and returns a pandas DataFrame with the results.

    Args:
        path (str): The file path to the GOA CSV file. Defaults to "./data/GOA_Ziffern.csv".
        fully (bool): If True, return the full DataFrame. If False, process and return a subset.
                      Defaults to False.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the processed GOA data.

    Raises:
        FileNotFoundError: If the specified file is not found.
        pd.errors.EmptyDataError: If the CSV file is empty.
    """
    logger.info(f"Reading GOA data from {path}")

    try:
        # Read in the csv file with pandas
        goa = pd.read_csv(path, sep=";", encoding="utf-8", encoding_errors="replace")
    except FileNotFoundError:
        logger.error(f"GOA file not found at {path}")
        raise
    except pd.errors.EmptyDataError:
        logger.error(f"GOA file at {path} is empty")
        raise

    if fully:
        logger.info("Returning full GOA DataFrame")
        return goa

    logger.info("Processing GOA data")
    # Use only the columns "GOÄZiffer" and "Beschreibung"
    goa = goa[
        [
            "GOÄZiffer",
            "Beschreibung",
            "Einfachfaktor",
            "Einfachsatz",
            "Regelhöchstfaktor",
            "Regelhöchstsatz",
            "Höchstfaktor",
            "Höchstsatz",
            "go",
            "ziffer",
            "analog",
        ]
    ]

    # Drop rows with NaN values
    # goa = goa.dropna()

    # Cast type of "Einfachfaktor", "Einachsatz", "Regelhöchstfaktor", "Regelhöchstsatz", "Höchstfaktor", "Höchstsatz" to float
    # Replace "-" with None
    goa["Einfachfaktor"] = goa["Einfachfaktor"].replace("-", None)
    goa["Einfachfaktor"] = goa["Einfachfaktor"].str.replace(",", ".").astype(float)
    goa["Einfachsatz"] = goa["Einfachsatz"].replace("-", None)
    goa["Einfachsatz"] = goa["Einfachsatz"].str.replace(",", ".").astype(float)
    goa["Regelhöchstfaktor"] = goa["Regelhöchstfaktor"].replace("-", None)
    goa["Regelhöchstfaktor"] = (
        goa["Regelhöchstfaktor"].str.replace(",", ".").astype(float)
    )
    goa["Regelhöchstsatz"] = goa["Regelhöchstsatz"].replace("-", None)
    goa["Regelhöchstsatz"] = goa["Regelhöchstsatz"].str.replace(",", ".").astype(float)
    goa["Höchstfaktor"] = goa["Höchstfaktor"].replace("-", None)
    goa["Höchstfaktor"] = goa["Höchstfaktor"].str.replace(",", ".").astype(float)
    goa["Höchstsatz"] = goa["Höchstsatz"].replace("-", None)
    goa["Höchstsatz"] = goa["Höchstsatz"].str.replace(",", ".").astype(float)

    # For every row in the DataFrame add a new row with the same values but the GOÄZiffer with an " A" at the end
    # Replace the Beschreibung with the text "Analogziffer zu " + original GO'Ziffer
    goa_analog = goa.copy()
    # Filter out all rows, where "analog" is empty
    goa_analog = goa_analog[goa_analog["analog"].isnull()]
    goa_analog["Beschreibung"] = "Analogziffer zu " + goa_analog["GOÄZiffer"]
    goa_analog["analog"] = goa_analog["GOÄZiffer"]
    goa_analog["GOÄZiffer"] = goa_analog["GOÄZiffer"] + " A"
    goa_analog["ziffer"] = goa_analog["GOÄZiffer"]
    goa_analog["go"] = goa_analog["go"]

    # Concatenate the original DataFrame with the analog DataFrame
    goa = pd.concat([goa, goa_analog])

    # Combine the two columns into a single string using " - " as separator
    goa["Ziffern"] = goa["GOÄZiffer"] + " - " + goa["Beschreibung"]

    logger.info("GOA data processing completed")
    return goa


def get_goa_description(goa_number: str, goa_df: Optional[pd.DataFrame] = None) -> str:
    """
    Retrieve the description for a given GOA number.

    This function looks up the description for a specified GOA number in the provided DataFrame
    or in a newly loaded DataFrame if none is provided.

    Args:
        goa_number (str): The GOA number to look up.
        goa_df (Optional[pd.DataFrame]): A pre-loaded GOA DataFrame. If None, the function will
                                         load the data using read_in_goa(). Defaults to None.

    Returns:
        str: The description corresponding to the given GOA number, or an error message if not found.

    Raises:
        ValueError: If the provided goa_number is not a valid string.
    """
    if not isinstance(goa_number, str):
        logger.error(f"Invalid GOA number type: {type(goa_number)}")
        raise ValueError("GOA number must be a string")

    if goa_df is None:
        logger.info("Loading GOA data")
        goa_df = read_in_goa()

    logger.info(f"Looking up description for GOA number: {goa_number}")
    matching_row = goa_df[goa_df["GOÄZiffer"] == goa_number]

    if matching_row.empty:
        logger.warning(f"No description found for GOA number: {goa_number}")
        return f"No description found for GOA number: {goa_number}"

    description = matching_row.iloc[0]["Beschreibung"]
    logger.info(f"Description found for GOA number {goa_number}")
    return description
