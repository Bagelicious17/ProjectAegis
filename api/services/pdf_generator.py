"""
PDF report generator for Aegis Due Diligence reports.

Converts Markdown reports into professional, downloadable PDF documents
with branding and formatting.
"""

import io
import logging
from datetime import datetime

logger = logging.getLogger("aegis.services.pdf")


def generate_pdf_report(company_name: str, report_markdown: str) -> bytes:
    """Generate a professional PDF from the Markdown report.

    Uses reportlab to create a styled PDF with cover page, headers,
    and formatted content.

    Args:
        company_name: Name of the analyzed company.
        report_markdown: The full Markdown report text.

    Returns:
        PDF file content as bytes.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
            HRFlowable,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    except ImportError:
        logger.error("reportlab not installed. Install with: pip install reportlab")
        raise ImportError("reportlab is required for PDF generation. Run: pip install reportlab")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    # --- Styles ---
    styles = getSampleStyleSheet()

    style_cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontSize=32,
        textColor=HexColor("#1a1a2e"),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    style_cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontSize=16,
        textColor=HexColor("#4a4a6a"),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName="Helvetica",
    )

    style_h1 = ParagraphStyle(
        "H1Custom",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=HexColor("#1a1a2e"),
        spaceBefore=20,
        spaceAfter=10,
        fontName="Helvetica-Bold",
    )

    style_h2 = ParagraphStyle(
        "H2Custom",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=HexColor("#2d3a8c"),
        spaceBefore=14,
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )

    style_body = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=HexColor("#333333"),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
    )

    style_bold = ParagraphStyle(
        "BoldCustom",
        parent=style_body,
        fontName="Helvetica-Bold",
    )

    style_footer = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#888888"),
        alignment=TA_CENTER,
    )

    # --- Build Content ---
    story = []

    # Cover Page
    story.append(Spacer(1, 3 * inch))
    story.append(Paragraph("🛡️ AEGIS", style_cover_title))
    story.append(Paragraph("Autonomous Due Diligence System", style_cover_subtitle))
    story.append(Spacer(1, 0.5 * inch))
    story.append(
        HRFlowable(width="60%", thickness=2, color=HexColor("#2d3a8c"), spaceAfter=20)
    )
    story.append(Paragraph(f"Risk Assessment Report", style_cover_subtitle))
    story.append(
        Paragraph(
            f"<b>{_escape_html(company_name)}</b>",
            ParagraphStyle(
                "CompanyName",
                parent=style_cover_title,
                fontSize=24,
                textColor=HexColor("#2d3a8c"),
            ),
        )
    )
    story.append(Spacer(1, 0.5 * inch))
    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            style_cover_subtitle,
        )
    )
    story.append(
        Paragraph("Classification: CONFIDENTIAL", style_cover_subtitle)
    )
    story.append(PageBreak())

    # Parse Markdown into PDF elements
    lines = report_markdown.split("\n")
    for line in lines:
        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1, 6))
            continue

        # Headers
        if stripped.startswith("## "):
            text = _escape_html(stripped[3:])
            story.append(Paragraph(text, style_h1))
        elif stripped.startswith("### "):
            text = _escape_html(stripped[4:])
            story.append(Paragraph(text, style_h2))
        elif stripped.startswith("# "):
            text = _escape_html(stripped[2:])
            story.append(Paragraph(text, style_h1))
        # Horizontal rules
        elif stripped in ("---", "***", "___"):
            story.append(
                HRFlowable(
                    width="100%", thickness=1, color=HexColor("#cccccc"), spaceAfter=10
                )
            )
        # Bold lines
        elif stripped.startswith("**") and stripped.endswith("**"):
            text = _escape_html(stripped[2:-2])
            story.append(Paragraph(f"<b>{text}</b>", style_bold))
        # Bullet points
        elif stripped.startswith("- ") or stripped.startswith("* "):
            text = _escape_html(stripped[2:])
            # Handle bold within bullets
            text = text.replace("**", "<b>", 1).replace("**", "</b>", 1)
            story.append(Paragraph(f"  •  {text}", style_body))
        # Table rows (simple rendering)
        elif stripped.startswith("|") and stripped.endswith("|"):
            # Skip separator rows
            if all(c in "|-: " for c in stripped):
                continue
            text = _escape_html(stripped)
            story.append(Paragraph(text, style_body))
        # Regular text
        else:
            text = _escape_html(stripped)
            # Handle inline bold
            text = text.replace("**", "<b>", 1).replace("**", "</b>", 1)
            story.append(Paragraph(text, style_body))

    # Footer
    story.append(Spacer(1, 1 * inch))
    story.append(
        HRFlowable(width="100%", thickness=1, color=HexColor("#cccccc"), spaceAfter=10)
    )
    story.append(
        Paragraph(
            f"Generated by Aegis Autonomous Due Diligence System • {datetime.now().strftime('%Y-%m-%d %H:%M')} • CONFIDENTIAL",
            style_footer,
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info(f"PDF generated for '{company_name}' ({len(pdf_bytes)} bytes)")
    return pdf_bytes


def _escape_html(text: str) -> str:
    """Escape HTML special characters for ReportLab Paragraph compatibility."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
