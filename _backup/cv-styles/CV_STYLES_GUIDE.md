# CV Collection - Three Professional Styles

This package contains your CV in three distinct professional styles, each optimized for 2-page PDF output.

## 📄 The Three Versions

### Version 1: Modern Teal
**File:** `cv_v1_modern_teal.html`

**Style Characteristics:**
- Clean, professional corporate design
- Teal (#14b8a6) accent color
- Inter font family
- Traditional layout with clear sections
- Balanced white space

**Best For:**
- Traditional corporate roles
- Consulting positions
- Established tech companies
- Finance and insurance sectors

---

### Version 2: Editorial Burgundy
**File:** `cv_v2_editorial.html`

**Style Characteristics:**
- Elegant magazine/editorial aesthetic
- Burgundy (#5C1A1A) and gold (#B8860B) color scheme
- Playfair Display (serif) and Lora fonts
- Sophisticated typography with generous spacing
- Refined, luxury feel

**Best For:**
- Senior/executive positions
- Creative leadership roles
- Premium consulting firms
- Positions where design sensibility matters
- European companies with traditional values

---

### Version 3: Tech Dark
**File:** `cv_v3_tech_dark.html`

**Style Characteristics:**
- Futuristic dark theme
- Cyan (#00fff9) and purple (#a855f7) neon accents
- Outfit and JetBrains Mono fonts
- Geometric patterns and grid elements
- Tech-forward, modern aesthetic

**Best For:**
- Tech startups and scale-ups
- Modern software companies
- AI/ML specific roles
- Developer-focused positions
- Innovation-driven organizations

---

## 🎨 Visual Comparison

| Feature | Modern Teal | Editorial Burgundy | Tech Dark |
|---------|-------------|-------------------|-----------|
| **Primary Color** | Teal | Burgundy/Gold | Cyan/Purple |
| **Background** | White | Cream | Dark (#0a0a0a) |
| **Typography** | Sans-serif | Serif | Mono + Sans |
| **Mood** | Professional | Elegant | Cutting-edge |
| **Formality** | Medium-High | High | Medium |
| **Age Range** | All | 35+ preferred | Under 45 |

---

## 🔄 Converting to PDF

### Quick Method (Browser)
1. Open any HTML file in Chrome/Firefox
2. Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac)
3. Settings:
   - Destination: "Save as PDF"
   - Paper size: A4
   - Margins: None
   - Background graphics: **ON** (critical!)
   - Scale: 100%
4. Save

**Special Note for Dark Theme (v3):**
- Ensure "Background graphics" is enabled to preserve dark background
- Some browsers may show white in preview - this is normal, final PDF will be correct

### Python Method (Best Quality)
```bash
# Install weasyprint
pip install weasyprint

# Run conversion script
python convert_all_cvs.py
```

This will generate:
- `Temiloluwa_Adeoti_CV_Modern.pdf`
- `Temiloluwa_Adeoti_CV_Editorial.pdf`
- `Temiloluwa_Adeoti_CV_Tech.pdf`

---

## ✏️ Customization Guide

### Changing Colors

**Version 1 (Teal):**
Find and replace `#14b8a6` with your color

**Version 2 (Burgundy/Gold):**
Modify CSS variables at top of `<style>`:
```css
--burgundy: #5C1A1A;  /* Change this */
--gold: #B8860B;       /* Change this */
```

**Version 3 (Dark):**
Modify CSS variables:
```css
--cyan: #00fff9;       /* Change this */
--purple: #a855f7;     /* Change this */
```

### Changing Fonts

**Version 1:** Replace `Inter` in the `@import` URL and CSS
**Version 2:** Replace `Playfair Display` and `Lora`
**Version 3:** Replace `Outfit` and `JetBrains Mono`

Example:
```css
/* Change this line: */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* To this: */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;600;700&display=swap');

/* Then update font-family references */
font-family: 'Roboto', sans-serif;
```

### Adjusting Content Spacing

If content overflows to 3 pages or doesn't fill 2 pages:

**Reduce spacing (to fit more):**
```css
.page { padding: 35px 45px; }  /* Reduce from 40px 50px */
.section-heading { margin-top: 20px; }  /* Reduce from 25px */
```

**Increase spacing (to fill pages):**
```css
.page { padding: 50px 60px; }  /* Increase padding */
.section-heading { margin-top: 35px; }  /* Increase margins */
```

---

## 🎯 Which Version Should You Use?

### Use Modern Teal (v1) if:
- You're applying to traditional corporations
- You want universal appeal
- The role is client-facing
- Company culture is formal/conservative

### Use Editorial Burgundy (v2) if:
- You're targeting senior positions
- You want to stand out in traditional industries
- The company values design and aesthetics
- You're applying to European firms

### Use Tech Dark (v3) if:
- You're applying to tech startups
- The role is highly technical (ML/Data Science)
- Company has a modern, innovative culture
- You want to showcase your tech-forward mindset

**Pro Tip:** Keep all three versions ready and choose based on the specific company/role!

---

## 📐 Logo Customization

All versions include SVG logos. To update logos with your own:

### Option 1: Keep SVG (Recommended)
Edit the `<svg>` elements directly with company colors

### Option 2: Use Image Files
Replace SVG with:
```html
<img src="company_logo.png" alt="Company" class="company-logo">
```

Place image files in same directory as HTML

---

## 🔧 Technical Specifications

- **Page Size:** A4 (210mm × 297mm)
- **Page Count:** Exactly 2 pages
- **File Format:** HTML5 with embedded CSS
- **Print Optimization:** @page and @media print rules included
- **Font Loading:** Google Fonts CDN
- **Browser Support:** All modern browsers

---

## 📱 Responsive Behavior

While optimized for print/PDF:
- Version 1 & 2: Maintain layout on screens
- Version 3 (Dark): Best in dark mode browsers

---

## 🚀 Quick Start

1. **Choose your version** based on target role/company
2. **Open in browser** to preview
3. **Make any edits** directly in HTML
4. **Convert to PDF** using browser or Python script
5. **Verify** that it's exactly 2 pages

---

## 📋 Checklist Before Sending

- [ ] Content is current and accurate
- [ ] No typos or grammatical errors
- [ ] PDF is exactly 2 pages
- [ ] Colors display correctly
- [ ] All text is readable (especially dark theme)
- [ ] Links work (if PDF supports them)
- [ ] Filename is professional: `Firstname_Lastname_CV.pdf`

---

## 🎨 Advanced: Creating Your Own Style

Want to create a 4th version? Follow these principles:

1. **Choose a dominant color** (avoid purple gradients!)
2. **Pick 2 complementary fonts** (display + body)
3. **Commit to an aesthetic**: minimal, maximal, organic, geometric, etc.
4. **Use CSS variables** for easy color changes
5. **Test print early and often**
6. **Maintain 2-page constraint**

---

## 💾 File Organization

```
cv-collection/
├── cv_v1_modern_teal.html
├── cv_v2_editorial.html
├── cv_v3_tech_dark.html
├── convert_all_cvs.py
├── browser_helper.js
└── README.md
```

---

## 🤝 Support

If you encounter issues:
- **Spacing problems:** Adjust padding/margins in CSS
- **Color not showing:** Enable "Background graphics" in print
- **Font not loading:** Check internet connection
- **Too many pages:** Reduce font sizes by 1px globally

---

## 📄 License

These CV templates are free to use and modify for personal use.

---

**Ready to make an impression? Choose your style and convert to PDF!**
