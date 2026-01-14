"""Text wrapping and font sizing utilities for label generation."""

import re
from reportlab.pdfbase.pdfmetrics import stringWidth


def get_text_width(text: str, font_name: str, font_size: float) -> float:
    """
    Get the width of a text string in points.

    Args:
        text: The text to measure
        font_name: Name of the font (e.g., "Helvetica")
        font_size: Font size in points

    Returns:
        Width of the text in points
    """
    return stringWidth(text, font_name, font_size)


def wrap_text(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    """
    Wrap text to fit within a maximum width.

    Args:
        text: The text to wrap
        font_name: Name of the font
        font_size: Font size in points
        max_width: Maximum width in points

    Returns:
        List of text lines that fit within max_width
    """
    if not text:
        return []

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Try adding word to current line
        test_line = ' '.join(current_line + [word])
        test_width = get_text_width(test_line, font_name, font_size)

        if test_width <= max_width:
            current_line.append(word)
        else:
            # Start new line
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

            # Check if single word is too long
            word_width = get_text_width(word, font_name, font_size)
            if word_width > max_width:
                # Truncate the word
                truncated = truncate_text(word, font_name, font_size, max_width)
                lines.append(truncated)
                current_line = []

    # Don't forget the last line
    if current_line:
        lines.append(' '.join(current_line))

    return lines


def truncate_text(text: str, font_name: str, font_size: float,
                  max_width: float, suffix: str = "...") -> str:
    """
    Truncate text to fit within a maximum width, adding suffix if truncated.

    Args:
        text: The text to truncate
        font_name: Name of the font
        font_size: Font size in points
        max_width: Maximum width in points
        suffix: Suffix to add when truncated (default "...")

    Returns:
        Truncated text with suffix if needed
    """
    if get_text_width(text, font_name, font_size) <= max_width:
        return text

    suffix_width = get_text_width(suffix, font_name, font_size)
    available_width = max_width - suffix_width

    # Binary search for the right length
    for i in range(len(text), 0, -1):
        test_text = text[:i]
        if get_text_width(test_text, font_name, font_size) <= available_width:
            return test_text.rstrip() + suffix

    return suffix


def fit_text_to_width(text: str, font_name: str, max_size: float,
                      min_size: float, max_width: float,
                      step: float = 0.5) -> tuple[float, str]:
    """
    Find the largest font size that fits text within a width.

    Args:
        text: The text to fit
        font_name: Name of the font
        max_size: Maximum font size to try
        min_size: Minimum font size to use
        max_width: Maximum width in points
        step: Size decrement step

    Returns:
        Tuple of (font_size, text) - text may be truncated if min_size still too large
    """
    size = max_size

    while size >= min_size:
        width = get_text_width(text, font_name, size)
        if width <= max_width:
            return (size, text)
        size -= step

    # Text doesn't fit even at min_size, truncate it
    truncated = truncate_text(text, font_name, min_size, max_width)
    return (min_size, truncated)


def wrap_text_to_height(text: str, font_name: str, font_size: float,
                        max_width: float, max_height: float,
                        line_spacing: float = 1.2) -> list[str]:
    """
    Wrap text to fit within a box (width and height constraints).

    Args:
        text: The text to wrap
        font_name: Name of the font
        font_size: Font size in points
        max_width: Maximum width in points
        max_height: Maximum height in points
        line_spacing: Line spacing multiplier (default 1.2)

    Returns:
        List of text lines that fit within the box
    """
    lines = wrap_text(text, font_name, font_size, max_width)

    line_height = font_size * line_spacing
    max_lines = int(max_height / line_height)

    if len(lines) <= max_lines:
        return lines

    # Truncate to fit height
    result = lines[:max_lines - 1]

    # Add truncated last line
    remaining_text = ' '.join(lines[max_lines - 1:])
    truncated_last = truncate_text(remaining_text, font_name, font_size, max_width)
    result.append(truncated_last)

    return result


def strip_statement_code(statement: str) -> str:
    """
    Strip the P-code or H-code prefix from a hazard/precautionary statement.

    Examples:
        "P210: Keep away from heat..." -> "Keep away from heat..."
        "H225: Highly flammable liquid" -> "Highly flammable liquid"
        "P303+P361+P353: IF ON SKIN..." -> "IF ON SKIN..."

    Args:
        statement: The full statement with code prefix

    Returns:
        Statement text without the code prefix
    """
    # Pattern matches: P-codes, H-codes, and combined codes like P303+P361+P353
    # Format: <code(s)>: <text>
    pattern = r'^[PH]\d+(\+[PH]\d+)*:\s*'
    return re.sub(pattern, '', statement)


def process_precautionary_statements(statements: list[str],
                                     add_sds_note: bool = True) -> list[str]:
    """
    Process precautionary statements: strip codes and add SDS reference.

    Args:
        statements: List of precautionary statements with P-codes
        add_sds_note: Whether to add the SDS reference note at the end

    Returns:
        List of processed statement texts (codes stripped, SDS note added)
    """
    processed = [strip_statement_code(s) for s in statements]

    if add_sds_note and processed:
        processed.append("See SDS for complete precautionary information.")

    return processed


def calculate_line_height(font_size: float, spacing: float = 1.15) -> float:
    """
    Calculate line height based on font size and spacing.

    Args:
        font_size: Font size in points
        spacing: Line spacing multiplier (default 1.15)

    Returns:
        Line height in points
    """
    return font_size * spacing


def fit_statements_to_area(statements: list[str], font_name: str,
                           max_size: float, min_size: float,
                           width: float, height: float,
                           line_spacing: float = 1.15) -> tuple[float, list[str]]:
    """
    Find the largest font size that fits all statements in an area.

    Args:
        statements: List of statement strings
        font_name: Name of the font
        max_size: Maximum font size to try
        min_size: Minimum font size to use
        width: Available width in points
        height: Available height in points
        line_spacing: Line spacing multiplier

    Returns:
        Tuple of (font_size, wrapped_lines)
    """
    size = max_size

    while size >= min_size:
        all_lines = []
        for statement in statements:
            lines = wrap_text(statement, font_name, size, width)
            all_lines.extend(lines)

        total_height = len(all_lines) * (size * line_spacing)

        if total_height <= height:
            return (size, all_lines)

        size -= 0.25

    # Still doesn't fit at min size, return what we can
    all_lines = []
    line_height = min_size * line_spacing
    max_lines = int(height / line_height)

    for statement in statements:
        if len(all_lines) >= max_lines:
            break
        lines = wrap_text(statement, font_name, min_size, width)
        remaining = max_lines - len(all_lines)
        all_lines.extend(lines[:remaining])

    return (min_size, all_lines)
