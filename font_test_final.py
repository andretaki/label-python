"""Generate final font comparison samples."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT_DIR = Path("/home/andre/label-python/output")
FONTS_DIR = Path("/home/andre/label-python/fonts")

FONTS = {
    "Barlow": ("Barlow-Regular.ttf", "Barlow-Bold.ttf"),
    "BarlowCondensed": ("BarlowCondensed-Regular.ttf", "BarlowCondensed-Bold.ttf"),
    "IBMPlexSans": ("IBMPlexSans-Regular.ttf", "IBMPlexSans-Bold.ttf"),
    "IBMPlexMono": ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Bold.ttf"),
    "TitilliumWeb": ("TitilliumWeb-Regular.ttf", "TitilliumWeb-Bold.ttf"),
    "JetBrainsMono": ("JetBrainsMono-Regular.ttf", "JetBrainsMono-Bold.ttf"),
}

def generate_sample(font_name, reg_font, bold_font):
    width, height = 432, 288
    output_path = OUTPUT_DIR / f"font-test-{font_name}.pdf"
    
    c = canvas.Canvas(str(output_path), pagesize=(width, height))
    
    c.setFillColor(Color(0, 180/255, 150/255))
    c.rect(0, height - 44, width, 44, fill=1, stroke=0)
    c.setFillColor(Color(1, 1, 1))
    c.setFont(bold_font, 14)
    c.drawString(20, height - 28, f"Font: {font_name}")
    
    y = height - 70
    
    c.setFillColor(Color(0, 0, 0))
    c.setFont(bold_font, 16)
    c.drawString(20, y, "Isopropyl Alcohol")
    y -= 20
    
    c.setFont(reg_font, 10)
    c.setFillColor(Color(0.3, 0.3, 0.3))
    c.drawString(20, y, "99% ACS Reagent Grade")
    y -= 25
    
    c.setFont(reg_font, 7)
    c.setFillColor(Color(0.5, 0.5, 0.5))
    c.drawString(20, y, "SKU")
    y -= 10
    c.setFont(bold_font, 11)
    c.setFillColor(Color(0, 0, 0))
    c.drawString(20, y, "AC-IPA-99-55")
    y -= 18
    
    c.setFont(reg_font, 7)
    c.setFillColor(Color(0.5, 0.5, 0.5))
    c.drawString(20, y, "CAS-No: 67-63-0  |  LOT: TEST-001")
    y -= 18
    
    c.setFont(bold_font, 9)
    c.setFillColor(Color(0.8, 0, 0))
    c.drawString(20, y, "DANGER")
    y -= 14
    
    c.setFont(reg_font, 6)
    c.setFillColor(Color(0, 0, 0))
    h_text = "H225: Highly flammable liquid and vapor. H319: Causes serious eye irritation. H336: May cause drowsiness or dizziness."
    
    words = h_text.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if pdfmetrics.stringWidth(test, reg_font, 6) < 390:
            line = test
        else:
            c.drawString(20, y, line)
            y -= 8
            line = word
    if line:
        c.drawString(20, y, line)
    y -= 12
    
    c.setFillColor(Color(0.15, 0.15, 0.15))
    c.setFont(reg_font, 5)
    p_text = "Keep away from heat, sparks, open flames, hot surfaces. No smoking. Keep container tightly closed. Ground and bond container and receiving equipment. Use explosion-proof electrical, ventilating, and lighting equipment. Use non-sparking tools. Take action to prevent static discharges. Wash hands thoroughly after handling. Wear protective gloves, eye protection, face protection. See SDS for complete precautionary information."
    
    words = p_text.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if pdfmetrics.stringWidth(test, reg_font, 5) < 390:
            line = test
        else:
            c.drawString(20, y, line)
            y -= 6.5
            line = word
    if line:
        c.drawString(20, y, line)
    
    c.setFillColor(Color(0.1, 0.1, 0.12))
    c.rect(0, 0, width, 24, fill=1, stroke=0)
    c.setFillColor(Color(0, 0.7, 0.55))
    c.setFont(bold_font, 7)
    c.drawString(10, 9, "Emergency:")
    c.setFillColor(Color(0.9, 0.9, 0.9))
    c.setFont(reg_font, 7)
    c.drawString(55, 9, "CHEMTEL 1-800-255-3924")
    
    c.save()
    print(f"✓ {font_name}")

print("=== Industrial/Technical Fonts ===\n")

for name, (reg_file, bold_file) in FONTS.items():
    reg_path = FONTS_DIR / reg_file
    bold_path = FONTS_DIR / bold_file
    
    if reg_path.exists() and bold_path.exists():
        try:
            pdfmetrics.registerFont(TTFont(f"{name}-Reg", str(reg_path)))
            pdfmetrics.registerFont(TTFont(f"{name}-Bold", str(bold_path)))
            generate_sample(name, f"{name}-Reg", f"{name}-Bold")
        except Exception as e:
            print(f"✗ {name}: {e}")

print("\n" + "="*50)
print("TOP PICKS FOR CHEMICAL LABELS:")
print("="*50)
print("1. Barlow         - Industrial, fits well")
print("2. BarlowCondensed - Fits MORE text (dense P-statements)")
print("3. IBMPlexSans    - Technical documentation feel")
print("4. TitilliumWeb   - Space agency / tech vibe")
print("5. JetBrainsMono  - Great for SKU/LOT/CAS codes")
print("\nCheck output/font-test-*.pdf")
