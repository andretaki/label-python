"""Visual effects utilities for premium label rendering.

Implements glow, shadow, and other visual effects for ReportLab.
Since ReportLab doesn't support blur, we simulate effects with layered shapes.
"""

from reportlab.lib.colors import Color


def draw_glow_rect(canvas, x: float, y: float, width: float, height: float,
                   glow_color: tuple, glow_radius: float = 4, glow_opacity: float = 0.3,
                   corner_radius: float = 0, layers: int = 4) -> None:
    """
    Draw a glowing rectangle effect around an area.

    Creates a soft glow by drawing multiple progressively larger,
    more transparent rectangles behind the main shape.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        glow_color: Glow color as (r, g, b) tuple
        glow_radius: Maximum glow spread in points
        glow_opacity: Base opacity of the glow (0-1)
        corner_radius: Corner radius for rounded rectangles
        layers: Number of glow layers (more = smoother)
    """
    canvas.saveState()

    for i in range(layers, 0, -1):
        # Calculate layer properties
        layer_t = i / layers
        layer_spread = glow_radius * layer_t
        layer_opacity = glow_opacity * (1 - layer_t) * 0.7

        if layer_opacity <= 0:
            continue

        # Set color with alpha
        canvas.setFillColor(Color(*glow_color, alpha=layer_opacity))

        # Draw expanded rectangle
        canvas.roundRect(
            x - layer_spread,
            y - layer_spread,
            width + (layer_spread * 2),
            height + (layer_spread * 2),
            corner_radius + layer_spread * 0.5,
            fill=1, stroke=0
        )

    canvas.restoreState()


def draw_glow_line(canvas, x1: float, y1: float, x2: float, y2: float,
                   line_width: float, glow_color: tuple,
                   glow_radius: float = 3, glow_opacity: float = 0.25,
                   layers: int = 3) -> None:
    """
    Draw a glowing line effect.

    Args:
        canvas: ReportLab canvas object
        x1, y1: Start point
        x2, y2: End point
        line_width: Main line width in points
        glow_color: Glow color as (r, g, b) tuple
        glow_radius: Maximum glow spread in points
        glow_opacity: Base opacity of the glow
        layers: Number of glow layers
    """
    canvas.saveState()

    # Draw glow layers (wider, more transparent lines behind)
    for i in range(layers, 0, -1):
        layer_t = i / layers
        layer_width = line_width + (glow_radius * 2 * layer_t)
        layer_opacity = glow_opacity * (1 - layer_t) * 0.8

        if layer_opacity <= 0:
            continue

        canvas.setStrokeColor(Color(*glow_color, alpha=layer_opacity))
        canvas.setLineWidth(layer_width)
        canvas.line(x1, y1, x2, y2)

    canvas.restoreState()


def draw_drop_shadow(canvas, x: float, y: float, width: float, height: float,
                     shadow_color: tuple = (0, 0, 0), shadow_opacity: float = 0.4,
                     offset_x: float = 0, offset_y: float = -2,
                     blur_radius: float = 4, corner_radius: float = 0,
                     layers: int = 3) -> None:
    """
    Draw a drop shadow effect beneath a rectangle.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        shadow_color: Shadow color as (r, g, b) tuple
        shadow_opacity: Maximum shadow opacity
        offset_x: Horizontal shadow offset
        offset_y: Vertical shadow offset (negative = shadow below)
        blur_radius: Shadow blur amount
        corner_radius: Corner radius for rounded rectangles
        layers: Number of blur layers
    """
    canvas.saveState()

    # Draw shadow layers from most spread to least
    for i in range(layers, 0, -1):
        layer_t = i / layers
        layer_spread = blur_radius * layer_t
        layer_opacity = shadow_opacity * (1 - layer_t * 0.7)

        if layer_opacity <= 0:
            continue

        canvas.setFillColor(Color(*shadow_color, alpha=layer_opacity))

        canvas.roundRect(
            x + offset_x - layer_spread * 0.5,
            y + offset_y - layer_spread * 0.5,
            width + layer_spread,
            height + layer_spread,
            corner_radius,
            fill=1, stroke=0
        )

    canvas.restoreState()


def draw_inner_shadow(canvas, x: float, y: float, width: float, height: float,
                      shadow_color: tuple = (0, 0, 0), shadow_opacity: float = 0.2,
                      shadow_size: float = 3, corner_radius: float = 0) -> None:
    """
    Draw a subtle inner shadow at the bottom of a rectangle.

    Creates depth by darkening the bottom edge.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        shadow_color: Shadow color as (r, g, b) tuple
        shadow_opacity: Shadow opacity
        shadow_size: Height of the shadow gradient
        corner_radius: Corner radius for rounded rectangles
    """
    canvas.saveState()

    # Create clipping path to stay within bounds
    path = canvas.beginPath()
    if corner_radius > 0:
        path.roundRect(x, y, width, height, corner_radius)
    else:
        path.rect(x, y, width, height)
    canvas.clipPath(path, stroke=0, fill=0)

    # Draw gradient from bottom
    steps = 5
    for i in range(steps):
        t = i / steps
        layer_height = shadow_size * (1 - t)
        layer_opacity = shadow_opacity * (1 - t)

        canvas.setFillColor(Color(*shadow_color, alpha=layer_opacity))
        canvas.rect(x, y, width, layer_height, fill=1, stroke=0)

    canvas.restoreState()


def draw_text_shadow(canvas, text: str, x: float, y: float,
                     font_name: str, font_size: float,
                     shadow_color: tuple = (0, 0, 0), shadow_opacity: float = 0.5,
                     offset_x: float = 1, offset_y: float = -1) -> None:
    """
    Draw text with a subtle shadow for depth effect.

    Call this BEFORE drawing the main text.

    Args:
        canvas: ReportLab canvas object
        text: Text string to draw
        x: X position in points
        y: Y position in points
        font_name: Font name
        font_size: Font size in points
        shadow_color: Shadow color as (r, g, b) tuple
        shadow_opacity: Shadow opacity
        offset_x: Horizontal shadow offset
        offset_y: Vertical shadow offset
    """
    canvas.saveState()
    canvas.setFont(font_name, font_size)
    canvas.setFillColor(Color(*shadow_color, alpha=shadow_opacity))
    canvas.drawString(x + offset_x, y + offset_y, text)
    canvas.restoreState()


def draw_border_glow(canvas, x: float, y: float, width: float, height: float,
                     border_color: tuple, border_width: float = 1.5,
                     glow_color: tuple = None, glow_radius: float = 3,
                     glow_opacity: float = 0.2, corner_radius: float = 3) -> None:
    """
    Draw a border with outer glow effect.

    Useful for QR codes, data blocks, etc.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        border_color: Border color as (r, g, b) tuple
        border_width: Border width in points
        glow_color: Glow color (defaults to border_color)
        glow_radius: Glow spread in points
        glow_opacity: Glow opacity
        corner_radius: Corner radius
    """
    if glow_color is None:
        glow_color = border_color

    # Draw glow first
    draw_glow_rect(canvas, x, y, width, height,
                   glow_color, glow_radius, glow_opacity,
                   corner_radius)

    # Draw border
    canvas.saveState()
    canvas.setStrokeColor(Color(*border_color))
    canvas.setLineWidth(border_width)
    canvas.roundRect(x, y, width, height, corner_radius, fill=0, stroke=1)
    canvas.restoreState()


def draw_glowing_accent_line(canvas, x: float, y: float, width: float,
                             line_color: tuple, line_height: float = 2,
                             glow_color: tuple = None, glow_radius: float = 3,
                             glow_opacity: float = 0.25) -> None:
    """
    Draw a horizontal accent line with glow effect.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (center of line) in points
        width: Width in points
        line_color: Line color as (r, g, b) tuple
        line_height: Line thickness in points
        glow_color: Glow color (defaults to line_color)
        glow_radius: Glow spread in points
        glow_opacity: Glow opacity
    """
    if glow_color is None:
        glow_color = line_color

    # Draw glow
    draw_glow_rect(canvas, x, y - line_height / 2, width, line_height,
                   glow_color, glow_radius, glow_opacity)

    # Draw solid line
    canvas.saveState()
    canvas.setFillColor(Color(*line_color))
    canvas.rect(x, y - line_height / 2, width, line_height, fill=1, stroke=0)
    canvas.restoreState()
