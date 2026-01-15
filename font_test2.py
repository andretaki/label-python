"""Test system fonts + show package options."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT_DIR = Path("/home/andre/label-python/output")

# System fonts we can use
SYSTEM_FONTS = {
    "Ubuntu": ("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"),
    "UbuntuMono": ("/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf", "/usr/share/fonts/truetype/ubuntu/UbuntuMono-B.ttf"),
    "Liberation": ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    "LiberationSerif": ("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"),
    "DejaVuSans": ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    "DejaVuSerif": ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
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
    
    # Title
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
    p_text = "Keep away from heat, sparks, open flames, hot surfaces. No smoking. Keep container tightly closed. Ground and bond container and receiving equipment. Use explosion-proof equipment."
    
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
    c.setFont(font_bold, 7)
    c.drawString(10, 9, "Emergency:")
    c.setFillColor(Color(0.9, 0.9, 0.9))
    c.setFont(font_regular, 7)
    c.drawString(55, 9, "CHEMTEL 1-800-255-3924")
    
    c.save()
    print(f"✓ {output_path.name}")

print("=== System Fonts ===")
for name, (regular_path, bold_path) in SYSTEM_FONTS.items():
    if Path(regular_path).exists() and Path(bold_path).exists():
        try:
            pdfmetrics.registerFont(TTFont(f"{name}-Regular", regular_path))
            pdfmetrics.registerFont(TTFont(f"{name}-Bold", bold_path))
            generate_font_sample(name, f"{name}-Regular", f"{name}-Bold")
        except Exception as e:
            print(f"✗ {name}: {e}")
    else:
        print(f"✗ {name}: files not found")

print("\nAll font samples in output/font-test-*.pdf")
