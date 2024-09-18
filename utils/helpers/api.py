import http.client
import json
import time
from io import BytesIO
from typing import Dict, Optional, Union

import pandas as pd
import requests
import streamlit as st
from jinja2 import Environment, FileSystemLoader
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.logger import logger
from utils.helpers.transform import df_to_items, format_ziffer_to_4digits


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


def analyze_api_call(text: str) -> Optional[Dict]:
    """
    Analyze the given text using the API and return the prediction.

    Args:
        text (str): The text to be analyzed.

    Returns:
        Optional[Dict]: The prediction result or None if an error occurred.
    """
    logger.info("Analyzing text... : ", text)

    url = f"{st.session_state.api_url}/process_document"
    payload = {
        "text": text,
        "category": st.session_state.category,
        "process_type": "predict",
    }
    headers = {"x-api-key": st.session_state.api_key}

    try:
        response = requests.post(url, headers=headers, data=payload)
        logger.info(f"Done analyzing text. Response status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error calling API for text analysis: {e}")
        st.error(
            f"Ein Fehler ist aufgetreten beim Aufrufen der API für die Analyse des Textes. "
            f"Bitte überprüfen Sie die URL und den API Key und speichern Sie die Einstellungen erneut.\n\n"
            f"Fehlerdetails: {e}"
        )
        return None

    if response.status_code != 200:
        request_id = response.headers.get("X-Request-ID", "nicht-vorhanden")
        logger.error(
            f"API error: Status Code: {response.status_code}, Message: {response.text}, Request ID: {request_id}"
        )
        st.error(
            f"Ein Fehler ist aufgetreten beim Aufrufen der API für die Analyse des Textes.\n\n"
            f"API-Fehler:\n"
            f"Status Code: {response.status_code}\n"
            f"Nachricht: {response.text}\n"
            f"Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): {request_id}"
        )
        return None

    return response.json()["prediction"]


def ocr_pdf_to_text_api(file: Union[Image.Image, UploadedFile]) -> Optional[str]:
    """
    Perform OCR on the given file using the API and return the extracted text.

    Args:
        file (Union[Image.Image, UploadedFile]): The file to be processed.

    Returns:
        Optional[str]: The extracted text or None if an error occurred.
    """
    logger.info("Performing OCR on the document...")
    url = f"{st.session_state.api_url}/process_document"
    payload = {
        "ocr_processor": "google_document_ai",
        "process_type": "ocr",
        "category": st.session_state.category,
    }
    headers = {"x-api-key": st.session_state.api_key}

    if isinstance(file, Image.Image):
        file_bytes = BytesIO()
        file.save(file_bytes, format="PNG")
        file_bytes = file_bytes.getvalue()
        file_name = "clipboard_image.png"
        mime_type = "image/png"
    else:  # UploadedFile
        file_bytes = file.read()
        file_name = file.name
        mime_type = file.type or "application/octet-stream"

    files = {"file": (file_name, file_bytes, mime_type)}

    try:
        response = requests.post(url, headers=headers, data=payload, files=files)
    except Exception as e:
        logger.error(f"Error calling API for OCR: {e}")
        st.error(
            f"Ein Fehler ist aufgetreten beim Aufrufen der API für OCR. "
            f"Bitte überprüfen Sie die URL und den API Key und speichern Sie die Einstellungen erneut.\n\n"
            f"Fehlerdetails: {e}"
        )
        return None

    logger.info(
        f"Done performing OCR on the document. Response status: {response.status_code}, {response.headers}"
    )
    if response.status_code != 200:
        logger.error(
            (
                f"API error: Status Code: {response.status_code}, "
                f"Message: {response.text}, "
                f"Request ID: {response.headers.get('X-Request-ID', '')}"
            )
        )
        st.error(
            f"Ein Fehler ist beim Aufrufen der API für OCR aufgetreten. "
            f"Überprüfen Sie die API-Einstellungen und speichern Sie die Einstellungen erneut.\n"
            f"API-Fehler:\n"
            f"Status Code: {response.status_code}\n"
            f"Nachricht: {response.text}\n"(
                f"Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): "
                f"{response.headers.get('X-Request-ID', '')}"
            )
        )
        return None

    return response.json()["ocr"]["ocr_text"]


def generate_pdf_from_df(df: Optional[pd.DataFrame] = None) -> str:
    """
    Generate a PDF file from the given DataFrame.

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

    items = df_to_items(df)
    data["items"] = items
    data["total"] = sum(item["total"] for item in data["items"])
    data["discount"] = data["total"] * 0.25
    data["final_price"] = data["total"] - data["discount"]

    for item in data["items"]:
        for key, value in item.items():
            if isinstance(value, (int, float)):
                if key in ["preis", "total", "discount", "final_price"]:
                    item[key] = f"{value:.2f} €".replace(".", ",")
                else:
                    item[key] = str(value)
        item["ziffer"] = format_ziffer_to_4digits(item["ziffer"])
        if int(item["Häufigkeit"]) > 1:
            item["ziffer"] = f"{item['Häufigkeit']}x {item['ziffer']}"

    data["total"] = f"{data['total']:.2f} €".replace(".", ",")
    data["discount"] = f"{data['discount']:.2f} €".replace(".", ",")
    data["final_price"] = f"{data['final_price']:.2f} €".replace(".", ",")

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("./data/template_rechnung.html")
    html_content = template.render(data)

    with open("./data/rechnung_generiert.html", "w") as file:
        file.write(html_content)

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

    headers = {
        "content-type": "application/json",
        "x-rapidapi-key": "18a7c1f0a3mshc09f133b9c99f34p1fab4cjsn3f4de4a18cfa",
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
                (
                    "Der API-Key ist nicht korrekt. Bitte überprüfen Sie den API-Key "
                    "und speichern Sie die Einstellungen erneut."
                )
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
                f"Ein unerwarteter Fehler ist beim Aufrufen der API aufgetreten. "
                f"Überprüfen Sie die API-Einstellungen und speichern Sie die Einstellungen erneut.\n\n"
                f"Fehlerdetails:\n"
                f"Status Code: {response.status_code}\n"
                f"Nachricht: {response.text}\n"(
                    f"Anfrage-ID (Kann von Qodia verwendet werden, um den Fehler zu finden): "
                    f"{response.headers.get('X-Request-ID', 'nicht-vorhanden')}"
                )
            )
            return False
    except Exception as e:
        logger.error(f"Error connecting to API: {e}")
        st.error(
            f"Ein Fehler ist beim Aufrufen der API aufgetreten. "
            f"Bitte überprüfen Sie die URL und den API-Key und speichern Sie die Einstellungen erneut.\n\n"
            f"Fehlerdetails: {e}"
        )
        return False

    logger.info("API settings are correct. URL and API key are working.")
    st.success(
        "Die API-Einstellungen sind korrekt. Die URL und der API-Key funktionieren."
    )
    return True
