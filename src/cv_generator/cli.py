from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import ROLE_VARIANTS
from .loader import CVContentError, load_cv_content
from .pdf import convert_html_directory_to_pdf
from .renderer import render_all_html


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    project_root = _project_root()
    content_path = project_root / "cv-content.yaml"
    template_dir = project_root / "src" / "cv_generator" / "templates"
    cv_data = load_cv_content(content_path)
    output_root = project_root / "output"
    html_dir = output_root / "html"
    pdf_dir = output_root / "pdf"

    try:
        if args.command == "html":
            rendered = _run_html(cv_data, template_dir, html_dir, project_root)
            for item in rendered:
                print(
                    f"HTML [{item.variant.label}] -> {item.html_path} "
                    f"(pages={item.page_count}, scale={item.fit_params.scale:.4f}, split={item.experience_split})"
                )
            return 0

        if args.command == "pdf":
            pdf_paths = convert_html_directory_to_pdf(html_dir, pdf_dir)
            for pdf_path in pdf_paths:
                print(f"PDF -> {pdf_path}")
            return 0

        if args.command == "all":
            rendered = _run_html(cv_data, template_dir, html_dir, project_root)
            pdf_paths = convert_html_directory_to_pdf(html_dir, pdf_dir)
            for item in rendered:
                print(
                    f"HTML [{item.variant.label}] -> {item.html_path} "
                    f"(pages={item.page_count}, scale={item.fit_params.scale:.4f}, split={item.experience_split})"
                )
            for pdf_path in pdf_paths:
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
        description="Generate role-specific CV HTML and PDF files from cv-content.yaml.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("html", help="Render the CV to HTML")
    subparsers.add_parser("pdf", help="Convert rendered HTML to PDF")
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

    legacy_candidates = (
        html_dir / "cv.html",
        pdf_dir / "cv.pdf",
    )

    for candidate in legacy_candidates:
        if candidate.exists():
            candidate.unlink()
            removed.append(candidate)

    for variant in ROLE_VARIANTS:
        for candidate in (
            html_dir / variant.html_filename,
            pdf_dir / variant.pdf_filename,
        ):
            if candidate.exists():
                candidate.unlink()
                removed.append(candidate)

    return removed


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    raise SystemExit(main())
