import io
import uuid

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def text_to_pdf(text: str) -> tuple[str, bytes]:
    """
    Convert text input to PDF bytes.

    Args:
        text: The input text to convert

    Returns:
        tuple[str, bytes]: Document ID and PDF bytes
    """
    # Generate unique document ID
    doc_id = f"text_{uuid.uuid4()}.pdf"

    # Create PDF in memory
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Set up text parameters
    text_object = c.beginText()
    text_object.setTextOrigin(50, A4[1] - 50)  # Start 50 points from top and left
    text_object.setFont("Helvetica", 12)

    # Split text into lines and add them to PDF
    y_position = A4[1] - 50  # Start from top
    for line in text.split("\n"):
        if not line.strip():  # Handle empty lines
            y_position -= 20  # Add some space for empty lines
            continue

        text_object.setTextOrigin(50, y_position)
        text_object.textLine(line)
        y_position -= 20  # Line spacing

        # Check if we need a new page
        if y_position < 50:  # Bottom margin
            c.drawText(text_object)
            c.showPage()
            y_position = A4[1] - 50
            text_object = c.beginText()
            text_object.setFont("Helvetica", 12)

    c.drawText(text_object)
    c.save()

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return doc_id, pdf_bytes
