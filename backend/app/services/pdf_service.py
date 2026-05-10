"""Generate a PDF summary of the user's results using ReportLab."""

from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models import Recommendation
from app.schemas.schemas import AIAnalysis

# Try to register a Cyrillic-friendly TTF if present on the OS image (Debian/slim).
_CYRILLIC_FONT = "Helvetica"
for path in [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]:
    try:
        pdfmetrics.registerFont(TTFont("PDFCyrillic", path))
        _CYRILLIC_FONT = "PDFCyrillic"
        break
    except Exception:
        continue


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName=_CYRILLIC_FONT,
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#3730a3"),
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName=_CYRILLIC_FONT,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName=_CYRILLIC_FONT,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#111827"),
            spaceAfter=4,
        ),
        "muted": ParagraphStyle(
            "muted",
            parent=base["BodyText"],
            fontName=_CYRILLIC_FONT,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#6b7280"),
        ),
    }
    return styles


def render_results_pdf(
    *,
    user_name: str | None,
    raw_scores: dict,
    analysis: AIAnalysis,
    recommendations: list[Recommendation],
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Career Guidance KZ — результаты",
    )
    s = _styles()
    story = []

    story.append(Paragraph("Ваш психологический портрет", s["title"]))
    if user_name:
        story.append(Paragraph(f"Студент: <b>{user_name}</b>", s["muted"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("О вас", s["h2"]))
    story.append(Paragraph(analysis.personality_summary, s["body"]))

    story.append(Paragraph("Сильные стороны", s["h2"]))
    for st in analysis.strengths:
        story.append(Paragraph(f"• {st}", s["body"]))

    story.append(Paragraph("Зоны роста", s["h2"]))
    for g in analysis.growth_areas:
        story.append(Paragraph(f"• {g}", s["body"]))

    story.append(Paragraph("Идеальная среда работы", s["h2"]))
    story.append(Paragraph(analysis.ideal_work_environment, s["body"]))

    story.append(Paragraph("Советы по обучению", s["h2"]))
    story.append(Paragraph(analysis.study_tips, s["body"]))

    story.append(Paragraph("Мотивирующее напутствие", s["h2"]))
    story.append(Paragraph(analysis.motivational_message, s["body"]))

    story.append(Paragraph("Топ карьерных направлений", s["h2"]))
    for cp in analysis.career_paths[:6]:
        story.append(
            Paragraph(
                f"<b>{cp.title_ru}</b> — соответствие {int(round(cp.match_score))}%",
                s["body"],
            )
        )
        story.append(Paragraph(cp.why_match, s["muted"]))
        story.append(Spacer(1, 4))

    if recommendations:
        story.append(Paragraph("Рекомендованные специальности", s["h2"]))
        rows: list[list] = [
            [
                Paragraph("<b>Специальность</b>", s["body"]),
                Paragraph("<b>Университет, город</b>", s["body"]),
                Paragraph("<b>Match</b>", s["body"]),
            ]
        ]
        for r in recommendations[:12]:
            spec = r.specialization
            uni = spec.university
            rows.append(
                [
                    Paragraph(f"{spec.code} — {spec.name_ru}", s["body"]),
                    Paragraph(f"{uni.name_ru}, {uni.city}", s["body"]),
                    Paragraph(f"{int(round(r.match_score))}%", s["body"]),
                ]
            )
        table = Table(rows, colWidths=[7 * cm, 6.5 * cm, 2 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2ff")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, -1), _CYRILLIC_FONT),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(table)

    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "Сгенерировано Career Guidance KZ. Этот отчёт носит рекомендательный характер.",
            s["muted"],
        )
    )

    doc.build(story)
    return buf.getvalue()
