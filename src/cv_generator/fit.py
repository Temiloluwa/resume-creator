from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

TARGET_PAGE_COUNT = 2
MIN_SCALE = 0.10
MAX_SCALE = 6.00


@dataclass(frozen=True)
class FitParams:
    scale: float
    margin_mm: float
    section_gap_scale: float
    line_height: float


@dataclass(frozen=True)
class FitResult:
    params: FitParams
    html: str
    page_count: int
    iterations: int


@dataclass(frozen=True)
class _FitCandidate:
    scale: float
    params: FitParams
    pages: int
    html: str


PageCounter = Callable[[str, str | None], int]
TemplateRenderer = Callable[[FitParams], str]


def params_from_scale(scale: float) -> FitParams:
    scale = _clamp(scale, MIN_SCALE, MAX_SCALE)
    margin_mm = _clamp(9.0 + (scale - 1.0) * 2.5, 5.0, 16.0)
    section_gap_scale = _clamp(1.0 + (scale - 1.0) * 0.9, 0.35, 2.2)
    line_height = _clamp(1.32 + (scale - 1.0) * 0.28, 0.92, 2.0)
    return FitParams(
        scale=scale,
        margin_mm=margin_mm,
        section_gap_scale=section_gap_scale,
        line_height=line_height,
    )


def count_pages_from_html(html: str, base_url: str | None = None) -> int:
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:  # pragma: no cover - dependency dependent
        raise RuntimeError(
            "WeasyPrint runtime libraries are missing. "
            "Install the required native libraries for WeasyPrint (Pango/Cairo/GObject)."
        ) from exc

    document = HTML(string=html, base_url=base_url).render()
    return len(document.pages)


def fit_to_two_pages(
    render_html: TemplateRenderer,
    base_url: str | None = None,
    target_pages: int = TARGET_PAGE_COUNT,
    page_counter: PageCounter | None = None,
    max_iterations: int = 36,
) -> FitResult:
    counter = page_counter or count_pages_from_html
    cache: dict[float, _FitCandidate] = {}

    def evaluate(scale: float) -> _FitCandidate:
        rounded = round(_clamp(scale, MIN_SCALE, MAX_SCALE), 6)
        cached = cache.get(rounded)
        if cached is not None:
            return cached

        params = params_from_scale(rounded)
        html = render_html(params)
        pages = counter(html, base_url)
        candidate = _FitCandidate(scale=rounded, params=params, pages=pages, html=html)
        cache[rounded] = candidate
        return candidate

    iterations = 0
    initial = evaluate(1.0)
    iterations += 1

    if initial.pages == target_pages:
        result = _maximize_exact_target(
            initial=initial,
            evaluate=evaluate,
            target_pages=target_pages,
            max_iterations=max_iterations,
        )
        return FitResult(result.params, result.html, result.pages, iterations + len(cache) - 1)

    if initial.pages > target_pages:
        bad = initial
        probe_scale = initial.scale
        good = initial
        while bad.pages > target_pages and probe_scale > MIN_SCALE:
            probe_scale = max(MIN_SCALE, probe_scale * 0.84)
            good = evaluate(probe_scale)
            iterations += 1
            if good.pages <= target_pages:
                break

        if good.pages > target_pages:
            raise RuntimeError(
                "Unable to force content into two pages even at minimum scale."
            )

        result = _maximize_exact_target_in_bracket(
            good=good,
            bad=bad,
            evaluate=evaluate,
            target_pages=target_pages,
            max_iterations=max_iterations,
        )
        return FitResult(result.params, result.html, result.pages, iterations)

    good = initial
    probe_scale = initial.scale
    bad = initial
    while good.pages < target_pages and probe_scale < MAX_SCALE:
        probe_scale = min(MAX_SCALE, probe_scale * 1.18)
        bad = evaluate(probe_scale)
        iterations += 1
        if bad.pages >= target_pages:
            break

    if bad.pages < target_pages:
        raise RuntimeError("Unable to expand content to exactly two pages.")

    if bad.pages == target_pages:
        result = _maximize_exact_target(
            initial=bad,
            evaluate=evaluate,
            target_pages=target_pages,
            max_iterations=max_iterations,
        )
        return FitResult(result.params, result.html, result.pages, iterations)

    result = _maximize_exact_target_in_bracket(
        good=good,
        bad=bad,
        evaluate=evaluate,
        target_pages=target_pages,
        max_iterations=max_iterations,
    )
    return FitResult(result.params, result.html, result.pages, iterations)


def _maximize_exact_target(
    *,
    initial: _FitCandidate,
    evaluate: Callable[[float], _FitCandidate],
    target_pages: int,
    max_iterations: int,
) -> _FitCandidate:
    good = initial
    probe_scale = initial.scale
    bad: _FitCandidate | None = None

    while probe_scale < MAX_SCALE:
        probe_scale = min(MAX_SCALE, probe_scale * 1.12)
        candidate = evaluate(probe_scale)
        if candidate.pages > target_pages:
            bad = candidate
            break
        if candidate.pages == target_pages:
            good = candidate

    if bad is None:
        return good

    return _maximize_exact_target_in_bracket(
        good=good,
        bad=bad,
        evaluate=evaluate,
        target_pages=target_pages,
        max_iterations=max_iterations,
    )


def _maximize_exact_target_in_bracket(
    *,
    good: _FitCandidate,
    bad: _FitCandidate,
    evaluate: Callable[[float], _FitCandidate],
    target_pages: int,
    max_iterations: int,
) -> _FitCandidate:
    if good.pages > target_pages:
        raise ValueError("'good' candidate must have pages <= target")
    if bad.pages <= target_pages:
        raise ValueError("'bad' candidate must have pages > target")

    best: _FitCandidate | None = good if good.pages == target_pages else None
    low = good.scale
    high = bad.scale

    for _ in range(max_iterations):
        midpoint = (low + high) / 2.0
        candidate = evaluate(midpoint)

        if candidate.pages <= target_pages:
            low = candidate.scale
            good = candidate
            if candidate.pages == target_pages:
                if best is None or candidate.scale > best.scale:
                    best = candidate
        else:
            high = candidate.scale
            bad = candidate

    if best is not None:
        return best

    # Final dense scan in case of a discontinuity around page-break threshold.
    step = (high - low) / 120.0 if high > low else 0.0
    probe = low
    while probe <= high and step > 0:
        candidate = evaluate(probe)
        if candidate.pages == target_pages:
            if best is None or candidate.scale > best.scale:
                best = candidate
        probe += step

    if best is None:
        raise RuntimeError("Unable to find a scale that produces exactly two pages.")

    return best


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
