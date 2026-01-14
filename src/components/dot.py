"""DOT shipping information block rendering - clean light mode styling."""

from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth

from src.config import COLORS, FONTS, FONT_SIZES


def draw_dot_block(canvas, x: float, y: float, width: float, height: float,
                   proper_shipping_name: str, un_number: str,
                   hazard_class: str, packing_group: str) -> None:
    """
    Draw a DOT shipping information block.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width of the block in points
        height: Height of the block in points
        proper_shipping_name: DOT proper shipping name
        un_number: UN number (e.g., "UN1219")
        hazard_class: DOT hazard class (e.g., "3")
        packing_group: Packing group (e.g., "II")
    """
    # Light background with teal left border
    canvas.setFillColor(Color(*COLORS['bg_secondary']))
    canvas.setStrokeColor(Color(*COLORS['border_light']))
    canvas.setLineWidth(0.5)
    canvas.roundRect(x, y, width, height, 3, stroke=1, fill=1)

    # Teal left accent
    canvas.setFillColor(Color(*COLORS['accent_teal']))
    canvas.rect(x, y + 2, 2.5, height - 4, fill=1, stroke=0)

    # Internal padding
    padding = 4
    inner_x = x + padding + 4
    inner_width = width - (2 * padding) - 4

    # Font sizes
    header_size = 6.5
    content_size = 6

    # Current Y position (start from top)
    current_y = y + height - padding - header_size

    # Header: "DOT Shipping" in teal
    canvas.setFont(FONTS['bold'], header_size)
    canvas.setFillColor(Color(*COLORS['accent_teal_dark']))
    canvas.drawString(inner_x, current_y, "DOT Shipping")

    current_y -= (content_size + 2)

    # Proper shipping name
    canvas.setFont(FONTS['regular'], content_size)
    canvas.setFillColor(Color(*COLORS['text_primary']))

    from src.utils.text_fitting import wrap_text
    name_lines = wrap_text(proper_shipping_name, FONTS['regular'], content_size, inner_width)

    for line in name_lines:
        canvas.drawString(inner_x, current_y, line)
        current_y -= (content_size + 1)

    # UN Number
    canvas.setFillColor(Color(*COLORS['text_secondary']))
    canvas.drawString(inner_x, current_y, f"UN#: {un_number}")
    current_y -= (content_size + 1)

    # Class and Packing Group
    class_pg_text = f"Class: {hazard_class}  PG: {packing_group}"
    canvas.drawString(inner_x, current_y, class_pg_text)


def draw_dot_block_compact(canvas, x: float, y: float, width: float, height: float,
                           proper_shipping_name: str, un_number: str,
                           hazard_class: str, packing_group: str) -> None:
    """
    Draw a compact DOT shipping information block.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width of the block in points
        height: Height of the block in points
        proper_shipping_name: DOT proper shipping name
        un_number: UN number (e.g., "UN1219")
        hazard_class: DOT hazard class (e.g., "3")
        packing_group: Packing group (e.g., "II")
    """
    # Light background with border
    canvas.setFillColor(Color(*COLORS['bg_secondary']))
    canvas.setStrokeColor(Color(*COLORS['border_light']))
    canvas.setLineWidth(0.5)
    canvas.roundRect(x, y, width, height, 2, stroke=1, fill=1)

    # Tight padding
    padding = 3
    inner_x = x + padding
    inner_width = width - (2 * padding)

    # Smaller fonts for compact layout
    header_size = 5.5
    content_size = 5

    line_height = content_size + 1
    current_y = y + height - padding - header_size

    # Header - teal
    canvas.setFont(FONTS['bold'], header_size)
    canvas.setFillColor(Color(*COLORS['accent_teal_dark']))
    canvas.drawString(inner_x, current_y, "DOT Shipping")

    current_y -= line_height + 1

    # Shipping name (truncate if needed)
    canvas.setFont(FONTS['regular'], content_size)
    canvas.setFillColor(Color(*COLORS['text_primary']))
    max_chars = int(inner_width / (content_size * 0.5))
    name = proper_shipping_name[:max_chars] if len(proper_shipping_name) > max_chars else proper_shipping_name
    canvas.drawString(inner_x, current_y, name)

    current_y -= line_height

    # UN#
    canvas.setFillColor(Color(*COLORS['text_secondary']))
    canvas.drawString(inner_x, current_y, f"UN#: {un_number}")

    current_y -= line_height

    # Class/PG
    canvas.drawString(inner_x, current_y, f"Class: {hazard_class}  PG: {packing_group}")


def _draw_dot_badge_shadow(canvas, x: float, y: float, width: float, height: float,
                            corner_radius: float = 4) -> None:
    """Draw drop shadow for DOT badge."""
    canvas.saveState()
    shadow_opacity = 0.12
    offset_y = -2
    blur_radius = 4
    layers = 3

    for i in range(layers, 0, -1):
        layer_t = i / layers
        layer_spread = blur_radius * layer_t
        layer_opacity = shadow_opacity * (1 - layer_t * 0.7)

        if layer_opacity <= 0:
            continue

        canvas.setFillColor(Color(0, 0, 0, alpha=layer_opacity))
        canvas.roundRect(
            x - layer_spread * 0.5,
            y + offset_y - layer_spread * 0.5,
            width + layer_spread,
            height + layer_spread,
            corner_radius,
            fill=1, stroke=0
        )
    canvas.restoreState()


def draw_dot_inline_badge(canvas, x: float, y: float, width: float,
                          un_number: str, hazard_class: str, packing_group: str) -> float:
    """
    Draw DOT info as a dark card badge with teal text.

    "DOT · UN1219 · CLASS 3 · PG II" style with dark background and teal accents.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Available width in points
        un_number: UN number (e.g., "UN1219")
        hazard_class: DOT hazard class (e.g., "3")
        packing_group: Packing group (e.g., "II")

    Returns:
        Height of the badge drawn
    """
    # Badge styling
    badge_height = 18
    padding = 8
    corner_radius = 4
    border_width = 1.5
    font_size = FONT_SIZES.get('dot_badge', 7)

    # Build the inline text with dot separators
    badge_text = f"DOT · {un_number} · CLASS {hazard_class} · PG {packing_group}"

    # Calculate badge width based on text
    canvas.setFont(FONTS['bold'], font_size)
    text_width = stringWidth(badge_text, FONTS['bold'], font_size)
    badge_width = min(text_width + (padding * 2), width)

    # Draw drop shadow
    _draw_dot_badge_shadow(canvas, x, y, badge_width, badge_height, corner_radius)

    # Dark card background
    canvas.setFillColor(Color(*COLORS['bg_dark_secondary']))
    canvas.roundRect(x, y, badge_width, badge_height, corner_radius, fill=1, stroke=0)

    # Teal border
    canvas.setStrokeColor(Color(*COLORS['accent_teal']))
    canvas.setLineWidth(border_width)
    canvas.roundRect(x, y, badge_width, badge_height, corner_radius, fill=0, stroke=1)

    # Draw "DOT" in teal, separators in muted, rest in teal
    current_x = x + padding
    text_y = y + (badge_height - font_size) / 2 + 1

    # Split text into parts for color coding
    parts = badge_text.split(' · ')
    for i, part in enumerate(parts):
        # Draw the text part in teal
        canvas.setFillColor(Color(*COLORS['accent_teal']))
        canvas.setFont(FONTS['bold'], font_size)
        canvas.drawString(current_x, text_y, part)
        current_x += stringWidth(part, FONTS['bold'], font_size)

        # Draw separator in muted gray (except after last part)
        if i < len(parts) - 1:
            separator = ' · '
            canvas.setFillColor(Color(*COLORS['text_light_muted']))
            canvas.drawString(current_x, text_y, separator)
            current_x += stringWidth(separator, FONTS['bold'], font_size)

    return badge_height
