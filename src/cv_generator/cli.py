from __future__ import annotations

import argparse
import sys
import re
from datetime import datetime
from pathlib import Path

from .config import STYLES
from .loader import CVContentError, load_cv_content
from .pdf import convert_all_html_to_pdf
from .renderer import render_all_html


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    project_root = _project_root()
    content_path = project_root / "cv-content.yaml"
    template_dir = project_root / "src" / "cv_generator" / "templates"
    cv_data = load_cv_content(content_path)
    role_dir = _normalized_role(cv_data.basics.label or "cv")
    date_dir = datetime.now().date().isoformat()
    output_root = project_root / "output" / role_dir / date_dir
    html_dir = output_root / "html"
    pdf_dir = output_root / "pdf"

    try:
        if args.command == "html":
            rendered = _run_html(cv_data, template_dir, html_dir, project_root)
            for item in rendered:
                print(
                    f"HTML [{item.style.display_name}] -> {item.html_path} "
                    f"(pages={item.page_count}, scale={item.fit_params.scale:.3f})"
                )
            return 0

        if args.command == "pdf":
            outputs = convert_all_html_to_pdf(html_dir, pdf_dir)
            for pdf_path in outputs:
                print(f"PDF -> {pdf_path}")
            return 0

        if args.command == "all":
            rendered = _run_html(cv_data, template_dir, html_dir, project_root)
            outputs = convert_all_html_to_pdf(html_dir, pdf_dir)
            for item in rendered:
                print(
                    f"HTML [{item.style.display_name}] -> {item.html_path} "
                    f"(pages={item.page_count}, scale={item.fit_params.scale:.3f})"
                )
            for pdf_path in outputs:
                print(f"PDF -> {pdf_path}")
            return 0

        if args.command == "clean":
            removed = _clean_outputs(html_dir, pdf_dir)
            for path in removed:
                print(f"Removed {path}")
            if not removed:
                print("No generated files found to remove.")
            return 0

    except (CVContentError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cv-gen",
        description="Generate two-page CV HTML and PDF files from cv-content.yaml.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("html", help="Render all CV styles to HTML with exact two-page fitting")
    subparsers.add_parser("pdf", help="Convert rendered HTML files to PDF")
    subparsers.add_parser("all", help="Run HTML render and PDF conversion")
    subparsers.add_parser("clean", help="Delete generated HTML/PDF artifacts")

    parser.set_defaults(command="all")
    return parser


def _run_html(
    cv_data,
    template_dir: Path,
    html_dir: Path,
    project_root: Path,
):
    return render_all_html(
        cv_data=cv_data,
        template_dir=template_dir,
        output_dir=html_dir,
        base_url=str(project_root),
    )


def _clean_outputs(html_dir: Path, pdf_dir: Path) -> list[Path]:
    removed: list[Path] = []

    for style in STYLES:
        for candidate in (html_dir / style.html_filename, pdf_dir / style.pdf_filename):
            if candidate.exists():
                candidate.unlink()
                removed.append(candidate)

    return removed


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _normalized_role(label: str) -> str:
    primary = re.split(r"[|/,-]", label)[0].strip().lower()
    replacements = {
        "machine learning": "ai",
        "ml": "ai",
        "applied ai": "ai",
        "artificial intelligence": "ai",
    }
    for src, dst in replacements.items():
        primary = primary.replace(src, dst)

    primary = re.sub(
        r"\b(senior|jr|junior|principal|staff|lead|head|sr)\b",
        "",
        primary,
    )
    slug = re.sub(r"[^a-z0-9]+", "-", primary).strip("-")
    if not slug:
        return "cv"
    slug = re.sub(r"-{2,}", "-", slug)
    return slug


if __name__ == "__main__":
    raise SystemExit(main())
