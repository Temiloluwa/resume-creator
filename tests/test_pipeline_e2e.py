from __future__ import annotations

from pathlib import Path

import pytest

try:
    import weasyprint  # noqa: F401
except Exception as exc:  # pragma: no cover - environment-dependent native libs
    pytest.skip(f"WeasyPrint runtime unavailable: {exc}", allow_module_level=True)

from cv_generator.loader import load_cv_content
from cv_generator.pdf import convert_all_html_to_pdf, count_pdf_pages
from cv_generator.renderer import render_all_html


def _all_content_strings_present(html: str, values: list[str]) -> None:
    for value in values:
        text = value.strip()
        if text:
            assert text in html


def test_full_pipeline_generates_three_two_page_html_and_pdfs(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    data = load_cv_content(repo_root / "cv-content.yaml")

    html_dir = tmp_path / "html"
    pdf_dir = tmp_path / "pdf"

    rendered = render_all_html(
        cv_data=data,
        template_dir=repo_root / "src" / "cv_generator" / "templates",
        output_dir=html_dir,
        base_url=str(repo_root),
    )

    assert len(rendered) == 3

    expected_strings = []
    expected_strings.extend(data.core_expertise)
    expected_strings.extend(data.certifications)
    expected_strings.extend([item.name for item in data.selected_projects])
    expected_strings.extend([item.description for item in data.selected_projects])

    for item in data.experience:
        expected_strings.append(item.company)
        expected_strings.append(item.position)
        expected_strings.append(item.summary)
        expected_strings.extend(item.highlights)

    for item in data.skills:
        expected_strings.append(item.category)
        expected_strings.extend(item.keywords)

    for item in data.education:
        expected_strings.append(item.institution)
        expected_strings.append(item.area)
        expected_strings.append(item.date)
        expected_strings.append(item.grade)

    for item in data.volunteers:
        expected_strings.append(item.organization)
        expected_strings.append(item.position)
        expected_strings.append(item.period)

    expected_strings.extend(data.professional_focus.details)

    for result in rendered:
        assert result.page_count == 2
        assert result.fit_params.margin_mm <= 16
        assert result.fit_params.margin_mm >= 5

        html_text = result.html_path.read_text(encoding="utf-8")
        assert "<!-- Page 1 -->" not in html_text
        assert "<!-- Page 2 -->" not in html_text
        assert "page-break-after: always" not in html_text

        _all_content_strings_present(html_text, expected_strings)

    generated_pdfs = convert_all_html_to_pdf(html_dir, pdf_dir)
    assert len(generated_pdfs) == 3

    for pdf_path in generated_pdfs:
        assert count_pdf_pages(pdf_path) == 2
