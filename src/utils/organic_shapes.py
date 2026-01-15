"""Organic shape utilities for flowing, dimensional label designs.

Implements diagonal gradients, organic bezier blobs, dissolving edges,
and frosted glass panel effects.

v2 - Critical fixes:
- Diagonal gradient now VISIBLE (more saturated colors)
- Dissolving header has proper bezier wave curves
- Blobs are more prominent and use signature arrangements
- Added soft shadow utilities for depth
"""

import math
from reportlab.lib.colors import Color


def interpolate_color(color1: tuple, color2: tuple, t: float) -> tuple:
    """Linearly interpolate between two RGB(A) colors."""
    t = max(0, min(1, t))
    if len(color1) == 3:
        color1 = (*color1, 1.0)
    if len(color2) == 3:
        color2 = (*color2, 1.0)
    return tuple(c1 + (c2 - c1) * t for c1, c2 in zip(color1, color2))


def interpolate_color_stops(color_stops: list, t: float) -> tuple:
    """Interpolate through multiple color stops."""
    if not color_stops:
        return (1, 1, 1)
    if len(color_stops) == 1:
        return color_stops[0][1]

    stops = sorted(color_stops, key=lambda x: x[0])

    for i in range(len(stops) - 1):
        pos1, color1 = stops[i]
        pos2, color2 = stops[i + 1]

        if pos1 <= t <= pos2:
            segment_t = (t - pos1) / (pos2 - pos1) if pos2 != pos1 else 0
            return interpolate_color(color1, color2, segment_t)

    if t <= stops[0][0]:
        return stops[0][1]
    return stops[-1][1]


def draw_diagonal_gradient(canvas, x: float, y: float, width: float, height: float,
                           color_stops: list, steps: int = 60) -> None:
    """
    Draw a VISIBLE diagonal gradient from top-left (warm) to bottom-right (cool).

    Uses horizontal strips with colors sampled along the diagonal.
    The gradient should be clearly perceptible, not subtle.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge)
        y: Y position (bottom edge)
        width: Width in points
        height: Height in points
        color_stops: List of (position, color) tuples
        steps: Number of gradient bands
    """
    canvas.saveState()

    # We'll draw horizontal strips, but sample color based on diagonal position
    # This creates a diagonal gradient effect
    step_height = height / steps

    for i in range(steps):
        # Calculate the diagonal position for this strip
        # Top of label = 0, bottom = 1
        strip_y = y + height - (i + 0.5) * step_height
        strip_center_y_ratio = 1 - (strip_y - y) / height

        # Sample along diagonal: combine y position with x bias
        # This creates the top-left to bottom-right flow
        # At top (y_ratio=0): more warm
        # At bottom (y_ratio=1): more cool
        t = strip_center_y_ratio

        # Add slight horizontal variation within the strip
        # Left side slightly warmer, right side slightly cooler
        color = interpolate_color_stops(color_stops, t)

        if len(color) >= 4:
            canvas.setFillColor(Color(color[0], color[1], color[2], color[3]))
        else:
            canvas.setFillColor(Color(*color[:3]))

        # Draw strip with slight overlap to prevent gaps
        canvas.rect(x, strip_y - step_height / 2, width, step_height + 1, fill=1, stroke=0)

    canvas.restoreState()


def draw_diagonal_gradient_v2(canvas, x: float, y: float, width: float, height: float,
                              warm_color: tuple, cool_color: tuple,
                              mid_warm: tuple = None, mid_cool: tuple = None,
                              steps: int = 80) -> None:
    """
    Draw a more visible diagonal gradient using explicit warm/cool colors.

    This version creates a more pronounced diagonal effect by varying
    color across both X and Y axes.

    Args:
        canvas: ReportLab canvas object
        x, y: Position (bottom-left)
        width, height: Dimensions
        warm_color: Top-left color (RGB tuple)
        cool_color: Bottom-right color (RGB tuple)
        mid_warm: Optional mid-warm color
        mid_cool: Optional mid-cool color
        steps: Number of gradient steps
    """
    canvas.saveState()

    # Clip to bounds
    path = canvas.beginPath()
    path.rect(x, y, width, height)
    canvas.clipPath(path, stroke=0, fill=0)

    # Draw diagonal strips
    diagonal = math.sqrt(width ** 2 + height ** 2)
    strip_width = diagonal / steps * 1.5  # Overlap strips

    for i in range(steps + 5):
        t = i / steps

        # Calculate color at this diagonal position
        if mid_warm and mid_cool and t < 0.5:
            # First half: warm to mid-warm
            local_t = t * 2
            color = interpolate_color(warm_color, mid_warm, local_t)
        elif mid_warm and mid_cool:
            # Second half: mid-cool to cool
            local_t = (t - 0.5) * 2
            color = interpolate_color(mid_cool, cool_color, local_t)
        else:
            color = interpolate_color(warm_color, cool_color, t)

        canvas.setFillColor(Color(*color[:3]))

        # Position along diagonal
        offset = i * (diagonal / steps)

        # Draw a wide strip perpendicular to diagonal
        # Start from top-left corner
        cx = x + offset * math.cos(math.pi / 4)
        cy = y + height - offset * math.sin(math.pi / 4)

        # Create rotated rectangle
        canvas.saveState()
        canvas.translate(cx, cy)
        canvas.rotate(-45)
        canvas.rect(-diagonal, -strip_width / 2, diagonal * 2, strip_width, fill=1, stroke=0)
        canvas.restoreState()

    canvas.restoreState()


def draw_dissolving_header(canvas, x: float, y: float, width: float, height: float,
                           fill_color: tuple, wave_depth: float = 20,
                           wave_count: int = 4) -> None:
    """
    Draw a header with dissolving/wave bottom edge.

    Sharp at top, organic curved edge at bottom that melts into content.
    Uses proper bezier curves for smooth wave undulations.

    Args:
        canvas: ReportLab canvas object
        x: X position (left edge)
        y: Y position (bottom of wave troughs)
        width: Width in points
        height: Height in points
        fill_color: RGB(A) color tuple for the header
        wave_depth: How deep the waves extend (15-25pt recommended)
        wave_count: Number of wave undulations (3-5 recommended)
    """
    canvas.saveState()

    if len(fill_color) >= 4:
        canvas.setFillColor(Color(fill_color[0], fill_color[1], fill_color[2], fill_color[3]))
    else:
        canvas.setFillColor(Color(*fill_color))

    path = canvas.beginPath()

    # Start at bottom-left
    path.moveTo(x, y)

    # Draw wavy bottom edge using bezier curves
    wave_width = width / wave_count

    for i in range(wave_count):
        wave_start_x = x + i * wave_width
        wave_end_x = wave_start_x + wave_width

        # Vary wave depth for organic feel
        # Diagonal flow: waves get slightly deeper toward the right
        depth_factor = 0.7 + 0.6 * (i / wave_count)
        current_depth = wave_depth * depth_factor

        # Also offset the wave baseline diagonally (higher on left, lower on right)
        baseline_offset = -8 * (i / wave_count)

        # Control points for smooth bezier curve
        # Each wave has a peak (up) and trough (down)
        ctrl1_x = wave_start_x + wave_width * 0.25
        ctrl1_y = y + baseline_offset + current_depth * 0.8  # Rise

        peak_x = wave_start_x + wave_width * 0.5
        peak_y = y + baseline_offset - current_depth * 0.3  # Dip down

        ctrl2_x = wave_start_x + wave_width * 0.75
        ctrl2_y = y + baseline_offset + current_depth * 0.5  # Rise back

        # Bezier curve for this wave segment
        path.curveTo(ctrl1_x, ctrl1_y, peak_x, peak_y, wave_end_x, y + baseline_offset - 5)

    # Up the right edge
    path.lineTo(x + width, y + height)

    # Across the top (sharp edge)
    path.lineTo(x, y + height)

    # Close
    path.close()

    canvas.drawPath(path, fill=1, stroke=0)
    canvas.restoreState()


def draw_organic_blob(canvas, center_x: float, center_y: float,
                      width: float, height: float, rotation: float,
                      fill_color: tuple, opacity: float = 0.25,
                      curve_tension: float = 0.4) -> None:
    """
    Draw a single organic blob shape using smooth bezier curves.

    The blob is an irregular, organic shape - not a circle or ellipse.
    Curve tension controls how smooth vs angular the curves are.

    Args:
        canvas: ReportLab canvas object
        center_x, center_y: Center position of the blob
        width, height: Approximate dimensions
        rotation: Rotation angle in degrees
        fill_color: RGB color tuple
        opacity: Blob opacity (0.15-0.30 recommended for visibility)
        curve_tension: 0.2 = very smooth, 0.7 = more angular
    """
    canvas.saveState()

    # Set fill color with opacity
    if len(fill_color) >= 4:
        canvas.setFillColor(Color(fill_color[0], fill_color[1], fill_color[2],
                                  fill_color[3] * opacity))
    else:
        canvas.setFillColor(Color(*fill_color, opacity))

    # Translate and rotate
    canvas.translate(center_x, center_y)
    canvas.rotate(rotation)

    # Generate organic blob points
    # Use 6-8 control points for natural shape
    num_points = 6
    points = []

    for i in range(num_points):
        angle = (2 * math.pi * i / num_points) - math.pi / 2

        # Vary radius for organic feel
        # Add some randomness based on index (deterministic)
        radius_variance = 0.15 + 0.1 * math.sin(i * 2.5)
        rx = (width / 2) * (1 + radius_variance * math.cos(i * 1.7))
        ry = (height / 2) * (1 + radius_variance * math.sin(i * 1.3))

        px = rx * math.cos(angle)
        py = ry * math.sin(angle)
        points.append((px, py))

    # Draw smooth closed curve through points
    path = canvas.beginPath()

    if len(points) >= 3:
        # Start at first point
        path.moveTo(points[0][0], points[0][1])

        # Draw bezier curves between points
        n = len(points)
        tension = curve_tension

        for i in range(n):
            p0 = points[i]
            p1 = points[(i + 1) % n]
            p2 = points[(i + 2) % n]

            # Calculate control points based on tension
            # Lower tension = smoother curves
            ctrl1_x = p0[0] + (p1[0] - points[(i - 1) % n][0]) * tension
            ctrl1_y = p0[1] + (p1[1] - points[(i - 1) % n][1]) * tension
            ctrl2_x = p1[0] - (p2[0] - p0[0]) * tension
            ctrl2_y = p1[1] - (p2[1] - p0[1]) * tension

            path.curveTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, p1[0], p1[1])

        path.close()

    canvas.drawPath(path, fill=1, stroke=0)
    canvas.restoreState()


def get_blob_positions(arrangement: str, label_width: float, label_height: float,
                       scale: float = 1.0) -> list:
    """
    Get blob positions and sizes based on arrangement type.

    Returns list of (center_x, center_y, width, height, rotation) tuples.
    """
    if arrangement == "diagonal_sweep":
        # Flowing diagonal sweep - smooth, liquid feel
        return [
            (label_width * 0.25, label_height * 0.72, 200 * scale, 140 * scale, -15),
            (label_width * 0.55, label_height * 0.48, 160 * scale, 110 * scale, -20),
            (label_width * 0.82, label_height * 0.28, 120 * scale, 90 * scale, -25),
        ]

    elif arrangement == "angular_clash":
        # Angular, aggressive - sharper, more energetic
        return [
            (label_width * 0.30, label_height * 0.68, 180 * scale, 110 * scale, -35),
            (label_width * 0.72, label_height * 0.32, 160 * scale, 100 * scale, 20),
        ]

    elif arrangement == "rising_flow":
        # Rising curves - upward energy
        return [
            (label_width * 0.22, label_height * 0.38, 170 * scale, 120 * scale, 25),
            (label_width * 0.52, label_height * 0.55, 150 * scale, 105 * scale, 30),
            (label_width * 0.78, label_height * 0.72, 120 * scale, 85 * scale, 35),
        ]

    elif arrangement == "slow_pool":
        # Smooth, slow, rounded - viscous feel
        return [
            (label_width * 0.35, label_height * 0.58, 220 * scale, 180 * scale, 5),
            (label_width * 0.72, label_height * 0.38, 170 * scale, 140 * scale, -5),
        ]

    elif arrangement == "contained_circles":
        # Clean, contained - safe/pure feel
        return [
            (label_width * 0.32, label_height * 0.52, 150 * scale, 140 * scale, 0),
            (label_width * 0.72, label_height * 0.42, 130 * scale, 120 * scale, 0),
        ]

    elif arrangement == "dynamic_intersect":
        # Dynamic, intersecting - premium feel
        return [
            (label_width * 0.28, label_height * 0.62, 190 * scale, 125 * scale, -12),
            (label_width * 0.52, label_height * 0.52, 170 * scale, 115 * scale, 8),
            (label_width * 0.76, label_height * 0.38, 140 * scale, 95 * scale, -8),
        ]

    # Default fallback
    return [
        (label_width * 0.3, label_height * 0.6, 180 * scale, 120 * scale, -10),
        (label_width * 0.7, label_height * 0.4, 150 * scale, 100 * scale, 10),
    ]


def draw_frosted_panel(canvas, x: float, y: float, width: float, height: float,
                       opacity: float = 0.82, corner_radius: float = 4,
                       border_color: tuple = None, border_opacity: float = 0.4,
                       border_width: float = 1, shadow: bool = True,
                       shadow_opacity: float = 0.12, shadow_offset: float = 3,
                       shadow_blur: float = 6) -> None:
    """
    Draw a frosted glass panel effect with proper depth shadow.

    The panel is semi-transparent so the gradient shows through.
    Includes soft drop shadow for dimensional lift.

    Args:
        canvas: ReportLab canvas object
        x, y: Position (bottom-left)
        width, height: Dimensions
        opacity: Panel opacity (0.75-0.85 recommended)
        corner_radius: Corner radius (4-6 for sharp but soft)
        border_color: Optional border color (RGB tuple)
        border_opacity: Border transparency
        border_width: Border width in points
        shadow: Whether to draw drop shadow
        shadow_opacity: Shadow darkness (0.10-0.15 for subtle)
        shadow_offset: Shadow offset in points
        shadow_blur: Shadow blur radius
    """
    canvas.saveState()

    # Draw soft drop shadow for depth (multiple layers for blur effect)
    if shadow:
        blur_steps = 4
        for i in range(blur_steps, 0, -1):
            layer_t = i / blur_steps
            layer_offset = shadow_offset * layer_t
            layer_blur = shadow_blur * layer_t
            layer_opacity = shadow_opacity * (1 - layer_t * 0.5)

            canvas.setFillColor(Color(0, 0, 0, layer_opacity))
            if corner_radius > 0:
                canvas.roundRect(
                    x + layer_offset - layer_blur / 2,
                    y - layer_offset - layer_blur / 2,
                    width + layer_blur,
                    height + layer_blur,
                    corner_radius + layer_blur / 4,
                    fill=1, stroke=0
                )
            else:
                canvas.rect(
                    x + layer_offset - layer_blur / 2,
                    y - layer_offset - layer_blur / 2,
                    width + layer_blur,
                    height + layer_blur,
                    fill=1, stroke=0
                )

    # Draw frosted glass panel
    canvas.setFillColor(Color(1, 1, 1, opacity))
    if corner_radius > 0:
        canvas.roundRect(x, y, width, height, corner_radius, fill=1, stroke=0)
    else:
        canvas.rect(x, y, width, height, fill=1, stroke=0)

    # Draw border if specified
    if border_color:
        canvas.setStrokeColor(Color(*border_color[:3], border_opacity))
        canvas.setLineWidth(border_width)
        if corner_radius > 0:
            canvas.roundRect(x, y, width, height, corner_radius, fill=0, stroke=1)
        else:
            canvas.rect(x, y, width, height, fill=0, stroke=1)

    canvas.restoreState()


def draw_floating_pill(canvas, x: float, y: float, width: float, height: float,
                       fill_color: tuple = (1, 1, 1), opacity: float = 0.92,
                       border_color: tuple = None, border_opacity: float = 0.3,
                       shadow: bool = True) -> None:
    """
    Draw a floating pill-shaped element (for footer).

    Pill has fully rounded ends (radius = height/2).
    """
    canvas.saveState()

    radius = height / 2

    # Draw shadow
    if shadow:
        for i in range(3, 0, -1):
            layer_t = i / 3
            canvas.setFillColor(Color(0, 0, 0, 0.08 * (1 - layer_t * 0.5)))
            canvas.roundRect(
                x + 2 * layer_t,
                y - 3 * layer_t,
                width + 4 * layer_t,
                height + 2 * layer_t,
                radius + layer_t,
                fill=1, stroke=0
            )

    # Draw pill body
    canvas.setFillColor(Color(*fill_color[:3], opacity))
    canvas.roundRect(x, y, width, height, radius, fill=1, stroke=0)

    # Draw border
    if border_color:
        canvas.setStrokeColor(Color(*border_color[:3], border_opacity))
        canvas.setLineWidth(0.75)
        canvas.roundRect(x, y, width, height, radius, fill=0, stroke=1)

    canvas.restoreState()


def draw_soft_shadow(canvas, x: float, y: float, width: float, height: float,
                     opacity: float = 0.15, offset_x: float = 2, offset_y: float = -3,
                     blur: float = 8, corner_radius: float = 0) -> None:
    """
    Draw a soft, diffused drop shadow.

    Args:
        canvas: ReportLab canvas object
        x, y: Position of the element casting the shadow
        width, height: Element dimensions
        opacity: Shadow darkness (0.10-0.20 for subtle)
        offset_x, offset_y: Shadow offset (positive x = right, negative y = down)
        blur: Blur radius
        corner_radius: Corner radius of the shape
    """
    canvas.saveState()

    # Multiple layers for blur effect
    layers = 5
    for i in range(layers, 0, -1):
        layer_t = i / layers
        layer_blur = blur * layer_t
        layer_opacity = opacity * (1 - layer_t * 0.6)

        canvas.setFillColor(Color(0, 0, 0, layer_opacity))

        sx = x + offset_x - layer_blur / 2
        sy = y + offset_y - layer_blur / 2
        sw = width + layer_blur
        sh = height + layer_blur

        if corner_radius > 0:
            canvas.roundRect(sx, sy, sw, sh, corner_radius + layer_blur / 3, fill=1, stroke=0)
        else:
            canvas.rect(sx, sy, sw, sh, fill=1, stroke=0)

    canvas.restoreState()


def draw_text_glow(canvas, text: str, x: float, y: float,
                   font_name: str, font_size: float,
                   glow_color: tuple, glow_opacity: float = 0.15,
                   glow_radius: float = 6) -> None:
    """
    Draw a soft glow behind text for dimensional lift.

    Call this BEFORE drawing the main text.
    """
    canvas.saveState()

    # Draw multiple layers of text with increasing size/opacity
    layers = 4
    for i in range(layers, 0, -1):
        layer_t = i / layers
        layer_size = font_size + glow_radius * layer_t
        layer_opacity = glow_opacity * (1 - layer_t * 0.7)

        canvas.setFont(font_name, layer_size)
        canvas.setFillColor(Color(*glow_color[:3], layer_opacity))

        # Offset to keep centered
        offset = (layer_size - font_size) / 2
        canvas.drawString(x - offset, y - offset * 0.3, text)

    canvas.restoreState()


def draw_text_shadow(canvas, text: str, x: float, y: float,
                     font_name: str, font_size: float,
                     shadow_color: tuple = (0, 0, 0),
                     shadow_opacity: float = 0.2,
                     offset_x: float = 1.5, offset_y: float = -2,
                     blur_layers: int = 3) -> None:
    """
    Draw a soft shadow behind text for dimensional lift.

    Call this BEFORE drawing the main text.
    """
    canvas.saveState()
    canvas.setFont(font_name, font_size)

    for i in range(blur_layers, 0, -1):
        layer_t = i / blur_layers
        layer_opacity = shadow_opacity * (1 - layer_t * 0.5)
        layer_offset_x = offset_x * layer_t
        layer_offset_y = offset_y * layer_t

        canvas.setFillColor(Color(*shadow_color[:3], layer_opacity))
        canvas.drawString(x + layer_offset_x, y + layer_offset_y, text)

    canvas.restoreState()
