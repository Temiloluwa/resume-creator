# Resume Creator

A Python-based CV generator that transforms YAML content into a single fixed-style HTML and PDF export.

## 🚀 Overview

This project provides a workflow for maintaining CV content in a structured YAML format and generating one HTML and PDF pair that matches the reference design in `reference/cv_v4_modern_teal_single_column.html`.

## ✨ Key Features

- **YAML-Driven Content**: Maintain your professional history in a single, version-controlled `cv-content.yaml`.
- **Reference-Driven Styling**: The generated HTML preserves the layout and CSS of the locked reference file.
- **Stable Exports**: `task build` writes `output/html/cv.html` and `output/pdf/cv.pdf`.
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
| `task build` | Generate `output/html/cv.html` and `output/pdf/cv.pdf`. |
| `task html` | Generate only `output/html/cv.html`. |
| `task pdf` | Convert `output/html/cv.html` into `output/pdf/cv.pdf`. |
| `task clean` | Remove all generated artifacts in `output/`. |
| `task rebuild` | Full clean and rebuild. |

## 📂 Project Structure

- `cv-content.yaml`: The source of truth for all CV data.
- `reference/`: Locked HTML source-of-truth for the visual design.
- `output/`: Generated HTML and PDF files.
- `src/`: Python source code for the `cv-gen` CLI.
- `Taskfile.yml`: Automation task definitions.

---
