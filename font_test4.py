"""Download and test industrial/technical fonts."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import urllib.request

OUTPUT_DIR = Path("/home/andre/label-python/output")
FONTS_DIR = Path("/home/andre/label-python/fonts")
FONTS_DIR.mkdir(exist_ok=True)

# Industrial/Technical fonts from Google Fonts
FONTS_TO_DOWNLOAD = {
    # Top picks
    "Inter": {
        "regular": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.ttf",
        "bold": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.ttf",
    },
    "IBMPlexSans": {
        "regular": "https://github.com/IBM/plex/raw/master/IBM-Plex-Sans/fonts/complete/ttf/IBMPlexSans-Regular.ttf",
        "bold": "https://github.com/IBM/plex/raw/master/IBM-Plex-Sans/fonts/complete/ttf/IBMPlexSans-Bold.ttf",
    },
    "Barlow": {
        "regular": "https://github.com/jpt/barlow/raw/main/fonts/ttf/Barlow-Regular.ttf",
        "bold": "https://github.com/jpt/barlow/raw/main/fonts/ttf/Barlow-Bold.ttf",
    },
    "BarlowCondensed": {
        "regular": "https://github.com/jpt/barlow/raw/main/fonts/ttf/BarlowCondensed-Regular.ttf",
        "bold": "https://github.com/jpt/barlow/raw/main/fonts/ttf/BarlowCondensed-Bold.ttf",
    },
    # Industrial
    "TitilliumWeb": {
        "regular": "https://github.com/google/fonts/raw/main/ofl/titilliumweb/TitilliumWeb-Regular.ttf",
        "bold": "https://github.com/google/fonts/raw/main/ofl/titilliumweb/TitilliumWeb-Bold.ttf",
    },
    "Exo2": {
        "regular": "https://github.com/google/fonts/raw/main/ofl/exo2/Exo2%5Bwght%5D.ttf",
        "bold": "https://github.com/google/fonts/raw/main/ofl/exo2/Exo2%5Bwght%5D.ttf",
    },
    "Rajdhani": {
        "regular": "https://github.com/AkhileshYadav/Rajdhani/raw/master/fonts/ttf/Rajdhani-Regular.ttf",
        "bold": "https://github.com/AkhileshYadav/Rajdhani/raw/master/fonts/ttf/Rajdhani-Bold.ttf",
    },
    "Archivo": {
        "regular": "https://github.com/Omnibus-Type/Archivo/raw/main/fonts/ttf/Archivo-Regular.ttf",
        "bold": "https://github.com/Omnibus-Type/Archivo/raw/main/fonts/ttf/Archivo-Bold.ttf",
    },
    # Monospace for codes
    "JetBrainsMono": {
        "regular": "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Regular.ttf",
        "bold": "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/JetBrainsMono-Bold.ttf",
    },
    "IBMPlexMono": {
        "regular": "https://github.com/IBM/plex/raw/master/IBM-Plex-Mono/fonts/complete/ttf/IBMPlexMono-Regular.ttf",
        "bold": "https://github.com/IBM/plex/raw/master/IBM-Plex-Mono/fonts/complete/ttf/IBMPlexMono-Bold.ttf",
    },
    "SpaceMono": {
        "regular": "https://github.com/googlefonts/spacemono/raw/main/fonts/SpaceMono-Regular.ttf",
        "bold": "https://github.com/googlefonts/spacemono/raw/main/fonts/SpaceMono-Bold.ttf",
    },
}

def download_font(name, url, suffix):
    path = FONTS_DIR / f"{name}-{suffix}.ttf"
    if not path.exists():
        try:
            urllib.request.urlretrieve(url, path)
            return path
        except Exception as e:
            print(f"  Failed to download {name}-{suffix}: {e}")
            return None
    return path

def generate_sample(font_name, reg_font, bold_font):
    width, height = 432, 288
    output_path = OUTPUT_DIR / f"font-test-{font_name}.pdf"
    
    c = canvas.Canvas(str(output_path), pagesize=(width, height))
    
    # Header
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
    
    # Footer
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

print("=== Downloading Industrial/Technical Fonts ===\n")

for name, urls in FONTS_TO_DOWNLOAD.items():
    reg_path = download_font(name, urls["regular"], "Regular")
    bold_path = download_font(name, urls["bold"], "Bold")
    
    if reg_path and bold_path:
        try:
            pdfmetrics.registerFont(TTFont(f"{name}-Regular", str(reg_path)))
            # For variable fonts, bold might be same file
            if reg_path != bold_path:
                pdfmetrics.registerFont(TTFont(f"{name}-Bold", str(bold_path)))
                generate_sample(name, f"{name}-Regular", f"{name}-Bold")
            else:
                generate_sample(name, f"{name}-Regular", f"{name}-Regular")
        except Exception as e:
            print(f"✗ {name}: {e}")

print("\n=== TOP RECOMMENDATIONS ===")
print("1. Inter - Best overall, extremely legible")
print("2. IBM Plex Sans - Industrial/technical feel")
print("3. Barlow - Fits more text, industrial")
print("4. BarlowCondensed - Even denser text")
print("\nCheck output/font-test-*.pdf files!")
