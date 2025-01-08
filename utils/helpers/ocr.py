from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import List, Optional, Union

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from pytesseract import Output
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.logger import logger


def perform_ocr_on_file(
    file_data: Union[bytes, Image.Image, UploadedFile], return_coordinates: bool = False
) -> Union[str, dict]:
    """
    Perform OCR on a complete PDF or image file.

    Args:
        file_data: Either raw bytes, a PIL Image, or an UploadedFile containing the document
        return_coordinates: If True, returns dict with text and word coordinates

    Returns:
        Union[str, dict]: Either the extracted text or a dict with text and word_map
    """
    logger.info(f"Starting OCR on complete file of type: {type(file_data)}")

    if isinstance(file_data, Image.Image):
        return (
            perform_ocr_with_coordinates(file_data)
            if return_coordinates
            else pytesseract.image_to_string(file_data, lang="deu")
        )

    if isinstance(file_data, bytes):
        # Try to detect if it's a PDF by checking magic numbers
        if file_data.startswith(b"%PDF"):
            return _process_complete_pdf_bytes(file_data)
        else:
            # Assume it's an image if not PDF
            image = Image.open(BytesIO(file_data))
            return (
                perform_ocr_with_coordinates(image)
                if return_coordinates
                else pytesseract.image_to_string(image, lang="deu")
            )

    if isinstance(file_data, UploadedFile):
        if file_data.type == "application/pdf":
            return _process_complete_pdf_bytes(file_data.read())
        elif file_data.type.startswith("image"):
            image = Image.open(file_data)
            return (
                perform_ocr_with_coordinates(image)
                if return_coordinates
                else pytesseract.image_to_string(image, lang="deu")
            )
        else:
            raise ValueError(f"Unsupported file type: {file_data.type}")

    raise ValueError(f"Unsupported input type: {type(file_data)}")


def _process_complete_pdf_bytes(pdf_bytes: bytes) -> str:
    """Process a complete PDF from bytes."""
    logger.info("Processing complete PDF from bytes")
    pages = convert_from_bytes(pdf_bytes)

    results = []
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(pytesseract.image_to_string, page, lang="deu"): i
            for i, page in enumerate(pages)
        }

        for future in as_completed(futures):
            try:
                text = future.result()
                if text.strip():
                    results.append(text)
            except Exception as e:
                logger.error(f"Error processing page: {str(e)}")

    return "\n".join(results)


def _process_complete_image_bytes(image_bytes: bytes) -> str:
    """Process a complete image from bytes."""
    logger.info("Processing complete image from bytes")
    image = Image.open(BytesIO(image_bytes))
    return pytesseract.image_to_string(image, lang="deu")


def perform_ocr_on_file_with_selection(
    uploaded_file: Union[Image.Image, UploadedFile],
    selections: Optional[List[List[dict]]] = None,
) -> str:
    """
    Perform OCR on specific selections of a PDF or image file.

    Args:
        uploaded_file (Union[Image.Image, UploadedFile]): The file to perform OCR on.
        selections (Optional[List[List[dict]]]): List of pages, where each page contains a list of
            selection dictionaries. Each selection contains normalized coordinates
            ('left', 'top', 'width', 'height') ranging from 0.0 to 1.0.

    Returns:
        str: The extracted text from the file, with text from each selection separated by newlines.

    Raises:
        ValueError: If the file type is not supported.
    """
    logger.info(f"Starting OCR on file of type: {type(uploaded_file)}")

    if isinstance(uploaded_file, Image.Image):
        return perform_ocr_on_image(
            uploaded_file, selections[0] if selections else None
        )

    if not hasattr(uploaded_file, "type"):
        raise ValueError("Unsupported file type")

    if uploaded_file.type == "application/pdf":
        return _process_pdf(uploaded_file, selections)
    elif uploaded_file.type.startswith("image"):
        return _process_image(uploaded_file, selections)
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.type}")


def _process_pdf(pdf_file: UploadedFile, selections: Optional[List[List[dict]]]) -> str:
    """
    Process a PDF file for OCR.

    Args:
        pdf_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The PDF file to process.
        selections (Optional[List[List[dict]]]): List of pages, where each page contains a list of
            selection dictionaries with normalized coordinates.

    Returns:
        str: The extracted text from the PDF, with text from each selection and page
            separated by newlines.
    """
    logger.info("Processing PDF file")
    pdf_file.seek(0)
    pages = convert_from_bytes(pdf_file.read())

    total_pages = len(pages)  # Get the total number of pages
    results = [""] * total_pages  # Initialize results with the total number of pages

    with ThreadPoolExecutor() as executor:
        futures = {
            # Only process pages if selections for that page are present
            executor.submit(
                perform_ocr_on_image,
                page,
                selections[i]
                if selections and len(selections) > i and selections[i]
                else None,
            ): i
            for i, page in enumerate(pages)
            if selections and len(selections) > i and selections[i]
        }

        for future in as_completed(futures):
            page_index = futures[future]  # Get the page index for this future
            try:
                results[
                    page_index
                ] = future.result()  # Assign result to the correct page index
            except Exception as e:
                logger.error(f"Error processing page {page_index}: {str(e)}")
                results[page_index] = ""  # Leave the page blank in case of an error

    # Concatenate only non-empty results
    return "\n".join(filter(None, results))


def _process_image(
    image_file: UploadedFile, selections: Optional[List[List[dict]]]
) -> str:
    """
    Process an image file for OCR.

    Args:
        image_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The image file to process.
        selections (Optional[List[List[dict]]]): List of pages (single page for images), where each page
            contains a list of selection dictionaries with normalized coordinates.

    Returns:
        str: The extracted text from the image selections, separated by newlines.
    """
    logger.info("Processing image file")
    image = Image.open(image_file)

    # Only perform OCR if selections are provided
    if selections and selections[0]:
        return perform_ocr_on_image(image, selections[0])
    return ""  # Skip if no selections


def perform_ocr_on_image(image: Image.Image, selections: Optional[List[dict]]) -> str:
    """
    Perform OCR on an image, limiting it to the selected regions if provided.

    Args:
        image (Image.Image): The image to perform OCR on.
        selections (Optional[List[dict]]): List of selections for a single page, where each selection
            is a dictionary containing normalized coordinates ('left', 'top', 'width', 'height')
            ranging from 0.0 to 1.0.

    Returns:
        str: The extracted text from the image selections, separated by newlines.
    """
    logger.info(f"Performing OCR on image of size: {image.size}")

    if not selections:
        # Skip OCR if no selections
        return ""

    results = []
    for selection in selections:
        try:
            result = process_selection(image, selection)
            if result.strip():  # Only add non-empty results
                results.append(result)
        except Exception as e:
            logger.error(f"Error processing selection: {str(e)}")

    return "\n".join(results)


def process_selection(image: Image.Image, selection: dict) -> str:
    """
    Process a single selection for OCR.

    Args:
        image (Image.Image): The image to process.
        selection (dict): A single selection dictionary containing normalized coordinates:
            - left (float): Left position (0.0 to 1.0)
            - top (float): Top position (0.0 to 1.0)
            - width (float): Width (0.0 to 1.0)
            - height (float): Height (0.0 to 1.0)

    Returns:
        str: The extracted text from the selection.

    Raises:
        ValueError: If the selection coordinates are invalid or out of bounds.
    """
    original_width, original_height = image.size
    left = int(selection["left"] * original_width)
    top = int(selection["top"] * original_height)
    width = int(selection["width"] * original_width)
    height = int(selection["height"] * original_height)

    # Ensure the selection is within the image bounds
    left = max(0, min(left, original_width))
    top = max(0, min(top, original_height))
    right = max(0, min(left + width, original_width))
    bottom = max(0, min(top + height, original_height))

    if left >= right or top >= bottom:
        raise ValueError("Invalid selection coordinates")

    cropped_image = image.crop((left, top, right, bottom))
    return pytesseract.image_to_string(cropped_image, lang="deu")


def perform_ocr_with_coordinates(image: Image.Image) -> dict:
    """
    Perform OCR on an image and return both text and word coordinates.

    Args:
        image (Image.Image): The image to process

    Returns:
        dict: Contains 'text' and 'word_map' with coordinates
    """
    # Get detailed OCR data including coordinates
    ocr_data = pytesseract.image_to_data(image, lang="deu", output_type=Output.DICT)

    # Build word map
    word_map = []
    n_boxes = len(ocr_data["text"])

    for i in range(n_boxes):
        # Skip empty results
        if not ocr_data["text"][i].strip():
            continue

        # Get confidence and coordinates
        conf = int(ocr_data["conf"][i])
        if conf < 0:  # Skip low confidence or invalid results
            continue

        (x, y, w, h) = (
            ocr_data["left"][i],
            ocr_data["top"][i],
            ocr_data["width"][i],
            ocr_data["height"][i],
        )

        word_map.append(
            {
                "text": ocr_data["text"][i],
                "bbox": [x, y, x + w, y + h],
                "page": ocr_data["page_num"][i],
                "confidence": conf / 100.0,
                "block_num": ocr_data["block_num"][i],
                "par_num": ocr_data["par_num"][i],
                "line_num": ocr_data["line_num"][i],
                "word_num": ocr_data["word_num"][i],
            }
        )

    # Combine text
    full_text = " ".join(word["text"] for word in word_map)

    return {"text": full_text, "word_map": word_map}
