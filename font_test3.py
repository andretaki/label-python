"""Test newly installed fonts."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import subprocess

OUTPUT_DIR = Path("/home/andre/label-python/output")

# Find the new fonts
def find_font(name):
    """Find font path using fc-match."""
    try:
        result = subprocess.run(['fc-match', '-f', '%{file}', name], capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return None

# New system fonts
NEW_FONTS = {
    "Roboto-System": ("Roboto:style=Regular", "Roboto:style=Bold"),
    "Lato-System": ("Lato:style=Regular", "Lato:style=Bold"),
    "OpenSans-System": ("Open Sans:style=Regular", "Open Sans:style=Bold"),
    "FiraCode": ("Fira Code:style=Regular", "Fira Code:style=Bold"),
}

def generate_font_sample(font_name, font_regular, font_bold):
    width, height = 432, 288
    output_path = OUTPUT_DIR / f"font-test-{font_name}.pdf"
    
    c = canvas.Canvas(str(output_path), pagesize=(width, height))
    
    # Header
    c.setFillColor(Color(0, 180/255, 150/255))
    c.rect(0, height - 44, width, 44, fill=1, stroke=0)
    c.setFillColor(Color(1, 1, 1))
    c.setFont(font_bold, 14)
    c.drawString(20, height - 28, f"Font: {font_name}")
    
    y = height - 70
    
    c.setFillColor(Color(0, 0, 0))
    c.setFont(font_bold, 16)
    c.drawString(20, y, "Isopropyl Alcohol")
    y -= 20
    
    c.setFont(font_regular, 10)
    c.setFillColor(Color(0.3, 0.3, 0.3))
    c.drawString(20, y, "99% ACS Reagent Grade")
    y -= 25
    
    c.setFont(font_regular, 7)
    c.setFillColor(Color(0.5, 0.5, 0.5))
    c.drawString(20, y, "SKU")
    y -= 10
    c.setFont(font_bold, 11)
    c.setFillColor(Color(0, 0, 0))
    c.drawString(20, y, "AC-IPA-99-55")
    y -= 20
    
    c.setFont(font_bold, 9)
    c.setFillColor(Color(0.8, 0, 0))
    c.drawString(20, y, "DANGER")
    y -= 15
    
    c.setFont(font_regular, 6)
    c.setFillColor(Color(0, 0, 0))
    sample_text = "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation. H336: May cause drowsiness or dizziness."
    
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
    
    c.setFillColor(Color(0.2, 0.2, 0.2))
    c.setFont(font_regular, 5)
    p_text = "Keep away from heat, sparks, open flames, hot surfaces. No smoking. Keep container tightly closed. Ground and bond container. Use explosion-proof equipment. Wash hands thoroughly after handling."
    
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
    
    c.setFillColor(Color(0.1, 0.1, 0.12))
    c.rect(0, 0, width, 24, fill=1, stroke=0)
    c.setFillColor(Color(0, 0.7, 0.55))
    c.setFont(font_bold, 7)
    c.drawString(10, 9, "Emergency:")
    c.setFillColor(Color(0.9, 0.9, 0.9))
    c.setFont(font_regular, 7)
    c.drawString(55, 9, "CHEMTEL 1-800-255-3924")
    
    c.save()
    print(f"✓ {output_path.name}")

print("=== Newly Installed Fonts ===\n")

for name, (reg_query, bold_query) in NEW_FONTS.items():
    reg_path = find_font(reg_query)
    bold_path = find_font(bold_query)
    
    if reg_path and bold_path and Path(reg_path).exists() and Path(bold_path).exists():
        try:
            pdfmetrics.registerFont(TTFont(f"{name}-Regular", reg_path))
            pdfmetrics.registerFont(TTFont(f"{name}-Bold", bold_path))
            generate_font_sample(name, f"{name}-Regular", f"{name}-Bold")
            print(f"   Regular: {reg_path}")
            print(f"   Bold: {bold_path}\n")
        except Exception as e:
            print(f"✗ {name}: {e}\n")
    else:
        print(f"✗ {name}: not found")
        print(f"   Tried: {reg_path}, {bold_path}\n")

print("\n=== All Available Test PDFs ===")
for f in sorted(OUTPUT_DIR.glob("font-test-*.pdf")):
    print(f"  {f.name}")
