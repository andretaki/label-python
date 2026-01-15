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


# =============================================================================
# ORGANIC FLOW STYLE (Premium/Futuristic)
# =============================================================================

# Organic color palette - Warm to Cool diagonal flow
ORGANIC_COLORS = {
    # Warm zone (top-left)
    "warm_white": (1.0, 0.973, 0.941),           # #FFF8F0
    "warm_peach": (1.0, 0.91, 0.84),             # #FFE8D6
    "warm_cream": (0.992, 0.965, 0.925),         # #FDF6EC

    # Cool zone (bottom-right)
    "cool_teal": (0, 0.831, 0.667),              # #00D4AA
    "cool_teal_dark": (0, 0.706, 0.588),         # #00B496
    "cool_white": (0.941, 0.98, 0.98),           # #F0FAFA
    "cool_gray": (0.91, 0.957, 0.949),           # #E8F4F2

    # Frosted glass
    "frosted_white": (1.0, 1.0, 1.0),            # White (use with opacity)
    "frosted_border": (0.9, 0.9, 0.92),          # Subtle gray border

    # Signal words
    "danger_red": (0.863, 0.149, 0.149),         # #DC2626
    "warning_amber": (0.961, 0.62, 0.043),       # #F59E0B

    # Text on gradient
    "text_dark": (0.1, 0.1, 0.12),               # Near black
    "text_secondary": (0.3, 0.3, 0.35),          # Dark gray
    "text_muted": (0.5, 0.5, 0.55),              # Medium gray
}

# Gradient color stops for diagonal warm-to-cool
ORGANIC_GRADIENT_STOPS = [
    (0.0, ORGANIC_COLORS["warm_white"]),
    (0.25, ORGANIC_COLORS["warm_peach"]),
    (0.5, ORGANIC_COLORS["warm_cream"]),
    (0.75, ORGANIC_COLORS["cool_gray"]),
    (1.0, ORGANIC_COLORS["cool_white"]),
]

# Three-column widths for organic style
ORGANIC_COL1_WIDTH_PCT = 0.22
ORGANIC_COL2_WIDTH_PCT = 0.33
ORGANIC_COL3_WIDTH_PCT = 0.45
ORGANIC_COLUMN_GAP = 8

# Header/footer dimensions
ORGANIC_HEADER_HEIGHT = 40
ORGANIC_FOOTER_HEIGHT = 22
ORGANIC_FOOTER_PILL_WIDTH_PCT = 0.55  # 55% of label width

# Frosted panel settings
ORGANIC_FROSTED_OPACITY = 0.85
ORGANIC_FROSTED_CORNER_RADIUS = 4

# Font sizes for organic style
ORGANIC_FONT_SIZES = {
    "product_name_hero": 18,       # Large hero treatment with shadow lift
    "product_name_min": 14,        # Minimum if wrapping
    "product_code": 11,
    "sku": 9,
    "lot": 9,
    "cas": 7,
    "grade": 10,
    "net_contents_us": 18,         # PROMINENT - key selling point
    "net_contents_metric": 10,
    "signal_word": 11,
    "h_statement": 6,
    "h_statement_min": 5,
    "p_statement": 5,
    "p_statement_min": 4.5,
    "supplier": 5,
    "footer": 7,
    "label": 6,
}

# GHS settings for organic style
ORGANIC_GHS_SIZE = 32
ORGANIC_GHS_GAP = 4

# Layered depth settings - blobs at different opacities for dimensional feel
ORGANIC_BLOB_SETTINGS = {
    # Warm blob - top-left, largest, lowest opacity (furthest back)
    "warm_blob": {
        "color": "warm_peach",
        "opacity": 0.15,
        "z_order": 1,  # Furthest back
    },
    # Center wave - spans columns, medium opacity (middle layer)
    "center_wave": {
        "color": "cool_gray",
        "opacity": 0.12,
        "z_order": 2,
    },
    # Cool blob - bottom-right, medium-high opacity (closer)
    "cool_blob": {
        "color": "cool_teal",
        "opacity": 0.08,
        "z_order": 3,  # Closest to content
    },
}

# Product name "lift" effect - subtle shadow for dimensional pop
ORGANIC_HERO_SHADOW = {
    "offset_x": 1,
    "offset_y": -2,
    "blur_layers": 2,
    "opacity": 0.15,
}

# Net contents highlight treatment
ORGANIC_NET_CONTENTS_HIGHLIGHT = {
    "glow_color": "cool_teal",
    "glow_opacity": 0.15,
    "underline": True,
    "underline_color": "cool_teal",
}

# Frosted panel - gradient shows through
ORGANIC_FROSTED_PANEL = {
    "opacity": 0.82,              # Lower to let gradient show
    "border_color": "cool_teal",  # Subtle teal accent
    "border_opacity": 0.4,
    "border_width": 1,
    "corner_radius": 4,           # Sharp but slightly softened
    "shadow_opacity": 0.08,
}

# Center column - NO container, free floating (airy zone)
ORGANIC_CENTER_COLUMN = {
    "has_container": False,       # Explicit: no frosted panel
    "vertical_spacing": 10,       # Generous whitespace
}

# =============================================================================
# PRODUCT FAMILY COLOR PALETTES
# =============================================================================
# Each product family gets a unique color palette so products are instantly
# distinguishable by their visual signature.

ORGANIC_PRODUCT_FAMILIES = {
    "solvents": {
        "name": "Solvents & Alcohols",
        "warm_primary": (1.0, 0.945, 0.878),      # #FFF1E0 - Warm cream
        "warm_secondary": (1.0, 0.878, 0.741),    # #FFE0BD - Soft peach
        "cool_primary": (0.0, 0.831, 0.667),      # #00D4AA - Alliance teal
        "cool_secondary": (0.878, 0.969, 0.957),  # #E0F7F4 - Cool teal white
        "accent": (0.0, 0.710, 0.569),            # #00B591 - Deep teal
    },
    "acids": {
        "name": "Acids & Corrosives",
        "warm_primary": (1.0, 0.933, 0.918),      # #FFEEEA - Warm blush
        "warm_secondary": (1.0, 0.796, 0.737),    # #FFCBBC - Soft coral
        "cool_primary": (0.918, 0.341, 0.341),    # #EA5757 - Warning red
        "cool_secondary": (0.969, 0.906, 0.906),  # #F7E7E7 - Cool pink white
        "accent": (0.776, 0.231, 0.231),          # #C63B3B - Deep red
    },
    "bases": {
        "name": "Bases & Alkalines",
        "warm_primary": (0.969, 0.949, 0.988),    # #F7F2FC - Warm lavender
        "warm_secondary": (0.918, 0.867, 0.969),  # #EADDF7 - Soft violet
        "cool_primary": (0.608, 0.518, 0.827),    # #9B84D3 - Purple
        "cool_secondary": (0.941, 0.933, 0.969),  # #F0EEF7 - Cool violet white
        "accent": (0.478, 0.376, 0.702),          # #7A60B3 - Deep purple
    },
    "oils": {
        "name": "Oils & Lubricants",
        "warm_primary": (0.988, 0.973, 0.929),    # #FCF8ED - Warm cream
        "warm_secondary": (0.969, 0.925, 0.804),  # #F7ECCD - Soft gold
        "cool_primary": (0.608, 0.725, 0.490),    # #9BB97D - Sage green
        "cool_secondary": (0.933, 0.953, 0.918),  # #EEF3EA - Cool sage white
        "accent": (0.447, 0.584, 0.337),          # #729556 - Deep green
    },
    "food_grade": {
        "name": "Food Grade",
        "warm_primary": (1.0, 0.996, 0.960),      # #FFFEF5 - Clean cream
        "warm_secondary": (0.957, 0.988, 0.937),  # #F4FCEF - Hint of green
        "cool_primary": (0.400, 0.808, 0.616),    # #66CE9D - Fresh mint
        "cool_secondary": (0.925, 0.976, 0.949),  # #ECF9F2 - Cool mint white
        "accent": (0.259, 0.647, 0.471),          # #42A578 - Deep mint
    },
    "specialty": {
        "name": "Specialty Chemicals",
        "warm_primary": (0.996, 0.941, 0.965),    # #FEF0F6 - Warm pink
        "warm_secondary": (0.988, 0.867, 0.918),  # #FCDDEA - Soft rose
        "cool_primary": (0.376, 0.627, 0.918),    # #60A0EA - Electric blue
        "cool_secondary": (0.925, 0.949, 0.984),  # #ECF2FB - Cool blue white
        "accent": (0.251, 0.502, 0.800),          # #4080CC - Deep blue
    },
}

# =============================================================================
# BLOB SIGNATURE ARRANGEMENTS
# =============================================================================
# Each product family has a distinctive blob shape and arrangement pattern.

ORGANIC_BLOB_SIGNATURES = {
    "solvents": {
        "description": "Flowing diagonal sweep - smooth, liquid feel",
        "blob_count": 3,
        "arrangement": "diagonal_sweep",
        "curve_tension": 0.4,  # Smooth curves
        "primary_blob_scale": 1.0,
    },
    "acids": {
        "description": "Angular, aggressive curves - sharper, more energetic",
        "blob_count": 2,
        "arrangement": "angular_clash",
        "curve_tension": 0.7,  # Sharper curves
        "primary_blob_scale": 0.9,
    },
    "bases": {
        "description": "Rising, lifting curves - upward energy",
        "blob_count": 3,
        "arrangement": "rising_flow",
        "curve_tension": 0.5,
        "primary_blob_scale": 1.0,
    },
    "oils": {
        "description": "Smooth, slow, rounded - viscous feel",
        "blob_count": 2,
        "arrangement": "slow_pool",
        "curve_tension": 0.2,  # Very smooth curves
        "primary_blob_scale": 1.2,  # Larger blobs
    },
    "food_grade": {
        "description": "Clean, contained, circular - safe/pure feel",
        "blob_count": 2,
        "arrangement": "contained_circles",
        "curve_tension": 0.3,
        "primary_blob_scale": 0.85,
    },
    "specialty": {
        "description": "Dynamic, intersecting - premium/unique feel",
        "blob_count": 3,
        "arrangement": "dynamic_intersect",
        "curve_tension": 0.5,
        "primary_blob_scale": 1.1,
    },
}
