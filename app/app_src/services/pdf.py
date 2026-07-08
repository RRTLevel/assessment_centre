"""ReportLab rendering for the candidate performance PDF export."""

import io
from xml.sax.saxutils import escape

from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Mirrors the .score.s1–s6 palette in candidate_dashboard.html
SCORE_COLOURS = {
    1: ("#d73027", "#ffffff"),
    2: ("#fc8d59", "#000000"),
    3: ("#fee08b", "#000000"),
    4: ("#d9ef8b", "#000000"),
    5: ("#91cf60", "#000000"),
    6: ("#1a9850", "#ffffff"),
}

NO_SCORE_COLOURS = ("#f5f5f5", "#999999")


def render_candidate_dashboard_pdf(questions, rows, date_from=None, date_to=None):
    """Render the dashboard heatmap plus one detail page per candidate.

    ``questions`` and ``rows`` come from
    :func:`app_src.services.dashboard.candidate_dashboard_data`.
    Returns the PDF as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        title="Candidate Performance",
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    elements = [Paragraph("Candidate Performance", styles["Title"])]

    if date_from or date_to:
        elements.append(Paragraph(
            f"Period: {escape(date_from or 'start')} to {escape(date_to or 'today')}",
            styles["Normal"],
        ))

    elements.append(Paragraph(
        timezone.localtime().strftime("Generated %d %b %Y %H:%M"),
        styles["Normal"],
    ))
    elements.append(Spacer(1, 12))

    if rows:
        elements.append(_heatmap_table(questions, rows))
    else:
        elements.append(Paragraph("No results yet.", styles["Normal"]))

    elements.extend(_question_key(questions, styles))

    for row in rows:
        if row["application"] is not None:
            elements.extend(_candidate_page(row, styles))

    doc.build(elements)
    return buffer.getvalue()


def _heatmap_table(questions, rows):
    """The summary table: one row per candidate, one coloured cell per score."""
    header = ["Candidate", "Application Date"]
    header += [f"Q{i}" for i in range(1, len(questions) + 1)]
    header.append("Average")

    data = [header]

    for row in rows:
        line = [
            row["name"],
            row["date"].strftime("%d %b %Y") if row["date"] else "—",
        ]
        line += ["—" if score is None else str(score) for score in row["cells"]]
        line.append("—" if row["avg"] is None else f"{row['avg']:.1f}")
        data.append(line)

    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#363636")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e5e5")),
        ("BACKGROUND", (-1, 1), (-1, -1), colors.HexColor("#f0f0f0")),
        ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
    ]

    for row_index, row in enumerate(rows, start=1):
        for column_index, score in enumerate(row["cells"], start=2):
            background, text = SCORE_COLOURS.get(score, NO_SCORE_COLOURS)
            cell = (column_index, row_index)
            table_style.append(("BACKGROUND", cell, cell, colors.HexColor(background)))
            table_style.append(("TEXTCOLOR", cell, cell, colors.HexColor(text)))

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle(table_style))
    return table


def _question_key(questions, styles):
    """A key mapping the Q1..Qn column headers to their full question text."""
    if not questions:
        return []

    elements = [Spacer(1, 16), Paragraph("Questions", styles["Heading3"])]

    for index, question in enumerate(questions, start=1):
        elements.append(Paragraph(
            f"Q{index}: {escape(question.text)}",
            styles["Normal"],
        ))

    return elements


def _candidate_page(row, styles):
    """One detail page per candidate: their pre-interview answers, then each
    interview question they answered with the score, notes and feedback."""
    application = row["application"]

    elements = [
        PageBreak(),
        Paragraph(escape(row["name"]), styles["Heading1"]),
    ]

    summary = f"Applied {row['date'].strftime('%d %b %Y')}"
    if row["avg"] is not None:
        summary += f" — Average score: {row['avg']:.1f}"
    elements.append(Paragraph(summary, styles["Normal"]))

    pack = application.pack
    pre_interview = [
        (pack.pre_interview_question_1, application.answer_1),
        (pack.pre_interview_question_2, application.answer_2),
        (pack.pre_interview_question_3, application.answer_3),
    ]
    pre_interview = [(question, answer) for question, answer in pre_interview if question and answer]

    if pre_interview:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph("Pre-Interview Answers", styles["Heading3"]))

        for question_text, answer in pre_interview:
            elements.append(KeepTogether([
                Paragraph(f"<b>{escape(question_text)}</b>", styles["Normal"]),
                Paragraph(escape(answer), styles["Normal"]),
                Spacer(1, 6),
            ]))

    answered = [
        result for result in application.results.all()
        if result.score is not None or result.notes or result.feedback
    ]

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Interview Questions", styles["Heading3"]))

    if not answered:
        elements.append(Paragraph("No interview answers recorded.", styles["Normal"]))

    for result in answered:
        elements.append(_result_block(result, styles))

    return elements


def _result_block(result, styles):
    """A single question's heading, score badge, notes and feedback."""
    heading = f"<b>{escape(result.question.text)}</b>"
    if result.score is not None:
        background, text = SCORE_COLOURS.get(result.score, NO_SCORE_COLOURS)
        heading += (
            f' — <font backColor="{background}" color="{text}">'
            f"<b> Score: {result.score} </b></font>"
        )
    else:
        heading += " — <b>Score: —</b>"

    block = [Paragraph(heading, styles["Normal"])]

    if result.notes:
        block.append(Paragraph(f"<b>Notes:</b> {escape(result.notes)}", styles["Normal"]))

    if result.feedback:
        block.append(Paragraph(f"<b>Feedback:</b> {escape(result.feedback)}", styles["Normal"]))

    block.append(Spacer(1, 8))
    return KeepTogether(block)
