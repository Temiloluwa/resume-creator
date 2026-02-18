from __future__ import annotations

from pathlib import Path

import yaml

from .models import CVData


class CVContentError(ValueError):
    """Raised when CV content cannot be parsed."""


def load_cv_content(path: Path) -> CVData:
    if not path.exists():
        raise CVContentError(f"CV content file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CVContentError(f"Invalid YAML in {path}: {exc}") from exc

    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise CVContentError(f"Expected top-level mapping in {path}")

    return CVData.from_dict(raw)
