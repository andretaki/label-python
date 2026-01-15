"""Configuration constants and layout regions for label generation.

Layout: Frame Approach - Dark header/footer with white main area
Dark floating cards (GHS, data block, DOT) create premium tech-industrial feel
while keeping main content area white for print efficiency.
"""

from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
GHS_ASSETS_DIR = ASSETS_DIR / "ghs"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Label dimensions (6x4 inches in points, 72 points = 1 inch)
LABEL_WIDTH = 6 * 72  # 432 points
LABEL_HEIGHT = 4 * 72  # 288 points

# Margins
MARGIN = 10  # 10pt outer margin

# Usable content area
CONTENT_LEFT = MARGIN
CONTENT_RIGHT = LABEL_WIDTH - MARGIN
CONTENT_TOP = LABEL_HEIGHT - MARGIN
CONTENT_BOTTOM = MARGIN
CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT
CONTENT_HEIGHT = CONTENT_TOP - CONTENT_BOTTOM

# Header band (dark gradient)
HEADER_HEIGHT = 55  # Points
HEADER_TOP = CONTENT_TOP
HEADER_BOTTOM = HEADER_TOP - HEADER_HEIGHT

# Footer band (dark gradient)
FOOTER_HEIGHT = 28  # Points
FOOTER_BOTTOM = CONTENT_BOTTOM
FOOTER_TOP = FOOTER_BOTTOM + FOOTER_HEIGHT

# Accent lines
ACCENT_LINE_HEIGHT = 2.5

# Main content area (white, between accent lines)
MAIN_TOP = HEADER_BOTTOM - ACCENT_LINE_HEIGHT - 8
MAIN_BOTTOM = FOOTER_TOP + ACCENT_LINE_HEIGHT + 8
MAIN_HEIGHT = MAIN_TOP - MAIN_BOTTOM

# =============================================================================
# SPACING CONSTANTS (CRITICAL)
# =============================================================================
COLUMN_GAP = 12           # Gap between columns
ELEMENT_GAP_LARGE = 16    # Between major sections
ELEMENT_GAP_MEDIUM = 12   # Between related elements
ELEMENT_GAP_SMALL = 8     # Between tightly coupled elements

# QR Code spacing
QR_TOP_MARGIN = 20        # Gap above QR, below data block
QR_SIZE = 55              # QR code size

# Two-column layout
LEFT_COLUMN_WIDTH = CONTENT_WIDTH * 0.38   # 38%
LEFT_COLUMN_LEFT = CONTENT_LEFT
LEFT_COLUMN_RIGHT = LEFT_COLUMN_LEFT + LEFT_COLUMN_WIDTH

RIGHT_COLUMN_WIDTH = CONTENT_WIDTH * 0.58  # 58%
RIGHT_COLUMN_LEFT = LEFT_COLUMN_RIGHT + COLUMN_GAP
RIGHT_COLUMN_RIGHT = CONTENT_RIGHT

# GHS pictogram grid
GHS_GRID_TOP = MAIN_TOP
GHS_PICTOGRAM_SIZE = 36   # Inner pictogram size
GHS_CARD_SIZE = 42        # Outer card size (with padding)
GHS_GRID_COLS = 3
GHS_GRID_ROWS = 2
GHS_CARD_GAP = 6
GHS_GRID_HEIGHT = (GHS_CARD_SIZE * 2) + GHS_CARD_GAP

# Barcode positioning
BARCODE_WIDTH = 65
BARCODE_HEIGHT = 24
BARCODE_RIGHT_MARGIN = 8  # From right edge of header

# Font configuration
FONTS = {
    "bold": "Helvetica-Bold",
    "regular": "Helvetica",
    "oblique": "Helvetica-Oblique",
    "mono": "Courier",
    "mono_bold": "Courier-Bold",
}

# Font sizes
FONT_SIZES = {
    # Header (on dark)
    "company_name": 9,
    "company_details": 6,

    # Product Identity (on white)
    "product_name": 20,
    "product_name_min": 14,
    "grade": 11,

    # Technical Data Block (on dark card)
    "data_label": 6.5,
    "data_value": 7.5,

    # Net Contents (on white)
    "net_contents_us": 16,
    "net_contents_metric": 9,

    # Hazard Communication (on white)
    "signal_word": 10,
    "h_statement": 7,
    "p_statement": 6,
    "p_statement_min": 5,

    # DOT Badge (on dark card)
    "dot_badge": 7,

    # Footer (on dark)
    "footer": 6.5,
    "footer_small": 6,

    # QR label
    "qr_label": 5.5,
}

# =============================================================================
# COLORS - Frame Approach Palette
# =============================================================================
COLORS = {
    # BACKGROUNDS
    "bg_white": (1, 1, 1),                             # Main content area
    "bg_light": (248/255, 248/255, 250/255),           # Subtle off-white
    "bg_dark": (13/255, 13/255, 15/255),               # Header/footer
    "bg_dark_secondary": (26/255, 26/255, 30/255),     # Dark cards/panels
    "bg_dark_tertiary": (37/255, 37/255, 41/255),      # Elevated dark

    # GRADIENTS
    "gradient_dark_start": (26/255, 26/255, 30/255),
    "gradient_dark_mid": (42/255, 42/255, 50/255),
    "gradient_dark_end": (26/255, 26/255, 30/255),

    # TEXT - On white background
    "text_dark": (13/255, 13/255, 15/255),             # Primary on white
    "text_dark_secondary": (80/255, 80/255, 88/255),   # Secondary on white
    "text_muted": (140/255, 140/255, 148/255),         # Fine print on white

    # TEXT - On dark backgrounds
    "text_light": (1, 1, 1),                           # White text
    "text_light_secondary": (180/255, 180/255, 188/255),
    "text_light_muted": (107/255, 107/255, 115/255),

    # ACCENT - Teal
    "accent_teal": (0/255, 212/255, 170/255),          # #00D4AA - bright
    "accent_teal_dark": (0/255, 170/255, 136/255),     # #00AA88 - darker

    # SIGNAL WORDS
    "danger_red": (220/255, 38/255, 38/255),           # #DC2626
    "danger_red_light": (255/255, 68/255, 68/255),     # #FF4444
    "warning_amber": (245/255, 158/255, 11/255),       # #F59E0B
    "warning_amber_light": (251/255, 191/255, 36/255), # #FBBF24

    # GHS
    "ghs_red": (255/255, 0/255, 0/255),                # Standard GHS red
    "ghs_border": (0/255, 212/255, 170/255),           # Teal border for GHS cards

    # NFPA 704 Diamond
    "nfpa_blue": (0/255, 112/255, 192/255),            # Health (blue, left)
    "nfpa_red": (255/255, 0/255, 0/255),               # Fire (red, top)
    "nfpa_yellow": (255/255, 255/255, 0/255),          # Reactivity (yellow, right)
    "nfpa_white": (1, 1, 1),                            # Special (white, bottom)

    # UTILITY
    "white": (1, 1, 1),
    "black": (0, 0, 0),
    "border_light": (229/255, 229/255, 234/255),
    "border_dark": (37/255, 37/255, 41/255),

    # Legacy mappings
    "text_primary": (13/255, 13/255, 15/255),
    "text_secondary": (80/255, 80/255, 88/255),
    "text_tertiary": (140/255, 140/255, 148/255),
    "text_on_dark": (1, 1, 1),
    "product_navy": (13/255, 13/255, 15/255),
    "bg_secondary": (26/255, 26/255, 30/255),
    "bg_header": (13/255, 13/255, 15/255),
}

# Company information
COMPANY_INFO = {
    "name": "ALLIANCE CHEMICAL",
    "address": "204 S. Edmond St., Taylor, TX 76574",
    "phone": "512-365-6838",
    "website": "alliancechemical.com",
}

# Template configurations
TEMPLATES = {
    "small": {"product_name_size": 16, "net_contents_size": 12},
    "medium": {"product_name_size": 18, "net_contents_size": 14},
    "drum": {"product_name_size": 20, "net_contents_size": 16},
    "dry": {"product_name_size": 18, "net_contents_size": 14},
}

PACKAGE_TO_TEMPLATE = {
    "unknown": "medium",
    "quart_1": "small",
    "gallon_1": "medium",
    "gallon_2.5": "medium",
    "gallon_5": "medium",
    "drum_55gal": "drum",
    "tote_275gal": "drum",
    "tote_330gal": "drum",
    "bag_25lb": "dry",
    "bag_50lb": "dry",
}


# =============================================================================
# SCIENTIFIC STYLE LAYOUT (Sigma-Aldrich style)
# =============================================================================

# Header/Footer dimensions
SCIENTIFIC_HEADER_HEIGHT = 36
SCIENTIFIC_HEADER_COLOR = (0 / 255, 180 / 255, 150 / 255)  # Solid teal #00B496
SCIENTIFIC_FOOTER_HEIGHT = 20
SCIENTIFIC_FOOTER_COLOR = (26 / 255, 26 / 255, 31 / 255)  # Dark gray

# Three-column widths (percentages)
SCIENTIFIC_COL1_WIDTH_PCT = 0.22
SCIENTIFIC_COL2_WIDTH_PCT = 0.33
SCIENTIFIC_COL3_WIDTH_PCT = 0.45
SCIENTIFIC_COLUMN_GAP = 6

# GHS settings (standard format, no cards)
SCIENTIFIC_GHS_SIZE = 32
SCIENTIFIC_GHS_GAP = 4
SCIENTIFIC_GHS_GRID_COLS = 3

# Font sizes - CRITICAL: Very small for statements
SCIENTIFIC_FONT_SIZES = {
    "product_code": 11,
    "sku": 9,
    "lot": 9,
    "cas": 7,
    "product_name": 12,
    "grade": 9,
    "net_contents_us": 14,
    "net_contents_metric": 9,
    "signal_word": 8,
    "h_statement": 5,  # TINY - fits all statements
    "p_statement": 5,  # TINY - fits all statements
    "supplier": 5,
    "footer": 7,
    "label": 6,
}
