"""Frosted glass GHS island component for Organic Flow style.

The GHS compliance zone is a sharp-edged "precision island" that contrasts
with the flowing organic background. It uses a frosted glass effect that
lets the warm-to-cool gradient show through subtly.
"""

from pathlib import Path
from reportlab.lib.colors import Color

from src.config import (
    GHS_ASSETS_DIR,
    ORGANIC_COLORS,
    ORGANIC_GHS_SIZE,
    ORGANIC_GHS_GAP,
    ORGANIC_FROSTED_PANEL,
)


def draw_ghs_frosted_island(
    canvas,
    pictogram_ids: list,
    x: float,
    y: float,
    width: float,
    height: float,
    padding: float = 8,
) -> float:
    """
    Draw the GHS compliance island with frosted glass effect.

    This is a "precision element" - sharp edges contrast with organic flow.
    The frosted white panel lets the gradient show through subtly.

    Args:
        canvas: ReportLab canvas object
        pictogram_ids: List of GHS pictogram IDs
        x: X position (left edge)
        y: Y position (bottom edge)
        width: Available width
        height: Available height
        padding: Internal padding

    Returns:
        Height used by the island
    """
    if not pictogram_ids:
        return 0

    # Calculate pictogram grid dimensions
    num = len(pictogram_ids)
    cols = min(3, num)
    rows = (num + cols - 1) // cols

    ghs_size = ORGANIC_GHS_SIZE
    ghs_gap = ORGANIC_GHS_GAP

    grid_width = (ghs_size * cols) + (ghs_gap * (cols - 1))
    grid_height = (ghs_size * rows) + (ghs_gap * (rows - 1))

    # Island dimensions (just big enough for pictograms + padding)
    island_width = grid_width + (padding * 2)
    island_height = grid_height + (padding * 2)

    # Position island at top-right of available area
    island_x = x + width - island_width
    island_y = y + height - island_height

    # Draw frosted glass panel
    _draw_frosted_glass_panel(canvas, island_x, island_y, island_width, island_height)

    # Draw pictograms inside
    pic_start_x = island_x + padding
    pic_start_y = island_y + island_height - padding - ghs_size

    for i, pic_id in enumerate(pictogram_ids):
        row = i // cols
        col = i % cols

        pic_x = pic_start_x + (col * (ghs_size + ghs_gap))
        pic_y = pic_start_y - (row * (ghs_size + ghs_gap))

        _draw_ghs_pictogram(canvas, pic_id, pic_x, pic_y, ghs_size)

    return island_height


def _draw_frosted_glass_panel(canvas, x: float, y: float, width: float, height: float):
    """
    Draw a frosted glass panel with subtle teal accent border.

    The panel is semi-transparent so the gradient shows through.
    Sharp corners for "precision element" contrast.
    """
    canvas.saveState()

    settings = ORGANIC_FROSTED_PANEL
    corner_radius = settings["corner_radius"]

    # Draw subtle shadow for depth
    canvas.setFillColor(Color(0, 0, 0, settings["shadow_opacity"]))
    canvas.roundRect(
        x + 1, y - 2, width, height, corner_radius, fill=1, stroke=0
    )

    # Draw frosted glass fill (gradient shows through)
    canvas.setFillColor(Color(1, 1, 1, settings["opacity"]))
    canvas.roundRect(x, y, width, height, corner_radius, fill=1, stroke=0)

    # Draw subtle teal accent border
    teal = ORGANIC_COLORS["cool_teal"]
    canvas.setStrokeColor(Color(*teal, settings["border_opacity"]))
    canvas.setLineWidth(settings["border_width"])
    canvas.roundRect(x, y, width, height, corner_radius, fill=0, stroke=1)

    canvas.restoreState()


def _draw_ghs_pictogram(canvas, pictogram_id: str, x: float, y: float, size: float):
    """
    Draw a single GHS pictogram (standard red diamond on white).

    No card/container - just the standard GHS symbol.
    """
    if hasattr(pictogram_id, "value"):
        pictogram_id = pictogram_id.value

    png_path = GHS_ASSETS_DIR / f"{pictogram_id}.png"

    if not png_path.exists():
        return

    canvas.drawImage(
        str(png_path),
        x, y,
        width=size,
        height=size,
        preserveAspectRatio=True,
        mask="auto",
    )


def draw_ghs_statements_in_island(
    canvas,
    signal_word: str,
    h_statements: list,
    p_statements: list,
    supplier_info: dict,
    x: float,
    y: float,
    width: float,
    height: float,
    fonts: dict,
    font_sizes: dict,
) -> float:
    """
    Draw signal word and statements inside the frosted GHS island.

    Args:
        canvas: ReportLab canvas object
        signal_word: "DANGER" or "WARNING"
        h_statements: List of hazard statements
        p_statements: List of precautionary statements
        supplier_info: Dict with name, address, phone
        x: X position (left edge of text area)
        y: Y position (top edge, text flows down)
        width: Available text width
        height: Available text height
        fonts: Font name dictionary
        font_sizes: Font size dictionary

    Returns:
        Y position after all text
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth
    import re

    current_y = y

    # Signal word
    if signal_word:
        signal_text = signal_word.upper() if isinstance(signal_word, str) else signal_word.value.upper()
        signal_size = font_sizes.get("signal_word", 11)

        canvas.setFont(fonts["bold"], signal_size)

        if signal_text == "DANGER":
            canvas.setFillColor(Color(*ORGANIC_COLORS["danger_red"]))
        else:
            canvas.setFillColor(Color(*ORGANIC_COLORS["warning_amber"]))

        canvas.drawString(x, current_y - signal_size, signal_text)

        # Underline for emphasis
        text_width = stringWidth(signal_text, fonts["bold"], signal_size)
        if signal_text == "DANGER":
            canvas.setStrokeColor(Color(*ORGANIC_COLORS["danger_red"]))
        else:
            canvas.setStrokeColor(Color(*ORGANIC_COLORS["warning_amber"]))
        canvas.setLineWidth(1.5)
        canvas.line(x, current_y - signal_size - 2, x + text_width, current_y - signal_size - 2)

        current_y -= signal_size + 8

    # H-statements (slightly larger, bold, keep codes visible)
    if h_statements:
        h_size = font_sizes.get("h_statement", 6)
        canvas.setFont(fonts["bold"], h_size)
        canvas.setFillColor(Color(*ORGANIC_COLORS["text_dark"]))

        for statement in h_statements:
            lines = _wrap_text(statement, fonts["bold"], h_size, width)
            for line in lines:
                canvas.drawString(x, current_y - h_size, line)
                current_y -= h_size * 1.15

        # Separator line
        current_y -= 3
        canvas.setStrokeColor(Color(0.7, 0.7, 0.7))
        canvas.setLineWidth(0.5)
        canvas.line(x, current_y, x + width * 0.5, current_y)
        current_y -= 5

    # P-statements (smaller, regular, strip codes)
    if p_statements:
        p_size = font_sizes.get("p_statement", 5)
        canvas.setFont(fonts["regular"], p_size)
        canvas.setFillColor(Color(*ORGANIC_COLORS["text_secondary"]))

        # Combine and strip codes
        clean_statements = []
        for stmt in p_statements:
            clean = re.sub(r"^[PH]\d+(\+[PH]\d+)*:\s*", "", stmt)
            clean_statements.append(clean)

        combined_text = " ".join(clean_statements)
        combined_text += " See SDS for complete precautionary information."

        lines = _wrap_text(combined_text, fonts["regular"], p_size, width)
        for line in lines:
            if current_y - p_size < y - height + 30:  # Leave room for supplier
                break
            canvas.drawString(x, current_y - p_size, line)
            current_y -= p_size * 1.1

    # Supplier info at bottom
    current_y -= 6
    supplier_size = font_sizes.get("supplier", 5)
    canvas.setFont(fonts["regular"], supplier_size)
    canvas.setFillColor(Color(*ORGANIC_COLORS["text_muted"]))

    if supplier_info:
        if "name" in supplier_info:
            canvas.drawString(x, current_y - supplier_size, supplier_info["name"])
            current_y -= supplier_size + 1
        if "address" in supplier_info:
            canvas.drawString(x, current_y - supplier_size, supplier_info["address"])
            current_y -= supplier_size + 1
        if "phone" in supplier_info:
            canvas.drawString(x, current_y - supplier_size, supplier_info["phone"])
            current_y -= supplier_size

    return current_y


def _wrap_text(text: str, font_name: str, font_size: float, max_width: float) -> list:
    """Simple text wrapping utility."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

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
