#!/usr/bin/env python3
"""
HTML to PDF Converter for CV
Uses Playwright to convert the HTML CV to a high-quality PDF
"""

from playwright.sync_api import sync_playwright
import os
from pathlib import Path

def convert_html_to_pdf(html_file, output_file):
    """
    Convert HTML file to PDF using Playwright
    
    Args:
        html_file (str): Path to the HTML file
        output_file (str): Path for the output PDF file
    """
    print(f"Converting {html_file} to PDF...")
    
    abs_html_path = os.path.abspath(html_file)
    abs_output_path = os.path.abspath(output_file)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Open the HTML file
        page.goto(f"file://{abs_html_path}")
        
        # Wait for fonts/content to load if necessary
        # page.wait_for_load_state('networkidle') 
        
        # Generate PDF
        page.pdf(
            path=abs_output_path,
            format="A4",
            print_background=True,
            margin={"top": "0cm", "right": "0cm", "bottom": "0cm", "left": "0cm"}
        )
        
        browser.close()
    
    print(f"✓ PDF created successfully: {output_file}")
    file_size = Path(output_file).stat().st_size / 1024
    print(f"  File size: {file_size:.1f} KB")

if __name__ == "__main__":
    # File paths
    html_file = "src/index.html"
    output_file = "output/Temiloluwa_Adeoti_CV.pdf"
    
    # Convert
    convert_html_to_pdf(html_file, output_file)
