from __future__ import annotations

from cv_generator.fit import fit_to_two_pages


def _extract_scale(html: str) -> float:
    marker = "SCALE="
    start = html.index(marker) + len(marker)
    return float(html[start:])


def test_fit_overflow_converges_to_two_pages() -> None:
    def render(params):
        return f"SCALE={params.scale}"

    def page_counter(html: str, _base_url: str | None) -> int:
        scale = _extract_scale(html)
        if scale > 0.86:
            return 3
        if scale >= 0.42:
            return 2
        return 1

    result = fit_to_two_pages(render, page_counter=page_counter)

    assert result.page_count == 2
    assert 0.42 <= result.params.scale <= 0.86


def test_fit_underflow_converges_to_two_pages() -> None:
    def render(params):
        return f"SCALE={params.scale}"

    def page_counter(html: str, _base_url: str | None) -> int:
        scale = _extract_scale(html)
        if scale < 1.55:
            return 1
        if scale <= 2.20:
            return 2
        return 3

    result = fit_to_two_pages(render, page_counter=page_counter)

    assert result.page_count == 2
    assert 1.55 <= result.params.scale <= 2.20
