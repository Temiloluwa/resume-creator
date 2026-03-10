from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Callable

from pypdf import PdfReader

TARGET_PAGE_COUNT = 2
MAX_SCALE = 1.0
MIN_SCALE = 0.84


@dataclass(frozen=True)
class FitParams:
    scale: float


@dataclass(frozen=True)
class FitResult:
    params: FitParams
    html: str
    page_count: int


TemplateRenderer = Callable[[FitParams], str]
PageCounter = Callable[[str, str | None], int]


def count_pages_from_html(html: str, base_url: str | None = None) -> int:
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:  # pragma: no cover - dependency dependent
        raise RuntimeError(
            "WeasyPrint runtime libraries are missing. "
            "Install the required native libraries for WeasyPrint (Pango/Cairo/GObject)."
        ) from exc

    pdf_bytes = HTML(string=html, base_url=base_url).write_pdf()
    reader = PdfReader(BytesIO(pdf_bytes))
    return len(reader.pages)


def fit_to_two_pages(
    render_html: TemplateRenderer,
    *,
    base_url: str | None = None,
    page_counter: PageCounter | None = None,
    max_iterations: int = 18,
) -> FitResult:
    counter = page_counter or count_pages_from_html
    cache: dict[float, FitResult] = {}

    def evaluate(scale: float) -> FitResult:
        rounded = round(max(MIN_SCALE, min(MAX_SCALE, scale)), 4)
        cached = cache.get(rounded)
        if cached is not None:
            return cached
        params = FitParams(scale=rounded)
        html = render_html(params)
        result = FitResult(params=params, html=html, page_count=counter(html, base_url))
        cache[rounded] = result
        return result

    full = evaluate(MAX_SCALE)
    if full.page_count == TARGET_PAGE_COUNT:
        return full

    if full.page_count < TARGET_PAGE_COUNT:
        raise RuntimeError("Rendered CV underflowed below two pages.")

    low = MIN_SCALE
    high = MAX_SCALE
    best: FitResult | None = None

    min_result = evaluate(MIN_SCALE)
    if min_result.page_count > TARGET_PAGE_COUNT:
        raise RuntimeError("Unable to fit CV content into exactly two pages.")
    if min_result.page_count == TARGET_PAGE_COUNT:
        best = min_result

    for _ in range(max_iterations):
        mid = (low + high) / 2.0
        result = evaluate(mid)
        if result.page_count > TARGET_PAGE_COUNT:
            high = mid
            continue

        low = mid
        if result.page_count == TARGET_PAGE_COUNT:
            best = result

    if best is None:
        raise RuntimeError("Unable to find a bounded scale that produces exactly two pages.")
    return best
