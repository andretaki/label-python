"""Scientific-style label renderer (Sigma-Aldrich style).

Key characteristics:
- 3-column layout
- Solid color header (no gradient)
- Standard GHS pictograms (no decorative cards)
- Dense 5pt text for ALL statements
- White background, minimal effects
- Barlow Condensed font for industrial feel
"""

from pathlib import Path

from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from src.components.ghs import draw_ghs_pictograms_standard
from src.components.nfpa import draw_nfpa_diamond
from src.components.qrcode import draw_qr_code
from src.config import (
    ASSETS_DIR,
    COMPANY_INFO,
    LABEL_HEIGHT,
    LABEL_WIDTH,
    OUTPUT_DIR,
    PROJECT_ROOT,
    SCIENTIFIC_COL1_WIDTH_PCT,
    SCIENTIFIC_COL2_WIDTH_PCT,
    SCIENTIFIC_COL3_WIDTH_PCT,
    SCIENTIFIC_COLUMN_GAP,
    SCIENTIFIC_FONT_SIZES,
    SCIENTIFIC_FOOTER_COLOR,
    SCIENTIFIC_FOOTER_HEIGHT,
    SCIENTIFIC_GHS_GAP,
    SCIENTIFIC_GHS_SIZE,
    SCIENTIFIC_HEADER_COLOR,
    SCIENTIFIC_HEADER_HEIGHT,
)
from src.models import SKUData
from src.utils.text_fitting import draw_dense_paragraph, wrap_text

# Register custom fonts
FONTS_DIR = PROJECT_ROOT / "fonts"
_fonts_registered = False


def _register_fonts():
    """Register Barlow Condensed + JetBrains Mono fonts (called once)."""
    global _fonts_registered
    if _fonts_registered:
        return

    # Barlow Condensed for body text
    barlow_regular = FONTS_DIR / "BarlowCondensed-Regular.ttf"
    barlow_bold = FONTS_DIR / "BarlowCondensed-Bold.ttf"

    # JetBrains Mono for codes (SKU, LOT, CAS)
    jetbrains_regular = FONTS_DIR / "JetBrainsMono-Regular.ttf"
    jetbrains_bold = FONTS_DIR / "JetBrainsMono-Bold.ttf"

    if barlow_regular.exists() and barlow_bold.exists():
        pdfmetrics.registerFont(TTFont("BarlowCondensed", str(barlow_regular)))
        pdfmetrics.registerFont(TTFont("BarlowCondensed-Bold", str(barlow_bold)))
    else:
        raise FileNotFoundError(f"Barlow Condensed fonts not found in {FONTS_DIR}")

    if jetbrains_regular.exists() and jetbrains_bold.exists():
        pdfmetrics.registerFont(TTFont("JetBrainsMono", str(jetbrains_regular)))
        pdfmetrics.registerFont(TTFont("JetBrainsMono-Bold", str(jetbrains_bold)))

    _fonts_registered = True


# Scientific style fonts
FONTS = {
    "bold": "BarlowCondensed-Bold",
    "regular": "BarlowCondensed",
    "mono": "JetBrainsMono",
    "mono_bold": "JetBrainsMono-Bold",
}


class ScientificLabelRenderer:
    """
    Renders labels in scientific/laboratory style.

    Key features:
    - 3-column layout
    - Solid color header (no gradient)
    - Standard GHS pictograms (no decorative cards)
    - Dense 5pt text for ALL statements
    - White background, minimal effects
    """

    def __init__(self, sku_data: SKUData):
        self.data = sku_data
        self.c = None

        # Register custom fonts
        _register_fonts()

        # Calculate layout
        self.margin = 8
        self.content_width = LABEL_WIDTH - (self.margin * 2)
        self.header_height = SCIENTIFIC_HEADER_HEIGHT
        self.footer_height = SCIENTIFIC_FOOTER_HEIGHT

        # Column positions
        col1_w = self.content_width * SCIENTIFIC_COL1_WIDTH_PCT
        col2_w = self.content_width * SCIENTIFIC_COL2_WIDTH_PCT
        col3_w = self.content_width * SCIENTIFIC_COL3_WIDTH_PCT
        gap = SCIENTIFIC_COLUMN_GAP

        self.col1_left = self.margin
        self.col1_width = col1_w
        self.col2_left = self.col1_left + col1_w + gap
        self.col2_width = col2_w
        self.col3_left = self.col2_left + col2_w + gap
        self.col3_width = col3_w

        # Vertical bounds
        self.header_bottom = LABEL_HEIGHT - self.margin - self.header_height
        self.footer_top = self.margin + self.footer_height
        self.main_top = self.header_bottom - 4
        self.main_bottom = self.footer_top + 4

    def render(self, output_path: Path, lot_number: str = None) -> Path:
        """Render the label to PDF."""
        if lot_number:
            self.data.lot_number = lot_number

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH, LABEL_HEIGHT))

        # Draw all sections
        self._draw_header()
        self._draw_column_1()
        self._draw_column_2()
        self._draw_column_3()
        self._draw_footer()

        self.c.save()
        return output_path

    def _draw_header(self):
        """Solid color header with decorative lines and logo."""
        c = self.c

        # Solid background (NO gradient)
        c.setFillColor(Color(*SCIENTIFIC_HEADER_COLOR))
        c.rect(0, self.header_bottom, LABEL_WIDTH, self.header_height, fill=1, stroke=0)

        # Decorative white vertical lines
        c.setStrokeColor(Color(1, 1, 1))
        c.setLineWidth(1.5)
        for i in range(5):
            x = self.margin + 4 + (i * 8)
            c.line(
                x,
                self.header_bottom + 4,
                x,
                self.header_bottom + self.header_height - 4,
            )

        # Company name
        c.setFont(FONTS["bold"], 11)
        c.setFillColor(Color(1, 1, 1))
        c.drawString(
            self.margin + 50,
            self.header_bottom + self.header_height / 2 - 4,
            COMPANY_INFO["name"],
        )

        # Logo (right side)
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            c.drawImage(
                str(logo_path),
                LABEL_WIDTH - self.margin - 60,
                self.header_bottom + 4,
                width=55,
                height=self.header_height - 8,
                preserveAspectRatio=True,
                mask="auto",
            )

    def _draw_column_1(self):
        """Left column: SKU, lot, CAS, NFPA, QR code."""
        c = self.c
        x = self.col1_left
        y = self.main_top
        sizes = SCIENTIFIC_FONT_SIZES
        col_w = self.col1_width

        # SKU (large, mono bold) - Primary identifier for B2B customers
        c.setFont(FONTS["regular"], 6)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawString(x, y - 6, "SKU")
        y -= 8

        c.setFont(FONTS["mono_bold"], sizes["product_code"])
        c.setFillColor(Color(0, 0, 0))
        c.drawString(x, y - sizes["product_code"], self.data.sku)
        y -= sizes["product_code"] + 8

        # LOT
        if self.data.lot_number:
            c.setFont(FONTS["regular"], 6)
            c.setFillColor(Color(0.4, 0.4, 0.4))
            c.drawString(x, y - 6, "LOT")
            y -= 8

            c.setFont(FONTS["mono"], sizes["lot"])
            c.setFillColor(Color(0, 0, 0))
            c.drawString(x, y - sizes["lot"], self.data.lot_number)
            y -= sizes["lot"] + 6

        # CAS Number
        if self.data.cas_number:
            c.setFont(FONTS["mono"], sizes["cas"])
            c.setFillColor(Color(0, 0, 0))
            c.drawString(x, y - sizes["cas"], f"CAS: {self.data.cas_number}")
            y -= sizes["cas"] + 6

        # UPC/GTIN
        c.setFont(FONTS["mono"], 6)
        c.setFillColor(Color(0.3, 0.3, 0.3))
        c.drawString(x, y - 6, f"UPC: {self.data.upc_gtin12}")
        y -= 12

        # NFPA Diamond (if data available)
        if self.data.has_nfpa:
            nfpa_size = 40
            nfpa_y = y - nfpa_size - 4
            # Center NFPA in column
            nfpa_x = x + (col_w - nfpa_size) / 2
            draw_nfpa_diamond(
                c, nfpa_x, nfpa_y, nfpa_size,
                self.data.nfpa_health or 0,
                self.data.nfpa_fire or 0,
                self.data.nfpa_reactivity or 0,
                self.data.nfpa_special,
            )
            # NFPA label - centered under diamond
            c.setFont(FONTS["regular"], 5)
            c.setFillColor(Color(0.4, 0.4, 0.4))
            c.drawCentredString(nfpa_x + nfpa_size / 2, nfpa_y - 8, "NFPA 704")

        # QR Code at bottom
        qr_size = 48
        qr_y = self.main_bottom + 10
        if self.data.sds_url:
            draw_qr_code(c, self.data.sds_url, x, qr_y, qr_size)
            c.setFont(FONTS["regular"], 5)
            c.setFillColor(Color(0.4, 0.4, 0.4))
            c.drawString(x, qr_y - 7, "Scan for SDS")

    def _draw_column_2(self):
        """Center column: product name, grade, net contents, DOT."""
        c = self.c
        x = self.col2_left
        y = self.main_top
        w = self.col2_width
        sizes = SCIENTIFIC_FONT_SIZES

        # Product Name
        c.setFont(FONTS["bold"], sizes["product_name"])
        c.setFillColor(Color(0, 0, 0))
        lines = wrap_text(self.data.product_name, FONTS["bold"], sizes["product_name"], w)
        for line in lines:
            c.drawString(x, y - sizes["product_name"], line)
            y -= sizes["product_name"] + 2
        y -= 4

        # Grade
        if self.data.grade_or_concentration:
            c.setFont(FONTS["regular"], sizes["grade"])
            c.setFillColor(Color(0.2, 0.2, 0.2))
            c.drawString(x, y - sizes["grade"], self.data.grade_or_concentration)
            y -= sizes["grade"] + 12

        # Separator
        c.setStrokeColor(Color(0.8, 0.8, 0.8))
        c.setLineWidth(0.5)
        c.line(x, y, x + w * 0.7, y)
        y -= 10

        # Net Contents - BIGGER, key selling point
        net_size_us = 18  # Larger than default
        c.setFont(FONTS["bold"], net_size_us)
        c.setFillColor(Color(0, 0, 0))
        c.drawString(x, y - net_size_us, self.data.net_contents_us)
        y -= net_size_us + 2

        c.setFont(FONTS["regular"], sizes["net_contents_metric"])
        c.setFillColor(Color(0.3, 0.3, 0.3))
        c.drawString(x, y - sizes["net_contents_metric"], self.data.net_contents_metric)
        y -= sizes["net_contents_metric"] + 10

        # DOT Info (if applicable) - SIMPLE TEXT, not fancy badge
        if self.data.dot_regulated:
            c.setStrokeColor(Color(0.8, 0.8, 0.8))
            c.line(x, y, x + w * 0.7, y)
            y -= 8

            c.setFont(FONTS["regular"], 8)
            c.setFillColor(Color(0, 0, 0))
            c.drawString(x, y - 8, f"DOT: {self.data.un_number}")
            y -= 10

            if self.data.proper_shipping_name:
                lines = wrap_text(self.data.proper_shipping_name, FONTS["regular"], 7, w)
                c.setFont(FONTS["regular"], 7)
                for line in lines:
                    c.drawString(x, y - 7, line)
                    y -= 9

            pg = self.data.packing_group.value if self.data.packing_group else ""
            c.drawString(x, y - 7, f"Class {self.data.hazard_class}, PG {pg}")
            y -= 10

        # Website at bottom
        c.setFont(FONTS["regular"], 7)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawString(x, self.main_bottom + 4, "alliancechemical.com")

    def _draw_column_3(self):
        """Right column: GHS pictograms, signal word, ALL statements."""
        c = self.c
        x = self.col3_left
        y = self.main_top
        w = self.col3_width
        sizes = SCIENTIFIC_FONT_SIZES

        if not self.data.hazcom_applicable:
            return

        # GHS Pictograms - STANDARD format, no cards
        pictogram_ids = [
            p.value if hasattr(p, "value") else p for p in self.data.ghs_pictograms
        ]

        ghs_height = draw_ghs_pictograms_standard(
            c, pictogram_ids, x, y, size=SCIENTIFIC_GHS_SIZE, gap=SCIENTIFIC_GHS_GAP
        )
        y -= ghs_height + 4

        # Signal Word - LARGER, more prominent
        if self.data.signal_word:
            signal = (
                self.data.signal_word.value
                if hasattr(self.data.signal_word, "value")
                else str(self.data.signal_word)
            )
            signal_size = 12  # Bigger than before (was 8)
            c.setFont(FONTS["bold"], signal_size)
            if signal.upper() == "DANGER":
                c.setFillColor(Color(0.85, 0, 0))
            else:
                c.setFillColor(Color(0.9, 0.5, 0))
            c.drawString(x, y - signal_size, signal.upper())
            y -= signal_size + 2

            # Red underline for DANGER
            if signal.upper() == "DANGER":
                c.setStrokeColor(Color(0.85, 0, 0))
                c.setLineWidth(1.5)
                text_w = stringWidth(signal.upper(), FONTS["bold"], signal_size)
                c.line(x, y, x + text_w, y)
            y -= 6

        # H-Statements (keep codes visible) - slightly larger, bold
        if self.data.hazard_statements:
            h_size = 6  # Larger than P-statements
            y = draw_dense_paragraph(
                c,
                self.data.hazard_statements,
                x,
                y,
                w - 4,
                FONTS["bold"],  # Bold for H-statements
                h_size,
                (0, 0, 0),
                strip_codes=False,
            )
            y -= 4

            # Thin separator line between H and P statements
            c.setStrokeColor(Color(0.7, 0.7, 0.7))
            c.setLineWidth(0.5)
            c.line(x, y, x + w * 0.5, y)
            y -= 6

        # P-Statements (strip codes, just text) - smaller, lighter
        if self.data.precaution_statements:
            p_stmts = list(self.data.precaution_statements)
            p_stmts.append("See SDS for complete precautionary information.")

            p_size = 5  # Smaller than H-statements
            y = draw_dense_paragraph(
                c,
                p_stmts,
                x,
                y,
                w - 4,
                FONTS["regular"],
                p_size,
                (0.25, 0.25, 0.25),  # Lighter gray
                strip_codes=True,
            )

        # Supplier info - flows right after P-statements (not anchored to bottom)
        y -= 8
        c.setFont(FONTS["regular"], 5)
        c.setFillColor(Color(0.4, 0.4, 0.4))
        c.drawString(x, y - 5, COMPANY_INFO["name"])
        y -= 6
        c.drawString(x, y - 5, COMPANY_INFO["address"])
        y -= 6
        c.drawString(x, y - 5, COMPANY_INFO["phone"])

    def _draw_footer(self):
        """Dark footer bar with emergency contact."""
        c = self.c

        # Dark background
        c.setFillColor(Color(*SCIENTIFIC_FOOTER_COLOR))
        c.rect(0, self.margin, LABEL_WIDTH, self.footer_height, fill=1, stroke=0)

        # Emergency contact
        text_y = self.margin + self.footer_height / 2 - 3

        c.setFont(FONTS["bold"], 7)
        c.setFillColor(Color(0, 0.7, 0.55))  # Teal
        c.drawString(self.margin, text_y, "Emergency:")

        c.setFont(FONTS["regular"], 7)
        c.setFillColor(Color(0.9, 0.9, 0.9))
        c.drawString(self.margin + 45, text_y, f"CHEMTEL {self.data.chemtel_number}")

        # Website right side
        c.drawRightString(LABEL_WIDTH - self.margin, text_y, COMPANY_INFO["website"])


def generate_scientific_label(sku: str, lot_number: str, output_dir: Path = None) -> Path:
    """Generate a scientific-style label for the given SKU."""
    from src.label_renderer import load_sku_data

    if output_dir is None:
        output_dir = OUTPUT_DIR

    sku_data = load_sku_data(sku)
    output_path = output_dir / f"{sku}-{lot_number}-scientific.pdf"

    renderer = ScientificLabelRenderer(sku_data)
    return renderer.render(output_path, lot_number)
