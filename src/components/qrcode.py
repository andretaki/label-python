"""QR code generation for SDS URLs."""

import io
import qrcode
from qrcode.constants import ERROR_CORRECT_M
from reportlab.lib.utils import ImageReader


def generate_qr_bytes(url: str, box_size: int = 10, border: int = 1) -> io.BytesIO:
    """
    Generate a QR code as PNG bytes.

    Args:
        url: The URL to encode in the QR code
        box_size: Size of each box in pixels (higher = larger image)
        border: Border size in boxes

    Returns:
        BytesIO buffer containing PNG image data
    """
    qr = qrcode.QRCode(
        version=None,  # Auto-size based on data
        error_correction=ERROR_CORRECT_M,  # Medium error correction (~15%)
        box_size=box_size,
        border=border,
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Create image with white background
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to PNG bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer


def draw_qr_code(canvas, url: str, x: float, y: float, size: float) -> None:
    """
    Draw a QR code directly on a ReportLab canvas.

    Args:
        canvas: ReportLab canvas object
        url: The URL to encode
        x: X position (left edge) in points
        y: Y position (bottom edge) in points
        size: Width and height in points (QR codes are square)
    """
    if not url:
        return

    # Generate QR code with appropriate resolution
    # Higher box_size for larger output, scaled down for quality
    qr_bytes = generate_qr_bytes(url, box_size=10, border=1)

    # Create ImageReader from bytes
    img_reader = ImageReader(qr_bytes)

    # Draw on canvas
    canvas.drawImage(
        img_reader,
        x, y,
        width=size,
        height=size,
        preserveAspectRatio=True,
        anchor='sw'
    )


def get_qr_image_reader(url: str) -> ImageReader:
    """
    Get a ReportLab ImageReader for a QR code.

    Args:
        url: The URL to encode

    Returns:
        ImageReader object for use with canvas.drawImage
    """
    qr_bytes = generate_qr_bytes(url, box_size=10, border=1)
    return ImageReader(qr_bytes)
