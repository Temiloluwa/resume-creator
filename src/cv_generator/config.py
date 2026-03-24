from __future__ import annotations

import re
from dataclasses import dataclass

TEMPLATE_NAME = "cv_v4_modern_teal_single_column.j2.html"


def sanitize_role(label: str) -> str:
    """
    Sanitize a role label by removing stop words and slugifying.
    Example: 'Senior Applied AI Engineer' -> 'applied-ai-engineer'
    """
    stop_words = {"senior", "junior", "lead", "principal", "staff"}
    # Lowercase and split into words
    words = label.lower().split()
    # Filter out stop words
    filtered_words = [w for w in words if w not in stop_words]
    # Join and replace non-alphanumeric with hyphens
    text = "-".join(filtered_words)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Collapse multiple hyphens and trim
    text = re.sub(r"-+", "-", text).strip("-")
    return text


@dataclass(frozen=True)
class RoleVariant:
    slug: str
    label: str
    introduction: str

    def get_html_filename(self, template: str | None = None) -> str:
        if template:
            sanitized = sanitize_role(self.label)
            # Replace <role> and change extension to .html
            filename = template.replace("<role>", sanitized)
            return filename.rsplit(".", 1)[0] + ".html"
        return f"{self.slug}.html"

    def get_pdf_filename(self, template: str | None = None) -> str:
        if template:
            sanitized = sanitize_role(self.label)
            return template.replace("<role>", sanitized)
        return f"{self.slug}.pdf"
