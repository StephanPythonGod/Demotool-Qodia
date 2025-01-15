import concurrent.futures
import os
from typing import Optional

import fitz
import streamlit as st

from utils.helpers.anonymization import anonymize_text_german
from utils.helpers.api import analyze_api_call, ocr_pdf_to_text_api
from utils.helpers.distribution_store import DistributionStatus, get_distribution_store
from utils.helpers.document_store import DocumentStatus, get_document_store
from utils.helpers.logger import logger
from utils.helpers.ocr import perform_ocr_on_file
from utils.utils import get_temp_dir, redact_text_in_pdf


@st.cache_resource(ttl=3600)
def get_thread_pool():
    """Get or create a ThreadPoolExecutor instance."""
    if "thread_pool" not in st.session_state:
        st.session_state.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="doc_processor"
        )
    return st.session_state.thread_pool


def process_document(
    document_id: str,
    file_data: bytes,
    file_type: str,
    category: str,
    api_key: str,
    api_url: str,
    arzt_hash: Optional[str] = None,
    kassenname_hash: Optional[str] = None,
) -> None:
    """
    Process a document in the background.

    Args:
        document_id: The ID of the document (filename)
        file_data: The binary content of the file
        file_type: The MIME type of the file
        category: The category to analyze against
        api_key: The API key for authentication
        api_url: The base URL for the API
        arzt_hash: Optional hash value for the doctor
        kassenname_hash: Optional hash value for the insurance provider
    """
    document_store = get_document_store(api_key)

    try:
        # Update status to PROCESSING
        document_store.update_status(document_id, DocumentStatus.PROCESSING)

        # Perform OCR on the complete document
        if os.getenv("DEPLOYMENT_ENV") == "local":
            # Get OCR results with coordinates
            ocr_result = perform_ocr_on_file(file_data, return_coordinates=True)
            text = ocr_result["text"]

            # Store OCR data with coordinates
            document_store.store_ocr_data(document_id, ocr_result)

            # First run anonymization
            anonymization_result = anonymize_text_german(
                text, use_spacy=False, use_flair=True
            )
            text = anonymization_result["anonymized_text"]

            # Create redacted version of PDF using anonymization results
            pdf_path = document_store.get_document_path(document_id)
            temp_dir = get_temp_dir()
            redacted_pdf_path = redact_text_in_pdf(
                pdf_path=pdf_path,
                word_map=ocr_result["word_map"],
                detected_entities=anonymization_result["detected_entities"],
                temp_dir=temp_dir,
            )

            # Store path to redacted PDF
            document_store.store_redacted_pdf_path(document_id, redacted_pdf_path)

            # Read the redacted PDF for sending to API
            with open(redacted_pdf_path, "rb") as f:
                redacted_pdf_data = f.read()

            # Send redacted PDF to API for analysis
            result = analyze_api_call(
                category=category,
                api_key=api_key,
                api_url=api_url,
                arzt_hash=arzt_hash,
                kassenname_hash=kassenname_hash,
                file=redacted_pdf_data,
                process_type="ocr_and_predict",
                ocr_processor="smart",
            )

        else:
            # For API mode, we still need text coordinates
            # First get text from API
            text = ocr_pdf_to_text_api(
                file=file_data,
                category=category,
                api_key=api_key,
                api_url=api_url,
                filename=document_id,
            )

            # Then get coordinates locally
            ocr_result = perform_ocr_on_file(file_data, return_coordinates=True)
            document_store.store_ocr_data(document_id, ocr_result)

            # Analyze text
            result = analyze_api_call(
                text=text,
                category=category,
                api_key=api_key,
                api_url=api_url,
                arzt_hash=arzt_hash,
                kassenname_hash=kassenname_hash,
            )

        if not result:
            raise Exception("API analysis failed")

        # Store response headers along with results
        response_headers = getattr(analyze_api_call, "last_response_headers", None)
        if not response_headers:
            raise Exception("API response headers not available")

        # Update status to COMPLETED with results and headers
        document_store.update_status(
            document_id,
            DocumentStatus.COMPLETED,
            result=result,
            api_headers=response_headers,
        )

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
        document_store.update_status(
            document_id, DocumentStatus.FAILED, error_message=str(e)
        )


def queue_document(
    document_id: str,
    file_data: bytes,
    file_type: str,
    category: str,
    api_key: str,
    api_url: str,
    arzt_hash: Optional[str] = None,
    kassenname_hash: Optional[str] = None,
) -> None:
    """Queue a document for processing."""
    thread_pool = get_thread_pool()
    document_store = get_document_store(api_key)

    # Check if document is already being processed
    doc = document_store.get_document(document_id)
    if doc and doc["status"] in [
        DocumentStatus.QUEUED.value,
        DocumentStatus.PROCESSING.value,
    ]:
        logger.info(f"Document {document_id} is already being processed, skipping")
        return

    # Validate required parameters
    if not all([category, api_key, api_url]):
        error_msg = "Missing required parameters. Please check settings."
        logger.error(error_msg)
        document_store.update_status(
            document_id, DocumentStatus.FAILED, error_message=error_msg
        )
        return

    try:
        # Store the original document file
        document_store.store_document_file(document_id, file_data, file_type)

        # Add document to store
        document_store.add_document(document_id)

        # Queue processing with all required parameters
        future = thread_pool.submit(
            process_document,
            document_id,
            file_data,
            file_type,
            category,
            api_key,
            api_url,
            arzt_hash,
            kassenname_hash,
        )

        # Add callback to remove future from session state when done
        future.add_done_callback(
            lambda f: st.session_state.futures.remove(f)
            if hasattr(st.session_state, "futures")
            else None
        )

        # Store future in session state to prevent garbage collection
        if "futures" not in st.session_state:
            st.session_state.futures = set()
        st.session_state.futures.add(future)

    except Exception as e:
        logger.error(f"Error queueing document {document_id}: {e}", exc_info=True)
        document_store.update_status(
            document_id, DocumentStatus.FAILED, error_message=str(e)
        )
        raise


def process_distribution_document(document_id: str, selected_pages: list[int]) -> None:
    """Process selected pages of a distribution document in the background."""
    thread_pool = get_thread_pool()
    distribution_store = get_distribution_store()

    try:
        # Update status to PROCESSING
        distribution_store.update_status(document_id, DistributionStatus.PROCESSING)

        # Create new PDF with selected pages
        doc_path = distribution_store.get_document_path(document_id)
        doc = fitz.open(doc_path)
        new_doc = fitz.open()

        for page_num in selected_pages:
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # Convert to bytes for OCR
        pdf_bytes = new_doc.write()
        doc.close()
        new_doc.close()

        # Submit to thread pool
        future = thread_pool.submit(
            _process_distribution_document_background, document_id, pdf_bytes
        )

        # Add callback
        future.add_done_callback(
            lambda f: st.session_state.futures.remove(f)
            if hasattr(st.session_state, "futures")
            else None
        )

        # Store future in session state
        if "futures" not in st.session_state:
            st.session_state.futures = set()
        st.session_state.futures.add(future)

    except Exception as e:
        logger.error(
            f"Error queueing distribution document {document_id}: {e}", exc_info=True
        )
        distribution_store.update_status(
            document_id, DistributionStatus.FAILED, error_message=str(e)
        )
        raise


def _process_distribution_document_background(
    document_id: str, pdf_bytes: bytes
) -> None:
    """Background processing of distribution document."""
    distribution_store = get_distribution_store()

    try:
        # Perform OCR with coordinates
        ocr_result = perform_ocr_on_file(pdf_bytes, return_coordinates=True)
        text = ocr_result["text"]

        if not text:
            raise Exception("OCR failed to extract text from document")

        # Anonymize text
        anonymization_result = anonymize_text_german(
            text, use_spacy=False, use_flair=True
        )

        # Store original PDF path
        pdf_path = distribution_store.get_document_path(document_id)

        # Create redacted version of PDF
        temp_dir = get_temp_dir()
        redacted_pdf_path = redact_text_in_pdf(
            pdf_path=pdf_path,
            word_map=ocr_result["word_map"],
            detected_entities=anonymization_result["detected_entities"],
            temp_dir=temp_dir,
        )

        # Store path to redacted PDF
        distribution_store.store_redacted_pdf_path(document_id, redacted_pdf_path)

        # Update status to COMPLETED
        distribution_store.update_status(
            document_id,
            DistributionStatus.COMPLETED,
            processed_text=anonymization_result[
                "anonymized_text"
            ],  # Keep this for backwards compatibility
        )

    except Exception as e:
        logger.error(
            f"Error processing distribution document {document_id}: {e}", exc_info=True
        )
        distribution_store.update_status(
            document_id, DistributionStatus.FAILED, error_message=str(e)
        )
