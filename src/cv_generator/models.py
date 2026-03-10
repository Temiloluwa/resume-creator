from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Profile:
    network: str = ""
    username: str = ""
    url: str = ""


@dataclass
class Basics:
    name: str = ""
    label: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    work_authorization: str = ""
    profiles: list[Profile] = field(default_factory=list)


@dataclass
class ExperienceItem:
    company: str = ""
    position: str = ""
    location: str = ""
    startDate: str = ""
    endDate: str = ""
    summary: str = ""
    highlights: list[str] = field(default_factory=list)


@dataclass
class ProjectItem:
    name: str = ""
    description: str = ""


@dataclass
class SkillCategory:
    category: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class EducationItem:
    institution: str = ""
    area: str = ""
    date: str = ""
    grade: str = ""


@dataclass
class VolunteerItem:
    organization: str = ""
    position: str = ""
    period: str = ""


@dataclass
class ProfessionalFocus:
    intro: str = ""
    details: list[str] = field(default_factory=list)


@dataclass
class CVData:
    basics: Basics = field(default_factory=Basics)
    introduction: str = ""
    key_achievements: list[str] = field(default_factory=list)
    technical_leadership: list[str] = field(default_factory=list)
    core_expertise: list[str] = field(default_factory=list)
    experience: list[ExperienceItem] = field(default_factory=list)
    selected_projects: list[ProjectItem] = field(default_factory=list)
    skills: list[SkillCategory] = field(default_factory=list)
    education: list[EducationItem] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    volunteers: list[VolunteerItem] = field(default_factory=list)
    professional_focus: ProfessionalFocus = field(default_factory=ProfessionalFocus)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CVData":
        root = _resolve_root(data)
        raw_experience_entries = _as_list_of_dicts(
            _pick(
                root,
                "experience",
                "work_experience",
                "professional_experience",
                "employment",
                "positions",
            )
        )
        experience_entries, skill_entries_from_experience = _split_experience_and_skills(
            raw_experience_entries
        )

        basics_raw = _as_dict(_pick(root, "basics", "contact", "personal"))
        basics = Basics(
            name=_as_text(_pick(basics_raw, "name", "full_name")),
            label=_as_text(_pick(basics_raw, "label", "headline", "title", "role")),
            email=_as_text(_pick(basics_raw, "email", "mail")),
            phone=_as_text(_pick(basics_raw, "phone", "telephone", "mobile")),
            location=_normalize_location(_pick(basics_raw, "location", "address", "city")),
            work_authorization=_as_text(
                _pick(
                    basics_raw,
                    "work_authorization",
                    "workAuthorization",
                    "work_permit",
                    "visa",
                )
            ),
            profiles=_parse_profiles(_pick(basics_raw, "profiles", "social", "links")),
        )

        professional_focus_raw = _as_dict(
            _pick(root, "professional_focus", "focus", "what_i_build")
        )
        technical_leadership = _as_list_of_text(
            _pick(root, "technical_leadership", "leadership", "platform_focus")
        )
        core_expertise = _as_list_of_text(
            _pick(root, "core_expertise", "expertise", "specializations", "strengths")
        )
        if not core_expertise:
            core_expertise = technical_leadership

        return cls(
            basics=basics,
            introduction=_as_text(
                _pick(root, "introduction", "summary", "profile", "about")
            ),
            key_achievements=_as_list_of_text(
                _pick(root, "key_achievements", "achievements", "impact_highlights")
            ),
            technical_leadership=technical_leadership,
            core_expertise=core_expertise,
            experience=[
                ExperienceItem(
                    company=_as_text(
                        _pick(item, "company", "organization", "employer", "client")
                    ),
                    position=_as_text(_pick(item, "position", "role", "title")),
                    location=_normalize_location(_pick(item, "location", "city", "onsite")),
                    startDate=_as_text(
                        _pick(item, "startDate", "start_date", "start", "from")
                    ),
                    endDate=_as_text(_pick(item, "endDate", "end_date", "end", "to")),
                    summary=_as_text(_pick(item, "summary", "overview", "description")),
                    highlights=_as_list_of_text(
                        _pick(
                            item,
                            "highlights",
                            "achievements",
                            "responsibilities",
                            "bullets",
                            "impact",
                        )
                    ),
                )
                for item in experience_entries
            ],
            selected_projects=[
                ProjectItem(
                    name=_as_text(_pick(item, "name", "title", "project")),
                    description=_as_text(_pick(item, "description", "summary", "details")),
                )
                for item in _as_list_of_dicts(
                    _pick(root, "selected_projects", "projects", "key_projects")
                )
            ],
            skills=_merge_skills(
                _parse_skills(_pick(root, "skills", "skill_groups", "competencies")),
                _parse_skills(skill_entries_from_experience),
            ),
            education=[
                EducationItem(
                    institution=_as_text(
                        _pick(item, "institution", "school", "university", "organization")
                    ),
                    area=_as_text(_pick(item, "area", "degree", "program", "qualification")),
                    date=_as_text(_pick(item, "date", "year", "period", "duration")),
                    grade=_as_text(_pick(item, "grade", "result", "gpa")),
                )
                for item in _as_list_of_dicts(_pick(root, "education", "academics"))
            ],
            certifications=_as_list_of_text(
                _pick(root, "certifications", "certs", "licenses")
            ),
            volunteers=[
                VolunteerItem(
                    organization=_as_text(
                        _pick(item, "organization", "org", "community", "group")
                    ),
                    position=_as_text(_pick(item, "position", "role", "title")),
                    period=_as_text(_pick(item, "period", "date", "dates", "duration")),
                )
                for item in _as_list_of_dicts(
                    _pick(root, "volunteers", "volunteering", "community")
                )
            ],
            professional_focus=ProfessionalFocus(
                intro=_as_text(_pick(professional_focus_raw, "intro", "summary")),
                details=_as_list_of_text(
                    _pick(professional_focus_raw, "details", "points", "bullets")
                ),
            ),
        )

    def to_context(self) -> dict[str, Any]:
        return asdict(self)


def _resolve_root(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}

    cv_root = _as_dict(data.get("cv"))
    if cv_root:
        return cv_root

    sections_root = _as_dict(data.get("sections"))
    if sections_root:
        merged = dict(data)
        merged.update(sections_root)
        return merged

    return data


def _pick(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _as_list_of_text(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        normalized: list[str] = []
        for item in value:
            if isinstance(item, dict):
                rendered = _as_text(
                    _pick(item, "name", "title", "text", "value", "description")
                )
                if rendered:
                    normalized.append(rendered)
                continue

            rendered = _as_text(item)
            if rendered:
                normalized.append(rendered)
        return normalized

    rendered = _as_text(value)
    return [rendered] if rendered else []


def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _normalize_location(value: Any) -> str:
    if isinstance(value, dict):
        parts = [
            _as_text(_pick(value, "city", "town")),
            _as_text(_pick(value, "state", "region")),
            _as_text(_pick(value, "country")),
        ]
        collapsed = ", ".join(part for part in parts if part)
        if collapsed:
            return collapsed
        return _as_text(_pick(value, "full", "label"))

    return _as_text(value)


def _parse_profiles(value: Any) -> list[Profile]:
    if isinstance(value, list):
        return [
            Profile(
                network=_as_text(_pick(item, "network", "name", "platform")),
                username=_as_text(_pick(item, "username", "handle", "label")),
                url=_as_text(_pick(item, "url", "href", "link")),
            )
            for item in _as_list_of_dicts(value)
        ]

    if isinstance(value, dict):
        profiles: list[Profile] = []
        for network, raw in value.items():
            if isinstance(raw, dict):
                profiles.append(
                    Profile(
                        network=_as_text(network),
                        username=_as_text(_pick(raw, "username", "handle", "label")),
                        url=_as_text(_pick(raw, "url", "href", "link")),
                    )
                )
            else:
                text = _as_text(raw)
                profiles.append(Profile(network=_as_text(network), username=text, url=text))
        return profiles

    return []


def _parse_skills(value: Any) -> list[SkillCategory]:
    if isinstance(value, dict):
        categories: list[SkillCategory] = []
        for category, raw_keywords in value.items():
            categories.append(
                SkillCategory(
                    category=_as_text(category),
                    keywords=_as_list_of_text(raw_keywords),
                )
            )
        return categories

    if isinstance(value, list):
        return [
            SkillCategory(
                category=_as_text(_pick(item, "category", "name", "group", "title")),
                keywords=_as_list_of_text(
                    _pick(item, "keywords", "items", "skills", "tools", "values")
                ),
            )
            for item in _as_list_of_dicts(value)
        ]

    return []


def _split_experience_and_skills(
    entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    experience_entries: list[dict[str, Any]] = []
    skill_entries: list[dict[str, Any]] = []

    for item in entries:
        if _looks_like_skill_entry(item):
            skill_entries.append(item)
        else:
            experience_entries.append(item)

    return experience_entries, skill_entries


def _looks_like_skill_entry(item: dict[str, Any]) -> bool:
    has_skill_shape = bool(_pick(item, "category", "group", "name")) and bool(
        _pick(item, "keywords", "skills", "items", "tools", "values")
    )
    has_experience_shape = bool(
        _pick(
            item,
            "company",
            "organization",
            "employer",
            "position",
            "role",
            "title",
            "startDate",
            "start_date",
            "endDate",
            "end_date",
        )
    )
    return has_skill_shape and not has_experience_shape


def _merge_skills(
    primary: list[SkillCategory], fallback: list[SkillCategory]
) -> list[SkillCategory]:
    if not primary and not fallback:
        return []

    merged: list[SkillCategory] = []
    seen: set[str] = set()
    for item in primary + fallback:
        key = item.category.strip().lower()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged
