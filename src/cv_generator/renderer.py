from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import unicodedata

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import STYLES, StyleConfig
from .fit import FitParams, fit_to_two_pages
from .models import CVData


@dataclass(frozen=True)
class RenderedHTML:
    style: StyleConfig
    html_path: Path
    fit_params: FitParams
    page_count: int


def build_template_environment(template_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        lstrip_blocks=True,
        trim_blocks=True,
    )


def render_all_html(
    cv_data: CVData,
    template_dir: Path,
    output_dir: Path,
    base_url: str | None = None,
) -> list[RenderedHTML]:
    output_dir.mkdir(parents=True, exist_ok=True)
    env = build_template_environment(template_dir)
    context = cv_data.to_context()
    root_path = Path(base_url).resolve() if base_url else Path.cwd()
    logos_dir = root_path / "logos"

    def logo_for(name: str | None) -> str:
        slug = _slugify(name or "")
        if slug:
            candidate = logos_dir / f"{slug}.png"
            if candidate.exists():
                return candidate.as_posix()
        return (logos_dir / "placeholder.png").as_posix()

    rendered: list[RenderedHTML] = []
    for style in STYLES:
        template = env.get_template(style.template_name)

        def render_for_fit(params: FitParams) -> str:
            return template.render(
                cv=context,
                fit=params,
                style=style,
                logo_for=logo_for,
            )

        fit_result = fit_to_two_pages(render_for_fit, base_url=base_url)
        html_path = output_dir / style.html_filename
        html_path.write_text(fit_result.html, encoding="utf-8")

        rendered.append(
            RenderedHTML(
                style=style,
                html_path=html_path,
                fit_params=fit_result.params,
                page_count=fit_result.page_count,
            )
        )

    return rendered


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return cleaned
