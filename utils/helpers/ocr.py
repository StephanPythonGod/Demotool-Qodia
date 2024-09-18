from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Union

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

from utils.helpers.logger import logger


def perform_ocr_on_file(
    uploaded_file: Union[Image.Image, UploadedFile],
    selections: Optional[List[dict]] = None,
) -> str:
    """
    Perform OCR on a PDF or image file, applying OCR to the selected areas if provided.

    Args:
        uploaded_file (Union[Image.Image, streamlit.runtime.uploaded_file_manager.UploadedFile]): The file to perform OCR on.
        selections (Optional[List[dict]]): List of selection areas to apply OCR to.

    Returns:
        str: The extracted text from the file.

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


def _process_pdf(pdf_file: UploadedFile, selections: Optional[List[dict]]) -> str:
    """
    Process a PDF file for OCR.

    Args:
        pdf_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The PDF file to process.
        selections (Optional[List[dict]]): List of selection areas to apply OCR to.

    Returns:
        str: The extracted text from the PDF.
    """
    logger.info("Processing PDF file")
    pdf_file.seek(0)
    pages = convert_from_bytes(pdf_file.read())

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                perform_ocr_on_image,
                page,
                selections[i] if selections and len(selections) > i else None,
            ): i
            for i, page in enumerate(pages)
        }

        results = [None] * len(pages)
        for future in as_completed(futures):
            page_index = futures[future]
            try:
                results[page_index] = future.result()
            except Exception as e:
                logger.error(f"Error processing page {page_index}: {str(e)}")
                results[page_index] = ""

    return "\n".join(filter(None, results))


def _process_image(image_file: UploadedFile, selections: Optional[List[dict]]) -> str:
    """
    Process an image file for OCR.

    Args:
        image_file (streamlit.runtime.uploaded_file_manager.UploadedFile): The image file to process.
        selections (Optional[List[dict]]): List of selection areas to apply OCR to.

    Returns:
        str: The extracted text from the image.
    """
    logger.info("Processing image file")
    image = Image.open(image_file)
    return perform_ocr_on_image(image, selections[0] if selections else None)


def perform_ocr_on_image(image: Image.Image, selections: Optional[List[dict]]) -> str:
    """
    Perform OCR on an image, limiting it to the selected regions if provided.

    Args:
        image (Image.Image): The image to perform OCR on.
        selections (Optional[List[dict]]): List of selection areas to apply OCR to.

    Returns:
        str: The extracted text from the image.
    """
    logger.info(f"Performing OCR on image of size: {image.size}")

    if not selections:
        return pytesseract.image_to_string(image, lang="deu")

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
        selection (dict): The selection area to process.

    Returns:
        str: The extracted text from the selection.

    Raises:
        ValueError: If the selection coordinates are invalid.
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


def convert_selections_to_image_space(
    selections: List[dict], original_width: int, original_height: int
) -> List[dict]:
    """
    Convert the canvas selection box coordinates to the original image's pixel coordinates.

    Args:
        selections (List[dict]): List of selection areas.
        original_width (int): The original image width.
        original_height (int): The original image height.

    Returns:
        List[dict]: List of converted selection areas.
    """
    return [
        {
            "left": selection["left"] * original_width,
            "top": selection["top"] * original_height,
            "width": selection["width"] * original_width,
            "height": selection["height"] * original_height,
        }
        for selection in selections
    ]
