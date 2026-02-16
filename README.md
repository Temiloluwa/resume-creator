# Resume Creator

A Python-based tool to generate a professional PDF CV from HTML using Playwright.

## Project Structure

-   `src/`: Source code.
    -   `index.html`: The CV content and styling. Edit this file to update your CV.
    -   `generate_pdf.py`: Python script to convert the HTML to PDF.
-   `data/`: Input data and reference files.
    -   `cv-info.txt`: Original text content.
    -   `AdeotiMachineDataScienceFullCV.pdf`: Reference PDF.
-   `output/`: Generated artifacts.
    -   `Temiloluwa_Adeoti_CV.pdf`: The final generated CV.

## Setup

1.  **Install Dependencies**:
    This project uses `uv` for dependency management.
    ```bash
    uv sync
    ```

2.  **Install Playwright Browsers**:
    ```bash
    uv run playwright install chromium
    ```

## Usage

To generate the PDF CV:

```bash
uv run src/generate_pdf.py
```

The output file will be saved to `output/Temiloluwa_Adeoti_CV.pdf`.

## Customization

To update your CV content or change the styling, simply edit `src/index.html`. You can open this file in your browser to preview changes before generating the PDF.
