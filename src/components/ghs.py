"""GHS pictogram rendering - dark card style with teal accents.

GHS pictograms are displayed inside dark card containers with teal borders
for premium tech-industrial aesthetic on white background.
"""

from pathlib import Path
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color

from src.config import GHS_ASSETS_DIR, GHS_PICTOGRAM_SIZE, GHS_CARD_SIZE, COLORS


def get_ghs_path(pictogram_id: str) -> Path:
    """
    Get the file path for a GHS pictogram PNG.

    Args:
        pictogram_id: GHS pictogram identifier (e.g., "GHS02", "GHS07")

    Returns:
        Path to the PNG file
    """
    # Handle both enum values and string IDs
    if hasattr(pictogram_id, 'value'):
        pictogram_id = pictogram_id.value

    png_path = GHS_ASSETS_DIR / f"{pictogram_id}.png"

    if not png_path.exists():
        raise FileNotFoundError(f"GHS pictogram not found: {png_path}")

    return png_path


def _draw_ghs_card_glow(canvas, x: float, y: float, size: float,
                        glow_color: tuple, glow_radius: float = 3,
                        glow_opacity: float = 0.2, corner_radius: float = 6) -> None:
    """Draw outer glow effect for GHS card."""
    canvas.saveState()
    layers = 4
    for i in range(layers, 0, -1):
        layer_t = i / layers
        layer_spread = glow_radius * layer_t
        layer_opacity = glow_opacity * (1 - layer_t) * 0.7

        if layer_opacity <= 0:
            continue

        canvas.setFillColor(Color(*glow_color, alpha=layer_opacity))
        canvas.roundRect(
            x - layer_spread,
            y - layer_spread,
            size + (layer_spread * 2),
            size + (layer_spread * 2),
            corner_radius + layer_spread * 0.5,
            fill=1, stroke=0
        )
    canvas.restoreState()


def _draw_ghs_card_shadow(canvas, x: float, y: float, size: float,
                          corner_radius: float = 6) -> None:
    """Draw drop shadow for GHS card."""
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
            size + layer_spread,
            size + layer_spread,
            corner_radius,
            fill=1, stroke=0
        )
    canvas.restoreState()


def draw_ghs_pictogram_card(canvas, pictogram_id: str, x: float, y: float,
                            card_size: float = None) -> None:
    """
    Draw a GHS pictogram inside a dark card with teal border.

    Dark card container creates premium tech-industrial aesthetic on white background.
    The pictogram itself sits on a WHITE background (GHS standard requirement).

    Args:
        canvas: ReportLab canvas object
        pictogram_id: GHS pictogram identifier (e.g., "GHS02")
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        card_size: Outer card size in points (default from config)
    """
    if card_size is None:
        card_size = GHS_CARD_SIZE

    corner_radius = 6
    border_width = 2
    padding = 4  # Padding between card edge and pictogram

    png_path = get_ghs_path(pictogram_id)
    pictogram_size = card_size - (padding * 2) - border_width

    # Draw drop shadow
    _draw_ghs_card_shadow(canvas, x, y, card_size, corner_radius)

    # Draw teal glow
    _draw_ghs_card_glow(canvas, x, y, card_size,
                        COLORS['accent_teal'], glow_radius=3,
                        glow_opacity=0.2, corner_radius=corner_radius)

    # Dark card background
    canvas.setFillColor(Color(*COLORS['bg_dark_secondary']))
    canvas.roundRect(x, y, card_size, card_size, corner_radius, fill=1, stroke=0)

    # Teal border
    canvas.setStrokeColor(Color(*COLORS['accent_teal']))
    canvas.setLineWidth(border_width)
    canvas.roundRect(x, y, card_size, card_size, corner_radius, fill=0, stroke=1)

    # Pictogram position (centered in card)
    pic_x = x + padding + border_width / 2
    pic_y = y + padding + border_width / 2

    # WHITE BACKGROUND for pictogram (GHS standard requirement)
    canvas.setFillColor(Color(*COLORS['white']))
    canvas.rect(pic_x, pic_y, pictogram_size, pictogram_size, fill=1, stroke=0)

    # Draw pictogram on white background
    canvas.drawImage(
        str(png_path),
        pic_x, pic_y,
        width=pictogram_size,
        height=pictogram_size,
        preserveAspectRatio=True,
        anchor='sw',
        mask='auto'
    )


def draw_ghs_pictogram(canvas, pictogram_id: str, x: float, y: float,
                       size: float = None, with_border: bool = True) -> None:
    """
    Draw a single GHS pictogram - legacy function for backwards compatibility.

    For the new dark card style, use draw_ghs_pictogram_card() instead.

    Args:
        canvas: ReportLab canvas object
        pictogram_id: GHS pictogram identifier (e.g., "GHS02")
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        size: Width and height in points (default from config)
        with_border: Draw subtle border around pictogram
    """
    if size is None:
        size = GHS_PICTOGRAM_SIZE

    png_path = get_ghs_path(pictogram_id)

    # Optional subtle border
    if with_border:
        canvas.setStrokeColor(Color(*COLORS['border_light']))
        canvas.setLineWidth(0.5)
        canvas.rect(x - 1, y - 1, size + 2, size + 2, fill=0, stroke=1)

    # Draw PNG on canvas
    canvas.drawImage(
        str(png_path),
        x, y,
        width=size,
        height=size,
        preserveAspectRatio=True,
        anchor='sw',
        mask='auto'
    )


def draw_ghs_pictograms_standard(
    canvas, pictogram_ids: list, x: float, y: float, size: float = 32, gap: float = 4
) -> float:
    """
    Draw GHS pictograms in STANDARD format.
    NO cards, NO teal borders, NO shadows, NO glow.
    Just the standard red diamond GHS symbols.

    Args:
        canvas: ReportLab canvas
        pictogram_ids: List of GHS IDs like ["GHS02", "GHS07"]
        x: Left edge position
        y: TOP edge position (pictograms draw downward)
        size: Size of each pictogram
        gap: Space between pictograms

    Returns:
        Total height used by the pictogram grid
    """
    if not pictogram_ids:
        return 0

    cols = 3
    num = len(pictogram_ids)
    rows = (num + cols - 1) // cols

    for i, pic_id in enumerate(pictogram_ids):
        row = i // cols
        col = i % cols

        pic_x = x + (col * (size + gap))
        pic_y = y - (row + 1) * (size + gap) + gap

        # Get path to PNG
        if hasattr(pic_id, "value"):
            pic_id = pic_id.value
        png_path = GHS_ASSETS_DIR / f"{pic_id}.png"

        if png_path.exists():
            canvas.drawImage(
                str(png_path),
                pic_x,
                pic_y,
                width=size,
                height=size,
                preserveAspectRatio=True,
                mask="auto",
            )

    return rows * (size + gap)


def draw_ghs_pictograms_grid(canvas, pictogram_ids: list, x: float, y: float,
                             width: float, height: float,
                             max_cols: int = 3, spacing: float = 8) -> float:
    """
    Draw GHS pictograms in a grid layout with dark card styling, right-aligned.

    Each pictogram is rendered inside a dark card with teal border for
    premium tech-industrial aesthetic.

    Args:
        canvas: ReportLab canvas object
        pictogram_ids: List of GHS pictogram identifiers
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Available width in points
        height: Available height in points
        max_cols: Maximum columns in grid (default 3)
        spacing: Spacing between cards in points (default 8)

    Returns:
        Height used by the grid
    """
    if not pictogram_ids:
        return 0

    num = len(pictogram_ids)

    # Determine grid dimensions
    if num <= 2:
        cols = num
        rows = 1
    elif num <= 4:
        cols = 2
        rows = 2
    elif num <= 6:
        cols = 3
        rows = 2
    else:
        cols = min(max_cols, num)
        rows = (num + cols - 1) // cols

    # Use card size from config (52pt outer, fits ~44pt pictogram)
    card_size = GHS_CARD_SIZE

    # Calculate if we need to scale down
    available_width = width - (spacing * (cols - 1))
    available_height = height - (spacing * (rows - 1))

    size_by_width = available_width / cols
    size_by_height = available_height / rows
    actual_card_size = min(size_by_width, size_by_height, card_size)

    # Calculate total grid dimensions
    grid_width = (actual_card_size * cols) + (spacing * (cols - 1))
    grid_height = (actual_card_size * rows) + (spacing * (rows - 1))

    # Start from top-left of grid area, right-aligned
    start_x = x + width - grid_width
    start_y = y + height - actual_card_size

    # Draw pictograms in grid (left to right, top to bottom)
    for i, pictogram_id in enumerate(pictogram_ids):
        row = i // cols
        col = i % cols

        card_x = start_x + (col * (actual_card_size + spacing))
        card_y = start_y - (row * (actual_card_size + spacing))

        draw_ghs_pictogram_card(canvas, pictogram_id, card_x, card_y, actual_card_size)

    return grid_height
