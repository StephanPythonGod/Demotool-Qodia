import http.client
import json
import os
import pickle
import time
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional, Union

import pandas as pd
import requests
import streamlit as st
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.document_store import get_document_store
from utils.helpers.logger import logger
from utils.helpers.transform import df_to_items, format_ziffer_to_4digits

DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "local")
USE_CACHE = os.getenv("USE_CACHE", "true").lower() == "true"


def check_if_default_credentials() -> None:
    """
    Check if the default API key is being used and display a warning if so.
    """
    if st.session_state.api_key == "AIzaSyDQAAPcTJECYfwwFV9QDm9HeHAME99PbQo":
        st.warning(
            (
                "Bitte ändern Sie die Standard-API-Schlüssel-Einstellungen, um die Anwendung zu testen. "
                "Dieser Testlauf wird noch funktionieren, aber bitte fügen Sie Ihren Organisations-API-Schlüssel ein, "
                "um die Anwendung zu verwenden. Details hierzu finden Sie in der Dokumentation."
            ),
            icon="⚠️",
        )


def get_workflows() -> List[str]:
    """
    Retrieve the list of available workflows from the API for the user.

    Returns:
        List[str]: The list of available workflows.
    """
    logger.info("Retrieving available workflows...")
    url = f"{st.session_state.api_url}/workflows"
    headers = {"x-api-key": st.session_state.api_key}

    try:
        response = requests.get(url, headers=headers)
        logger.info(
            f"Done retrieving workflows. Response status: {response.status_code}"
        )
    except Exception as e:
        logger.error(f"Error retrieving workflows: {e}", exc_info=True)
        st.error(
            "Ein Fehler ist beim Abrufen der verfügbaren Workflows aufgetreten. "
            "Bitte überprüfen Sie die URL und den API Key und speichern Sie die Einstellungen erneut.\n\n"
            f"Fehlerdetails: {e}"
        )
        return []

    if response.status_code != 200:
        logger.error(
            (
                f"API error: Status Code: {response.status_code}, "
                f"Message: {response.text}, "
                f"Request ID: {response.headers.get('X-Request-ID', '')}"
            ),
            exc_info=True,
        )
        st.error(
            "Ein Fehler ist beim Abrufen der verfügbaren Workflows aufgetreten.\n\n"
            "API-Fehler:\n"
            f"Status Code: {response.status_code}\n"
            f"Nachricht: {response.text}\n"
            f"Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): "
            f"{response.headers.get('X-Request-ID', '')}"
        )
        return []

    return response.json()["workflows"]


def analyze_api_call(
    text: str,
    category: str,
    api_key: str,
    api_url: str,
    arzt_hash: Optional[str] = None,
    kassenname_hash: Optional[str] = None,
) -> Optional[Dict]:
    """
    Analyze the given text using the API and return the prediction.

    Args:
        text (str): The text to be analyzed
        category (str): The category to analyze against
        api_key (str): The API key for authentication
        api_url (str): The base URL for the API
        arzt_hash (Optional[str]): Hash value for the doctor
        kassenname_hash (Optional[str]): Hash value for the insurance provider

    Returns:
        Optional[Dict]: The prediction result or None if an error occurred
    """
    logger.info("Analyzing text...")

    if not category:
        logger.error("No category selected")
        raise ValueError(
            "No category selected. Please select a category before analyzing text."
        )

    data_folder = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_folder, exist_ok=True)
    safe_filename = os.path.join(data_folder, f"{hash(text[100:120])}_response.pkl")

    if USE_CACHE and os.path.exists(safe_filename):
        logger.info(f"Using cached response from {safe_filename}")
        try:
            with open(safe_filename, "rb") as file:
                cached_response = pickle.load(file)
            response = cached_response["response"]
            st.session_state.analyze_api_response = response
            return cached_response["prediction"]
        except Exception as e:
            logger.error(f"Error loading cached response: {e}", exc_info=True)

    url = f"{api_url}/process_document"
    payload = {
        "text": text,
        "category": category,
        "process_type": "predict",
    }

    if arzt_hash is not None:
        payload["arzt"] = arzt_hash

    if kassenname_hash is not None:
        payload["kassenname"] = kassenname_hash

    headers = {"x-api-key": api_key}

    try:
        response = requests.post(url, headers=headers, data=payload)
        # Store headers for later use
        analyze_api_call.last_response_headers = dict(response.headers)
        logger.info(f"Done analyzing text. Response status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error calling API for text analysis: {e}", exc_info=True)
        raise

    if response.status_code != 200:
        request_id = response.headers.get("X-Request-ID", "nicht-vorhanden")
        error_msg = f"API error: Status Code: {response.status_code}, Message: {response.text}, Request ID: {request_id}"
        logger.error(error_msg)
        raise Exception(error_msg)

    st.session_state.analyze_api_response = response

    try:
        prediction = response.json()["result"]["prediction"]
    except KeyError:
        try:
            prediction = response.json()["prediction"]
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}", exc_info=True)
            raise

    if USE_CACHE:
        cached_response = {"response": response, "prediction": prediction}
        try:
            with open(safe_filename, "wb") as file:
                pickle.dump(cached_response, file)
            logger.info(f"Response saved to {safe_filename}")
        except Exception as e:
            logger.error(f"Error saving response to file: {e}", exc_info=True)

    return prediction


def ocr_pdf_to_text_api(
    file: Union[Image.Image, UploadedFile, bytes],
    category: str,
    api_key: str,
    api_url: str,
    filename: Optional[str] = None,
) -> Optional[str]:
    """
    Perform OCR on the given file using the API.

    Args:
        file: The file to be processed (Image, UploadedFile, or bytes)
        category: The category to process against
        api_key: The API key for authentication
        api_url: The base URL for the API
        filename: Optional filename when passing raw bytes

    Returns:
        Optional[str]: The extracted text or None if an error occurred
    """
    logger.info("Performing OCR on the document...")

    if not category:
        logger.error("No category selected")
        raise ValueError(
            "No category selected. Please select a category before analyzing text."
        )

    # Get the filename for caching
    cache_filename = filename
    if isinstance(file, UploadedFile):
        cache_filename = file.name
    elif isinstance(file, Image.Image):
        cache_filename = "clipboard_image.png"

    if not cache_filename:
        cache_filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    data_folder = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_folder, exist_ok=True)
    safe_filename = os.path.join(
        data_folder, f"{hash(cache_filename + category)}_ocr_response.pkl"
    )

    if USE_CACHE and os.path.exists(safe_filename):
        logger.info(f"Using cached OCR response from {safe_filename}")
        try:
            with open(safe_filename, "rb") as file:
                cached_response = pickle.load(file)
            return cached_response["ocr_text"]
        except Exception as e:
            logger.error(f"Error loading cached OCR response: {e}", exc_info=True)

    url = f"{api_url}/process_document"
    payload = {
        "ocr_processor": "google_document_ai",
        "process_type": "ocr",
        "category": category,
    }
    headers = {"x-api-key": api_key}

    # Handle different input types
    if isinstance(file, Image.Image):
        file_bytes = BytesIO()
        file.save(file_bytes, format="PNG")
        file_bytes = file_bytes.getvalue()
        file_name = "clipboard_image.png"
        mime_type = "image/png"
    elif isinstance(file, UploadedFile):
        file.seek(0)
        file_bytes = file.read()
        file_name = file.name
        mime_type = file.type or "application/octet-stream"
    else:  # bytes
        file_bytes = file
        file_name = filename or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        mime_type = "application/octet-stream"

    files = {"file": (file_name, file_bytes, mime_type)}

    try:
        response = requests.post(url, headers=headers, data=payload, files=files)
    except Exception as e:
        logger.error(f"Error calling API for OCR: {e}", exc_info=True)
        raise

    logger.info(
        f"Done performing OCR on the document. Response status: {response.status_code}"
    )
    if response.status_code != 200:
        request_id = response.headers.get("X-Request-ID", "nicht-vorhanden")
        error_msg = f"API error: Status Code: {response.status_code}, Message: {response.text}, Request ID: {request_id}"
        logger.error(error_msg)
        raise Exception(error_msg)

    st.session_state.ocr_api_response = response

    try:
        ocr_text = response.json()["result"]["ocr"]["ocr_text"]
    except KeyError:
        try:
            ocr_text = response.json()["ocr"]["ocr_text"]
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}", exc_info=True)
            raise

    if USE_CACHE:
        cached_response = {"ocr_text": ocr_text}
        try:
            with open(safe_filename, "wb") as file:
                pickle.dump(cached_response, file)
            logger.info(f"OCR response saved to {safe_filename}")
        except Exception as e:
            logger.error(f"Error saving OCR response to file: {e}", exc_info=True)

    return ocr_text


def send_feedback_api(response_object: Dict) -> None:
    """
    Send feedback to the API for the given response object.
    Args:
        response_object (Dict): The response object from the API.
    """
    document_store = get_document_store()
    document_id = st.session_state.selected_document_id

    # Get document from store
    document = document_store.get_document(document_id)
    if not document:
        raise Exception(f"Document {document_id} not found")

    # Get API headers
    api_headers = document.get("api_headers")
    if not api_headers:
        raise Exception(f"API headers not found for document {document_id}")

    try:
        api_headers = json.loads(api_headers)
    except json.JSONDecodeError:
        raise Exception(f"Invalid API headers format for document {document_id}")

    api_request_id = api_headers.get("x-request-id")
    if not api_request_id:
        raise Exception(
            f"Request ID not found in API headers for document {document_id}"
        )

    url = f"{st.session_state.api_url}/feedback/{api_request_id}"
    payload = json.dumps(response_object, indent=4)
    headers = {
        "x-api-key": st.session_state.api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        logger.info(f"Feedback sent. Response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"API Feedback error: {response.text}")
            raise Exception(f"API Feedback error: {response.text}")
    except Exception as e:
        logger.error(f"Error sending feedback: {e}", exc_info=True)
        raise


def generate_pdf_from_df(df: Optional[pd.DataFrame] = None) -> str:
    """
    Generate a PDF file from the given DataFrame, taking into account any applicable discount.

    Args:
        df (Optional[pd.DataFrame]): The DataFrame containing the data for the PDF.

    Returns:
        str: The path to the generated PDF file.
    """
    data = {
        "customer_name": "Max Mustermann",
        "customer_street": "Musterstraße",
        "customer_street_number": "123",
        "customer_city": "Musterstadt",
        "customer_country": "Deutschland",
        "date_today": time.strftime("%d.%m.%Y"),
        "date_bill": time.strftime("%d.%m.%Y"),
        "diagnosis": (
            "Große subxiphoidale Narbenhernie mit Einklemmung"
            "von präperitonealem Fettgewebe und Omentum majus"
            "bei Z.n. Sternotomie und aortokoronarer Bypassopertaion"
            "und Bio-Aortenklappenimplantation. Kleine primäre epigastrische"
            "Bauchwandhernie im mitteleren Epigastrium. KHK, Z. n. "
            "Implantation von 10 Koronarstents. Z. n. Myokardinfarkt 1998."
        ),
    }

    # Prepare items and calculate the total price
    items = df_to_items(df)
    data["items"] = items
    data["total"] = sum(item["total"] for item in data["items"])

    # Handling discount logic based on user selection
    discount_option = st.session_state["minderung_data"]["prozentsatz"]
    begruendung = st.session_state["minderung_data"]["begruendung"]

    if discount_option and discount_option != "keine":
        discount_percentage = float(discount_option.replace("%", ""))
        data["discount"] = data["total"] * (discount_percentage / 100)
        data["final_price"] = data["total"] - data["discount"]
        data["discount_reason"] = begruendung  # Include reason for discount
    else:
        data["discount"] = None  # No discount applied
        data["final_price"] = data["total"]
        data["discount_reason"] = None  # No discount reason

    # Format items' values for currency display
    for item in data["items"]:
        for key, value in item.items():
            if isinstance(value, (int, float)):
                if key in ["preis", "total"]:
                    item[key] = f"{value:.2f} €".replace(".", ",")
                else:
                    item[key] = str(value)
        item["ziffer"] = format_ziffer_to_4digits(item["ziffer"])
        if int(item["anzahl"]) > 1:
            item["ziffer"] = f"{item['anzahl']}x {item['ziffer']}"

    # Format total, discount, and final price
    data["total"] = f"{data['total']:.2f} €".replace(".", ",")
    if data["discount"] is not None:
        data["discount"] = f"{data['discount']:.2f} €".replace(".", ",")
    data["final_price"] = f"{data['final_price']:.2f} €".replace(".", ",")

    # Render the HTML content using the template
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("./data/template_rechnung.html")
    html_content = template.render(data)

    # Save HTML to file
    with open("./data/rechnung_generiert.html", "w") as file:
        file.write(html_content)

    # Generate PDF via API
    pdf_file = "./data/rechnung_generiert.pdf"
    conn = http.client.HTTPSConnection("yakpdf.p.rapidapi.com")

    payload = {
        "pdf": {
            "format": "A4",
            "printBackground": True,
            "scale": 1,
            "margin": {"top": "0cm", "right": "0cm", "bottom": "0cm", "left": "0cm"},
        },
        "source": {"html": html_content},
        "wait": {"for": "navigation", "timeout": 250, "waitUntil": "load"},
    }

    api_key = os.getenv("RAPID_API_KEY")

    if api_key is None:
        logger.error("API key for PDF generation not found.")
        st.error("Fehler bei der PDF Generierung. API-Schlüssel nicht gefunden.")
        return

    headers = {
        "content-type": "application/json",
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "yakpdf.p.rapidapi.com",
    }

    conn.request("POST", "/pdf", json.dumps(payload).encode("utf-8"), headers)
    res = conn.getresponse()
    data = res.read()

    with open(pdf_file, "wb") as file:
        file.write(data)

    return pdf_file


def generate_pdf(df: pd.DataFrame) -> bytes:
    """
    Generate a PDF file from the given DataFrame and return it as bytes.

    Args:
        df (pd.DataFrame): The DataFrame containing the data for the PDF.

    Returns:
        bytes: The generated PDF file as bytes.
    """
    pdf_file_path = generate_pdf_from_df(df)
    with open(pdf_file_path, "rb") as file:
        pdf_data = file.read()
    return pdf_data


def test_api() -> bool:
    """
    Test if the settings for the API are correct.

    Returns:
        bool: True if the API settings are correct, False otherwise.
    """
    url = f"{st.session_state.api_url}"
    headers = {"x-api-key": st.session_state.api_key}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            logger.error("API authentication failed: Incorrect API key")
            st.error(
                "Der API-Key ist nicht korrekt. Bitte überprüfen Sie den API-Key und speichern Sie die Einstellungen erneut."
            )
            return False
        elif response.status_code not in (200, 201):
            logger.error(
                (
                    f"Unexpected API error: Status Code: {response.status_code}, "
                    f"Message: {response.text}, "
                    f"Request ID: {response.headers.get('X-Request-ID', 'nicht-vorhanden')}"
                )
            )
            st.error(
                "Ein unerwarteter Fehler ist beim Aufrufen der API aufgetreten. "
                "Überprüfen Sie die API-Einstellungen und speichern Sie die Einstellungen erneut.\n\n"
                "Fehlerdetails:\n"
                f"Status Code: {response.status_code}\n"
                f"Nachricht: {response.text}\n"
                f"Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): "
                f"{response.headers.get('X-Request-ID', 'nicht-vorhanden')}"
            )
            return False
    except Exception as e:
        logger.error(f"Error connecting to API: {e}", exc_info=True)
        st.error(
            "Ein Fehler ist beim Aufrufen der API aufgetreten. "
            "Bitte überprüfen Sie die URL und den API-Key und speichern Sie die Einstellungen erneut.\n\n"
            f"Fehlerdetails:\n{e}"
        )
        return False

    logger.info("API settings are correct. URL and API key are working.")
    return True
