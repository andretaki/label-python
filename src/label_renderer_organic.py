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
from src.components.barcode import draw_barcode
from src.components.nfpa import draw_nfpa_diamond
from src.components.qrcode import draw_qr_code
from src.utils.organic_shapes import (
    draw_diagonal_header,
    draw_frosted_panel,
    draw_diagonal_cut_panel,
)

# Register fonts
FONTS_DIR = PROJECT_ROOT / "fonts"
_fonts_registered = False


def _register_fonts():
    """Register Barlow + JetBrains Mono + Anton fonts."""
    global _fonts_registered
    if _fonts_registered:
        return

    barlow_regular = FONTS_DIR / "Barlow-Regular.ttf"
    barlow_bold = FONTS_DIR / "Barlow-Bold.ttf"
    jetbrains_regular = FONTS_DIR / "JetBrainsMono-Regular.ttf"
    jetbrains_bold = FONTS_DIR / "JetBrainsMono-Bold.ttf"
    anton_regular = FONTS_DIR / "Anton-Regular.ttf"

    if barlow_regular.exists() and barlow_bold.exists():
        pdfmetrics.registerFont(TTFont("Barlow", str(barlow_regular)))
        pdfmetrics.registerFont(TTFont("Barlow-Bold", str(barlow_bold)))

    if jetbrains_regular.exists() and jetbrains_bold.exists():
        pdfmetrics.registerFont(TTFont("JetBrainsMono", str(jetbrains_regular)))
        pdfmetrics.registerFont(TTFont("JetBrainsMono-Bold", str(jetbrains_bold)))

    # Anton for hero product names (bold condensed)
    if anton_regular.exists():
        pdfmetrics.registerFont(TTFont("Anton", str(anton_regular)))

    _fonts_registered = True


FONTS = {
    "bold": "Barlow-Bold",
    "regular": "Barlow",
    "mono": "JetBrainsMono",
    "mono_bold": "JetBrainsMono-Bold",
    "hero": "Anton",  # Bold condensed for product names
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
                     'ammonia', 'lye', 'caustic', 'bicarbonate', 'carbonate',
                     'sodium bicarbonate', 'baking soda', 'soda ash', 'borax']
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

        # Column positions - adapt based on whether GHS is needed
        col1_w = self.content_width * ORGANIC_COL1_WIDTH_PCT
        gap = ORGANIC_COLUMN_GAP

        self.col1_left = self.margin
        self.col1_width = col1_w

        # Check if this product has hazmat info
        has_hazmat = sku_data.hazcom_applicable

        if has_hazmat:
            # Standard 3-column layout
            col2_w = self.content_width * ORGANIC_COL2_WIDTH_PCT
            col3_w = self.content_width * ORGANIC_COL3_WIDTH_PCT
            self.col2_left = self.col1_left + col1_w + gap
            self.col2_width = col2_w
            self.col3_left = self.col2_left + col2_w + gap
            self.col3_width = col3_w
        else:
            # Expanded layout - col2 takes col2 + col3 space
            col2_w = self.content_width * (ORGANIC_COL2_WIDTH_PCT + ORGANIC_COL3_WIDTH_PCT)
            self.col2_left = self.col1_left + col1_w + gap
            self.col2_width = col2_w
            self.col3_left = 0
            self.col3_width = 0

        self.has_hazmat = has_hazmat

        # Vertical zones
        self.header_height = ORGANIC_HEADER_HEIGHT
        self.footer_height = ORGANIC_FOOTER_HEIGHT
        self.header_bottom = LABEL_HEIGHT - self.margin - self.header_height
        self.footer_top = self.margin + self.footer_height

        # Main content area (extra clearance for diagonal header slope)
        self.main_top = self.header_bottom - 22
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
        Draw clean white background.

        Dark header + white content + black footer creates enough visual interest.
        No diagonal gradient or stripes needed.
        """
        c = self.c
        # Clean white background
        c.setFillColor(Color(1, 1, 1))
        c.rect(0, 0, LABEL_WIDTH, LABEL_HEIGHT, fill=1, stroke=0)

    def _compute_hero_safe_zone(self) -> tuple:
        """
        Compute the hero safe zone rectangle to keep blobs out of title area.

        Returns (safe_x0, safe_y0, safe_x1, safe_y1) in points.
        """
        # X bounds: full width of column 2 with padding
        safe_x0 = self.col2_left - 6

        if self.has_hazmat:
            # Hazmat: col2 ends before GHS column
            col2_right = self.col3_left - 8
        else:
            # Non-hazmat: col2 expands to fill space
            col2_right = LABEL_WIDTH - self.margin - 8
        safe_x1 = col2_right + 6

        # Y bounds: product name + grade line area
        product_name_size = 22 if not self.has_hazmat else ORGANIC_FONT_SIZES["product_name_hero"]
        grade_size = 12 if not self.has_hazmat else ORGANIC_FONT_SIZES["grade"]

        safe_y1 = self.main_top + 6
        safe_y0 = self.main_top - (product_name_size + 8 + grade_size + 10)

        return (safe_x0, safe_y0, safe_x1, safe_y1)

    def _adjust_blob_for_safe_zone(self, cx, cy, bw, bh, safe_zone, is_primary=False) -> tuple:
        """
        Adjust blob position to avoid the hero safe zone.

        Returns adjusted (cx, cy).
        """
        safe_x0, safe_y0, safe_x1, safe_y1 = safe_zone
        margin = 12

        # Compute blob AABB
        blob_x0 = cx - bw / 2
        blob_x1 = cx + bw / 2
        blob_y0 = cy - bh / 2
        blob_y1 = cy + bh / 2

        # Check intersection with safe zone
        intersects = not (blob_x1 < safe_x0 or blob_x0 > safe_x1 or
                         blob_y1 < safe_y0 or blob_y0 > safe_y1)

        if not intersects:
            return (cx, cy)

        # Strategy 1: Push blob DOWN so its top is below safe zone
        new_cy = (safe_y0 - margin) - bh / 2

        # Check if pushed blob is still on canvas (above footer)
        min_cy = self.footer_top + bh / 2 + 10

        if new_cy >= min_cy:
            # Maintain column unity for primary blob
            if is_primary:
                # Keep cx in 35-50% range, adjust cy to mid-body
                target_cy_ratio = 0.50 if self.has_hazmat else 0.45
                new_cy = max(new_cy, LABEL_HEIGHT * target_cy_ratio - bh / 4)
                new_cy = min(new_cy, LABEL_HEIGHT * 0.55)
            return (cx, new_cy)

        # Strategy 2: Push sideways if down doesn't work
        # Try pushing left first, then right
        for shift in [-30, -50, 30, 50]:
            shifted_cx = cx + shift
            shifted_x0 = shifted_cx - bw / 2
            shifted_x1 = shifted_cx + bw / 2

            # Check if shifted position avoids safe zone
            still_intersects = not (shifted_x1 < safe_x0 or shifted_x0 > safe_x1 or
                                   blob_y1 < safe_y0 or blob_y0 > safe_y1)

            if not still_intersects and shifted_x0 > 0 and shifted_x1 < LABEL_WIDTH:
                return (shifted_cx, cy)

        # Fallback: push down anyway
        return (cx, new_cy)

    def _draw_organic_blobs(self):
        """
        Blobs disabled - clean white background is sufficient.

        Dark header + white content + black footer creates enough visual interest.
        The diagonal elements (header edge, data card cut) are the signature.
        """
        pass  # No blobs - clean industrial look

    def _draw_header(self):
        """
        Draw header with clean diagonal bottom edge.

        Sharp at top, clean diagonal edge at bottom sloping down left to right.
        This creates architectural/industrial feel echoing the diagonal cut panel.
        ALWAYS uses deep eggplant purple - brand anchor across all products.
        """
        c = self.c

        # Deep eggplant purple - nearly black with purple undertone
        header_color = (*ORGANIC_COLORS["header_purple"], 0.95)

        draw_diagonal_header(
            c,
            x=0,
            y=self.header_bottom,
            width=LABEL_WIDTH,
            height=self.header_height + self.margin,
            fill_color=header_color,
            angle_degrees=4  # Clean diagonal slope down from left to right
        )

        # Company logo (left side)
        # Since header is dark purple, prefer white/reversed logo if available
        logo_white = ASSETS_DIR / "logo_white.png"
        logo_reversed = ASSETS_DIR / "logo_color_reversed.png"
        logo_default = ASSETS_DIR / "logo.png"

        # Try white version first, then reversed, then default
        if logo_white.exists():
            logo_path = logo_white
        elif logo_reversed.exists():
            logo_path = logo_reversed
        else:
            logo_path = logo_default

        logo_y = self.header_bottom + self.header_height / 2 - 22
        if logo_path.exists():
            c.drawImage(
                str(logo_path),
                self.margin + 4,
                logo_y,
                width=100,
                height=44,
                preserveAspectRatio=True,
                mask="auto",
            )

        # Barcode in white card (right side of header) - sized for scan reliability
        if self.data.upc_gtin12 and len(self.data.upc_gtin12) == 12:
            barcode_width = 78
            barcode_height = 20
            digits_height = 6
            card_padding = 4
            card_width = barcode_width + card_padding * 2
            card_height = barcode_height + digits_height + card_padding * 2 + 1

            card_x = LABEL_WIDTH - self.margin - card_width - 4
            card_y = self.header_bottom + (self.header_height - card_height) / 2

            # White card background
            c.setFillColor(Color(1, 1, 1, 0.95))
            c.roundRect(card_x, card_y, card_width, card_height, 3, fill=1, stroke=0)

            # Draw barcode
            barcode_x = card_x + card_padding
            barcode_y = card_y + card_padding + digits_height + 1
            try:
                draw_barcode(c, self.data.upc_gtin12, barcode_x, barcode_y,
                           barcode_width, barcode_height)
            except Exception:
                pass  # Barcode failed, digits below will still show

            # Digits below bars (human fallback)
            c.setFont(FONTS["mono"], 5.5)
            c.setFillColor(Color(0, 0, 0))
            c.drawCentredString(
                barcode_x + barcode_width / 2,
                card_y + card_padding + 1,
                self.data.upc_gtin12
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
        padding = 16  # Increased padding for better text clearance
        card_content_height = content_lines * line_height + padding * 2

        nfpa_height = 0
        if self.data.has_nfpa:
            nfpa_height = 50

        card_height = card_content_height + nfpa_height

        # Draw diagonal cut panel (signature element) with shadow
        card_y = y_top - card_height
        draw_diagonal_cut_panel(
            c,
            x, card_y,
            col_w - 4, card_height,
            cut_angle=15,  # 15° diagonal cut on bottom-right
            fill_color=(1, 1, 1),
            opacity=0.90,  # Frosted: 0.88-0.92 so gradient shows slightly
            border_color=colors["accent"],
            border_opacity=0.35,
            shadow=True,
            shadow_opacity=0.05,
            shadow_offset=1,
            shadow_blur=2
        )

        # Draw data inside card
        text_x = x + padding
        text_y = y_top - padding
        max_text_width = col_w - padding * 2 - 4  # Available width for text

        # SKU (mono bold, scaled to fit)
        c.setFont(FONTS["regular"], 6)
        c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
        c.drawString(text_x, text_y - 6, "SKU")
        text_y -= 8

        # Scale SKU font to fit within card
        sku_size = sizes["product_code"]
        sku_width = stringWidth(self.data.sku, FONTS["mono_bold"], sku_size)
        while sku_width > max_text_width and sku_size > 7:
            sku_size -= 0.5
            sku_width = stringWidth(self.data.sku, FONTS["mono_bold"], sku_size)

        # SKU: BOLD, prominent - read first in 3-second glance
        c.setFont(FONTS["mono_bold"], sku_size)
        c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
        c.drawString(text_x, text_y - sku_size, self.data.sku)
        text_y -= sku_size + 8

        # LOT: Medium weight - clearly secondary
        if self.data.lot_number:
            c.setFont(FONTS["regular"], 5.5)
            c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
            c.drawString(text_x, text_y - 5.5, "LOT")
            text_y -= 7

            c.setFont(FONTS["mono"], sizes["lot"])
            c.setFillColor(Color(*ORGANIC_COLORS["text_secondary"]))
            c.drawString(text_x, text_y - sizes["lot"], self.data.lot_number)
            text_y -= sizes["lot"] + 5

        # CAS: Light weight, smallest - tertiary info
        if self.data.cas_number:
            cas_size = sizes["cas"] - 1  # -1pt from current
            c.setFont(FONTS["regular"], cas_size)
            c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
            c.drawString(text_x, text_y - cas_size, f"CAS: {self.data.cas_number}")
            text_y -= cas_size + 5

        # UPC removed - barcode with digits is in header

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

        # QR Code - utility zone, centered in col1, tight to footer
        pill_y = self.margin + 2
        pill_height = self.footer_height + 4
        pill_top = pill_y + pill_height

        qr_size = 40  # Scannable but compact
        qr_x = self.col1_left + (self.col1_width - qr_size) / 2  # Centered in col1
        qr_y = pill_top + 2  # Tight to pill (2pt)

        if self.data.sds_url:
            # Caption ABOVE so it never crashes into the pill
            c.setFont(FONTS["regular"], 5)
            c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
            c.drawCentredString(qr_x + qr_size / 2, qr_y + qr_size + 3, "Scan for SDS")
            # White border around QR for clean separation
            c.setFillColor(Color(1, 1, 1))
            c.rect(qr_x - 2, qr_y - 2, qr_size + 4, qr_size + 4, fill=1, stroke=0)
            draw_qr_code(c, self.data.sds_url, qr_x, qr_y, qr_size)

    def _draw_column_2(self):
        """
        Draw center column: Hero product name, grade, net contents.

        NO CONTAINER - floats free in the "airy zone" between precision islands.
        Product name has shadow for dimensional lift.
        Net contents is prominent (key selling point).

        When no GHS info (non-hazmat), expands to fill the extra space.
        """
        c = self.c
        colors = self.family_colors
        x = self.col2_left
        y = self.main_top
        w = self.col2_width
        sizes = ORGANIC_FONT_SIZES

        # For non-hazmat products, use larger sizes
        if not self.has_hazmat:
            product_name_size = 22  # Larger hero for expanded layout
            net_size = 22
        else:
            product_name_size = sizes["product_name_hero"]
            net_size = sizes["net_contents_us"]

        # Product Name - HERO treatment with Anton font (bold condensed)
        # Try Anton first, fall back to Barlow-Bold if not available
        hero_font = FONTS["hero"] if "hero" in FONTS else FONTS["bold"]
        try:
            name_width = stringWidth(self.data.product_name, hero_font, product_name_size)
        except KeyError:
            hero_font = FONTS["bold"]
            name_width = stringWidth(self.data.product_name, hero_font, product_name_size)

        # Scale down if needed
        while name_width > w and product_name_size > sizes["product_name_min"]:
            product_name_size -= 1
            name_width = stringWidth(self.data.product_name, hero_font, product_name_size)

        # Draw main product name - Anton bold condensed for industrial feel
        # Premium = simple + confident, not busy
        c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
        c.setFont(hero_font, product_name_size)
        c.drawString(x, y - product_name_size, self.data.product_name)
        y -= product_name_size + 14

        # Grade/concentration - darker than metric for hierarchy
        if self.data.grade_or_concentration:
            grade_size = sizes["grade"] + (2 if not self.has_hazmat else 0)
            c.setFont(FONTS["regular"], grade_size)
            c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
            c.drawString(x, y - grade_size, self.data.grade_or_concentration)
            y -= grade_size + 16

        # Subtle separator - wider for non-hazmat
        sep_width = w * 0.6 if not self.has_hazmat else w * 0.5
        c.setStrokeColor(Color(*colors["accent"], 0.4))
        c.setLineWidth(1.0)
        c.line(x, y, x + sep_width, y)
        y -= 16

        # Net Contents - PROMINENT (key selling point)
        # Clean text, no shadow - premium = confident simplicity
        c.setFont(FONTS["bold"], net_size)
        c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))
        c.drawString(x, y - net_size, self.data.net_contents_us)

        # Accent underline for emphasis
        net_width = stringWidth(self.data.net_contents_us, FONTS["bold"], net_size)
        c.setStrokeColor(Color(*colors["accent"], 0.7))
        c.setLineWidth(3.0 if not self.has_hazmat else 2.5)
        c.line(x, y - net_size - 7, x + net_width, y - net_size - 7)

        y -= net_size + 10

        # Metric conversion (smaller)
        metric_size = sizes["net_contents_metric"] + (2 if not self.has_hazmat else 0)
        c.setFont(FONTS["regular"], metric_size)
        c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
        c.drawString(x, y - metric_size, self.data.net_contents_metric)
        y -= metric_size + 14

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

        # Non-hazmat badge is now drawn in column 3, no inline text needed here

    def _draw_column_3(self):
        """
        Draw right column: Frosted GHS island (hazmat) or Non-hazardous badge (non-hazmat).

        For hazmat: Sharp-edged compliance zone with GHS pictograms and statements.
        For non-hazmat: Smaller badge panel to maintain 3-column visual balance.
        """
        c = self.c
        colors = self.family_colors
        sizes = ORGANIC_FONT_SIZES

        if not self.data.hazcom_applicable:
            # Non-hazmat: Typography-only NON-HAZARDOUS panel
            # NO icons, NO shields, NO checkmarks - typography does all the work
            badge_width = 108
            badge_height = 76  # Slightly shorter without icon
            badge_x = LABEL_WIDTH - self.margin - badge_width - 4
            badge_y = self.main_top - badge_height - 8

            # Muted sage for safety (NOT red/orange/yellow which indicate hazard)
            safe_color = (0.29, 0.48, 0.44)  # Muted sage

            # Frosted badge panel with sharper corners
            draw_frosted_panel(
                c,
                badge_x, badge_y,
                badge_width, badge_height,
                opacity=0.94,
                corner_radius=4,
                border_color=safe_color,
                border_opacity=0.5,
                shadow=True,
                shadow_opacity=0.05,
                shadow_offset=1,
                shadow_blur=2
            )

            # "NON-" on first line, "HAZARDOUS" on second line
            # Bold 14pt teal - typography does all the work
            c.setFont(FONTS["bold"], 14)
            c.setFillColor(Color(*safe_color))
            c.drawCentredString(badge_x + badge_width / 2, badge_y + badge_height - 22, "NON-")
            c.drawCentredString(badge_x + badge_width / 2, badge_y + badge_height - 38, "HAZARDOUS")

            # Subtle teal underline below the text
            underline_width = 70
            underline_x = badge_x + (badge_width - underline_width) / 2
            c.setStrokeColor(Color(*safe_color, 0.6))
            c.setLineWidth(1.5)
            c.line(underline_x, badge_y + badge_height - 44,
                   underline_x + underline_width, badge_y + badge_height - 44)

            # "No GHS classification required" in smaller text below
            c.setFont(FONTS["regular"], 7)
            c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
            c.drawCentredString(badge_x + badge_width / 2, badge_y + 16, "No GHS classification")
            c.drawCentredString(badge_x + badge_width / 2, badge_y + 7, "required")

            return

        # Hazmat: Full GHS compliance panel
        x = self.col3_left
        y_top = self.main_top
        w = self.col3_width

        # Draw frosted glass island for entire column
        # Higher opacity for better text contrast on hazmat panel
        island_height = y_top - self.main_bottom - 8
        draw_frosted_panel(
            c,
            x, self.main_bottom + 4,
            w, island_height,
            opacity=0.94,  # More opaque for hazmat readability
            corner_radius=4,
            border_color=colors["accent"],
            border_opacity=0.35,
            shadow=True,
            shadow_opacity=0.05,
            shadow_offset=1,
            shadow_blur=2
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

        # Signal word with colored background badge
        if self.data.signal_word:
            signal = (
                self.data.signal_word.value
                if hasattr(self.data.signal_word, "value")
                else str(self.data.signal_word)
            )
            signal_text = signal.upper()
            signal_size = sizes["signal_word"]

            # Calculate badge dimensions
            text_w = stringWidth(signal_text, FONTS["bold"], signal_size)
            badge_padding_h = 8  # Horizontal padding
            badge_padding_v = 4  # Vertical padding
            badge_width = text_w + badge_padding_h * 2
            badge_height = signal_size + badge_padding_v * 2
            badge_radius = 3

            # Draw colored background badge
            badge_x = content_x
            badge_y = content_y - badge_height

            if signal_text == "DANGER":
                # Red background (#D91919) with white text
                c.setFillColor(Color(0.851, 0.098, 0.098))  # #D91919
                c.roundRect(badge_x, badge_y, badge_width, badge_height, badge_radius, fill=1, stroke=0)
                c.setFillColor(Color(1, 1, 1))  # White text
            else:
                # Amber background (#F59E0B) with dark text
                c.setFillColor(Color(0.961, 0.620, 0.043))  # #F59E0B
                c.roundRect(badge_x, badge_y, badge_width, badge_height, badge_radius, fill=1, stroke=0)
                c.setFillColor(Color(0.1, 0.1, 0.1))  # Dark text

            c.setFont(FONTS["bold"], signal_size)
            c.drawString(badge_x + badge_padding_h, badge_y + badge_padding_v, signal_text)

            content_y -= badge_height + 8

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

        # P-Statements grouped by category for better scannability
        if self.data.precaution_statements:
            p_size = sizes["p_statement"]
            supplier_space = 25
            min_y = self.main_bottom + padding + supplier_space

            # Group statements by P-code category
            prevention = []  # P2xx
            response = []    # P3xx
            storage = []     # P4xx
            disposal = []    # P5xx

            for stmt in self.data.precaution_statements:
                clean = re.sub(r"^[PH]\d+(\+[PH]\d+)*:\s*", "", stmt)
                # Extract P-code to determine category
                code_match = re.match(r"^P(\d)", stmt)
                if code_match:
                    first_digit = code_match.group(1)
                    if first_digit == "2":
                        prevention.append(clean)
                    elif first_digit == "3":
                        response.append(clean)
                    elif first_digit == "4":
                        storage.append(clean)
                    elif first_digit == "5":
                        disposal.append(clean)
                    else:
                        prevention.append(clean)  # Default
                else:
                    prevention.append(clean)

            # Draw grouped sections - darker text for readability
            c.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))

            def draw_group(label, items):
                nonlocal content_y
                if not items or content_y - p_size < min_y:
                    return
                # Section label in bold
                c.setFont(FONTS["bold"], p_size)
                c.drawString(content_x, content_y - p_size, label)
                content_y -= p_size * 1.2
                # Items in regular
                c.setFont(FONTS["regular"], p_size)
                combined = " ".join(items)
                lines = self._wrap_text(combined, FONTS["regular"], p_size, content_width)
                for line in lines:
                    if content_y - p_size < min_y:
                        break
                    c.drawString(content_x, content_y - p_size, line)
                    content_y -= p_size * 1.1
                content_y -= 2  # Small gap between sections

            draw_group("Prevention:", prevention)
            draw_group("Response:", response)
            draw_group("Storage:", storage)
            draw_group("Disposal:", disposal)

            # SDS reference
            if content_y - p_size >= min_y:
                c.setFont(FONTS["regular"], p_size - 0.5)
                c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
                c.drawString(content_x, content_y - p_size, "See SDS for complete info.")

        # Supplier info at bottom (address is in footer, avoid duplication)
        content_y = self.main_bottom + padding + 12
        supplier_size = sizes["supplier"]
        c.setFont(FONTS["regular"], supplier_size)
        c.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))
        c.drawString(content_x, content_y, COMPANY_INFO["name"])
        c.drawString(content_x, content_y - supplier_size - 1, COMPANY_INFO["phone"])

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
        """Draw full-bleed black footer bar with emergency info."""
        c = self.c

        # Full-width black bar - no gaps at edges
        bar_height = self.footer_height + 6
        bar_y = 0  # Start at bottom edge
        bar_color = (0.10, 0.08, 0.12)  # Near-black with purple tint

        # Draw the full-bleed footer bar
        c.setFillColor(Color(*bar_color))
        c.rect(0, bar_y, LABEL_WIDTH, bar_height, fill=1, stroke=0)

        # Content positioning
        content_margin = 12
        text_y1 = bar_y + bar_height / 2 + 3

        # "Emergency:" in RED (#D92525) as accent
        c.setFont(FONTS["bold"], 7)
        c.setFillColor(Color(0.851, 0.145, 0.145))  # #D92525
        c.drawString(content_margin, text_y1, "Emergency:")

        # CHEMTEL number in white
        c.setFont(FONTS["regular"], 7)
        c.setFillColor(Color(1, 1, 1))
        c.drawString(content_margin + 52, text_y1, f"CHEMTEL {self.data.chemtel_number}")

        # Website right-aligned in white
        c.drawRightString(LABEL_WIDTH - content_margin, text_y1, COMPANY_INFO["website"])

        # Address centered in muted gray
        text_y2 = bar_y + bar_height / 2 - 7
        c.setFont(FONTS["regular"], 6.5)
        c.setFillColor(Color(0.5, 0.5, 0.52))  # Muted gray
        c.drawCentredString(LABEL_WIDTH / 2, text_y2, COMPANY_INFO["address"])

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
