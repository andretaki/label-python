"""Main label renderer - Frame Approach design.

Dark header/footer bars frame a white main content area.
Dark floating cards (GHS, data block, DOT) on white create premium tech-industrial feel
while keeping the design print-efficient.
"""

import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth

from src.config import (
    LABEL_WIDTH, LABEL_HEIGHT, MARGIN,
    CONTENT_LEFT, CONTENT_RIGHT, CONTENT_WIDTH,
    HEADER_HEIGHT, HEADER_BOTTOM,
    FOOTER_HEIGHT, FOOTER_BOTTOM, FOOTER_TOP,
    ACCENT_LINE_HEIGHT,
    MAIN_TOP, MAIN_BOTTOM,
    LEFT_COLUMN_LEFT, LEFT_COLUMN_WIDTH,
    RIGHT_COLUMN_LEFT, RIGHT_COLUMN_RIGHT,
    QR_TOP_MARGIN, QR_SIZE,
    BARCODE_WIDTH, BARCODE_HEIGHT, BARCODE_RIGHT_MARGIN,
    GHS_CARD_SIZE, GHS_CARD_GAP,
    ELEMENT_GAP_SMALL, ELEMENT_GAP_MEDIUM,
    FONTS, FONT_SIZES, COLORS, COMPANY_INFO, ASSETS_DIR, OUTPUT_DIR,
)
from src.models import SKUData
from src.components.barcode import draw_barcode
from src.components.qrcode import draw_qr_code
from src.components.ghs import draw_ghs_pictograms_grid
from src.components.dot import draw_dot_inline_badge
from src.utils.text_fitting import (
    wrap_text, fit_text_to_width, fit_statements_to_area,
    process_precautionary_statements, calculate_line_height,
)


class LabelRenderer:
    """Renders chemical product labels with Frame Approach design."""

    def __init__(self, sku_data: SKUData):
        self.data = sku_data
        self.c = None

    def render(self, output_path: Path, lot_number: str = None) -> Path:
        """Render the label to a PDF file."""
        if lot_number:
            self.data.lot_number = lot_number

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH, LABEL_HEIGHT))

        # White background (default)
        # Draw frame elements
        self._draw_header()
        self._draw_teal_accent_line(HEADER_BOTTOM - ACCENT_LINE_HEIGHT)
        self._draw_teal_accent_line(FOOTER_TOP)
        self._draw_footer()

        # Draw content
        self._draw_product_identity()
        self._draw_left_column()
        self._draw_right_column()

        self.c.save()
        return output_path

    def _draw_header_gradient(self, y_base: float, height: float):
        """Draw brushed metal gradient for header."""
        c = self.c
        steps = 60
        step_width = LABEL_WIDTH / steps

        for i in range(steps):
            t = i / steps
            # Parabolic curve - brighter in center
            brightness = 0.4 * (1 - (2 * t - 1) ** 2)

            r = (26 + brightness * 30) / 255
            g = (26 + brightness * 30) / 255
            b = (30 + brightness * 35) / 255

            c.setFillColor(Color(r, g, b))
            c.rect(i * step_width, y_base, step_width + 1, height, fill=1, stroke=0)

    def _draw_teal_accent_line(self, y: float):
        """Draw teal gradient accent line with glow."""
        c = self.c
        width = LABEL_WIDTH
        height = ACCENT_LINE_HEIGHT

        # Draw subtle glow first
        c.setFillColor(Color(0, 212/255, 170/255, 0.15))
        c.rect(0, y - 1.5, width, height + 3, fill=1, stroke=0)

        # Draw gradient line
        steps = 40
        step_width = width / steps

        for i in range(steps):
            t = i / steps
            brightness = 1 - abs(2 * t - 1) * 0.3

            r = 0
            g = (170 + brightness * 42) / 255
            b = (136 + brightness * 34) / 255

            c.setFillColor(Color(r, g, b))
            c.rect(i * step_width, y, step_width + 1, height, fill=1, stroke=0)

    def _draw_header(self):
        """Draw dark header with gradient, logo, company info, barcode."""
        c = self.c
        y_base = HEADER_BOTTOM

        # Gradient background
        self._draw_header_gradient(y_base, HEADER_HEIGHT + MARGIN)

        # Logo
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            logo_height = HEADER_HEIGHT - 12
            logo_width = logo_height * 0.8
            c.drawImage(
                str(logo_path), CONTENT_LEFT, y_base + 8,
                width=logo_width, height=logo_height,
                preserveAspectRatio=True, anchor='sw', mask='auto'
            )
            text_x = CONTENT_LEFT + logo_width + 10
        else:
            text_x = CONTENT_LEFT

        # Company name - white
        c.setFont(FONTS['bold'], FONT_SIZES['company_name'])
        c.setFillColor(Color(*COLORS['text_light']))
        c.drawString(text_x, y_base + HEADER_HEIGHT - 14, COMPANY_INFO['name'])

        # Company details - secondary
        c.setFont(FONTS['regular'], FONT_SIZES['company_details'])
        c.setFillColor(Color(*COLORS['text_light_secondary']))
        c.drawString(text_x, y_base + HEADER_HEIGHT - 26, COMPANY_INFO['address'])
        c.drawString(text_x, y_base + HEADER_HEIGHT - 36,
                     f"{COMPANY_INFO['phone']} | {COMPANY_INFO['website']}")

        # Barcode - RIGHT ALIGNED
        barcode_x = CONTENT_RIGHT - BARCODE_WIDTH - BARCODE_RIGHT_MARGIN
        barcode_y = y_base + (HEADER_HEIGHT - BARCODE_HEIGHT) / 2

        # White background with shadow
        self._draw_shadow(barcode_x - 4, barcode_y - 3,
                         BARCODE_WIDTH + 8, BARCODE_HEIGHT + 6, corner_radius=4)
        c.setFillColor(Color(*COLORS['white']))
        c.roundRect(barcode_x - 4, barcode_y - 3,
                   BARCODE_WIDTH + 8, BARCODE_HEIGHT + 6, 4, fill=1, stroke=0)

        try:
            draw_barcode(c, self.data.upc_gtin12, barcode_x, barcode_y,
                        BARCODE_WIDTH, BARCODE_HEIGHT)
        except Exception:
            c.setFillColor(Color(*COLORS['black']))
            c.setFont(FONTS['mono'], 6)
            c.drawString(barcode_x, barcode_y + 5, self.data.upc_gtin12)

    def _draw_footer(self):
        """Draw dark footer with gradient."""
        c = self.c

        # Gradient background (darker at bottom)
        steps = 20
        step_height = FOOTER_TOP / steps

        for i in range(steps):
            t = i / steps
            brightness = t * 0.3  # Darker at bottom

            r = (26 - brightness * 13) / 255
            g = (26 - brightness * 13) / 255
            b = (30 - brightness * 15) / 255

            c.setFillColor(Color(r, g, b))
            c.rect(0, i * step_height, LABEL_WIDTH, step_height + 1, fill=1, stroke=0)

        # Emergency contact
        c.setFont(FONTS['bold'], FONT_SIZES['footer'])
        c.setFillColor(Color(*COLORS['accent_teal']))
        c.drawString(CONTENT_LEFT, FOOTER_BOTTOM + 8, "Emergency:")

        c.setFillColor(Color(*COLORS['text_light']))
        c.setFont(FONTS['regular'], FONT_SIZES['footer'])
        emergency_x = CONTENT_LEFT + stringWidth("Emergency: ", FONTS['bold'], FONT_SIZES['footer'])
        c.drawString(emergency_x, FOOTER_BOTTOM + 8, f"CHEMTEL {self.data.chemtel_number}")

        # Supplier line
        c.setFont(FONTS['regular'], FONT_SIZES['footer_small'])
        c.setFillColor(Color(*COLORS['text_light_muted']))
        c.drawRightString(CONTENT_RIGHT, FOOTER_BOTTOM + 8, "Supplied by Alliance Chemical")

    def _draw_shadow(self, x: float, y: float, width: float, height: float,
                    offset_y: float = -2, opacity: float = 0.12, corner_radius: float = 0):
        """Draw drop shadow."""
        c = self.c
        c.setFillColor(Color(0, 0, 0, opacity))
        if corner_radius > 0:
            c.roundRect(x, y + offset_y, width, height, corner_radius, fill=1, stroke=0)
        else:
            c.rect(x, y + offset_y, width, height, fill=1, stroke=0)

    def _draw_glow(self, x: float, y: float, width: float, height: float,
                  glow_color: tuple, radius: float = 4, opacity: float = 0.15,
                  corner_radius: float = 0):
        """Draw outer glow effect."""
        c = self.c
        for i in range(int(radius), 0, -1):
            alpha = opacity * (1 - i / radius)
            c.setFillColor(Color(*glow_color, alpha=alpha))
            expand = i * 1.5
            if corner_radius > 0:
                c.roundRect(x - expand, y - expand,
                           width + expand * 2, height + expand * 2,
                           corner_radius + expand / 2, fill=1, stroke=0)
            else:
                c.rect(x - expand, y - expand,
                      width + expand * 2, height + expand * 2, fill=1, stroke=0)

    def _draw_product_identity(self):
        """Draw product name, grade on white background. Returns y position after data block."""
        c = self.c
        y = MAIN_TOP - 4

        # Product name - large dark text
        product_name_size = FONT_SIZES['product_name']
        max_width = LEFT_COLUMN_WIDTH - 4
        name_width = stringWidth(self.data.product_name, FONTS['bold'], product_name_size)

        if name_width > max_width:
            product_name_size, _ = fit_text_to_width(
                self.data.product_name, FONTS['bold'],
                product_name_size, FONT_SIZES['product_name_min'], max_width
            )

        c.setFont(FONTS['bold'], product_name_size)
        c.setFillColor(Color(*COLORS['text_dark']))
        c.drawString(LEFT_COLUMN_LEFT, y - product_name_size, self.data.product_name)

        y -= product_name_size + 4

        # Teal underline with glow
        name_width = stringWidth(self.data.product_name, FONTS['bold'], product_name_size)
        line_width = min(name_width + 10, LEFT_COLUMN_WIDTH - 4)

        # Glow
        c.setFillColor(Color(0, 212/255, 170/255, 0.2))
        c.rect(LEFT_COLUMN_LEFT, y - 1, line_width, 5, fill=1, stroke=0)

        # Line gradient
        steps = 20
        step_w = line_width / steps
        for i in range(steps):
            t = i / steps
            brightness = 1 - abs(2 * t - 1) * 0.3
            g = (170 + brightness * 42) / 255
            b = (136 + brightness * 34) / 255
            c.setFillColor(Color(0, g, b))
            c.rect(LEFT_COLUMN_LEFT + i * step_w, y, step_w + 1, 2.5, fill=1, stroke=0)

        y -= 8

        # Grade/concentration - teal text
        if self.data.grade_or_concentration:
            c.setFont(FONTS['regular'], FONT_SIZES['grade'])
            c.setFillColor(Color(*COLORS['accent_teal']))
            c.drawString(LEFT_COLUMN_LEFT, y - FONT_SIZES['grade'], self.data.grade_or_concentration)
            y -= FONT_SIZES['grade'] + ELEMENT_GAP_MEDIUM

        # Data block (DARK CARD) - returns bottom y position
        if self.data.cas_number:
            y = self._draw_data_block(LEFT_COLUMN_LEFT, y)

        # Store for QR positioning
        self._data_block_bottom = y

    def _draw_data_block(self, x: float, y: float) -> float:
        """Draw dark card with CAS/SKU/LOT data. Returns bottom y position."""
        c = self.c

        block_padding = 10
        line_height = 12
        label_size = FONT_SIZES['data_label']
        value_size = FONT_SIZES['data_value']

        lines = []
        if self.data.cas_number:
            lines.append(("CAS", self.data.cas_number))
        lines.append(("SKU", self.data.sku))
        if self.data.lot_number:
            lines.append(("LOT", self.data.lot_number))

        c.setFont(FONTS['mono_bold'], label_size)
        max_label_width = max(stringWidth(label, FONTS['mono_bold'], label_size) for label, _ in lines)

        block_height = len(lines) * line_height + (block_padding * 2)
        block_width = LEFT_COLUMN_WIDTH - 8

        # Draw shadow
        self._draw_shadow(x, y - block_height, block_width, block_height,
                         offset_y=-2, opacity=0.15, corner_radius=4)

        # Draw teal glow on left side
        self._draw_glow(x, y - block_height, 3, block_height,
                       COLORS['accent_teal'], radius=4, opacity=0.15)

        # Dark background
        c.setFillColor(Color(*COLORS['bg_dark_secondary']))
        c.roundRect(x, y - block_height, block_width, block_height, 4, fill=1, stroke=0)

        # Teal left border
        c.setFillColor(Color(*COLORS['accent_teal']))
        c.rect(x, y - block_height + 3, 3, block_height - 6, fill=1, stroke=0)

        # Dark border
        c.setStrokeColor(Color(*COLORS['border_dark']))
        c.setLineWidth(1)
        c.roundRect(x, y - block_height, block_width, block_height, 4, fill=0, stroke=1)

        # Row separators
        c.setStrokeColor(Color(*COLORS['border_dark']))
        c.setLineWidth(0.5)
        for i in range(1, len(lines)):
            line_y = y - block_padding - (i * line_height)
            c.line(x + block_padding, line_y, x + block_width - block_padding, line_y)

        # Text
        current_y = y - block_padding - label_size - 2
        for label, value in lines:
            # Label - muted
            c.setFont(FONTS['mono_bold'], label_size)
            c.setFillColor(Color(*COLORS['text_light_muted']))
            c.drawString(x + block_padding + 6, current_y, label)

            # Value - white
            c.setFont(FONTS['mono'], value_size)
            c.setFillColor(Color(*COLORS['text_light']))
            c.drawString(x + block_padding + 6 + max_label_width + 12, current_y, value)
            current_y -= line_height

        # Return bottom of block
        return y - block_height

    def _draw_left_column(self):
        """Draw QR code and net contents at bottom of left column."""
        c = self.c

        # QR and net contents side by side at the bottom
        qr_size = 45
        bottom_y = MAIN_BOTTOM + 8

        # QR on left
        if self.data.sds_url:
            qr_x = LEFT_COLUMN_LEFT
            qr_y = bottom_y

            # Teal border glow
            self._draw_glow(qr_x - 2, qr_y - 2, qr_size + 4, qr_size + 4,
                           COLORS['accent_teal'], radius=3, opacity=0.2, corner_radius=3)

            # Teal border
            c.setStrokeColor(Color(*COLORS['accent_teal']))
            c.setLineWidth(2)
            c.roundRect(qr_x - 2, qr_y - 2, qr_size + 4, qr_size + 4, 3, fill=0, stroke=1)

            # White background for QR
            c.setFillColor(Color(*COLORS['white']))
            c.rect(qr_x, qr_y, qr_size, qr_size, fill=1, stroke=0)

            # QR code
            draw_qr_code(c, self.data.sds_url, qr_x, qr_y, qr_size)

            # Label BELOW QR
            c.setFont(FONTS['bold'], 5)
            c.setFillColor(Color(*COLORS['accent_teal_dark']))
            label = "SDS"
            label_width = stringWidth(label, FONTS['bold'], 5)
            c.drawString(qr_x + (qr_size - label_width) / 2, qr_y - 7, label)

            # Net contents to the right of QR
            net_x = qr_x + qr_size + 10
        else:
            net_x = LEFT_COLUMN_LEFT

        # Net contents beside QR (or at left if no QR)
        self._draw_net_contents(net_x, bottom_y)

    def _draw_net_contents(self, x: float, y: float):
        """Draw net contents with teal underline."""
        c = self.c

        us_size = FONT_SIZES['net_contents_us']
        c.setFont(FONTS['bold'], us_size)
        c.setFillColor(Color(*COLORS['text_dark']))
        c.drawString(x, y + 22, self.data.net_contents_us)

        # Teal underline with glow
        us_width = stringWidth(self.data.net_contents_us, FONTS['bold'], us_size)

        c.setFillColor(Color(0, 212/255, 170/255, 0.2))
        c.rect(x, y + 17, us_width, 4, fill=1, stroke=0)

        c.setFillColor(Color(*COLORS['accent_teal']))
        c.rect(x, y + 18, us_width, 2, fill=1, stroke=0)

        # Metric
        c.setFont(FONTS['regular'], FONT_SIZES['net_contents_metric'])
        c.setFillColor(Color(*COLORS['text_muted']))
        c.drawString(x, y + 6, self.data.net_contents_metric)

    def _draw_right_column(self):
        """Draw GHS pictograms, signal word, statements, DOT badge."""
        c = self.c

        if not self.data.hazcom_applicable:
            return

        right_x = RIGHT_COLUMN_LEFT
        right_width = CONTENT_RIGHT - RIGHT_COLUMN_LEFT

        # GHS pictograms
        num_pictograms = len(self.data.ghs_pictograms)
        ghs_rows = 1 if num_pictograms <= 3 else 2
        actual_ghs_height = (GHS_CARD_SIZE * ghs_rows) + (GHS_CARD_GAP * (ghs_rows - 1))

        ghs_y = MAIN_TOP - actual_ghs_height
        draw_ghs_pictograms_grid(
            c, self.data.ghs_pictograms,
            right_x, ghs_y, right_width, actual_ghs_height
        )

        text_y = ghs_y - ELEMENT_GAP_MEDIUM
        text_width = right_width

        # Signal word badge
        if self.data.signal_word:
            signal = self.data.signal_word.value if hasattr(self.data.signal_word, 'value') else str(self.data.signal_word)
            signal_text = signal.upper()

            c.setFont(FONTS['bold'], FONT_SIZES['signal_word'])
            text_width_signal = stringWidth(signal_text, FONTS['bold'], FONT_SIZES['signal_word'])

            pill_padding = 10
            pill_height = FONT_SIZES['signal_word'] + 10
            pill_width = text_width_signal + (pill_padding * 2)

            if signal.upper() == "DANGER":
                color_light = COLORS['danger_red_light']
                color_dark = COLORS['danger_red']
                glow_color = COLORS['danger_red']
            else:
                color_light = COLORS['warning_amber_light']
                color_dark = COLORS['warning_amber']
                glow_color = COLORS['warning_amber']

            # Glow
            self._draw_glow(right_x, text_y - pill_height, pill_width, pill_height,
                           glow_color, radius=6, opacity=0.35, corner_radius=4)

            # Shadow
            self._draw_shadow(right_x, text_y - pill_height, pill_width, pill_height,
                             offset_y=-2, opacity=0.2, corner_radius=4)

            # Gradient background
            steps = 10
            step_h = pill_height / steps
            for i in range(steps):
                t = i / steps
                r = color_light[0] + (color_dark[0] - color_light[0]) * t
                g = color_light[1] + (color_dark[1] - color_light[1]) * t
                b = color_light[2] + (color_dark[2] - color_light[2]) * t
                c.setFillColor(Color(r, g, b))
                c.rect(right_x, text_y - pill_height + i * step_h, pill_width, step_h + 1, fill=1, stroke=0)

            # Round corners overlay
            c.roundRect(right_x, text_y - pill_height, pill_width, pill_height, 4, fill=0, stroke=0)

            # Text
            if signal.upper() == "DANGER":
                c.setFillColor(Color(*COLORS['white']))
            else:
                c.setFillColor(Color(*COLORS['text_dark']))

            c.setFont(FONTS['bold'], FONT_SIZES['signal_word'])
            c.drawString(right_x + pill_padding, text_y - pill_height + 6, signal_text)
            text_y -= pill_height + ELEMENT_GAP_SMALL

        # Hazard statements
        c.setFont(FONTS['regular'], FONT_SIZES['h_statement'])
        c.setFillColor(Color(*COLORS['text_dark']))

        line_height = calculate_line_height(FONT_SIZES['h_statement'])
        for h_statement in self.data.hazard_statements:
            lines = wrap_text(h_statement, FONTS['regular'],
                             FONT_SIZES['h_statement'], text_width)
            for line in lines:
                c.drawString(right_x, text_y - FONT_SIZES['h_statement'], line)
                text_y -= line_height

        text_y -= 4

        # Separator
        c.setStrokeColor(Color(*COLORS['border_light']))
        c.setLineWidth(0.5)
        c.line(right_x, text_y, right_x + text_width * 0.6, text_y)
        text_y -= 6

        # P-statements
        p_statements = process_precautionary_statements(
            self.data.precaution_statements, add_sds_note=True
        )

        dot_badge_height = 22  # Account for badge + padding
        if self.data.dot_regulated:
            p_bottom = MAIN_BOTTOM + dot_badge_height + 4
        else:
            p_bottom = MAIN_BOTTOM + 4

        p_height = text_y - p_bottom

        # Use smaller minimum font (4.5pt) to fit more statements
        p_size, p_lines = fit_statements_to_area(
            p_statements, FONTS['regular'],
            FONT_SIZES['p_statement'], 4.5,
            text_width, p_height
        )

        c.setFont(FONTS['regular'], p_size)
        c.setFillColor(Color(*COLORS['text_dark_secondary']))
        p_line_height = calculate_line_height(p_size, spacing=1.15)  # Tighter line spacing

        for line in p_lines:
            if text_y - p_size < p_bottom:
                break
            c.drawString(right_x, text_y - p_size, line)
            text_y -= p_line_height

        # DOT badge
        if self.data.dot_regulated:
            draw_dot_inline_badge(
                c, right_x, MAIN_BOTTOM, right_width,
                self.data.un_number or "",
                self.data.hazard_class or "",
                self.data.packing_group.value if self.data.packing_group else ""
            )


def load_sku_data(sku: str) -> SKUData:
    """Load SKU data from JSON file."""
    from src.config import DATA_DIR

    json_path = DATA_DIR / "test_skus" / f"{sku}.json"
    if not json_path.exists():
        raise FileNotFoundError(f"SKU data not found: {json_path}")

    with open(json_path) as f:
        data = json.load(f)

    return SKUData(**data)


def generate_label(sku: str, lot_number: str, output_dir: Path = None) -> Path:
    """Generate a label PDF for the given SKU."""
    if output_dir is None:
        output_dir = OUTPUT_DIR

    sku_data = load_sku_data(sku)
    output_path = output_dir / f"{sku}-{lot_number}.pdf"

    renderer = LabelRenderer(sku_data)
    return renderer.render(output_path, lot_number)
