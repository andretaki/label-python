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

    Layout:
              FIRE (red)
               /\\
              /  \\
       HEALTH/    \\REACTIVITY
       (blue) \\  / (yellow)
               \\/
            SPECIAL (white)

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

    # NFPA standard colors (adjusted for better appearance)
    colors = {
        'fire': (1, 0, 0),              # Red - top
        'health': (0, 0.33, 0.65),      # NFPA blue - left (less electric)
        'reactivity': (1, 0.92, 0),     # Yellow - right (slightly warmer)
        'special': (1, 1, 1),           # White - bottom
    }

    # =========================================
    # CALCULATE EDGE MIDPOINTS
    # =========================================
    # Each quadrant is a small diamond, not a triangle
    # Vertices: center, two adjacent edge midpoints, one corner

    mid_top_left = (center_x - half / 2, center_y + half / 2)
    mid_top_right = (center_x + half / 2, center_y + half / 2)
    mid_bot_right = (center_x + half / 2, center_y - half / 2)
    mid_bot_left = (center_x - half / 2, center_y - half / 2)

    # Corner points
    top = (center_x, center_y + half)
    right = (center_x + half, center_y)
    bottom = (center_x, center_y - half)
    left = (center_x - half, center_y)

    # =========================================
    # DRAW THE FOUR QUADRANTS (as sub-diamonds)
    # =========================================

    # FIRE (top quadrant) - Red
    canvas.setFillColor(Color(*colors['fire']))
    fire_path = canvas.beginPath()
    fire_path.moveTo(center_x, center_y)
    fire_path.lineTo(*mid_top_left)
    fire_path.lineTo(*top)
    fire_path.lineTo(*mid_top_right)
    fire_path.close()
    canvas.drawPath(fire_path, fill=1, stroke=0)

    # HEALTH (left quadrant) - Blue
    canvas.setFillColor(Color(*colors['health']))
    health_path = canvas.beginPath()
    health_path.moveTo(center_x, center_y)
    health_path.lineTo(*mid_bot_left)
    health_path.lineTo(*left)
    health_path.lineTo(*mid_top_left)
    health_path.close()
    canvas.drawPath(health_path, fill=1, stroke=0)

    # REACTIVITY (right quadrant) - Yellow
    canvas.setFillColor(Color(*colors['reactivity']))
    react_path = canvas.beginPath()
    react_path.moveTo(center_x, center_y)
    react_path.lineTo(*mid_top_right)
    react_path.lineTo(*right)
    react_path.lineTo(*mid_bot_right)
    react_path.close()
    canvas.drawPath(react_path, fill=1, stroke=0)

    # SPECIAL (bottom quadrant) - White
    canvas.setFillColor(Color(*colors['special']))
    special_path = canvas.beginPath()
    special_path.moveTo(center_x, center_y)
    special_path.lineTo(*mid_bot_right)
    special_path.lineTo(*bottom)
    special_path.lineTo(*mid_bot_left)
    special_path.close()
    canvas.drawPath(special_path, fill=1, stroke=0)

    # =========================================
    # DRAW THE OUTER BORDER AND DIVIDING LINES
    # =========================================

    canvas.setStrokeColor(Color(0, 0, 0))  # Black
    canvas.setLineWidth(1.0)

    # Outer diamond border only (no internal cross lines)
    diamond_path = canvas.beginPath()
    diamond_path.moveTo(center_x, center_y + half)   # Top
    diamond_path.lineTo(center_x + half, center_y)   # Right
    diamond_path.lineTo(center_x, center_y - half)   # Bottom
    diamond_path.lineTo(center_x - half, center_y)   # Left
    diamond_path.close()
    canvas.drawPath(diamond_path, fill=0, stroke=1)

    # =========================================
    # DRAW THE RATING NUMBERS (CENTERED IN EACH QUADRANT)
    # =========================================

    # Font size scales with diamond size
    font_size = max(8, min(16, size * 0.22))
    canvas.setFont(FONTS['bold'], font_size)
    canvas.setFillColor(Color(0, 0, 0))  # Black text

    # Offset to center of each sub-diamond (halfway from center to corner)
    offset = half * 0.5

    # Vertical adjustment to center text visually
    text_v_offset = font_size * 0.35

    # FIRE number (top quadrant)
    canvas.drawCentredString(center_x, center_y + offset - text_v_offset, str(fire))

    # HEALTH number (left quadrant)
    canvas.drawCentredString(center_x - offset, center_y - text_v_offset, str(health))

    # REACTIVITY number (right quadrant)
    canvas.drawCentredString(center_x + offset, center_y - text_v_offset, str(reactivity))

    # SPECIAL symbol (bottom quadrant) - if provided
    if special:
        canvas.drawCentredString(center_x, center_y - offset - text_v_offset, str(special))


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
