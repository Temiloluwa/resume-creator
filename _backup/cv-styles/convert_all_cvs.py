#!/usr/bin/env python3
"""
Multi-CV HTML to PDF Converter
Converts all three CV style versions to high-quality PDFs
"""

from weasyprint import HTML, CSS
from pathlib import Path
import sys

# CV versions configuration
CV_VERSIONS = [
    {
        'input': 'cv_v1_modern_teal.html',
        'output': 'Temiloluwa_Adeoti_CV_Modern.pdf',
        'name': 'Modern Teal'
    },
    {
        'input': 'cv_v2_editorial.html',
        'output': 'Temiloluwa_Adeoti_CV_Editorial.pdf',
        'name': 'Editorial Burgundy'
    },
    {
        'input': 'cv_v3_tech_dark.html',
        'output': 'Temiloluwa_Adeoti_CV_Tech.pdf',
        'name': 'Tech Dark'
    }
]

def convert_html_to_pdf(html_file, output_file, version_name):
    """
    Convert HTML file to PDF with print optimization
    
    Args:
        html_file (str): Path to the HTML file
        output_file (str): Path for the output PDF file
        version_name (str): Name of the CV version for logging
    """
    if not Path(html_file).exists():
        print(f"❌ {version_name}: File not found - {html_file}")
        return False
    
    print(f"🔄 Converting {version_name}...")
    
    # Additional CSS for better PDF rendering
    additional_css = CSS(string='''
        @page {
            size: A4;
            margin: 0;
        }
        
        body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        /* Ensure dark backgrounds print */
        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    ''')
    
    try:
        # Convert HTML to PDF
        HTML(filename=html_file).write_pdf(
            output_file,
            stylesheets=[additional_css]
        )
        
        file_size = Path(output_file).stat().st_size / 1024
        print(f"✅ {version_name}: PDF created successfully")
        print(f"   → {output_file} ({file_size:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"❌ {version_name}: Conversion failed")
        print(f"   Error: {str(e)}")
        return False

def convert_single(version_index):
    """Convert a single CV version"""
    if version_index < 0 or version_index >= len(CV_VERSIONS):
        print(f"❌ Invalid version index. Choose 0-{len(CV_VERSIONS)-1}")
        return False
    
    version = CV_VERSIONS[version_index]
    return convert_html_to_pdf(
        version['input'],
        version['output'],
        version['name']
    )

def convert_all():
    """Convert all CV versions"""
    print("=" * 60)
    print("CV HTML to PDF Converter - All Versions")
    print("=" * 60)
    print()
    
    results = []
    for version in CV_VERSIONS:
        success = convert_html_to_pdf(
            version['input'],
            version['output'],
            version['name']
        )
        results.append(success)
        print()
    
    print("=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    
    successful = sum(results)
    total = len(results)
    
    for i, (version, success) in enumerate(zip(CV_VERSIONS, results)):
        status = "✅" if success else "❌"
        print(f"{status} {version['name']}: {version['output']}")
    
    print()
    print(f"Successfully converted: {successful}/{total}")
    
    if successful == total:
        print("\n🎉 All CVs converted successfully!")
        print("\nNext steps:")
        print("1. Review each PDF to ensure correct formatting")
        print("2. Verify exactly 2 pages per CV")
        print("3. Choose the best version for each application")
    elif successful > 0:
        print("\n⚠️  Some conversions failed. Check errors above.")
    else:
        print("\n❌ All conversions failed. Ensure WeasyPrint is installed:")
        print("   pip install weasyprint")
    
    return successful == total

def show_help():
    """Display help information"""
    print("""
CV HTML to PDF Converter
========================

Usage:
    python convert_all_cvs.py [option]

Options:
    (no args)    Convert all CV versions
    --all        Convert all CV versions
    --v1         Convert Modern Teal version only
    --v2         Convert Editorial version only
    --v3         Convert Tech Dark version only
    --help       Show this help message

Examples:
    python convert_all_cvs.py          # Convert all versions
    python convert_all_cvs.py --v1     # Convert only Modern Teal
    python convert_all_cvs.py --help   # Show help

Available Versions:
    """)
    
    for i, version in enumerate(CV_VERSIONS, 1):
        print(f"    {i}. {version['name']}")
        print(f"       Input:  {version['input']}")
        print(f"       Output: {version['output']}")
        print()

if __name__ == "__main__":
    # Check for WeasyPrint
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        print("❌ WeasyPrint is not installed!")
        print("\nInstall it with:")
        print("   pip install weasyprint")
        print("\nOr use browser printing:")
        print("   1. Open HTML file in Chrome/Firefox")
        print("   2. Press Ctrl+P (Cmd+P on Mac)")
        print("   3. Save as PDF with 'Background graphics' enabled")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h', 'help']:
            show_help()
        elif arg in ['--all', 'all']:
            convert_all()
        elif arg == '--v1':
            convert_single(0)
        elif arg == '--v2':
            convert_single(1)
        elif arg == '--v3':
            convert_single(2)
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Run with --help to see available options")
    else:
        # No arguments - convert all
        convert_all()
