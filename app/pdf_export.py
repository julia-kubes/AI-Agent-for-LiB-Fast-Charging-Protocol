"""PDF export for generated literature-assistant responses."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from collections.abc import Sequence
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
)

from .citations import answer_dois
from .presentation import format_parameter, format_transition, text_items
from .schemas import EvidenceChunk


def _font_names() -> tuple[str, str]:
    """Use a Unicode font when one is available, with portable fallbacks."""
    candidates = (
        (
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
    )
    for regular_path, bold_path in candidates:
        if regular_path.exists() and bold_path.exists():
            pdfmetrics.registerFont(TTFont("ResponseSans", regular_path))
            pdfmetrics.registerFont(TTFont("ResponseSans-Bold", bold_path))
            return "ResponseSans", "ResponseSans-Bold"
    return "Helvetica", "Helvetica-Bold"


def _paragraph_text(value: Any) -> str:
    text = str(value or "").strip()
    return escape(text).replace("\n", "<br/>")


def build_response_pdf(
    answer: dict[str, Any], evidence: Sequence[EvidenceChunk] = ()
) -> bytes:
    """Return a polished PDF representation of a generated answer."""
    regular_font, bold_font = _font_names()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ResponseTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=19,
        leading=23,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17324D"),
        spaceAfter=18,
    )
    heading_style = ParagraphStyle(
        "ResponseHeading",
        parent=styles["Heading2"],
        fontName=bold_font,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#176B87"),
        spaceBefore=11,
        spaceAfter=6,
    )
    subheading_style = ParagraphStyle(
        "ResponseSubheading",
        parent=styles["Heading3"],
        fontName=bold_font,
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#17324D"),
        spaceBefore=7,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ResponseBody",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#25313C"),
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "ResponseBullet",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-8,
        bulletIndent=3,
    )

    buffer = BytesIO()
    document = BaseDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.65 * inch,
        title="Fast-Charging Literature Assistant Response",
        author="Fast-Charging Literature Assistant",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="response",
    )

    def draw_page(canvas, doc) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D8E2EA"))
        canvas.line(0.7 * inch, 0.48 * inch, 7.8 * inch, 0.48 * inch)
        canvas.setFont(regular_font, 8)
        canvas.setFillColor(colors.HexColor("#667784"))
        canvas.drawString(0.7 * inch, 0.3 * inch, "Literature synthesis - verify experimentally")
        canvas.drawRightString(7.8 * inch, 0.3 * inch, f"Page {doc.page}")
        canvas.restoreState()

    document.addPageTemplates([PageTemplate(id="response", frames=[frame], onPage=draw_page)])

    story = [
        Paragraph("Fast-Charging Literature Assistant", title_style),
        Paragraph("Summary", heading_style),
        Paragraph(_paragraph_text(answer.get("summary")) or "No summary provided.", body_style),
        Paragraph("Protocol suggestions", heading_style),
    ]

    suggestions = answer.get("protocol_suggestions") or []
    if not suggestions:
        story.append(Paragraph("No protocol suggestions provided.", body_style))
    for index, suggestion in enumerate(suggestions, start=1):
        story.append(
            Paragraph(
                f"{index}. {_paragraph_text(suggestion.get('strategy') or 'Suggestion')}",
                subheading_style,
            )
        )
        story.append(Paragraph(_paragraph_text(suggestion.get("rationale")), body_style))
        target_conditions = suggestion.get("target_conditions") or {}
        target_text = "; ".join(
            f"{str(key).replace('_', ' ')}: {value}"
            for key, value in target_conditions.items()
            if value is not None and str(value).strip()
        )
        details = (
            ("Designation", suggestion.get("designation") or "unknown"),
            ("Protocol status", suggestion.get("protocol_status") or "unknown"),
            ("Origin", suggestion.get("reported_or_inferred") or "unknown"),
            ("Confidence", suggestion.get("confidence") or "unknown"),
            ("Target conditions", target_text or "Not provided"),
            (
                "Limitations",
                "; ".join(text_items(suggestion.get("limitations"), ["Not provided"])),
            ),
            ("DOI", ", ".join(answer_dois(suggestion, evidence))),
        )
        for label, value in details:
            story.append(
                Paragraph(
                    f'<font name="{bold_font}">{escape(label)}:</font> {_paragraph_text(value)}',
                    bullet_style,
                    bulletText="-",
                )
            )

        steps = suggestion.get("protocol_steps") or []
        if steps:
            story.append(Paragraph("Protocol steps", subheading_style))
        for step_index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            stage = (
                f"Stage {step.get('stage_number', step_index)}: "
                f"{step.get('stage_name', 'Stage')}"
            )
            story.append(Paragraph(_paragraph_text(stage), subheading_style))
            stage_details = (
                ("Mode", step.get("control_mode") or "Not provided"),
                ("Start", step.get("start_condition") or "Not provided"),
                ("Current", format_parameter(step.get("current"))),
                ("Voltage limit", format_parameter(step.get("voltage_limit"))),
                ("Temperature limit", format_parameter(step.get("temperature_limit"))),
                ("Transition", format_transition(step.get("transition"))),
                (
                    "Monitoring",
                    "; ".join(text_items(step.get("monitoring"), ["Not provided"])),
                ),
                (
                    "Stop conditions",
                    "; ".join(text_items(step.get("stop_conditions"), ["Not provided"])),
                ),
            )
            for label, value in stage_details:
                story.append(
                    Paragraph(
                        f'<font name="{bold_font}">{escape(label)}:</font> '
                        f"{_paragraph_text(value)}",
                        bullet_style,
                        bulletText="-",
                    )
                )

        extrapolation = suggestion.get("extrapolation") or {}
        if extrapolation.get("used"):
            story.append(Paragraph("Evidence transfer and reasoning", subheading_style))
            transfer_details = (
                ("Justification", extrapolation.get("justification") or "Not provided"),
                (
                    "Source conditions",
                    "; ".join(text_items(extrapolation.get("source_conditions"), ["Not provided"])),
                ),
                (
                    "Target conditions",
                    "; ".join(text_items(extrapolation.get("target_conditions"), ["Not provided"])),
                ),
                (
                    "Key differences",
                    "; ".join(text_items(extrapolation.get("key_differences"), ["Not provided"])),
                ),
            )
            for label, value in transfer_details:
                story.append(
                    Paragraph(
                        f'<font name="{bold_font}">{escape(label)}:</font> '
                        f"{_paragraph_text(value)}",
                        bullet_style,
                        bulletText="-",
                    )
                )

        validation_plan = text_items(suggestion.get("validation_plan"))
        if validation_plan:
            story.append(Paragraph("Validation plan", subheading_style))
            for item in validation_plan:
                story.append(
                    Paragraph(_paragraph_text(item), bullet_style, bulletText="-")
                )

    for heading, field in (
        ("Conflicting evidence", "conflicting_evidence"),
        ("Missing information", "missing_information"),
        ("Safety notes", "safety_notes"),
        ("Follow-up questions", "follow_up_questions"),
    ):
        story.append(Paragraph(heading, heading_style))
        values = text_items(answer.get(field))
        if not values:
            story.append(Paragraph("None provided.", body_style))
        for value in values:
            story.append(Paragraph(_paragraph_text(value), bullet_style, bulletText="-"))

    story.append(Spacer(1, 6))
    document.build(story)
    return buffer.getvalue()
