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


def draw_diagonal_header(canvas, x: float, y: float, width: float, height: float,
                         fill_color: tuple, angle_degrees: float = 4) -> None:
    """
    Draw header with clean diagonal bottom edge.

    The bottom edge slopes down from left to right at the specified angle.
    This creates an architectural/industrial feel and echoes the diagonal
    cut on the left data card.

    Args:
        canvas: ReportLab canvas object
        x: Left edge (usually 0)
        y: Bottom of header at LEFT side
        width: Full width (usually LABEL_WIDTH)
        height: Header height at the LEFT side
        fill_color: RGB(A) tuple
        angle_degrees: Angle of bottom edge (3-5° recommended)
    """
    canvas.saveState()

    # Calculate the drop on the right side based on angle
    angle_rad = math.radians(angle_degrees)
    right_drop = width * math.tan(angle_rad)

    # Set fill color
    if len(fill_color) >= 4:
        canvas.setFillColor(Color(fill_color[0], fill_color[1], fill_color[2], fill_color[3]))
    else:
        canvas.setFillColor(Color(*fill_color[:3]))

    # Build path: rectangle with angled bottom
    path = canvas.beginPath()
    path.moveTo(x, y)  # Bottom-left
    path.lineTo(x, y + height)  # Top-left (sharp corner)
    path.lineTo(x + width, y + height)  # Top-right (sharp corner)
    path.lineTo(x + width, y - right_drop)  # Bottom-right (lower due to angle)
    path.close()

    canvas.drawPath(path, fill=1, stroke=0)
    canvas.restoreState()


def draw_dissolving_header(canvas, x: float, y: float, width: float, height: float,
                           fill_color: tuple, wave_depth: float = 20,
                           wave_count: int = 4) -> None:
    """
    DEPRECATED: Use draw_diagonal_header() instead.

    Draw a header with dissolving/eroding bottom edge.
    Kept for backwards compatibility.
    """
    # Redirect to diagonal header for clean look
    draw_diagonal_header(canvas, x, y, width, height, fill_color, angle_degrees=4)


def _generate_wobble_sequence(seed: float, count: int) -> list:
    """
    Generate a deterministic sequence of wobble values based on seed.

    Uses a simple hash-based approach for reproducible "randomness"
    so the same blob always looks the same.
    """
    wobbles = []
    for i in range(count):
        # Create deterministic pseudo-random value from seed and index
        val = math.sin(seed * 12.9898 + i * 78.233) * 43758.5453
        wobbles.append((val - int(val)) * 2 - 1)  # Range -1 to 1
    return wobbles


def draw_organic_blob(canvas, center_x: float, center_y: float,
                      width: float, height: float, rotation: float,
                      fill_color: tuple, opacity: float = 0.25,
                      curve_tension: float = 0.4,
                      blob_style: str = "watercolor") -> None:
    """
    Draw a truly organic blob shape using irregular bezier curves.

    Creates irregular, flowing shapes like watercolor washes or ink drops -
    NOT geometric ellipses or polygons. Uses 8-12 anchor points with
    wobbled radii and varied control points for true organic feel.

    Args:
        canvas: ReportLab canvas object
        center_x, center_y: Center position of the blob
        width, height: Approximate dimensions
        rotation: Rotation angle in degrees (also serves as shape seed)
        fill_color: RGB color tuple
        opacity: Blob opacity (0.15-0.30 recommended for visibility)
        curve_tension: Influences curve smoothness (0.2-0.5 for organic feel)
        blob_style: "watercolor", "ink_drop", "flowing", "pool", or "rising"
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

    # Half dimensions for calculations
    hw = width / 2
    hh = height / 2

    # Style-specific parameters for anchor count and wobble intensity
    style_params = {
        "watercolor": {"anchors": 10, "wobble": 0.35, "asymmetry": 0.25},
        "ink_drop": {"anchors": 9, "wobble": 0.30, "asymmetry": 0.20},
        "flowing": {"anchors": 11, "wobble": 0.40, "asymmetry": 0.35},
        "pool": {"anchors": 8, "wobble": 0.20, "asymmetry": 0.15},
        "rising": {"anchors": 10, "wobble": 0.32, "asymmetry": 0.28},
    }

    params = style_params.get(blob_style, style_params["watercolor"])
    num_anchors = params["anchors"]
    wobble_intensity = params["wobble"]
    asymmetry = params["asymmetry"]

    # Use rotation as seed for deterministic wobble
    seed = rotation + (ord(blob_style[0]) if blob_style else 0)

    # Generate wobble sequences for radius, angle offset, and control points
    radius_wobbles = _generate_wobble_sequence(seed, num_anchors)
    angle_wobbles = _generate_wobble_sequence(seed + 100, num_anchors)
    ctrl_wobbles = _generate_wobble_sequence(seed + 200, num_anchors * 2)

    # Style-specific base shape modifications
    # These create the general character while wobbles add irregularity
    style_mods = {
        "watercolor": lambda a: 1.0 + 0.15 * math.sin(a * 2.3) - 0.1 * math.cos(a * 1.7),
        "ink_drop": lambda a: 0.9 + 0.2 * math.sin(a - 0.5) + 0.1 * math.cos(a * 2),
        "flowing": lambda a: 1.0 + 0.25 * math.sin(a * 1.5 + 0.8) - 0.15 * math.cos(a * 0.7),
        "pool": lambda a: 0.95 + 0.1 * math.sin(a * 1.2) + 0.08 * math.cos(a * 2.5),
        "rising": lambda a: 1.0 + 0.2 * math.sin(a + 1.2) + 0.15 * math.cos(a * 1.8 - 0.3),
    }
    style_mod = style_mods.get(blob_style, style_mods["watercolor"])

    # Generate anchor points around the perimeter with wobble
    anchors = []
    for i in range(num_anchors):
        # Base angle evenly distributed
        base_angle = (2 * math.pi * i / num_anchors)

        # Add angle wobble (shifts point position along perimeter)
        angle = base_angle + angle_wobbles[i] * 0.25

        # Base radius (ellipse) with style modification
        base_r_x = hw * style_mod(angle)
        base_r_y = hh * style_mod(angle + 0.5)  # Slight offset for asymmetry

        # Apply radius wobble (makes shape irregular)
        wobble_factor = 1.0 + radius_wobbles[i] * wobble_intensity

        # Additional asymmetry based on quadrant
        quadrant_factor = 1.0 + asymmetry * math.sin(angle * 1.3 + seed * 0.1)

        # Calculate final point
        r_x = base_r_x * wobble_factor * quadrant_factor
        r_y = base_r_y * wobble_factor * quadrant_factor

        x = r_x * math.cos(angle)
        y = r_y * math.sin(angle)

        anchors.append((x, y, angle))

    # Build path with bezier curves between anchors
    path = canvas.beginPath()
    path.moveTo(anchors[0][0], anchors[0][1])

    for i in range(num_anchors):
        curr = anchors[i]
        next_idx = (i + 1) % num_anchors
        next_pt = anchors[next_idx]

        # Calculate control points with wobble for organic curves
        # Distance between points
        dx = next_pt[0] - curr[0]
        dy = next_pt[1] - curr[1]
        dist = math.sqrt(dx * dx + dy * dy)

        # Tangent directions (perpendicular-ish to radius)
        curr_tangent_x = -math.sin(curr[2])
        curr_tangent_y = math.cos(curr[2])
        next_tangent_x = -math.sin(next_pt[2])
        next_tangent_y = math.cos(next_pt[2])

        # Control point distance with wobble
        ctrl_dist = dist * (0.3 + curve_tension * 0.2)
        ctrl1_wobble = 1.0 + ctrl_wobbles[i * 2] * 0.4
        ctrl2_wobble = 1.0 + ctrl_wobbles[i * 2 + 1] * 0.4

        # First control point (leaving current anchor)
        ctrl1_x = curr[0] + curr_tangent_x * ctrl_dist * ctrl1_wobble
        ctrl1_y = curr[1] + curr_tangent_y * ctrl_dist * ctrl1_wobble

        # Second control point (approaching next anchor)
        ctrl2_x = next_pt[0] - next_tangent_x * ctrl_dist * ctrl2_wobble
        ctrl2_y = next_pt[1] - next_tangent_y * ctrl_dist * ctrl2_wobble

        path.curveTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, next_pt[0], next_pt[1])

    path.close()
    canvas.drawPath(path, fill=1, stroke=0)
    canvas.restoreState()


def get_blob_positions(arrangement: str, label_width: float, label_height: float,
                       scale: float = 1.0) -> list:
    """
    Get blob positions and sizes based on arrangement type.

    Returns list of (center_x, center_y, width, height, rotation, blob_style) tuples.

    CRITICAL: Blobs are FAR-RIGHT DECORATIVE BAND ONLY.
    They must NEVER cross the content zones (columns 1-2).
    Position them at x > 85% of width, in the "decor gutter".
    """
    w, h = label_width, label_height

    # All arrangements: single subtle blob in far-right decorative band
    # This ensures blobs never compete with content
    if arrangement == "diagonal_sweep":
        return [
            (w * 0.92, h * 0.35, 60 * scale, 45 * scale, -12, "watercolor"),
        ]

    elif arrangement == "angular_clash":
        return [
            (w * 0.90, h * 0.30, 55 * scale, 40 * scale, -20, "ink_drop"),
        ]

    elif arrangement == "rising_flow":
        return [
            (w * 0.92, h * 0.32, 55 * scale, 40 * scale, 15, "rising"),
        ]

    elif arrangement == "slow_pool":
        return [
            (w * 0.91, h * 0.28, 60 * scale, 50 * scale, 5, "pool"),
        ]

    elif arrangement == "contained_circles":
        return [
            (w * 0.90, h * 0.30, 50 * scale, 45 * scale, 0, "pool"),
        ]

    elif arrangement == "dynamic_intersect":
        return [
            (w * 0.92, h * 0.32, 55 * scale, 40 * scale, -8, "watercolor"),
        ]

    # Default fallback
    return [
        (w * 0.92, h * 0.30, 55 * scale, 40 * scale, -8, "watercolor"),
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


def draw_diagonal_cut_panel(canvas, x: float, y: float, width: float, height: float,
                            cut_angle: float = 15,
                            fill_color: tuple = (1, 1, 1),
                            opacity: float = 0.90,
                            border_color: tuple = None,
                            border_opacity: float = 0.35,
                            shadow: bool = True,
                            shadow_opacity: float = 0.08,
                            shadow_offset: float = 2,
                            shadow_blur: float = 4) -> None:
    """
    Draw a frosted panel with diagonal cut on bottom-right corner.

    This is the signature "ownable" element that makes Alliance labels recognizable.
    The cut removes the bottom-right corner at the specified angle.

    Args:
        canvas: ReportLab canvas object
        x, y: Position (bottom-left)
        width, height: Dimensions
        cut_angle: Angle of the diagonal cut in degrees (default 15°)
        fill_color: Panel fill color (RGB tuple)
        opacity: Panel opacity
        border_color: Optional border color (RGB tuple)
        border_opacity: Border transparency
        shadow: Whether to draw drop shadow
        shadow_opacity: Shadow darkness
        shadow_offset: Shadow offset in points
        shadow_blur: Shadow blur radius
    """
    canvas.saveState()

    # Calculate cut dimensions for visible diagonal cut
    # Cut removes bottom-right corner: 26% of height, 28% of width
    # This creates a clearly visible, assertive signature element
    cut_depth = height * 0.26      # How high up the right edge the cut ends
    cut_horizontal = width * 0.28  # How far from right edge the cut starts on bottom

    def draw_cut_shape(sx, sy, sw, sh, cut_h, cut_d):
        """Draw panel with diagonal cut using simple lines (no arcs for reliability)."""
        path = canvas.beginPath()
        # Start bottom-left, go clockwise
        path.moveTo(sx, sy)                           # Bottom-left corner
        path.lineTo(sx + sw - cut_h, sy)              # Bottom edge to cut start
        path.lineTo(sx + sw, sy + cut_d)              # Diagonal cut upward
        path.lineTo(sx + sw, sy + sh)                 # Right edge to top
        path.lineTo(sx, sy + sh)                      # Top edge
        path.lineTo(sx, sy)                           # Left edge back to start
        path.close()
        return path

    # Draw shadow
    if shadow:
        for i in range(3, 0, -1):
            layer_t = i / 3
            layer_opacity = shadow_opacity * (1 - layer_t * 0.5)
            canvas.setFillColor(Color(0, 0, 0, layer_opacity))
            path = draw_cut_shape(
                x + shadow_offset * layer_t,
                y - shadow_offset * layer_t,
                width, height, cut_horizontal, cut_depth
            )
            canvas.drawPath(path, fill=1, stroke=0)

    # Draw main panel
    canvas.setFillColor(Color(*fill_color[:3], opacity))
    path = draw_cut_shape(x, y, width, height, cut_horizontal, cut_depth)
    canvas.drawPath(path, fill=1, stroke=0)

    # Draw border
    if border_color:
        canvas.setStrokeColor(Color(*border_color[:3], border_opacity))
        canvas.setLineWidth(1)
        path = draw_cut_shape(x, y, width, height, cut_horizontal, cut_depth)
        canvas.drawPath(path, fill=0, stroke=1)

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
