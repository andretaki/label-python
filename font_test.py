"""Generate test labels with different fonts."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import urllib.request
import os

OUTPUT_DIR = Path("/home/andre/label-python/output")
FONTS_DIR = Path("/home/andre/label-python/fonts")
FONTS_DIR.mkdir(exist_ok=True)

# Download Google Fonts
GOOGLE_FONTS = {
    "Roboto": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf",
    "Lato": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf", 
    "OpenSans": "https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans%5Bwdth%2Cwght%5D.ttf",
    "SourceSansPro": "https://github.com/google/fonts/raw/main/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf",
    "Nunito": "https://github.com/google/fonts/raw/main/ofl/nunito/Nunito%5Bwght%5D.ttf",
    "Poppins": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
}

def download_fonts():
    """Download Google Fonts."""
    for name, url in GOOGLE_FONTS.items():
        path = FONTS_DIR / f"{name}.ttf"
        if not path.exists():
            print(f"Downloading {name}...")
            try:
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"  Failed: {e}")

def generate_font_sample(font_name, font_regular, font_bold=None):
    """Generate a sample label with given font."""
    width, height = 432, 288
    output_path = OUTPUT_DIR / f"font-test-{font_name}.pdf"
    
    c = canvas.Canvas(str(output_path), pagesize=(width, height))
    
    # Header
    c.setFillColor(Color(0, 180/255, 150/255))
    c.rect(0, height - 44, width, 44, fill=1, stroke=0)
    
    # Font name in header
    c.setFillColor(Color(1, 1, 1))
    c.setFont(font_bold or font_regular, 14)
    c.drawString(20, height - 28, f"Font: {font_name}")
    
    # Sample content
    y = height - 70
    
    # Title
    c.setFillColor(Color(0, 0, 0))
    c.setFont(font_bold or font_regular, 16)
    c.drawString(20, y, "Isopropyl Alcohol")
    y -= 20
    
    # Subtitle
    c.setFont(font_regular, 10)
    c.setFillColor(Color(0.3, 0.3, 0.3))
    c.drawString(20, y, "99% ACS Reagent Grade")
    y -= 25
    
    # Labels
    c.setFont(font_regular, 7)
    c.setFillColor(Color(0.5, 0.5, 0.5))
    c.drawString(20, y, "SKU")
    y -= 10
    c.setFont(font_bold or font_regular, 11)
    c.setFillColor(Color(0, 0, 0))
    c.drawString(20, y, "AC-IPA-99-55")
    y -= 20
    
    # Hazard text sample
    c.setFont(font_bold or font_regular, 9)
    c.setFillColor(Color(0.8, 0, 0))
    c.drawString(20, y, "DANGER")
    y -= 15
    
    c.setFont(font_regular, 6)
    c.setFillColor(Color(0, 0, 0))
    sample_text = "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation. H336: May cause drowsiness or dizziness."
    
    # Word wrap
    words = sample_text.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if pdfmetrics.stringWidth(test, font_regular, 6) < 390:
            line = test
        else:
            c.drawString(20, y, line)
            y -= 8
            line = word
    if line:
        c.drawString(20, y, line)
    y -= 15
    
    # P-statements
    c.setFillColor(Color(0.2, 0.2, 0.2))
    p_text = "Keep away from heat, sparks, open flames, hot surfaces. No smoking. Keep container tightly closed. Ground and bond container and receiving equipment. Use explosion-proof electrical, ventilating, and lighting equipment."
    
    words = p_text.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if pdfmetrics.stringWidth(test, font_regular, 5) < 390:
            line = test
        else:
            c.drawString(20, y, line)
            y -= 7
            line = word
    if line:
        c.drawString(20, y, line)
    
    # Footer
    c.setFillColor(Color(0.1, 0.1, 0.12))
    c.rect(0, 0, width, 24, fill=1, stroke=0)
    c.setFillColor(Color(0, 0.7, 0.55))
    c.setFont(font_bold or font_regular, 7)
    c.drawString(10, 9, "Emergency:")
    c.setFillColor(Color(0.9, 0.9, 0.9))
    c.setFont(font_regular, 7)
    c.drawString(55, 9, "CHEMTEL 1-800-255-3924")
    
    c.save()
    print(f"Generated: {output_path}")

# Generate built-in font samples
print("=== Built-in Fonts ===")
generate_font_sample("Helvetica", "Helvetica", "Helvetica-Bold")
generate_font_sample("Times-Roman", "Times-Roman", "Times-Bold")
generate_font_sample("Courier", "Courier", "Courier-Bold")

# Download and test Google Fonts
print("\n=== Downloading Google Fonts ===")
download_fonts()

print("\n=== Google Fonts ===")
for name in GOOGLE_FONTS.keys():
    path = FONTS_DIR / f"{name}.ttf"
    if path.exists():
        try:
            pdfmetrics.registerFont(TTFont(name, str(path)))
            generate_font_sample(name, name, name)
        except Exception as e:
            print(f"Failed to use {name}: {e}")

print("\n✓ Done! Check output/ folder for font-test-*.pdf files")
