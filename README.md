# Resume Creator

A Python-based, two-page CV generator that transforms YAML content into professionally styled HTML and PDF documents.

## 🚀 Overview

This project provides a robust workflow for maintaining CV content in a structured YAML format and generating multiple styled variants. It handles complex layout challenges, such as fitting content precisely within two pages across various visual designs.

## ✨ Key Features

- **YAML-Driven Content**: Maintain your professional history in a single, version-controlled `cv-content.yaml`.
- **Multiple Style Variants**:
  - **Modern Teal**: A clean, contemporary design with sidebars.
  - **Editorial Burgundy**: A classic, structured layout.
  - **Tech Dark**: A high-contrast, modern aesthetic.
- **Auto-Fitting & Pagination**: Advanced logic to ensure the CV fits exactly on two pages by dynamically adjusting scale and spacing.
- **Logo Integration**: Automated institution logo sourcing and embedding.
- **Automated Workflow**: Simple commands via `Taskfile` for generation and cleanup.

## 🛠️ Technology Stack

- **Python 3.13+**
- **uv**: Next-generation Python package installer and resolver.
- **Jinja2**: For HTML templating.
- **WeasyPrint**: For high-fidelity HTML to PDF conversion.
- **PyYAML**: For content management.
- **Task**: Task runner for automation.

## 📥 Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) installed.
- [Task](https://taskfile.dev/) installed.

### Setup

1. Clone the repository.
2. Run the setup task:
   ```bash
   task setup
   ```

## 📋 Usage

Common commands available via the `Taskfile`:

| Command | Description |
| :--- | :--- |
| `task build` | Generate all HTML and PDF CV variants. |
| `task html` | Generate only HTML variants. |
| `task pdf` | Convert existing HTML to PDF. |
| `task clean` | Remove all generated artifacts in `output/`. |
| `task rebuild` | Full clean and rebuild. |

## 📂 Project Structure

- `cv-content.yaml`: The source of truth for all CV data.
- `cv-styles/`: HTML/CSS templates for each design variant.
- `logos/`: Institution logo assets.
- `output/`: Generated HTML and PDF files.
- `src/`: Python source code for the `cv-gen` CLI.
- `Taskfile.yml`: Automation task definitions.

---