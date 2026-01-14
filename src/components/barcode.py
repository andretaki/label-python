"""UPC-A barcode generation using python-barcode."""

import io
from barcode import UPCA
from barcode.writer import ImageWriter
from reportlab.lib.units import inch
from reportlab.platypus import Image
from PIL import Image as PILImage


def generate_barcode_image(upc_code: str, width: float, height: float) -> Image:
    """
    Generate a UPC-A barcode as a ReportLab Image.

    Args:
        upc_code: 12-digit UPC-A code
        width: Desired width in points
        height: Desired height in points

    Returns:
        ReportLab Image object ready to be drawn on a canvas
    """
    # Validate UPC code length
    if len(upc_code) != 12:
        raise ValueError(f"UPC code must be 12 digits, got {len(upc_code)}")

    # Create barcode with ImageWriter
    # UPC-A uses first 11 digits, 12th is check digit
    barcode = UPCA(upc_code[:11], writer=ImageWriter())

    # Configure writer options for clean output
    options = {
        'module_width': 0.33,  # Width of one bar module in mm
        'module_height': 15.0,  # Height of bars in mm
        'quiet_zone': 2.5,  # Quiet zone width in mm
        'font_size': 8,  # Font size for text below barcode
        'text_distance': 3.0,  # Distance between bars and text in mm
        'write_text': True,  # Include human-readable text
        'dpi': 300,  # High DPI for print quality
    }

    # Render to bytes buffer
    buffer = io.BytesIO()
    barcode.write(buffer, options=options)
    buffer.seek(0)

    # Create ReportLab Image from buffer
    img = Image(buffer, width=width, height=height)

    return img


def draw_barcode(canvas, upc_code: str, x: float, y: float,
                 width: float, height: float) -> None:
    """
    Draw a UPC-A barcode directly on a ReportLab canvas.

    Args:
        canvas: ReportLab canvas object
        upc_code: 12-digit UPC-A code
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        width: Desired width in points
        height: Desired height in points
    """
    if len(upc_code) != 12:
        raise ValueError(f"UPC code must be 12 digits, got {len(upc_code)}")

    # Create barcode with ImageWriter
    barcode = UPCA(upc_code[:11], writer=ImageWriter())

    # Configure for print quality
    options = {
        'module_width': 0.33,
        'module_height': 12.0,  # Slightly shorter for label space
        'quiet_zone': 2.0,
        'font_size': 7,
        'text_distance': 2.5,
        'write_text': True,
        'dpi': 300,
    }

    # Render to bytes buffer
    buffer = io.BytesIO()
    barcode.write(buffer, options=options)
    buffer.seek(0)

    # Load with PIL to get dimensions and draw
    pil_img = PILImage.open(buffer)

    # Save to new buffer in PNG format for ReportLab
    png_buffer = io.BytesIO()
    pil_img.save(png_buffer, format='PNG')
    png_buffer.seek(0)

    # Draw on canvas using ImageReader for BytesIO support
    from reportlab.lib.utils import ImageReader
    img_reader = ImageReader(png_buffer)
    canvas.drawImage(
        img_reader,
        x, y,
        width=width,
        height=height,
        preserveAspectRatio=True,
        anchor='sw'
    )


def get_barcode_bytes(upc_code: str) -> io.BytesIO:
    """
    Generate a UPC-A barcode and return as PNG bytes.

    Args:
        upc_code: 12-digit UPC-A code

    Returns:
        BytesIO buffer containing PNG image data
    """
    if len(upc_code) != 12:
        raise ValueError(f"UPC code must be 12 digits, got {len(upc_code)}")

    barcode = UPCA(upc_code[:11], writer=ImageWriter())

    options = {
        'module_width': 0.33,
        'module_height': 12.0,
        'quiet_zone': 2.0,
        'font_size': 7,
        'text_distance': 2.5,
        'write_text': True,
        'dpi': 300,
    }

    buffer = io.BytesIO()
    barcode.write(buffer, options=options)
    buffer.seek(0)

    # Convert to PNG
    pil_img = PILImage.open(buffer)
    png_buffer = io.BytesIO()
    pil_img.save(png_buffer, format='PNG')
    png_buffer.seek(0)

    return png_buffer
