from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
)

from reportlab.lib.styles import getSampleStyleSheet


REPORT_DIR = Path("reports")

REPORT_DIR.mkdir(exist_ok=True)


def generate_report(analysis):

    filename = f"analysis_{analysis.id}.pdf"

    pdf_path = REPORT_DIR / filename

    styles = getSampleStyleSheet()

    pdf = SimpleDocTemplate(str(pdf_path))

    story = []

    story.append(
        Paragraph(
            "<b>ML7-VIDS DeepSight Report</b>",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            f"Analysis ID : {analysis.id}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Prediction : {analysis.prediction}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Confidence : {analysis.confidence:.2f} %",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Risk : {analysis.risk_level}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Model : {analysis.model_version}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Processing Time : {analysis.processing_time:.4f} sec",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Filename : {analysis.filename}",
            styles["Normal"],
        )
    )

    pdf.build(story)

    return pdf_path