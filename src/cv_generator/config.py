from __future__ import annotations

from dataclasses import dataclass


TEMPLATE_NAME = "cv_v4_modern_teal_single_column.j2.html"


@dataclass(frozen=True)
class RoleVariant:
    slug: str
    label: str
    introduction: str

    @property
    def html_filename(self) -> str:
        return f"{self.slug}.html"

    @property
    def pdf_filename(self) -> str:
        return f"{self.slug}.pdf"


ROLE_VARIANTS: tuple[RoleVariant, ...] = (
    RoleVariant(
        slug="adeoti-t-applied-ai-engineer-2026",
        label="Senior Applied AI Engineer",
        introduction=(
            "Senior Applied AI Engineer with 5+ years building production ML systems — "
            "from multimodal LLM pipelines and RAG architectures to cloud-native inference "
            "infrastructure on AWS and Azure. Delivered enterprise AI solutions generating "
            "€500k+ revenue for Allianz, Volkswagen, and Porsche. Background spanning "
            "industrial field engineering, enterprise technology consulting, and applied AI, "
            "providing a practical understanding of noisy real-world data and operational "
            "system constraints."
        ),
    ),
    RoleVariant(
        slug="adeoti-t-ml-engineer-2026",
        label="Senior Machine Learning Engineer",
        introduction=(
            "Senior Machine Learning Engineer with 5+ years building production ML systems — "
            "from multimodal LLM pipelines and RAG architectures to cloud-native inference "
            "infrastructure on AWS and Azure. Delivered enterprise AI solutions generating "
            "€500k+ revenue for Allianz, Volkswagen, and Porsche. Background spanning "
            "industrial field engineering, enterprise technology consulting, and applied "
            "machine learning, providing a practical understanding of noisy real-world data "
            "and operational system constraints."
        ),
    ),
)
