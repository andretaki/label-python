"""Gradient rendering utilities for ReportLab.

ReportLab doesn't have native gradient fill support, so we simulate gradients
using multiple thin rectangles with interpolated colors.
"""

from reportlab.lib.colors import Color


def interpolate_color(color1: tuple, color2: tuple, t: float) -> tuple:
    """
    Linearly interpolate between two RGB colors.

    Args:
        color1: Start color as (r, g, b) tuple (0-1 range)
        color2: End color as (r, g, b) tuple (0-1 range)
        t: Interpolation factor (0 = color1, 1 = color2)

    Returns:
        Interpolated color as (r, g, b) tuple
    """
    t = max(0, min(1, t))  # Clamp to [0, 1]
    return (
        color1[0] + (color2[0] - color1[0]) * t,
        color1[1] + (color2[1] - color1[1]) * t,
        color1[2] + (color2[2] - color1[2]) * t,
    )


def interpolate_color_multi(color_stops: list, t: float) -> tuple:
    """
    Interpolate through multiple color stops.

    Args:
        color_stops: List of (position, color) tuples where position is 0-1
                    and color is (r, g, b) tuple
        t: Position along gradient (0-1)

    Returns:
        Interpolated color as (r, g, b) tuple
    """
    if not color_stops:
        return (0, 0, 0)

    if len(color_stops) == 1:
        return color_stops[0][1]

    # Sort by position
    stops = sorted(color_stops, key=lambda x: x[0])

    # Find surrounding stops
    for i in range(len(stops) - 1):
        pos1, color1 = stops[i]
        pos2, color2 = stops[i + 1]

        if pos1 <= t <= pos2:
            # Interpolate between these stops
            segment_t = (t - pos1) / (pos2 - pos1) if pos2 != pos1 else 0
            return interpolate_color(color1, color2, segment_t)

    # If t is outside range, return nearest endpoint
    if t <= stops[0][0]:
        return stops[0][1]
    return stops[-1][1]


def draw_horizontal_gradient(canvas, x: float, y: float, width: float, height: float,
                             color_stops: list, steps: int = 50) -> None:
    """
    Draw a horizontal linear gradient (left to right).

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        color_stops: List of (position, color) tuples
        steps: Number of gradient steps (more = smoother)
    """
    step_width = width / steps

    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        color = interpolate_color_multi(color_stops, t)
        canvas.setFillColor(Color(*color))
        # Add 0.5 to step_width to prevent gaps
        canvas.rect(x + (i * step_width), y, step_width + 0.5, height, fill=1, stroke=0)


def draw_vertical_gradient(canvas, x: float, y: float, width: float, height: float,
                           color_stops: list, steps: int = 50) -> None:
    """
    Draw a vertical linear gradient (bottom to top).

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        color_stops: List of (position, color) tuples where 0 = bottom, 1 = top
        steps: Number of gradient steps (more = smoother)
    """
    step_height = height / steps

    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        color = interpolate_color_multi(color_stops, t)
        canvas.setFillColor(Color(*color))
        # Add 0.5 to step_height to prevent gaps
        canvas.rect(x, y + (i * step_height), width, step_height + 0.5, fill=1, stroke=0)


def draw_gradient_line(canvas, x: float, y: float, width: float, height: float,
                       color_stops: list, steps: int = 30) -> None:
    """
    Draw a gradient-filled horizontal line (accent line style).

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Line height in points (typically 1.5-2)
        color_stops: List of (position, color) tuples
        steps: Number of gradient steps
    """
    draw_horizontal_gradient(canvas, x, y, width, height, color_stops, steps)


def draw_brushed_metal_gradient(canvas, x: float, y: float, width: float, height: float,
                                base_color: tuple, highlight_color: tuple,
                                steps: int = 50) -> None:
    """
    Draw a brushed metal effect gradient (darker edges, lighter center).

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        base_color: Edge color as (r, g, b) tuple
        highlight_color: Center highlight color as (r, g, b) tuple
        steps: Number of gradient steps
    """
    color_stops = [
        (0.0, base_color),
        (0.5, highlight_color),
        (1.0, base_color),
    ]
    draw_horizontal_gradient(canvas, x, y, width, height, color_stops, steps)


def draw_vignette_background(canvas, x: float, y: float, width: float, height: float,
                             center_color: tuple, edge_color: tuple,
                             steps: int = 30) -> None:
    """
    Draw a radial vignette effect (approximated with layered rectangles).

    This creates a subtle darkening toward the edges.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Width in points
        height: Height in points
        center_color: Center (lighter) color
        edge_color: Edge (darker) color
        steps: Number of gradient steps
    """
    # Fill with edge color first
    canvas.setFillColor(Color(*edge_color))
    canvas.rect(x, y, width, height, fill=1, stroke=0)

    # Layer progressively smaller, lighter rectangles
    for i in range(steps, 0, -1):
        t = i / steps
        inset = (1 - t) * min(width, height) * 0.15  # Max 15% inset

        if inset * 2 >= min(width, height):
            continue

        color = interpolate_color(center_color, edge_color, 1 - t)
        alpha = t * 0.5 + 0.5  # Fade alpha from 0.5 to 1.0

        canvas.setFillColor(Color(*color, alpha=alpha))
        canvas.rect(
            x + inset,
            y + inset,
            width - (inset * 2),
            height - (inset * 2),
            fill=1, stroke=0
        )
