from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("generated")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_certificate(
    name: str,
    event_name: str,
    event_date: str,
    certificate_id: str
) -> str:

    filename = f"certificate_{certificate_id}.pdf"

    output_path = OUTPUT_DIR / filename

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=A4
    )

    width, height = A4

    # Border
    pdf.setLineWidth(3)
    pdf.rect(
        40,
        40,
        width - 80,
        height - 80
    )

    # Title
    pdf.setFont(
        "Helvetica-Bold",
        28
    )

    pdf.drawCentredString(
        width / 2,
        height - 150,
        "CERTIFICATE OF PARTICIPATION"
    )

    # Subtitle
    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        width / 2,
        height - 210,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawCentredString(
        width / 2,
        height - 270,
        name
    )

    # Event information
    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawCentredString(
        width / 2,
        height - 330,
        f"For participating in {event_name}"
    )

    pdf.drawCentredString(
        width / 2,
        height - 360,
        f"Date: {event_date}"
    )

    # Signature
    pdf.line(
        width / 2 - 70,
        130,
        width / 2 + 70,
        130
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawCentredString(
        width / 2,
        110,
        "Authorized Signature"
    )

    pdf.save()

    return str(output_path)