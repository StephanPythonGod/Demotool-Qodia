from concurrent.futures import ThreadPoolExecutor, as_completed

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image


def perform_ocr_on_file(uploaded_file, selections=None):
    """
    Perform OCR on a PDF or image file, applying OCR to the selected areas if provided.
    """
    extracted_text = ""
    uploaded_file.seek(0)

    if isinstance(uploaded_file, Image.Image):
        extracted_text = perform_ocr_on_image(
            uploaded_file, selections[0] if selections else None
        )
    elif uploaded_file.type == "application/pdf":
        pages = convert_from_bytes(uploaded_file.read())

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    perform_ocr_on_image,
                    page,
                    selections[i] if selections and len(selections) > i else None,
                ): i
                for i, page in enumerate(pages)
            }

            # Collect results in order of page index
            results = [None] * len(pages)
            for future in as_completed(futures):
                page_index = futures[future]
                results[page_index] = future.result()

        extracted_text = "\n".join(filter(None, results))  # Filter out empty results
    elif uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        extracted_text = perform_ocr_on_image(
            image, selections[0] if selections else None
        )

    return extracted_text


def perform_ocr_on_image(image, selections):
    """
    Perform OCR on an image, limiting it to the selected regions if provided.
    """
    print(f"Performing OCR on image of size: {image.size}")

    if not selections:
        result = pytesseract.image_to_string(image, lang="deu")
        return result

    results = []
    for selection in selections:
        try:
            result = process_selection(image, selection)
            if result.strip():  # Only add non-empty results
                results.append(result)
        except Exception as e:
            print(f"Error processing selection: {e}")

    combined_result = "\n".join(results)
    return combined_result


def process_selection(image, selection):
    """
    Process a single selection for OCR.
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
        print("Invalid selection coordinates, skipping.")
        return ""

    cropped_image = image.crop((left, top, right, bottom))
    result = pytesseract.image_to_string(cropped_image, lang="deu")
    return result


def convert_selections_to_image_space(selections, original_width, original_height):
    """
    Convert the canvas selection box coordinates to the original image's pixel coordinates.
    """
    converted = [
        {
            "left": selection["left"],
            "top": selection["top"],
            "width": selection["width"],
            "height": selection["height"],
        }
        for selection in selections
    ]
    return converted
