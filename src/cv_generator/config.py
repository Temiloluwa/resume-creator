from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StyleConfig:
    style_id: str
    display_name: str
    template_name: str
    html_filename: str
    pdf_filename: str


STYLES: tuple[StyleConfig, ...] = (
    StyleConfig(
        style_id="modern_teal",
        display_name="Modern Teal",
        template_name="cv_v1_modern_teal.j2.html",
        html_filename="cv_v1_modern_teal.html",
        pdf_filename="cv_v1_modern_teal.pdf",
    ),
    StyleConfig(
        style_id="editorial",
        display_name="Editorial Burgundy",
        template_name="cv_v2_editorial.j2.html",
        html_filename="cv_v2_editorial.html",
        pdf_filename="cv_v2_editorial.pdf",
    ),
    StyleConfig(
        style_id="tech_dark",
        display_name="Tech Dark",
        template_name="cv_v3_tech_dark.j2.html",
        html_filename="cv_v3_tech_dark.html",
        pdf_filename="cv_v3_tech_dark.pdf",
    ),
)
