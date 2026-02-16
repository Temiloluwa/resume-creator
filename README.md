# Resume Creator

Generate three CV variants from a single YAML source file.

## Source of truth

- Content YAML: `/Users/david/codes-and-scripts/playground/resume-creator/cv-content.yaml`
- Style HTML sources:
  - `/Users/david/codes-and-scripts/playground/resume-creator/_backup/cv-styles/cv_v1_modern_teal.html`
  - `/Users/david/codes-and-scripts/playground/resume-creator/_backup/cv-styles/cv_v2_editorial.html`
  - `/Users/david/codes-and-scripts/playground/resume-creator/_backup/cv-styles/cv_v3_tech_dark.html`
- Logos: `/Users/david/codes-and-scripts/playground/resume-creator/data/logos` (PNG with transparency)

## Output

Generated into `/Users/david/codes-and-scripts/playground/resume-creator/output`:

- `cv_v1_modern_teal.html`
- `cv_v2_editorial.html`
- `cv_v3_tech_dark.html`
- `Temiloluwa_Adeoti_CV_v1_modern_teal.pdf`
- `Temiloluwa_Adeoti_CV_v2_editorial.pdf`
- `Temiloluwa_Adeoti_CV_v3_tech_dark.pdf`

## Build

```bash
task install
```

```bash
task build
```

Optional:

```bash
task clean
```

## Guarantees enforced by build

- A4 page format for every PDF
- Maximum 2 pages per PDF (`--max-pages 2`)
- Automatic overflow-aware print scaling to prevent cropped content
- Build fails if any PDF exceeds page limit
