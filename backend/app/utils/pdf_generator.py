from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.paths import REPORT_DIR, UPLOAD_DIR


def _safe(value) -> str:
    return escape("Unavailable" if value is None or value == "" else str(value))


def _label(analysis) -> str:
    if getattr(analysis, "display_label", None):
        return analysis.display_label
    if str(analysis.prediction).lower() == "real":
        return "Likely Real"
    if str(analysis.prediction).lower() == "fake":
        return "Likely Manipulated"
    return "Inconclusive"


def generate_report(analysis, details=None):
    details = details or {}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_id = f"DS-{analysis.id:06d}"
    generated = datetime.utcnow()
    destination = REPORT_DIR / f"analysis_{analysis.id}.pdf"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="DSCover", parent=styles["Title"], fontSize=25, leading=31, textColor=colors.HexColor("#0891B2"), alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle(name="DSHeading", parent=styles["Heading2"], fontSize=15, leading=19, textColor=colors.HexColor("#0E7490"), spaceBefore=12, spaceAfter=8))
    styles.add(ParagraphStyle(name="DSBody", parent=styles["BodyText"], fontSize=9.5, leading=14))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(18 * mm, 10 * mm, f"DeepSight System - {report_id}")
        canvas.drawRightString(192 * mm, 10 * mm, f"Page {doc.page} - {generated:%Y-%m-%d %H:%M UTC}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(destination), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=22*mm, title=f"DeepSight report {report_id}", author="DeepSight System")
    story = [Spacer(1, 20*mm), Paragraph("DeepSight System", styles["DSCover"]), Paragraph("Deepfake Detection Analysis Report", styles["Title"]), Spacer(1, 8*mm)]
    story += [_table([["Report ID", report_id], ["Analysis ID", analysis.id], ["Generated", f"{generated:%Y-%m-%d %H:%M UTC}"], ["Analysis type", analysis.file_type], ["Analysis source", analysis.source or "legacy"]], widths=[42*mm, 120*mm]), PageBreak()]
    story += [Paragraph("Executive Result", styles["DSHeading"]), _badge(_label(analysis)), Spacer(1, 4*mm), _table([["Overall result", _label(analysis)], ["Confidence", f"{analysis.confidence:.2f}%"], ["Selected / actual model", analysis.model_name], ["Model version", analysis.model_version], ["Processing duration", f"{analysis.processing_time:.3f} seconds"]])]
    story += [Paragraph("Input Information", styles["DSHeading"]), _table([["Original filename", analysis.filename], ["Format", analysis.file_extension], ["Dimensions", f"{analysis.image_width or 'Unavailable'} x {analysis.image_height or 'Unavailable'}"], ["Face count", analysis.face_count], ["Selected-face policy", "Largest valid detected face" if analysis.file_type.lower() == "image" else "Representative sampled face tracks"]])]

    media_path = Path(analysis.file_path)
    try:
        resolved = media_path.resolve()
        allowed = resolved.is_relative_to(UPLOAD_DIR.resolve())
    except (OSError, ValueError):
        allowed = False
    if allowed and resolved.is_file() and analysis.file_type.lower() == "image":
        try:
            story += [Spacer(1, 5*mm), Image(str(resolved), width=70*mm, height=52*mm, kind="proportional")]
        except Exception:
            pass

    warnings = analysis.quality_warnings or []
    story += [Paragraph("Detection Findings", styles["DSHeading"]), _table([["Binary prediction", analysis.prediction], ["Real probability", f"{(analysis.real_probability or 0):.2f}%"], ["Fake probability", f"{(analysis.fake_probability or 0):.2f}%"], ["Manipulation type", analysis.deepfake_type], ["Quality warnings", ", ".join(map(str, warnings)) if warnings else "None reported"]])]
    extension = details.get("extension")
    if extension:
        story += [Paragraph("Continuous Extension Session", styles["DSHeading"]), _table([["Page domain", extension.page_domain], ["Selected model", extension.selected_model_id], ["Actual model", extension.actual_model_id], ["Session duration", f"{((extension.completed_at or generated)-extension.started_at).total_seconds():.1f} seconds"], ["Frames received", extension.frames_received], ["Frames analysed", extension.frames_analysed], ["Frames skipped", extension.frames_skipped], ["Suspicious frames", extension.suspicious_frames]])]
    frames = details.get("frames") or details.get("extension_frames") or []
    if frames:
        rows = [["Timestamp", "Prediction", "Confidence", "Quality", "Suspicious"]]
        for frame in frames:
            if isinstance(frame, dict):
                timestamp, prediction, confidence, quality, fake = frame.get("timestampMs", 0), frame.get("prediction"), frame.get("confidence"), frame.get("quality", {}), frame.get("fakeProbability", 0)
            else:
                timestamp, prediction, confidence, quality, fake = frame.timestamp_ms, frame.prediction, frame.confidence, frame.quality_score, frame.fake_probability
            rows.append([f"{float(timestamp)/1000:.1f}s", prediction, f"{float(confidence or 0):.1f}%", quality, "Yes" if float(fake or 0) >= 55 else "No"])
        story += [Paragraph("Sampled Timeline", styles["DSHeading"]), _table(rows, repeat=True)]
    segments = details.get("segments") or []
    if segments:
        rows = [["Start", "End", "Confidence", "Result", "Frames"]] + [[f"{s.start_timestamp_ms/1000:.1f}s", f"{s.end_timestamp_ms/1000:.1f}s", f"{s.confidence:.1f}%", s.result, s.frame_count] for s in segments]
        story += [Paragraph("Suspicious Segments", styles["DSHeading"]), _table(rows, repeat=True)]
    story += [Paragraph("Model Information", styles["DSHeading"]), _table([["Model", analysis.model_name], ["Version", analysis.model_version], ["Task", "Binary deepfake detection"], ["Status", "Approved result model"], ["Threshold source", "Server model configuration"]]), Paragraph("Limitations", styles["DSHeading"]), Paragraph("This result is generated by an automated detection system and should be interpreted as decision support rather than absolute proof. Video and continuous-session conclusions may be based on sampled frames rather than every frame.", styles["DSBody"])]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return destination


def _table(rows, widths=None, repeat=False):
    style = getSampleStyleSheet()["BodyText"]
    normalized = [[Paragraph(_safe(cell), style) for cell in row] for row in rows]
    table = Table(normalized, colWidths=widths, repeatRows=1 if repeat else 0, hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E2E8F0") if repeat else colors.HexColor("#F1F5F9")), ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#0F172A")), ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"), ("PADDING", (0,0), (-1,-1), 6)]))
    return table


def _badge(text):
    table = Table([[Paragraph(f"<b>{_safe(text)}</b>", getSampleStyleSheet()["Heading2"])]], colWidths=[70*mm])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#CFFAFE")), ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#0891B2")), ("ALIGN", (0,0), (-1,-1), "CENTER"), ("PADDING", (0,0), (-1,-1), 10)]))
    return table
