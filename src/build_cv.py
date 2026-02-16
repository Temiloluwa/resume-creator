#!/usr/bin/env python3
"""Build three CV variants from cv-content.yaml into HTML and PDF outputs."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import Page, sync_playwright
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent.parent
CV_PATH = ROOT / "cv-content.yaml"
OUTPUT_DIR = ROOT / "output"
STYLE_DIR = ROOT / "_backup" / "cv-styles"
TEMPLATES_DIR = ROOT / "templates"
LOGO_DIR = ROOT / "data" / "logos"

SECTION_ORDER: tuple[str, ...] = (
    "experience",
    "education",
    "skills",
    "volunteers",
    "certifications",
    "languages",
)


@dataclass(frozen=True)
class Variant:
    key: str
    style_file: str
    template_file: str
    html_out: str
    pdf_out: str
    min_scale: float = 0.88
    max_scale: float = 1.00


@dataclass(frozen=True)
class LayoutPlan:
    html: str
    ratios: tuple[float, float]
    break_index: int
    fit_level: int
    scale: float
    score: float


VARIANTS: tuple[Variant, ...] = (
    Variant(
        key="modern",
        style_file="cv_v1_modern_teal.html",
        template_file="cv_v1_modern_teal.html.j2",
        html_out="cv_v1_modern_teal.html",
        pdf_out="Temiloluwa_Adeoti_CV_v1_modern_teal.pdf",
    ),
    Variant(
        key="editorial",
        style_file="cv_v2_editorial.html",
        template_file="cv_v2_editorial.html.j2",
        html_out="cv_v2_editorial.html",
        pdf_out="Temiloluwa_Adeoti_CV_v2_editorial.pdf",
    ),
    Variant(
        key="tech",
        style_file="cv_v3_tech_dark.html",
        template_file="cv_v3_tech_dark.html.j2",
        html_out="cv_v3_tech_dark.html",
        pdf_out="Temiloluwa_Adeoti_CV_v3_tech_dark.pdf",
    ),
)


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def read_style_block(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    match = re.search(r"<style>(.*?)</style>", source, re.DOTALL)
    if not match:
        raise ValueError(f"No <style> block found in {path}")
    return match.group(1).strip()


def logo_uri(filename: str) -> str:
    path = LOGO_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing logo: {path}")
    return path.resolve().as_uri()


def profile_map(data: dict[str, Any]) -> dict[str, dict[str, str]]:
    mapped = {
        "linkedin": {"url": "", "username": ""},
        "github": {"url": "", "username": ""},
        "website": {"url": "", "username": ""},
    }
    profiles = data.get("basics", {}).get("profiles", [])
    if not isinstance(profiles, list):
        return mapped

    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        key = str(profile.get("network", "")).lower()
        if key in mapped:
            mapped[key] = {
                "url": str(profile.get("url", "")),
                "username": str(profile.get("username", "")),
            }
    return mapped


def normalize_items(items: Any, with_logo: bool) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return out

    for raw in items:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        if with_logo:
            logo_name = str(item.get("logo", "")).strip()
            item["logo_uri"] = logo_uri(logo_name) if logo_name else ""
        out.append(item)
    return out


def normalize_entries(section: Any) -> list[str]:
    if isinstance(section, list):
        return [str(x) for x in section if x is not None]
    if isinstance(section, dict):
        return [str(x) for x in section.get("entries", []) if x is not None]
    return []


def build_context(data: dict[str, Any]) -> dict[str, Any]:
    basics = data.get("basics", {}) if isinstance(data.get("basics"), dict) else {}
    sections: dict[str, list[Any]] = {
        "experience": normalize_items(data.get("experience", []), with_logo=True),
        "education": normalize_items(data.get("education", []), with_logo=True),
        "skills": normalize_items(data.get("skills", []), with_logo=False),
        "volunteers": normalize_items(data.get("volunteers", []), with_logo=True),
        "certifications": normalize_entries(data.get("certifications", [])),
        "languages": normalize_entries(data.get("languages", [])),
    }

    return {
        "basics": {
            "name": str(basics.get("name", "")),
            "label": str(basics.get("label", "")),
            "phone": str(basics.get("phone", "")),
            "email": str(basics.get("email", "")),
            "location": str(basics.get("location", "")),
        },
        "profiles": profile_map(data),
        "introduction": str(data.get("introduction", "")).strip(),
        "sections": sections,
    }


def section_chunks(sections: dict[str, list[Any]]) -> list[tuple[str, list[Any]]]:
    chunks: list[tuple[str, list[Any]]] = []

    for entry in sections.get("experience", []):
        chunks.append(("experience", [entry]))

    for section in SECTION_ORDER[1:]:
        values = sections.get(section, [])
        if values:
            chunks.append((section, values))

    return chunks


def split_chunks(
    chunks: list[tuple[str, list[Any]]], break_index: int
) -> tuple[dict[str, list[Any]], dict[str, list[Any]]]:
    page1 = {name: [] for name in SECTION_ORDER}
    page2 = {name: [] for name in SECTION_ORDER}

    for idx, (name, entries) in enumerate(chunks):
        target = page1 if idx < break_index else page2
        target[name].extend(entries)

    return page1, page2


def fit_overrides_css(variant_key: str, fit_level: int) -> str:
    if fit_level <= 0:
        return ""

    modern = {
        1: """
body.variant-modern.fit-1 .page { padding: 36px 46px !important; }
body.variant-modern.fit-1 .name { font-size: 39px !important; }
body.variant-modern.fit-1 .title { font-size: 22px !important; }
body.variant-modern.fit-1 .section-heading { font-size: 19px !important; margin-top: 19px !important; margin-bottom: 10px !important; }
body.variant-modern.fit-1 .job { margin-bottom: 13px !important; }
body.variant-modern.fit-1 .job-description li { margin-bottom: 4px !important; line-height: 1.38 !important; }
body.variant-modern.fit-1 .education-item, body.variant-modern.fit-1 .volunteer-item { margin-bottom: 10px !important; }
""",
        2: """
body.variant-modern.fit-2 .page { padding: 32px 42px !important; }
body.variant-modern.fit-2 .name { font-size: 36px !important; }
body.variant-modern.fit-2 .title { font-size: 21px !important; }
body.variant-modern.fit-2 .section-heading { font-size: 18px !important; margin-top: 16px !important; margin-bottom: 8px !important; }
body.variant-modern.fit-2 .job { margin-bottom: 10px !important; }
body.variant-modern.fit-2 .job-description ul { font-size: 12px !important; }
body.variant-modern.fit-2 .job-description li { margin-bottom: 3px !important; line-height: 1.3 !important; }
body.variant-modern.fit-2 .education-item, body.variant-modern.fit-2 .volunteer-item { margin-bottom: 8px !important; }
""",
        3: """
body.variant-modern.fit-3 .page { padding: 28px 38px !important; }
body.variant-modern.fit-3 .name { font-size: 34px !important; }
body.variant-modern.fit-3 .title { font-size: 19px !important; }
body.variant-modern.fit-3 .section-heading { font-size: 17px !important; margin-top: 14px !important; margin-bottom: 7px !important; }
body.variant-modern.fit-3 .job { margin-bottom: 8px !important; }
body.variant-modern.fit-3 .job-title { font-size: 14px !important; }
body.variant-modern.fit-3 .job-period { font-size: 12px !important; }
body.variant-modern.fit-3 .job-description ul { font-size: 11.5px !important; }
body.variant-modern.fit-3 .job-description li { margin-bottom: 2px !important; line-height: 1.25 !important; }
body.variant-modern.fit-3 .education-item, body.variant-modern.fit-3 .volunteer-item { margin-bottom: 6px !important; }
""",
    }

    editorial = {
        1: """
body.variant-editorial.fit-1 .page { padding: 42px 52px !important; }
body.variant-editorial.fit-1 .name { font-size: 47px !important; }
body.variant-editorial.fit-1 .title { font-size: 16px !important; margin-bottom: 22px !important; }
body.variant-editorial.fit-1 .section-heading { font-size: 24px !important; margin: 26px 0 14px 0 !important; }
body.variant-editorial.fit-1 .experience-item { margin-bottom: 20px !important; padding-left: 66px !important; }
body.variant-editorial.fit-1 .job-description ul { font-size: 11px !important; line-height: 1.45 !important; }
body.variant-editorial.fit-1 .job-description li { margin-bottom: 5px !important; }
body.variant-editorial.fit-1 .education-item, body.variant-editorial.fit-1 .volunteer-item { margin-bottom: 12px !important; padding-left: 58px !important; }
body.variant-editorial.fit-1 .skills-grid { gap: 12px !important; }
""",
        2: """
body.variant-editorial.fit-2 .page { padding: 38px 46px !important; }
body.variant-editorial.fit-2 .name { font-size: 43px !important; }
body.variant-editorial.fit-2 .title { font-size: 15px !important; margin-bottom: 18px !important; }
body.variant-editorial.fit-2 .section-heading { font-size: 22px !important; margin: 22px 0 12px 0 !important; }
body.variant-editorial.fit-2 .contact-grid { margin-bottom: 22px !important; padding: 14px !important; }
body.variant-editorial.fit-2 .experience-item { margin-bottom: 16px !important; padding-left: 62px !important; }
body.variant-editorial.fit-2 .job-title { font-size: 14px !important; }
body.variant-editorial.fit-2 .job-description ul { font-size: 10.5px !important; line-height: 1.35 !important; }
body.variant-editorial.fit-2 .job-description li { margin-bottom: 4px !important; }
body.variant-editorial.fit-2 .education-item, body.variant-editorial.fit-2 .volunteer-item { margin-bottom: 10px !important; padding-left: 54px !important; }
body.variant-editorial.fit-2 .skills-grid { gap: 10px !important; }
""",
        3: """
body.variant-editorial.fit-3 .page { padding: 34px 42px !important; }
body.variant-editorial.fit-3 .name { font-size: 40px !important; }
body.variant-editorial.fit-3 .title { font-size: 14px !important; margin-bottom: 14px !important; }
body.variant-editorial.fit-3 .section-heading { font-size: 20px !important; margin: 18px 0 10px 0 !important; }
body.variant-editorial.fit-3 .contact-grid { margin-bottom: 18px !important; padding: 12px !important; gap: 8px 20px !important; }
body.variant-editorial.fit-3 .experience-item { margin-bottom: 12px !important; padding-left: 58px !important; }
body.variant-editorial.fit-3 .job-title { font-size: 13px !important; }
body.variant-editorial.fit-3 .job-period { font-size: 11px !important; margin-bottom: 6px !important; }
body.variant-editorial.fit-3 .job-description ul { font-size: 10px !important; line-height: 1.28 !important; }
body.variant-editorial.fit-3 .job-description li { margin-bottom: 3px !important; }
body.variant-editorial.fit-3 .education-item, body.variant-editorial.fit-3 .volunteer-item { margin-bottom: 8px !important; padding-left: 50px !important; }
body.variant-editorial.fit-3 .skills-grid { gap: 8px !important; }
""",
    }

    tech = {
        1: """
body.variant-tech.fit-1 .page { padding: 40px 44px !important; }
body.variant-tech.fit-1 .name { font-size: 44px !important; }
body.variant-tech.fit-1 .title { font-size: 13px !important; }
body.variant-tech.fit-1 .section-heading { font-size: 21px !important; margin: 24px 0 12px 0 !important; }
body.variant-tech.fit-1 .job { margin-bottom: 16px !important; padding: 14px !important; }
body.variant-tech.fit-1 .job-description ul { font-size: 10px !important; line-height: 1.45 !important; }
body.variant-tech.fit-1 .job-description li { margin-bottom: 5px !important; }
body.variant-tech.fit-1 .education-item, body.variant-tech.fit-1 .volunteer-item { margin-bottom: 12px !important; padding: 10px !important; }
""",
        2: """
body.variant-tech.fit-2 .page { padding: 36px 40px !important; }
body.variant-tech.fit-2 .name { font-size: 40px !important; }
body.variant-tech.fit-2 .title { font-size: 12px !important; }
body.variant-tech.fit-2 .section-heading { font-size: 20px !important; margin: 20px 0 10px 0 !important; }
body.variant-tech.fit-2 .contact-grid { margin-top: 18px !important; padding: 10px !important; }
body.variant-tech.fit-2 .job { margin-bottom: 12px !important; padding: 12px !important; }
body.variant-tech.fit-2 .job-description ul { font-size: 9.8px !important; line-height: 1.35 !important; }
body.variant-tech.fit-2 .job-description li { margin-bottom: 4px !important; }
body.variant-tech.fit-2 .education-item, body.variant-tech.fit-2 .volunteer-item { margin-bottom: 9px !important; padding: 8px !important; }
""",
        3: """
body.variant-tech.fit-3 .page { padding: 32px 36px !important; }
body.variant-tech.fit-3 .name { font-size: 37px !important; }
body.variant-tech.fit-3 .title { font-size: 11px !important; }
body.variant-tech.fit-3 .section-heading { font-size: 18px !important; margin: 16px 0 8px 0 !important; }
body.variant-tech.fit-3 .contact-grid { margin-top: 14px !important; padding: 8px !important; gap: 8px !important; }
body.variant-tech.fit-3 .job { margin-bottom: 10px !important; padding: 10px !important; }
body.variant-tech.fit-3 .job-title { font-size: 13px !important; }
body.variant-tech.fit-3 .job-period { font-size: 10px !important; }
body.variant-tech.fit-3 .job-description ul { font-size: 9.5px !important; line-height: 1.28 !important; }
body.variant-tech.fit-3 .job-description li { margin-bottom: 3px !important; }
body.variant-tech.fit-3 .education-item, body.variant-tech.fit-3 .volunteer-item { margin-bottom: 7px !important; padding: 7px !important; }
""",
    }

    if variant_key == "modern":
        return modern.get(fit_level, "")
    if variant_key == "editorial":
        return editorial.get(fit_level, "")
    if variant_key == "tech":
        return tech.get(fit_level, "")
    return ""


def render_html(
    env: Environment,
    variant: Variant,
    context: dict[str, Any],
    style_css: str,
    page1: dict[str, list[Any]],
    page2: dict[str, list[Any]],
    fit_level: int,
) -> str:
    template = env.get_template(variant.template_file)
    fit_class = f"fit-{fit_level}" if fit_level > 0 else ""
    return template.render(
        cv=context,
        page1=page1,
        page2=page2,
        style_css=style_css,
        fit_class=fit_class,
        variant_key=variant.key,
    )


def measure_overflow_ratios_from_page(page: Page, html_content: str) -> tuple[float, float]:
    page.set_content(html_content, wait_until="networkidle")
    page.emulate_media(media="print")
    ratios = page.evaluate(
        """
        () => {
          const pages = Array.from(document.querySelectorAll('.page'));
          const measured = pages.map((el) => {
            if (!el.clientHeight) return 1;
            return el.scrollHeight / el.clientHeight;
          });
          return [measured[0] ?? 1, measured[1] ?? 1];
        }
        """
    )
    return float(ratios[0]), float(ratios[1])


def compute_pdf_scale(ratios: tuple[float, float], min_scale: float, max_scale: float) -> float:
    max_ratio = max(ratios)
    scale = 0.995 / max_ratio if max_ratio > 1 else max_scale
    return max(min(scale, max_scale), min_scale)


def layout_score(ratios: tuple[float, float], scale: float, fit_level: int) -> float:
    scaled_fill = [min(1.0, r * scale) for r in ratios]
    overflow = sum(max(0.0, (r * scale) - 1.0) for r in ratios)
    underuse = sum(max(0.0, 1.0 - fill) for fill in scaled_fill)
    imbalance = abs(scaled_fill[0] - scaled_fill[1])
    scale_penalty = max(0.0, 1.0 - scale)

    return (
        overflow * 200.0
        + underuse
        + (imbalance * 0.35)
        + (scale_penalty * 35.0)
        + (fit_level * 0.45)
    )


def choose_layout(
    env: Environment,
    variant: Variant,
    context: dict[str, Any],
    base_style_css: str,
) -> LayoutPlan:
    chunks = section_chunks(context["sections"])
    best: LayoutPlan | None = None

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        for fit_level in range(0, 4):
            style_css = base_style_css + "\n" + fit_overrides_css(variant.key, fit_level)

            for break_index in range(len(chunks) + 1):
                page1, page2 = split_chunks(chunks, break_index)
                html_content = render_html(
                    env=env,
                    variant=variant,
                    context=context,
                    style_css=style_css,
                    page1=page1,
                    page2=page2,
                    fit_level=fit_level,
                )
                ratios = measure_overflow_ratios_from_page(page, html_content)
                scale = compute_pdf_scale(ratios, min_scale=variant.min_scale, max_scale=variant.max_scale)
                score = layout_score(ratios, scale, fit_level)

                plan = LayoutPlan(
                    html=html_content,
                    ratios=ratios,
                    break_index=break_index,
                    fit_level=fit_level,
                    scale=scale,
                    score=score,
                )

                if best is None or plan.score < best.score:
                    best = plan

        browser.close()

    if best is None:
        raise RuntimeError(f"Unable to compute layout plan for variant: {variant.key}")

    return best


def validate_scaled_fit(ratios: tuple[float, float], scale: float) -> None:
    if any((ratio * scale) > 1.001 for ratio in ratios):
        raise RuntimeError(
            f"Scaled content still overflows page bounds (ratios={ratios}, scale={scale:.3f})."
        )


def html_to_pdf(html_file: Path, pdf_file: Path, scale: float) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(html_file.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(pdf_file),
            format="A4",
            print_background=True,
            margin={"top": "0cm", "right": "0cm", "bottom": "0cm", "left": "0cm"},
            scale=scale,
        )
        browser.close()


def pdf_page_count(pdf_file: Path) -> int:
    return len(PdfReader(str(pdf_file)).pages)


def ensure_page_cap(pdf_file: Path, max_pages: int) -> None:
    pages = pdf_page_count(pdf_file)
    if pages > max_pages:
        raise RuntimeError(f"{pdf_file.name} has {pages} pages; max allowed is {max_pages}")


def build(max_pages: int) -> None:
    data = load_yaml(CV_PATH)
    context = build_context(data)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for variant in VARIANTS:
        base_style_css = read_style_block(STYLE_DIR / variant.style_file)
        plan = choose_layout(env=env, variant=variant, context=context, base_style_css=base_style_css)

        html_file = OUTPUT_DIR / variant.html_out
        pdf_file = OUTPUT_DIR / variant.pdf_out

        html_file.write_text(plan.html, encoding="utf-8")

        validate_scaled_fit(plan.ratios, plan.scale)
        html_to_pdf(html_file, pdf_file, plan.scale)
        ensure_page_cap(pdf_file, max_pages=max_pages)

        print(
            f"Built {variant.key}: {html_file.name}, {pdf_file.name} "
            f"(fit={plan.fit_level}, break={plan.break_index}, scale={plan.scale:.3f}, "
            f"pages={pdf_page_count(pdf_file)}, ratios=({plan.ratios[0]:.3f}, {plan.ratios[1]:.3f}))"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build all CV styles from YAML")
    parser.add_argument("--max-pages", type=int, default=2, help="Maximum page count per generated PDF")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build(max_pages=args.max_pages)


if __name__ == "__main__":
    main()
