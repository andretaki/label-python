"""NFPA 704 diamond rendering."""

import math
from reportlab.lib.colors import Color

from src.config import COLORS, FONTS, FONT_SIZES


def draw_nfpa_diamond(canvas, x: float, y: float, size: float,
                      health: int, fire: int, reactivity: int,
                      special: str = None) -> None:
    """
    Draw an NFPA 704 hazard diamond.

    The diamond is positioned with (x, y) as the bottom-left of the bounding box.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge of bounding box) in points
        y: Y position (bottom edge of bounding box) in points
        size: Width and height of the diamond in points
        health: Health hazard rating (0-4) - blue, left
        fire: Fire hazard rating (0-4) - red, top
        reactivity: Reactivity rating (0-4) - yellow, right
        special: Special hazard symbol (e.g., "W" for water reactive) - white, bottom
    """
    # Calculate center of the diamond
    center_x = x + size / 2
    center_y = y + size / 2

    # Half-size for drawing quadrants
    half = size / 2

    # Define colors for each quadrant
    colors = {
        'health': COLORS['nfpa_blue'],
        'fire': COLORS['nfpa_red'],
        'reactivity': COLORS['nfpa_yellow'],
        'special': COLORS['nfpa_white'],
    }

    # Draw background diamond (white border)
    canvas.setStrokeColor(Color(*COLORS['black']))
    canvas.setLineWidth(1)

    # Draw each quadrant as a filled polygon

    # Fire (top) - Red
    canvas.setFillColor(Color(*colors['fire']))
    top_path = canvas.beginPath()
    top_path.moveTo(center_x, center_y)  # Center
    top_path.lineTo(center_x - half, center_y)  # Left point
    top_path.lineTo(center_x, center_y + half)  # Top point
    top_path.lineTo(center_x + half, center_y)  # Right point
    top_path.close()
    canvas.drawPath(top_path, fill=1, stroke=0)

    # Health (left) - Blue
    canvas.setFillColor(Color(*colors['health']))
    left_path = canvas.beginPath()
    left_path.moveTo(center_x, center_y)  # Center
    left_path.lineTo(center_x - half, center_y)  # Left point
    left_path.lineTo(center_x, center_y - half)  # Bottom point
    left_path.close()
    canvas.drawPath(left_path, fill=1, stroke=0)

    # Reactivity (right) - Yellow
    canvas.setFillColor(Color(*colors['reactivity']))
    right_path = canvas.beginPath()
    right_path.moveTo(center_x, center_y)  # Center
    right_path.lineTo(center_x + half, center_y)  # Right point
    right_path.lineTo(center_x, center_y - half)  # Bottom point
    right_path.close()
    canvas.drawPath(right_path, fill=1, stroke=0)

    # Special (bottom) - White
    canvas.setFillColor(Color(*colors['special']))
    # This is actually drawn as part of the left/right quadrants meeting at bottom
    # For visual clarity, we just need the white section visible

    # Draw the outer diamond border
    canvas.setStrokeColor(Color(*COLORS['black']))
    canvas.setLineWidth(0.75)
    diamond_path = canvas.beginPath()
    diamond_path.moveTo(center_x, center_y + half)  # Top
    diamond_path.lineTo(center_x + half, center_y)  # Right
    diamond_path.lineTo(center_x, center_y - half)  # Bottom
    diamond_path.lineTo(center_x - half, center_y)  # Left
    diamond_path.close()
    canvas.drawPath(diamond_path, fill=0, stroke=1)

    # Draw internal dividing lines
    canvas.setLineWidth(0.5)
    # Horizontal line through center
    canvas.line(center_x - half, center_y, center_x + half, center_y)
    # Vertical line from center to bottom
    canvas.line(center_x, center_y, center_x, center_y - half)

    # Draw rating numbers
    font_size = FONT_SIZES.get('nfpa_rating', 9)
    # Scale font size based on diamond size
    scaled_font_size = font_size * (size / 72)  # 72pt = 1 inch baseline
    scaled_font_size = max(6, min(scaled_font_size, 12))

    canvas.setFont(FONTS['bold'], scaled_font_size)
    canvas.setFillColor(Color(*COLORS['black']))

    # Offset for positioning numbers in each quadrant
    offset = half * 0.45

    # Fire (top) - position above center
    canvas.drawCentredString(center_x, center_y + offset - scaled_font_size / 3, str(fire))

    # Health (left) - position left of center
    canvas.drawCentredString(center_x - offset, center_y - scaled_font_size / 3, str(health))

    # Reactivity (right) - position right of center
    canvas.drawCentredString(center_x + offset, center_y - scaled_font_size / 3, str(reactivity))

    # Special (bottom) - if provided
    if special:
        canvas.drawCentredString(center_x, center_y - offset - scaled_font_size / 3, special)


def draw_nfpa_with_label(canvas, x: float, y: float, width: float, height: float,
                         health: int, fire: int, reactivity: int,
                         special: str = None) -> None:
    """
    Draw NFPA diamond with a label showing the ratings.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Available width in points
        height: Available height in points
        health: Health hazard rating (0-4)
        fire: Fire hazard rating (0-4)
        reactivity: Reactivity rating (0-4)
        special: Special hazard symbol
    """
    # Calculate diamond size (leave room for label below)
    label_height = 10
    diamond_size = min(width, height - label_height) * 0.85

    # Center the diamond horizontally
    diamond_x = x + (width - diamond_size) / 2
    diamond_y = y + label_height + 2

    # Draw the diamond
    draw_nfpa_diamond(canvas, diamond_x, diamond_y, diamond_size,
                      health, fire, reactivity, special)

    # Draw label below: "1-3-0" format
    label_text = f"{health}-{fire}-{reactivity}"
    if special:
        label_text += f"-{special}"

    canvas.setFont(FONTS['regular'], 6)
    canvas.setFillColor(Color(*COLORS['black']))
    canvas.drawCentredString(x + width / 2, y + 2, label_text)
