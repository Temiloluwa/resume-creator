from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from .config import STYLES


def convert_html_to_pdf(html_path: Path, pdf_path: Path) -> Path:
    try:
        from weasyprint import CSS, HTML
    except (ImportError, OSError) as exc:  # pragma: no cover - dependency dependent
        raise RuntimeError(
            "WeasyPrint runtime libraries are missing. "
            "Install the required native libraries for WeasyPrint (Pango/Cairo/GObject)."
        ) from exc

    if not html_path.exists():
        raise FileNotFoundError(f"HTML not found: {html_path}")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_color_css = CSS(
        string="""
        @page {
          size: A4;
          margin: 0;
        }

        html, body {
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }

        * {
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        """
    )
    HTML(filename=str(html_path), base_url=str(html_path.parent)).write_pdf(
        str(pdf_path), stylesheets=[pdf_color_css]
    )
    return pdf_path


def convert_all_html_to_pdf(html_dir: Path, pdf_dir: Path) -> list[Path]:
    pdf_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    for style in STYLES:
        html_path = html_dir / style.html_filename
        pdf_path = pdf_dir / style.pdf_filename
        convert_html_to_pdf(html_path, pdf_path)
        outputs.append(pdf_path)

    return outputs


def count_pdf_pages(pdf_path: Path) -> int:
    with pdf_path.open("rb") as fh:
        reader = PdfReader(fh)
        return len(reader.pages)
