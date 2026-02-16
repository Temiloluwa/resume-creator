from __future__ import annotations

from pathlib import Path

from cv_generator.loader import load_cv_content


def test_load_real_cv_content() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    cv = load_cv_content(repo_root / "cv-content.yaml")

    assert cv.basics.name
    assert cv.basics.email
    assert cv.experience
    assert cv.skills


def test_optional_sections_default_to_empty(tmp_path: Path) -> None:
    content = tmp_path / "cv-content.yaml"
    content.write_text("basics:\n  name: Example\n", encoding="utf-8")

    cv = load_cv_content(content)

    assert cv.basics.name == "Example"
    assert cv.introduction == ""
    assert cv.experience == []
    assert cv.certifications == []
    assert cv.professional_focus.details == []


def test_loader_supports_aliases_and_nested_sections(tmp_path: Path) -> None:
    content = tmp_path / "cv-content.yaml"
    content.write_text(
        """
cv:
  personal:
    full_name: Jane Example
    title: Principal Engineer
    mail: jane@example.com
    telephone: "+1 555 111 2222"
    address:
      city: Austin
      country: USA
    links:
      LinkedIn: https://linkedin.com/in/jane
  summary: Builds robust distributed systems.
  expertise:
    - Platform Architecture
  work_experience:
    - employer: Example Corp
      role: Staff Engineer
      start_date: 2020
      end_date: Present
      city: Remote
      achievements:
        - Led migration
  projects:
    - title: Internal Platform
      summary: Reduced deployment time.
  competencies:
    Backend:
      - Python
      - Go
  academics:
    - school: Example University
      degree: M.Sc. Computer Science
      year: 2019
  certs:
    - AWS SAA
  volunteering:
    - org: Open Source Org
      role: Maintainer
      duration: 2021-2024
  focus:
    summary: Designing systems that
    bullets:
      - Scale safely
""",
        encoding="utf-8",
    )

    cv = load_cv_content(content)

    assert cv.basics.name == "Jane Example"
    assert cv.basics.label == "Principal Engineer"
    assert cv.basics.email == "jane@example.com"
    assert cv.basics.phone == "+1 555 111 2222"
    assert cv.basics.location == "Austin, USA"
    assert cv.introduction == "Builds robust distributed systems."
    assert cv.core_expertise == ["Platform Architecture"]
    assert cv.experience[0].company == "Example Corp"
    assert cv.experience[0].position == "Staff Engineer"
    assert cv.experience[0].highlights == ["Led migration"]
    assert cv.selected_projects[0].name == "Internal Platform"
    assert cv.skills[0].category == "Backend"
    assert cv.skills[0].keywords == ["Python", "Go"]
    assert cv.education[0].institution == "Example University"
    assert cv.certifications == ["AWS SAA"]
    assert cv.volunteers[0].organization == "Open Source Org"
    assert cv.professional_focus.details == ["Scale safely"]
