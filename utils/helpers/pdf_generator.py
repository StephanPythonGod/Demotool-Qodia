import io
import uuid

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate


def text_to_pdf(text: str) -> tuple[str, bytes]:
    """
    Convert text input to PDF bytes with automatic text wrapping.

    Args:
        text: The input text to convert

    Returns:
        tuple[str, bytes]: Document ID and PDF bytes
    """
    # Generate unique document ID
    doc_id = f"text_{uuid.uuid4()}.pdf"

    # Create PDF buffer
    buffer = io.BytesIO()

    # Create document template with margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    # Create paragraph style
    style = ParagraphStyle(
        "Normal",
        fontName="Helvetica",
        fontSize=12,
        leading=20,  # Line height
        alignment=TA_LEFT,
        hyphenation=True,  # Enable hyphenation
    )

    # Convert text to paragraph with proper wrapping
    story = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para, style)
            story.append(p)

    # Build PDF
    doc.build(story)

    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # For debugging purposes, save the PDF to the local directory
    with open(f"{doc_id}", "wb") as f:
        f.write(pdf_bytes)

    return doc_id, pdf_bytes
