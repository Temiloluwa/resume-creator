from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import ROLE_VARIANTS, TEMPLATE_NAME, RoleVariant
from .fit import FitParams, FitResult, fit_to_two_pages
from .models import CVData


@dataclass(frozen=True)
class RenderedHTML:
    variant: RoleVariant
    html_path: Path
    fit_params: FitParams
    page_count: int
    experience_split: int


def build_template_environment(template_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        lstrip_blocks=False,
        trim_blocks=False,
    )
    env.filters["collapse_lines"] = collapse_lines
    env.filters["company_name"] = company_name
    env.filters["company_note"] = company_note
    env.filters["join_date_range"] = join_date_range
    env.filters["join_keywords"] = join_keywords
    env.filters["display_location"] = display_location
    env.filters["display_profile"] = display_profile
    return env


def render_all_html(
    cv_data: CVData,
    template_dir: Path,
    output_dir: Path,
    *,
    base_url: str | None = None,
) -> list[RenderedHTML]:
    output_dir.mkdir(parents=True, exist_ok=True)
    env = build_template_environment(template_dir)
    template = env.get_template(TEMPLATE_NAME)

    rendered: list[RenderedHTML] = []
    for variant in ROLE_VARIANTS:
        base_context = _variant_context(cv_data, variant)
        best = _fit_variant(template, base_context, cv_data, base_url=base_url)

        html_path = output_dir / variant.html_filename
        html_path.write_text(best.html, encoding="utf-8")
        rendered.append(
            RenderedHTML(
                variant=variant,
                html_path=html_path,
                fit_params=best.params,
                page_count=best.page_count,
                experience_split=best.experience_split,
            )
        )

    return rendered


@dataclass(frozen=True)
class _VariantFit:
    html: str
    params: FitParams
    page_count: int
    experience_split: int


def _fit_variant(template, base_context: dict, cv_data: CVData, *, base_url: str | None) -> _VariantFit:
    experiences = base_context["cv"]["experience"]
    candidate_splits = list(range(1, len(experiences))) or [0]
    best: _VariantFit | None = None

    for split in candidate_splits:
        split_context = deepcopy(base_context)
        split_context["experience_page_one"] = experiences[:split]
        split_context["experience_page_two"] = experiences[split:]

        def render_for_fit(params: FitParams) -> str:
            return template.render(**split_context, fit=params)

        try:
            fit_result = fit_to_two_pages(render_for_fit, base_url=base_url)
        except RuntimeError:
            continue

        candidate = _VariantFit(
            html=fit_result.html,
            params=fit_result.params,
            page_count=fit_result.page_count,
            experience_split=split,
        )
        if best is None or candidate.params.scale > best.params.scale:
            best = candidate

    if best is not None:
        return best

    raise RuntimeError("Unable to fit CV content into exactly two pages for any experience split.")


def _variant_context(cv_data: CVData, variant: RoleVariant) -> dict:
    context = {"cv": deepcopy(cv_data.to_context())}
    context["cv"]["basics"]["label"] = variant.label
    context["cv"]["introduction"] = variant.introduction
    return context


def collapse_lines(value: str) -> str:
    return " ".join(part.strip() for part in value.splitlines() if part.strip())


def display_location(value: str) -> str:
    lines = [part.strip() for part in value.splitlines() if part.strip()]
    if lines:
        return lines[-1]
    return collapse_lines(value)


def company_name(value: str) -> str:
    name, _, _ = value.partition("(")
    return name.rstrip()


def company_note(value: str) -> str:
    _, sep, tail = value.partition("(")
    if not sep:
        return ""
    return f"({tail}".strip()


def join_date_range(start: str, end: str) -> str:
    values = [item.strip() for item in (start, end) if item and item.strip()]
    return " – ".join(values)


def join_keywords(values: list[str]) -> str:
    return " · ".join(value.strip() for value in values if value.strip())


def display_profile(url: str, username: str = "") -> str:
    if not url:
        return username

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    host = parsed.netloc.replace("www.", "")
    if path:
        return f"{host}{path}"
    return host or username or url
