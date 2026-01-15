"""Organic Flow label renderer v2 - Premium/Futuristic style.

Design philosophy:
- Organic fluidity with technical precision tension
- Warm-to-cool diagonal gradient (VISIBLE, not subtle)
- Layered depth through prominent organic blobs
- Frosted glass "precision islands" with soft shadows
- Hero product name with dimensional lift
- Product family color signatures for instant recognition

v2 Critical Fixes:
- Header properly dissolves with bezier wave curves
- Diagonal gradient is clearly visible warm→cool
- Blobs are prominent (20-30% opacity) and span columns
- Frosted panels have soft drop shadows for depth
- Product name has shadow for dimensional pop
- Product family palettes and blob signatures
"""

from pathlib import Path
import re

from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from src.config import (
    ASSETS_DIR,
    COMPANY_INFO,
    LABEL_HEIGHT,
    LABEL_WIDTH,
    OUTPUT_DIR,
    PROJECT_ROOT,
    ORGANIC_COLORS,
    ORGANIC_COL1_WIDTH_PCT,
    ORGANIC_COL2_WIDTH_PCT,
    ORGANIC_COL3_WIDTH_PCT,
    ORGANIC_COLUMN_GAP,
    ORGANIC_HEADER_HEIGHT,
    ORGANIC_FOOTER_HEIGHT,
    ORGANIC_FOOTER_PILL_WIDTH_PCT,
    ORGANIC_FONT_SIZES,
    ORGANIC_GHS_SIZE,
    ORGANIC_GHS_GAP,
    ORGANIC_PRODUCT_FAMILIES,
    ORGANIC_BLOB_SIGNATURES,
)
from src.models import SKUData
from src.components.nfpa import draw_nfpa_diamond
from src.components.qrcode import draw_qr_code
from src.utils.organic_shapes import (
    draw_diagonal_gradient_v2,
    draw_organic_blob,
    draw_dissolving_header,
    draw_frosted_panel,
    draw_floating_pill,
    draw_text_shadow,
    get_blob_positions,
)

# Register fonts
FONTS_DIR = PROJECT_ROOT / "fonts"
_fonts_registered = False


def _register_fonts():
    """Register Barlow + JetBrains Mono fonts."""
    global _fonts_registered
    if _fonts_registered:
        return

    barlow_regular = FONTS_DIR / "Barlow-Regular.ttf"
    barlow_bold = FONTS_DIR / "Barlow-Bold.ttf"
    jetbrains_regular = FONTS_DIR / "JetBrainsMono-Regular.ttf"
    jetbrains_bold = FONTS_DIR / "JetBrainsMono-Bold.ttf"

    if barlow_regular.exists() and barlow_bold.exists():
        pdfmetrics.registerFont(TTFont("Barlow", str(barlow_regular)))
        pdfmetrics.registerFont(TTFont("Barlow-Bold", str(barlow_bold)))

    if jetbrains_regular.exists() and jetbrains_bold.exists():
        pdfmetrics.registerFont(TTFont("JetBrainsMono", str(jetbrains_regular)))
        pdfmetrics.registerFont(TTFont("JetBrainsMono-Bold", str(jetbrains_bold)))

    _fonts_registered = True


FONTS = {
    "bold": "Barlow-Bold",
    "regular": "Barlow",
    "mono": "JetBrainsMono",
    "mono_bold": "JetBrainsMono-Bold",
}


def get_product_family(sku_data: SKUData) -> str:
    """Determine product family based on SKU data."""
    product_name_lower = sku_data.product_name.lower()
    family = getattr(sku_data, 'product_family', None)

    # Check explicit family first
    if family:
        family_lower = family.lower()
        if family_lower in ORGANIC_PRODUCT_FAMILIES:
            return family_lower

    # Infer from product name
    solvent_keywords = ['alcohol', 'acetone', 'solvent', 'thinner', 'isopropyl',
                        'ethanol', 'methanol', 'toluene', 'xylene', 'ipa']
    acid_keywords = ['acid', 'hcl', 'sulfuric', 'nitric', 'phosphoric',
                     'hydrochloric', 'muriatic']
    base_keywords = ['hydroxide', 'sodium hydroxide', 'potassium hydroxide',
                     'ammonia', 'lye', 'caustic']
    oil_keywords = ['oil', 'lubricant', 'mineral oil', 'glycerin', 'glycol']
    food_keywords = ['food grade', 'usp', 'nf', 'food-grade', 'fcc', 'fg']

    if any(kw in product_name_lower for kw in food_keywords):
        return 'food_grade'
    if any(kw in product_name_lower for kw in acid_keywords):
        return 'acids'
    if any(kw in product_name_lower for kw in base_keywords):
        return 'bases'
    if any(kw in product_name_lower for kw in oil_keywords):
        return 'oils'
    if any(kw in product_name_lower for kw in solvent_keywords):
        return 'solvents'

    return 'specialty'


class OrganicFlowLabelRenderer:
    """
    Renders labels in Organic Flow style with product family signatures.

    Key features:
    - Product family color palettes (solvents, acids, bases, oils, food_grade, specialty)
    - Signature blob arrangements per family
    - Visible warm→cool diagonal gradient
    - Dissolving header with bezier wave curves
    - Prominent organic blobs spanning columns
    - Frosted glass panels with soft shadows
    - Hero product name with dimensional lift
    - Floating pill footer
    """

    def __init__(self, sku_data: SKUData):
        self.data = sku_data
        self.c = None

        _register_fonts()

        # Determine product family for color/blob signature
        self.product_family = get_product_family(sku_data)
        self.family_colors = ORGANIC_PRODUCT_FAMILIES.get(self.product_family,
                                                          ORGANIC_PRODUCT_FAMILIES['solvents'])
        self.blob_signature = ORGANIC_BLOB_SIGNATURES.get(self.product_family,
                                                          ORGANIC_BLOB_SIGNATURES['solvents'])

        # Layout calculations
        self.margin = 8
        self.content_width = LABEL_WIDTH - (self.margin * 2)

        # Column positions
        col1_w = self.content_width * ORGANIC_COL1_WIDTH_PCT
        col2_w = self.content_width * ORGANIC_COL2_WIDTH_PCT
        col3_w = self.content_width * ORGANIC_COL3_WIDTH_PCT
        gap = ORGANIC_COLUMN_GAP

        self.col1_left = self.margin
        self.col1_width = col1_w
        self.col2_left = self.col1_left + col1_w + gap
        self.col2_width = col2_w
        self.col3_left = self.col2_left + col2_w + gap
        self.col3_width = col3_w

        # Vertical zones
        self.header_height = ORGANIC_HEADER_HEIGHT
        self.footer_height = ORGANIC_FOOTER_HEIGHT
        self.header_bottom = LABEL_HEIGHT - self.margin - self.header_height
        self.footer_top = self.margin + self.footer_height

        # Main content area (leave room for header waves)
        self.main_top = self.header_bottom - 15
        self.main_bottom = self.footer_top + 8

    def render(self, output_path: Path, lot_number: str = None) -> Path:
        """Render the label to PDF."""
        if lot_number:
            self.data.lot_number = lot_number

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH, LABEL_HEIGHT))

        # Layer 1: Diagonal gradient background (VISIBLE)
        self._draw_background_gradient()

        # Layer 2: Organic blobs (PROMINENT, spans columns)
        self._draw_organic_blobs()

        # Layer 3: Dissolving header (with wave curves)
        self._draw_header()

        # Layer 4: Content columns
        self._draw_column_1()  # Frosted data card
        self._draw_column_2()  # Hero product (no container, floats free)
        self._draw_column_3()  # Frosted GHS island

        # Layer 5: Floating footer pill
        self._draw_footer()

        self.c.save()
        return output_path

    def _draw_background_gradient(self):
        """
        Draw visible warm-to-cool diagonal gradient.

        Uses product family colors for distinctive look.
        The gradient should be FELT, not barely perceptible.
        """
        colors = self.family_colors

        draw_diagonal_gradient_v2(
            self.c,
            0, 0,
            LABEL_WIDTH, LABEL_HEIGHT,
            warm_color=colors["warm_primary"],
            cool_color=colors["cool_secondary"],
            mid_warm=colors["warm_secondary"],
            mid_cool=colors["cool_secondary"],
            steps=80
        )

    def _draw_organic_blobs(self):
        """
        Draw prominent organic blobs that span across columns.

        Uses product family blob signature for distinctive arrangement.
        Blobs should be VISIBLE (20-30% opacity) not barely there.
        """
        colors = self.family_colors
        signature = self.blob_signature

        # Get blob positions based on family signature
        positions = get_blob_positions(
            signature["arrangement"],
            LABEL_WIDTH,
            LABEL_HEIGHT,
            scale=signature["primary_blob_scale"]
        )

        # Blob colors: alternate between warm and cool for depth
        blob_colors = [
            colors["warm_secondary"],  # Warm blob (furthest back)
            colors["cool_primary"],     # Accent blob (middle)
            colors["cool_secondary"],   # Cool blob (closer)
        ]

        # Opacities: higher than before for visibility
        opacities = [0.25, 0.18, 0.20]

        curve_tension = signature["curve_tension"]

        for i, (cx, cy, w, h, rot) in enumerate(positions):
            color = blob_colors[i % len(blob_colors)]
            opacity = opacities[i % len(opacities)]

            draw_organic_blob(
                self.c,
                center_x=cx,
                center_y=cy,
                width=w,
                height=h,
                rotation=rot,
                fill_color=color,
                opacity=opacity,
                curve_tension=curve_tension
            )

    def _draw_header(self):
        """
        Draw dissolving header with proper bezier wave curves.

        Sharp at top, organic curved edge at bottom that melts into content.
        """
        c = self.c
        colors = self.family_colors

        # Header color from family accent
        header_color = (*colors["accent"], 0.95)

        draw_dissolving_header(
            c,
            x=0,
            y=self.header_bottom,
            width=LABEL_WIDTH,
            height=self.header_height + self.margin,
            fill_color=header_color,
            wave_depth=22,  # Prominent waves
            wave_count=4
        )

        # Company logo (left side)
        logo_path = ASSETS_DIR / "logo.png"
        logo_y = self.header_bottom + self.header_height / 2 - 12
        if logo_path.exists():
            c.drawImage(
                str(logo_path),
                self.margin + 4,
                logo_y,
                width=50,
                height=28,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Company name (white text on header)
        c.setFont(FONTS["bold"], 11)
        c.setFillColor(Color(1, 1, 1))
        c.drawString(
            self.margin + 60,
            self.header_bottom + self.header_height / 2 - 4,
            COMPANY_INFO["name"]
        )

    def _draw_column_1(self):
        """
        Draw left column: Frosted data card (precision element).

        Sharp edges with soft shadow for dimensional lift.
        Contains: SKU, LOT, CAS, NFPA, QR code
        """
        c = self.c
        colors = self.family_colors
        x = self.col1_left
        y_top = self.main_top
        col_w = self.col1_width
        sizes = ORGANIC_FONT_SIZES

        # Calculate data card content
        content_lines = 3
        if not self.data.lot_number:
            content_lines -= 1
        if not self.data.cas_number:
            content_lines -= 1

        line_height = 16
        padding = 10
        card_content_height = content_lines * line_height + padding * 2

        nfpa_height = 0
        if self.data.has_nfpa:
            nfpa_height = 50

        card_height = card_content_height + nfpa_height

        # Draw frosted glass card with shadow
        card_y = y_top - card_height
        draw_frosted_panel(
            c,
            x, card_y,
            col_w - 4, card_height,
            opacity=0.80,  # Let gradient show through
            corner_radius=4,
            border_color=colors["accent"],
            border_opacity=0.35,
            shadow=True,
            shadow_opacity=0.12,
            shadow_offset=3,
            shadow_blur=6
        )

        # Draw data inside card
        text_x = x + padding
        text_y = y_top - padding

        # SKU (large, mono bold)
        c.setFont(FONTS["regular"], 6)
        c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
        c.drawString(text_x, text_y - 6, "SKU")
        text_y -= 8

        c.setFont(FONTS["mono_bold"], sizes["product_code"])
        c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
        c.drawString(text_x, text_y - sizes["product_code"], self.data.sku)
        text_y -= sizes["product_code"] + 8

        # LOT
        if self.data.lot_number:
            c.setFont(FONTS["regular"], 6)
            c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
            c.drawString(text_x, text_y - 6, "LOT")
            text_y -= 8

            c.setFont(FONTS["mono"], sizes["lot"])
            c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
            c.drawString(text_x, text_y - sizes["lot"], self.data.lot_number)
            text_y -= sizes["lot"] + 6

        # CAS
        if self.data.cas_number:
            c.setFont(FONTS["mono"], sizes["cas"])
            c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
            c.drawString(text_x, text_y - sizes["cas"], f"CAS: {self.data.cas_number}")
            text_y -= sizes["cas"] + 6

        # UPC
        c.setFont(FONTS["mono"], 6)
        c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
        c.drawString(text_x, text_y - 6, f"UPC: {self.data.upc_gtin12}")
        text_y -= 12

        # NFPA Diamond
        if self.data.has_nfpa:
            nfpa_size = 40
            nfpa_x = x + (col_w - nfpa_size) / 2
            nfpa_y = text_y - nfpa_size - 4
            draw_nfpa_diamond(
                c, nfpa_x, nfpa_y, nfpa_size,
                self.data.nfpa_health or 0,
                self.data.nfpa_fire or 0,
                self.data.nfpa_reactivity or 0,
                self.data.nfpa_special,
            )
            c.setFont(FONTS["regular"], 5)
            c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
            c.drawCentredString(nfpa_x + nfpa_size / 2, nfpa_y - 8, "NFPA 704")

        # QR Code at bottom
        qr_size = 48
        qr_y = self.main_bottom + 8
        if self.data.sds_url:
            draw_qr_code(c, self.data.sds_url, x, qr_y, qr_size)
            c.setFont(FONTS["regular"], 5)
            c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
            c.drawString(x, qr_y - 7, "Scan for SDS")

    def _draw_column_2(self):
        """
        Draw center column: Hero product name, grade, net contents.

        NO CONTAINER - floats free in the "airy zone" between precision islands.
        Product name has shadow for dimensional lift.
        Net contents is prominent (key selling point).
        """
        c = self.c
        colors = self.family_colors
        x = self.col2_left
        y = self.main_top
        w = self.col2_width
        sizes = ORGANIC_FONT_SIZES

        # Product Name - HERO treatment with dimensional lift
        product_name_size = sizes["product_name_hero"]
        name_width = stringWidth(self.data.product_name, FONTS["bold"], product_name_size)

        # Scale down if needed
        if name_width > w:
            product_name_size = sizes["product_name_min"]

        # Draw shadow for dimensional "lift" effect
        draw_text_shadow(
            c,
            self.data.product_name,
            x, y - product_name_size,
            FONTS["bold"], product_name_size,
            shadow_color=(0, 0, 0),
            shadow_opacity=0.18,
            offset_x=1.5,
            offset_y=-2.5,
            blur_layers=3
        )

        # Draw main product name
        c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
        c.setFont(FONTS["bold"], product_name_size)
        c.drawString(x, y - product_name_size, self.data.product_name)
        y -= product_name_size + 6

        # Grade/concentration
        if self.data.grade_or_concentration:
            c.setFont(FONTS["regular"], sizes["grade"])
            c.setFillColor(Color(*ORGANIC_COLORS["text_secondary"]))
            c.drawString(x, y - sizes["grade"], self.data.grade_or_concentration)
            y -= sizes["grade"] + 14

        # Subtle separator
        c.setStrokeColor(Color(*colors["accent"], 0.3))
        c.setLineWidth(0.75)
        c.line(x, y, x + w * 0.5, y)
        y -= 14

        # Net Contents - PROMINENT (key selling point)
        net_size = sizes["net_contents_us"]

        # Draw shadow for lift
        draw_text_shadow(
            c,
            self.data.net_contents_us,
            x, y - net_size,
            FONTS["bold"], net_size,
            shadow_color=(0, 0, 0),
            shadow_opacity=0.12,
            offset_x=1,
            offset_y=-1.5,
            blur_layers=2
        )

        # Draw net contents text
        c.setFont(FONTS["bold"], net_size)
        c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
        c.drawString(x, y - net_size, self.data.net_contents_us)

        # Accent underline for emphasis
        net_width = stringWidth(self.data.net_contents_us, FONTS["bold"], net_size)
        c.setStrokeColor(Color(*colors["accent"], 0.7))
        c.setLineWidth(2.5)
        c.line(x, y - net_size - 4, x + net_width, y - net_size - 4)

        y -= net_size + 8

        # Metric conversion (smaller)
        c.setFont(FONTS["regular"], sizes["net_contents_metric"])
        c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
        c.drawString(x, y - sizes["net_contents_metric"], self.data.net_contents_metric)
        y -= sizes["net_contents_metric"] + 12

        # DOT shipping info (if applicable)
        if self.data.dot_regulated:
            c.setStrokeColor(Color(0.7, 0.7, 0.7, 0.5))
            c.setLineWidth(0.5)
            c.line(x, y, x + w * 0.5, y)
            y -= 8

            c.setFont(FONTS["regular"], 8)
            c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
            c.drawString(x, y - 8, f"DOT: {self.data.un_number}")
            y -= 10

            if self.data.proper_shipping_name:
                lines = self._wrap_text(self.data.proper_shipping_name, FONTS["regular"], 7, w)
                c.setFont(FONTS["regular"], 7)
                for line in lines:
                    c.drawString(x, y - 7, line)
                    y -= 9

            pg = self.data.packing_group.value if self.data.packing_group else ""
            c.drawString(x, y - 7, f"Class {self.data.hazard_class}, PG {pg}")

    def _draw_column_3(self):
        """
        Draw right column: Frosted GHS island (precision element).

        Sharp-edged compliance zone with soft shadow for depth.
        """
        c = self.c
        colors = self.family_colors
        x = self.col3_left
        y_top = self.main_top
        w = self.col3_width
        sizes = ORGANIC_FONT_SIZES

        if not self.data.hazcom_applicable:
            return

        # Draw frosted glass island for entire column
        island_height = y_top - self.main_bottom - 8
        draw_frosted_panel(
            c,
            x, self.main_bottom + 4,
            w, island_height,
            opacity=0.80,
            corner_radius=4,
            border_color=colors["accent"],
            border_opacity=0.35,
            shadow=True,
            shadow_opacity=0.12,
            shadow_offset=3,
            shadow_blur=6
        )

        # Content positioning inside island
        padding = 8
        content_x = x + padding
        content_y = y_top - padding
        content_width = w - (padding * 2)

        # GHS Pictograms at top
        pictogram_ids = [
            p.value if hasattr(p, "value") else p for p in self.data.ghs_pictograms
        ]

        if pictogram_ids:
            num = len(pictogram_ids)
            cols = min(3, num)
            rows = (num + cols - 1) // cols
            ghs_size = ORGANIC_GHS_SIZE
            ghs_gap = ORGANIC_GHS_GAP

            grid_width = (ghs_size * cols) + (ghs_gap * (cols - 1))
            grid_x = x + (w - grid_width) / 2

            for i, pic_id in enumerate(pictogram_ids):
                row = i // cols
                col = i % cols

                pic_x = grid_x + (col * (ghs_size + ghs_gap))
                pic_y = content_y - (row + 1) * (ghs_size + ghs_gap) + ghs_gap

                self._draw_ghs_pictogram(pic_id, pic_x, pic_y, ghs_size)

            content_y -= rows * (ghs_size + ghs_gap) + 4

        # Signal word
        if self.data.signal_word:
            signal = (
                self.data.signal_word.value
                if hasattr(self.data.signal_word, "value")
                else str(self.data.signal_word)
            )
            signal_text = signal.upper()
            signal_size = sizes["signal_word"]

            c.setFont(FONTS["bold"], signal_size)
            if signal_text == "DANGER":
                c.setFillColor(Color(*ORGANIC_COLORS["danger_red"]))
            else:
                c.setFillColor(Color(*ORGANIC_COLORS["warning_amber"]))

            c.drawString(content_x, content_y - signal_size, signal_text)

            # Underline
            text_w = stringWidth(signal_text, FONTS["bold"], signal_size)
            if signal_text == "DANGER":
                c.setStrokeColor(Color(*ORGANIC_COLORS["danger_red"]))
            else:
                c.setStrokeColor(Color(*ORGANIC_COLORS["warning_amber"]))
            c.setLineWidth(1.5)
            c.line(content_x, content_y - signal_size - 2,
                   content_x + text_w, content_y - signal_size - 2)

            content_y -= signal_size + 8

        # H-Statements (with codes visible)
        if self.data.hazard_statements:
            h_size = sizes["h_statement"]
            c.setFont(FONTS["bold"], h_size)
            c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))

            for stmt in self.data.hazard_statements:
                lines = self._wrap_text(stmt, FONTS["bold"], h_size, content_width)
                for line in lines:
                    c.drawString(content_x, content_y - h_size, line)
                    content_y -= h_size * 1.15

            content_y -= 3
            c.setStrokeColor(Color(0.7, 0.7, 0.7))
            c.setLineWidth(0.5)
            c.line(content_x, content_y, content_x + content_width * 0.5, content_y)
            content_y -= 5

        # P-Statements (strip codes)
        if self.data.precaution_statements:
            p_size = sizes["p_statement"]
            c.setFont(FONTS["regular"], p_size)
            c.setFillColor(Color(*ORGANIC_COLORS["text_secondary"]))

            clean_stmts = []
            for stmt in self.data.precaution_statements:
                clean = re.sub(r"^[PH]\d+(\+[PH]\d+)*:\s*", "", stmt)
                clean_stmts.append(clean)

            combined = " ".join(clean_stmts) + " See SDS for complete precautionary information."
            lines = self._wrap_text(combined, FONTS["regular"], p_size, content_width)

            supplier_space = 25
            min_y = self.main_bottom + padding + supplier_space

            for line in lines:
                if content_y - p_size < min_y:
                    break
                c.drawString(content_x, content_y - p_size, line)
                content_y -= p_size * 1.1

        # Supplier info at bottom
        content_y = self.main_bottom + padding + 18
        supplier_size = sizes["supplier"]
        c.setFont(FONTS["regular"], supplier_size)
        c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
        c.drawString(content_x, content_y, COMPANY_INFO["name"])
        c.drawString(content_x, content_y - supplier_size - 1, COMPANY_INFO["address"])
        c.drawString(content_x, content_y - (supplier_size + 1) * 2, COMPANY_INFO["phone"])

    def _draw_ghs_pictogram(self, pictogram_id: str, x: float, y: float, size: float):
        """Draw a single GHS pictogram."""
        from src.config import GHS_ASSETS_DIR

        if hasattr(pictogram_id, "value"):
            pictogram_id = pictogram_id.value

        png_path = GHS_ASSETS_DIR / f"{pictogram_id}.png"
        if png_path.exists():
            self.c.drawImage(
                str(png_path),
                x, y,
                width=size,
                height=size,
                preserveAspectRatio=True,
                mask="auto",
            )

    def _draw_footer(self):
        """Draw floating pill footer with emergency contact."""
        c = self.c
        colors = self.family_colors

        pill_width = LABEL_WIDTH * ORGANIC_FOOTER_PILL_WIDTH_PCT
        pill_height = self.footer_height - 4
        pill_x = (LABEL_WIDTH - pill_width) / 2
        pill_y = self.margin + 2

        draw_floating_pill(
            c,
            pill_x, pill_y,
            pill_width, pill_height,
            fill_color=(1, 1, 1),
            opacity=0.92,
            border_color=colors["accent"],
            border_opacity=0.3,
            shadow=True
        )

        text_y = pill_y + pill_height / 2 - 3

        # "Emergency:" in accent color
        c.setFont(FONTS["bold"], 7)
        c.setFillColor(Color(*colors["accent"]))
        c.drawString(pill_x + 12, text_y, "Emergency:")

        # CHEMTEL number
        c.setFont(FONTS["regular"], 7)
        c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
        c.drawString(pill_x + 60, text_y, f"CHEMTEL {self.data.chemtel_number}")

        # Website
        c.drawRightString(pill_x + pill_width - 12, text_y, COMPANY_INFO["website"])

    def _wrap_text(self, text: str, font_name: str, font_size: float, max_width: float) -> list:
        """Simple text wrapping."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test = " ".join(current_line + [word])
            if stringWidth(test, font_name, font_size) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines


def generate_organic_label(sku: str, lot_number: str, output_dir: Path = None) -> Path:
    """Generate an Organic Flow style label for the given SKU."""
    from src.label_renderer import load_sku_data

    if output_dir is None:
        output_dir = OUTPUT_DIR

    sku_data = load_sku_data(sku)
    output_path = output_dir / f"{sku}-{lot_number}-organic.pdf"

    renderer = OrganicFlowLabelRenderer(sku_data)
    return renderer.render(output_path, lot_number)
