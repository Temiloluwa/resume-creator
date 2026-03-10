from __future__ import annotations

from pathlib import Path

import pytest

try:
    import weasyprint  # noqa: F401
except Exception as exc:  # pragma: no cover - environment-dependent native libs
    pytest.skip(f"WeasyPrint runtime unavailable: {exc}", allow_module_level=True)

from cv_generator.config import ROLE_VARIANTS
from cv_generator.fit import fit_to_two_pages
from cv_generator.loader import load_cv_content
from cv_generator.pdf import convert_html_directory_to_pdf, count_pdf_pages
from cv_generator.renderer import display_location, display_profile, render_all_html


def _all_content_strings_present(html: str, values: list[str]) -> None:
    for value in values:
        text = value.strip()
        if text:
            assert text in html


def test_full_pipeline_generates_two_role_variants_with_reference_header(tmp_path: Path) -> None:
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

    assert len(rendered) == len(ROLE_VARIANTS) == 2

    html_texts: dict[str, str] = {}
    for item in rendered:
        assert item.page_count == 2
        assert 0.84 <= item.fit_params.scale <= 1.0
        html_text = item.html_path.read_text(encoding="utf-8")
        html_texts[item.variant.slug] = html_text

        assert '@page {' in html_text
        assert 'size: A4;' in html_text
        assert 'class="contact-row"' in html_text
        assert 'class="contact-grid"' not in html_text
        assert 'References available on request' not in html_text
        assert html_text.count('<div class="page">') == 2
        assert html_text.count('class="contact-row"') == 2
        assert 'Co. Louth, Ireland' in html_text
        assert data.basics.name in html_text
        assert data.basics.email in html_text
        assert data.basics.phone in html_text
        assert display_location(data.basics.location) in html_text
        assert data.basics.work_authorization in html_text

        for profile in data.basics.profiles:
            assert display_profile(profile.url, profile.username) in html_text

        expected_strings = []
        expected_strings.extend(data.key_achievements)
        expected_strings.extend(data.certifications)

        for exp in data.experience:
            expected_strings.append(exp.company.split("(")[0].rstrip())
            expected_strings.append(exp.position)
            expected_strings.append(exp.location)
            expected_strings.append(exp.startDate)
            expected_strings.append(exp.endDate)
            expected_strings.extend(exp.highlights)

        for edu in data.education:
            expected_strings.extend([edu.institution, edu.area, edu.startDate, edu.endDate, edu.grade])

        for lang in data.languages:
            expected_strings.extend([lang.language, lang.fluency])

        for volunteer in data.volunteers:
            expected_strings.extend([volunteer.organization, volunteer.period])
            if volunteer.position != volunteer.organization:
                expected_strings.append(volunteer.position)

        _all_content_strings_present(html_text, expected_strings)

    applied = html_texts["senior_applied_ai_engineer"]
    ml = html_texts["senior_machine_learning_engineer"]

    assert "Senior Applied AI Engineer" in applied
    assert "Senior Applied AI Engineer" not in ml
    assert "Senior Machine Learning Engineer" in ml
    assert "Senior Machine Learning Engineer" not in applied
    assert data.introduction in applied
    assert data.introduction not in ml

    pdf_paths = convert_html_directory_to_pdf(html_dir, pdf_dir)
    assert len(pdf_paths) == 2
    for pdf_path in pdf_paths:
        assert pdf_path.exists()
        assert count_pdf_pages(pdf_path) == 2


def test_fit_search_shrinks_overflow_to_two_pages() -> None:
    def render(params):
        return f"SCALE={params.scale:.4f}"

    def counter(html: str, _base_url: str | None) -> int:
        scale = float(html.split("=")[1])
        return 3 if scale > 0.91 else 2

    result = fit_to_two_pages(render, page_counter=counter)

    assert result.page_count == 2
    assert result.params.scale <= 0.91
    assert result.params.scale >= 0.84


def test_fit_search_fails_when_bounded_scale_cannot_reach_two_pages() -> None:
    def render(params):
        return f"SCALE={params.scale:.4f}"

    def counter(_html: str, _base_url: str | None) -> int:
        return 3

    with pytest.raises(RuntimeError, match="Unable to fit CV content into exactly two pages"):
        fit_to_two_pages(render, page_counter=counter)
