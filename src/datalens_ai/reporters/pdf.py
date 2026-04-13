"""Generate PDF reports (requires xhtml2pdf)."""

from __future__ import annotations

import logging

from datalens_ai.core.models import DataProfile, DataStory, QueryResult
from datalens_ai.reporters.html import generate_html_report

logger = logging.getLogger(__name__)


def generate_pdf_report(
    story: DataStory | None = None,
    profile: DataProfile | None = None,
    results: list[QueryResult] | None = None,
    title: str = "DataLens AI Report",
) -> bytes:
    """Generate a PDF report as bytes.

    Falls back to returning the HTML as UTF-8 bytes if xhtml2pdf
    is not installed.
    """
    html = generate_html_report(
        story=story,
        profile=profile,
        results=results,
        title=title,
    )

    try:
        from io import BytesIO

        from xhtml2pdf import pisa

        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buffer)
        if pisa_status.err:
            logger.warning("PDF generation had errors, returning HTML fallback")
            return html.encode("utf-8")
        return buffer.getvalue()

    except ImportError:
        logger.info("xhtml2pdf not installed — returning HTML as bytes")
        return html.encode("utf-8")
