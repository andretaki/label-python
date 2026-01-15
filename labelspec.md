# SIGMA-ALDRICH LABEL RECREATION SPECIFICATION
## Ultra-Detailed Implementation Guide for Claude Code

---

# EXECUTIVE SUMMARY

You are recreating a scientific chemical label based on the Sigma-Aldrich design style. This label prioritizes **regulatory compliance** and **information density** over visual aesthetics. Every GHS-required element MUST be visible on the label.

**CRITICAL MINDSET SHIFT**: The current Alliance Chemical label uses decorative dark cards, glowing borders, and visual effects. The Sigma-Aldrich style is the OPPOSITE - it uses a clean white background, standard GHS symbols, and extremely small text to fit ALL required information.

---

# PART 1: LABEL DIMENSIONS AND STRUCTURE

## 1.1 Overall Label Size
```
WIDTH:  432 points (6 inches × 72 points/inch)
HEIGHT: 288 points (4 inches × 72 points/inch)
```

## 1.2 Master Grid Layout
The label is divided into a **HEADER BAR** at top and **THREE COLUMNS** below.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         HEADER BAR (height: 36pt)                        │
│  [DECORATIVE LINES]  [COMPANY NAME]                           [LOGO]    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    COLUMN 1         │         COLUMN 2          │        COLUMN 3        │
│    (width: 22%)     │         (width: 33%)      │        (width: 45%)    │
│                     │                           │                        │
│    IDENTIFIERS      │       PRODUCT INFO        │     GHS HAZARD BLOCK   │
│    & CODES          │       & WARNINGS          │     & STATEMENTS       │
│                     │                           │                        │
│    - Product Code   │    - Product Name         │    - GHS Pictograms    │
│    - SKU/Source     │    - Description          │    - Signal Word       │
│    - Lot Number     │    - Multi-language       │    - H-Statements      │
│    - Expiry Date    │    - Contains statement   │    - P-Statements      │
│    - CAS Number     │    - Warnings             │    - ALL IN TINY TEXT  │
│    - Mol. Weight    │    - Use restrictions     │                        │
│    - Storage Temp   │    - Net Contents         │    - Supplier Info     │
│    - QR Code        │    - DOT Info             │                        │
│                     │                           │                        │
├──────────────────────────────────────────────────────────────────────────┤
│                        FOOTER BAR (height: 20pt)                         │
│  [EMERGENCY CONTACT]                              [WEBSITE]              │
└──────────────────────────────────────────────────────────────────────────┘
```

## 1.3 Exact Measurements in Points

```python
# LABEL DIMENSIONS
LABEL_WIDTH = 432   # 6 inches
LABEL_HEIGHT = 288  # 4 inches

# MARGINS
MARGIN_LEFT = 8
MARGIN_RIGHT = 8
MARGIN_TOP = 6
MARGIN_BOTTOM = 6

# CONTENT AREA (inside margins)
CONTENT_WIDTH = LABEL_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 416pt
CONTENT_HEIGHT = LABEL_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM  # 276pt

# HEADER BAR
HEADER_HEIGHT = 36
HEADER_TOP = LABEL_HEIGHT - MARGIN_TOP  # 282pt from bottom
HEADER_BOTTOM = HEADER_TOP - HEADER_HEIGHT  # 246pt from bottom

# FOOTER BAR
FOOTER_HEIGHT = 20
FOOTER_BOTTOM = MARGIN_BOTTOM  # 6pt from bottom
FOOTER_TOP = FOOTER_BOTTOM + FOOTER_HEIGHT  # 26pt from bottom

# MAIN CONTENT AREA (between header and footer)
MAIN_TOP = HEADER_BOTTOM - 4  # 242pt - small gap below header
MAIN_BOTTOM = FOOTER_TOP + 4  # 30pt - small gap above footer
MAIN_HEIGHT = MAIN_TOP - MAIN_BOTTOM  # 212pt

# THREE COLUMN WIDTHS (percentages of CONTENT_WIDTH)
COLUMN_1_WIDTH = CONTENT_WIDTH * 0.22  # ~91pt
COLUMN_2_WIDTH = CONTENT_WIDTH * 0.33  # ~137pt  
COLUMN_3_WIDTH = CONTENT_WIDTH * 0.45  # ~187pt

# COLUMN X POSITIONS (left edge of each column)
COLUMN_1_LEFT = MARGIN_LEFT  # 8pt
COLUMN_2_LEFT = COLUMN_1_LEFT + COLUMN_1_WIDTH + 6  # ~105pt (6pt gap)
COLUMN_3_LEFT = COLUMN_2_LEFT + COLUMN_2_WIDTH + 6  # ~248pt (6pt gap)

# COLUMN GAP
COLUMN_GAP = 6  # Space between columns
```

---

# PART 2: HEADER BAR SPECIFICATION

## 2.1 Visual Appearance
The header is a **SOLID COLOR BAR** (not a gradient). It contains:
- Decorative vertical white lines on the left
- Company name in the center-left area
- Company logo on the right

## 2.2 Exact Specifications

```python
# HEADER COLORS
HEADER_BACKGROUND_COLOR = (0/255, 128/255, 90/255)  # Sigma green: #00805A
# FOR ALLIANCE: Use teal instead
ALLIANCE_HEADER_COLOR = (0/255, 180/255, 150/255)  # Teal: #00B496

# HEADER ELEMENTS POSITIONING
HEADER_Y_CENTER = HEADER_BOTTOM + (HEADER_HEIGHT / 2)  # Vertical center of header

# DECORATIVE LINES (left side)
# These are 4-5 thin white vertical lines creating a visual accent
DECORATIVE_LINES_START_X = MARGIN_LEFT + 4
DECORATIVE_LINES_SPACING = 8  # Space between each line
DECORATIVE_LINE_HEIGHT = HEADER_HEIGHT - 8  # Slightly shorter than header
DECORATIVE_LINE_WIDTH = 1.5  # Thin lines
DECORATIVE_LINE_COLOR = (1, 1, 1)  # White
NUMBER_OF_DECORATIVE_LINES = 5

# COMPANY NAME TEXT
COMPANY_NAME_X = MARGIN_LEFT + 60  # After decorative lines
COMPANY_NAME_Y = HEADER_Y_CENTER - 4  # Slightly below center
COMPANY_NAME_FONT = "Helvetica-Bold"
COMPANY_NAME_SIZE = 11
COMPANY_NAME_COLOR = (1, 1, 1)  # White

# LOGO POSITION (right side)
LOGO_WIDTH = 60
LOGO_HEIGHT = 28
LOGO_X = LABEL_WIDTH - MARGIN_RIGHT - LOGO_WIDTH - 8
LOGO_Y = HEADER_BOTTOM + (HEADER_HEIGHT - LOGO_HEIGHT) / 2
```

## 2.3 Implementation Code

```python
def draw_header(canvas, sku_data):
    """Draw the solid color header bar with decorative lines and logo."""
    
    # 1. Draw solid color background (NO GRADIENT)
    canvas.setFillColor(Color(*ALLIANCE_HEADER_COLOR))
    canvas.rect(0, HEADER_BOTTOM, LABEL_WIDTH, HEADER_HEIGHT, fill=1, stroke=0)
    
    # 2. Draw decorative vertical white lines
    canvas.setStrokeColor(Color(1, 1, 1))  # White
    canvas.setLineWidth(DECORATIVE_LINE_WIDTH)
    
    line_bottom = HEADER_BOTTOM + 4
    line_top = HEADER_TOP - 4
    
    for i in range(NUMBER_OF_DECORATIVE_LINES):
        x = DECORATIVE_LINES_START_X + (i * DECORATIVE_LINES_SPACING)
        canvas.line(x, line_bottom, x, line_top)
    
    # 3. Draw company name
    canvas.setFont(COMPANY_NAME_FONT, COMPANY_NAME_SIZE)
    canvas.setFillColor(Color(1, 1, 1))  # White text
    canvas.drawString(COMPANY_NAME_X, COMPANY_NAME_Y, "ALLIANCE CHEMICAL")
    
    # 4. Draw logo (if exists)
    logo_path = ASSETS_DIR / "logo.png"
    if logo_path.exists():
        canvas.drawImage(
            str(logo_path), LOGO_X, LOGO_Y,
            width=LOGO_WIDTH, height=LOGO_HEIGHT,
            preserveAspectRatio=True, mask='auto'
        )
```

---

# PART 3: COLUMN 1 - IDENTIFIERS & CODES

## 3.1 Visual Layout (Top to Bottom)

```
┌─────────────────────┐
│ PCode               │  <- Label (6pt, gray)
│ 850123456789        │  <- Value (11pt, bold, black)
│                     │
│ SKU                 │  <- Label
│ AC-IPA-99-55        │  <- Value (9pt, regular)
│                     │
│ LOT                 │  <- Label
│ TEST-001            │  <- Value (9pt, regular)
│                     │
│ Exp. Date           │  <- Label (if applicable)
│ 12/31/2025          │  <- Value
│                     │
│ CAS-No: 67-63-0     │  <- Combined label+value (7pt)
│                     │
│ M = 60.10 g/mol     │  <- Molecular weight (7pt)
│                     │
│ ┌─────┐             │
│ │ 2°C │             │  <- Storage temp icon (if applicable)
│ │  ↕  │             │
│ │ 8°C │             │
│ └─────┘             │
│                     │
│ ┌─────────────┐     │
│ │ █▀▀▀▀▀▀▀█   │     │  <- QR Code (links to SDS)
│ │ █ ▄▄▄▄ █   │     │
│ │ █ █  █ █   │     │
│ │ █▄▄▄▄▄▄█   │     │
│ └─────────────┘     │
│ Scan for SDS        │  <- Label below QR (5pt)
└─────────────────────┘
```

## 3.2 Exact Specifications

```python
# COLUMN 1 TYPOGRAPHY
COL1_LABEL_FONT = "Helvetica"
COL1_LABEL_SIZE = 6
COL1_LABEL_COLOR = (0.4, 0.4, 0.4)  # Gray

COL1_VALUE_FONT_BOLD = "Helvetica-Bold"
COL1_VALUE_FONT_REGULAR = "Helvetica"

COL1_PRODUCT_CODE_SIZE = 11  # Largest - the main identifier
COL1_SKU_SIZE = 9
COL1_LOT_SIZE = 9
COL1_DATE_SIZE = 8
COL1_CAS_SIZE = 7
COL1_MOLWEIGHT_SIZE = 7

COL1_VALUE_COLOR = (0, 0, 0)  # Black

# SPACING
COL1_ELEMENT_GAP = 8  # Vertical space between elements
COL1_LABEL_VALUE_GAP = 2  # Space between label and its value

# QR CODE
QR_CODE_SIZE = 50  # 50x50 points
QR_CODE_MARGIN_BOTTOM = 8  # Space from bottom of column
```

## 3.3 Implementation Code

```python
def draw_column_1(canvas, sku_data):
    """Draw the left column with identifiers, codes, and QR."""
    
    x = COLUMN_1_LEFT
    y = MAIN_TOP  # Start from top of content area
    col_width = COLUMN_1_WIDTH
    
    # Helper function for label + value pairs
    def draw_labeled_value(label, value, label_size, value_size, value_bold=False):
        nonlocal y
        
        # Draw label (small, gray)
        if label:
            canvas.setFont(COL1_LABEL_FONT, label_size)
            canvas.setFillColor(Color(*COL1_LABEL_COLOR))
            canvas.drawString(x, y - label_size, label)
            y -= label_size + COL1_LABEL_VALUE_GAP
        
        # Draw value (larger, black)
        font = COL1_VALUE_FONT_BOLD if value_bold else COL1_VALUE_FONT_REGULAR
        canvas.setFont(font, value_size)
        canvas.setFillColor(Color(*COL1_VALUE_COLOR))
        canvas.drawString(x, y - value_size, str(value))
        y -= value_size + COL1_ELEMENT_GAP
    
    # 1. Product Code / UPC (largest, bold)
    draw_labeled_value("PCode", sku_data.upc_gtin12, 6, COL1_PRODUCT_CODE_SIZE, value_bold=True)
    
    # 2. SKU
    draw_labeled_value("SKU", sku_data.sku, 6, COL1_SKU_SIZE)
    
    # 3. Lot Number
    if sku_data.lot_number:
        draw_labeled_value("LOT", sku_data.lot_number, 6, COL1_LOT_SIZE)
    
    # 4. CAS Number (inline format: "CAS-No: 67-63-0")
    if sku_data.cas_number:
        canvas.setFont(COL1_VALUE_FONT_REGULAR, COL1_CAS_SIZE)
        canvas.setFillColor(Color(*COL1_VALUE_COLOR))
        canvas.drawString(x, y - COL1_CAS_SIZE, f"CAS-No: {sku_data.cas_number}")
        y -= COL1_CAS_SIZE + COL1_ELEMENT_GAP
    
    # 5. QR Code at bottom of column
    qr_y = MAIN_BOTTOM + QR_CODE_MARGIN_BOTTOM
    draw_qr_code(canvas, sku_data.sds_url, x, qr_y, QR_CODE_SIZE)
    
    # 6. "Scan for SDS" label below QR
    canvas.setFont(COL1_LABEL_FONT, 5)
    canvas.setFillColor(Color(*COL1_LABEL_COLOR))
    canvas.drawString(x, qr_y - 8, "Scan for SDS")
```

---

# PART 4: COLUMN 2 - PRODUCT INFORMATION

## 4.1 Visual Layout (Top to Bottom)

```
┌────────────────────────────────┐
│ Isopropyl Alcohol              │  <- Product Name (12pt, bold)
│                                │
│ 99% ACS Reagent Grade          │  <- Grade/Description (9pt)
│ Analytical reagent for         │
│ laboratory use                 │
│                                │
│ (Contains: Isopropanol)        │  <- Contains statement (7pt, gray)
│                                │
│ ⚠ Flammable. Keep away from   │  <- Warning (7pt)
│ heat and ignition sources.     │
│                                │
│ For industrial/laboratory      │  <- Use restriction (7pt, italic)
│ use only.                      │
│                                │
│ ─────────────────────────────  │  <- Thin separator line
│                                │
│ 55 Gallons                     │  <- Net Contents US (14pt, bold)
│ 208.2 L                        │  <- Net Contents Metric (9pt)
│                                │
│ ─────────────────────────────  │  <- Thin separator line
│                                │
│ DOT: UN1219                    │  <- DOT Info (8pt)
│ Flammable Liquid               │
│ Hazard Class 3, PG II          │
│                                │
│ Made in USA                    │  <- Origin (7pt)
│ alliancechemical.com           │  <- Website (7pt)
└────────────────────────────────┘
```

## 4.2 Exact Specifications

```python
# COLUMN 2 TYPOGRAPHY
COL2_PRODUCT_NAME_FONT = "Helvetica-Bold"
COL2_PRODUCT_NAME_SIZE = 12
COL2_PRODUCT_NAME_COLOR = (0, 0, 0)  # Black

COL2_GRADE_FONT = "Helvetica"
COL2_GRADE_SIZE = 9
COL2_GRADE_COLOR = (0.2, 0.2, 0.2)  # Dark gray

COL2_CONTAINS_FONT = "Helvetica"
COL2_CONTAINS_SIZE = 7
COL2_CONTAINS_COLOR = (0.5, 0.5, 0.5)  # Medium gray

COL2_WARNING_FONT = "Helvetica"
COL2_WARNING_SIZE = 7
COL2_WARNING_COLOR = (0.1, 0.1, 0.1)

COL2_NET_CONTENTS_US_FONT = "Helvetica-Bold"
COL2_NET_CONTENTS_US_SIZE = 14
COL2_NET_CONTENTS_METRIC_FONT = "Helvetica"
COL2_NET_CONTENTS_METRIC_SIZE = 9

COL2_DOT_FONT = "Helvetica"
COL2_DOT_SIZE = 8
COL2_DOT_COLOR = (0, 0, 0)

COL2_SMALL_TEXT_FONT = "Helvetica"
COL2_SMALL_TEXT_SIZE = 7
COL2_SMALL_TEXT_COLOR = (0.4, 0.4, 0.4)

# SEPARATOR LINE
COL2_SEPARATOR_COLOR = (0.8, 0.8, 0.8)  # Light gray
COL2_SEPARATOR_WIDTH = 0.5  # Thin line

# SPACING
COL2_SECTION_GAP = 10  # Between major sections
COL2_LINE_GAP = 3  # Between lines of text
```

## 4.3 Implementation Code

```python
def draw_column_2(canvas, sku_data):
    """Draw the center column with product info, net contents, DOT."""
    
    x = COLUMN_2_LEFT
    y = MAIN_TOP
    col_width = COLUMN_2_WIDTH
    
    # 1. PRODUCT NAME (large, bold)
    canvas.setFont(COL2_PRODUCT_NAME_FONT, COL2_PRODUCT_NAME_SIZE)
    canvas.setFillColor(Color(*COL2_PRODUCT_NAME_COLOR))
    
    # Wrap product name if too long
    name_lines = wrap_text(sku_data.product_name, COL2_PRODUCT_NAME_FONT, 
                           COL2_PRODUCT_NAME_SIZE, col_width)
    for line in name_lines:
        canvas.drawString(x, y - COL2_PRODUCT_NAME_SIZE, line)
        y -= COL2_PRODUCT_NAME_SIZE + 2
    
    y -= 4  # Extra space after name
    
    # 2. GRADE / CONCENTRATION
    if sku_data.grade_or_concentration:
        canvas.setFont(COL2_GRADE_FONT, COL2_GRADE_SIZE)
        canvas.setFillColor(Color(*COL2_GRADE_COLOR))
        canvas.drawString(x, y - COL2_GRADE_SIZE, sku_data.grade_or_concentration)
        y -= COL2_GRADE_SIZE + COL2_SECTION_GAP
    
    # 3. CONTAINS STATEMENT (if mixture)
    if sku_data.is_mixture:
        canvas.setFont(COL2_CONTAINS_FONT, COL2_CONTAINS_SIZE)
        canvas.setFillColor(Color(*COL2_CONTAINS_COLOR))
        contains_text = f"(Contains: {', '.join(sku_data.components)})"
        canvas.drawString(x, y - COL2_CONTAINS_SIZE, contains_text)
        y -= COL2_CONTAINS_SIZE + COL2_LINE_GAP
    
    # 4. SEPARATOR LINE
    y -= 4
    canvas.setStrokeColor(Color(*COL2_SEPARATOR_COLOR))
    canvas.setLineWidth(COL2_SEPARATOR_WIDTH)
    canvas.line(x, y, x + col_width * 0.8, y)
    y -= 8
    
    # 5. NET CONTENTS
    # US measurement (large, bold)
    canvas.setFont(COL2_NET_CONTENTS_US_FONT, COL2_NET_CONTENTS_US_SIZE)
    canvas.setFillColor(Color(*COL2_PRODUCT_NAME_COLOR))
    canvas.drawString(x, y - COL2_NET_CONTENTS_US_SIZE, sku_data.net_contents_us)
    y -= COL2_NET_CONTENTS_US_SIZE + 2
    
    # Metric measurement (smaller)
    canvas.setFont(COL2_NET_CONTENTS_METRIC_FONT, COL2_NET_CONTENTS_METRIC_SIZE)
    canvas.setFillColor(Color(*COL2_GRADE_COLOR))
    canvas.drawString(x, y - COL2_NET_CONTENTS_METRIC_SIZE, sku_data.net_contents_metric)
    y -= COL2_NET_CONTENTS_METRIC_SIZE + COL2_SECTION_GAP
    
    # 6. SEPARATOR LINE
    canvas.setStrokeColor(Color(*COL2_SEPARATOR_COLOR))
    canvas.line(x, y, x + col_width * 0.8, y)
    y -= 8
    
    # 7. DOT INFORMATION (if regulated)
    if sku_data.dot_regulated:
        canvas.setFont(COL2_DOT_FONT, COL2_DOT_SIZE)
        canvas.setFillColor(Color(*COL2_DOT_COLOR))
        
        canvas.drawString(x, y - COL2_DOT_SIZE, f"DOT: {sku_data.un_number}")
        y -= COL2_DOT_SIZE + 2
        
        canvas.drawString(x, y - COL2_DOT_SIZE, sku_data.proper_shipping_name or "")
        y -= COL2_DOT_SIZE + 2
        
        pg = sku_data.packing_group.value if sku_data.packing_group else ""
        canvas.drawString(x, y - COL2_DOT_SIZE, f"Hazard Class {sku_data.hazard_class}, PG {pg}")
        y -= COL2_DOT_SIZE + COL2_SECTION_GAP
    
    # 8. ORIGIN AND WEBSITE (bottom of column)
    canvas.setFont(COL2_SMALL_TEXT_FONT, COL2_SMALL_TEXT_SIZE)
    canvas.setFillColor(Color(*COL2_SMALL_TEXT_COLOR))
    canvas.drawString(x, MAIN_BOTTOM + 16, "Made in USA")
    canvas.drawString(x, MAIN_BOTTOM + 8, "alliancechemical.com")
```

---

# PART 5: COLUMN 3 - GHS HAZARD BLOCK (CRITICAL SECTION)

## 5.1 This is the Most Important Section

Column 3 contains ALL legally required GHS hazard communication elements:
1. GHS Pictograms (standard red diamond format)
2. Signal Word (DANGER or WARNING)
3. ALL Hazard Statements (H-codes)
4. ALL Precautionary Statements (P-codes)
5. Supplier Information

**KEY INSIGHT**: Sigma-Aldrich fits ALL this information by using **very small text (4-5pt)** in a **dense paragraph format**.

## 5.2 Visual Layout

```
┌────────────────────────────────────────┐
│  ┌────┐ ┌────┐ ┌────┐                  │
│  │ 🔥 │ │ ⚠️ │ │    │  <- Row 1: 3 GHS │
│  │GHS02│ │GHS07│ │    │     pictograms  │
│  └────┘ └────┘ └────┘                  │
│  ┌────┐ ┌────┐ ┌────┐                  │
│  │    │ │    │ │    │  <- Row 2: 3 more│
│  │    │ │    │ │    │     (if needed)  │
│  └────┘ └────┘ └────┘                  │
│                                        │
│  DANGER                                │  <- Signal Word (8pt, bold)
│                                        │
│  Highly flammable liquid and vapor.    │  <- H-statements start
│  Causes serious eye irritation. May    │     (5pt, continuous
│  cause drowsiness or dizziness.        │      paragraph)
│                                        │
│  Keep away from heat, hot surfaces,    │  <- P-statements
│  sparks, open flames and other         │     (5pt, continuous)
│  ignition sources. No smoking. Keep    │
│  container tightly closed. Ground      │
│  and bond container and receiving      │
│  equipment. Use explosion-proof        │
│  electrical, ventilating, lighting     │
│  equipment. Use non-sparking tools.    │
│  Take action to prevent static         │
│  discharges. Wash hands thoroughly     │
│  after handling. Wear protective       │
│  gloves, eye protection, face          │
│  protection. IF ON SKIN: Wash with     │
│  plenty of water. IF IN EYES: Rinse    │
│  cautiously with water for several     │
│  minutes. Remove contact lenses if     │
│  present. Continue rinsing. If eye     │
│  irritation persists: Get medical      │
│  advice. In case of fire: Use water    │
│  spray, dry chemical, CO2, or foam.    │
│  Store in well-ventilated place.       │
│  Keep cool. Dispose of contents per    │
│  local regulations.                    │
│                                        │
│  See SDS for complete information.     │  <- Final line
│                                        │
│  ────────────────────────────────────  │
│  Alliance Chemical                     │  <- Supplier info (5pt)
│  204 S. Edmond St., Taylor, TX 76574   │
│  512-365-6838                          │
└────────────────────────────────────────┘
```

## 5.3 GHS Pictogram Specifications

```python
# GHS PICTOGRAM LAYOUT
GHS_PICTOGRAM_SIZE = 32  # 32x32 points (SMALLER than current 52pt)
GHS_GRID_COLUMNS = 3
GHS_GRID_ROWS = 2  # Maximum 6 pictograms
GHS_GRID_GAP = 4  # Small gap between pictograms

# GHS PICTOGRAM STYLE
# CRITICAL: Use STANDARD GHS format - NO decorative borders
# - Red diamond border (45° rotated square)
# - White background inside diamond
# - Black symbol
# - NO teal borders, NO glow effects, NO shadows, NO cards

GHS_BORDER_COLOR = (1, 0, 0)  # Pure red: #FF0000
GHS_BORDER_WIDTH = 1.5
GHS_BACKGROUND_COLOR = (1, 1, 1)  # White

# POSITIONING
GHS_GRID_TOP = MAIN_TOP  # Start at top of column 3
GHS_GRID_LEFT = COLUMN_3_LEFT
GHS_TOTAL_WIDTH = (GHS_PICTOGRAM_SIZE * 3) + (GHS_GRID_GAP * 2)  # ~104pt
GHS_TOTAL_HEIGHT = (GHS_PICTOGRAM_SIZE * 2) + GHS_GRID_GAP  # ~68pt
```

## 5.4 GHS Implementation Code

```python
def draw_ghs_pictograms_standard(canvas, pictogram_ids, x, y, size=32, gap=4):
    """
    Draw GHS pictograms in STANDARD format (red diamond, white background).
    NO decorative cards, NO teal borders, NO shadows, NO glow effects.
    
    This matches the official GHS/UN specification for pictograms.
    """
    
    if not pictogram_ids:
        return 0  # Return 0 height used
    
    cols = 3
    rows = (len(pictogram_ids) + cols - 1) // cols
    
    total_height = (size * rows) + (gap * (rows - 1))
    
    for i, pictogram_id in enumerate(pictogram_ids):
        row = i // cols
        col = i % cols
        
        pic_x = x + (col * (size + gap))
        pic_y = y - (row * (size + gap)) - size
        
        # Get pictogram image path
        png_path = GHS_ASSETS_DIR / f"{pictogram_id}.png"
        
        if png_path.exists():
            # Draw the standard GHS pictogram (already has red diamond border)
            canvas.drawImage(
                str(png_path),
                pic_x, pic_y,
                width=size, height=size,
                preserveAspectRatio=True,
                mask='auto'
            )
        else:
            # Fallback: draw placeholder
            canvas.setStrokeColor(Color(1, 0, 0))
            canvas.setLineWidth(1)
            canvas.rect(pic_x, pic_y, size, size, fill=0, stroke=1)
    
    return total_height
```

## 5.5 Signal Word and Statement Text Specifications

```python
# SIGNAL WORD
SIGNAL_WORD_FONT = "Helvetica-Bold"
SIGNAL_WORD_SIZE = 8
SIGNAL_WORD_COLOR_DANGER = (0.8, 0, 0)  # Dark red for DANGER
SIGNAL_WORD_COLOR_WARNING = (0.9, 0.6, 0)  # Orange for WARNING

# HAZARD STATEMENTS (H-codes)
H_STATEMENT_FONT = "Helvetica"
H_STATEMENT_SIZE = 5  # VERY SMALL - this is key to fitting everything
H_STATEMENT_COLOR = (0, 0, 0)  # Black
H_STATEMENT_LINE_SPACING = 1.0  # Single-spaced (tight)

# PRECAUTIONARY STATEMENTS (P-codes)
P_STATEMENT_FONT = "Helvetica"
P_STATEMENT_SIZE = 5  # VERY SMALL
P_STATEMENT_COLOR = (0.1, 0.1, 0.1)  # Near-black
P_STATEMENT_LINE_SPACING = 1.0  # Single-spaced

# SUPPLIER INFO
SUPPLIER_FONT = "Helvetica"
SUPPLIER_SIZE = 5
SUPPLIER_COLOR = (0.3, 0.3, 0.3)

# TEXT BLOCK FORMATTING
# CRITICAL: Statements are formatted as CONTINUOUS PARAGRAPHS, not bullet lists
# This allows maximum information density
TEXT_BLOCK_FORMAT = "paragraph"  # NOT "bullets" or "list"
```

## 5.6 Dense Text Block Implementation

```python
def draw_dense_text_block(canvas, statements, x, y, width, font, size, color, 
                          line_spacing=1.0, strip_codes=True):
    """
    Draw statements as a dense continuous paragraph.
    
    This is the KEY function for fitting all GHS-required text.
    Uses very small font (5pt) and tight line spacing.
    
    Args:
        canvas: ReportLab canvas
        statements: List of statement strings
        x: Left edge X position
        y: Top Y position (text flows DOWN from here)
        width: Maximum text width
        font: Font name
        size: Font size in points
        color: RGB tuple
        line_spacing: Multiplier for line height (1.0 = single-spaced)
        strip_codes: If True, remove "P210:", "H225:" prefixes
    
    Returns:
        Y position after all text (bottom of text block)
    """
    
    canvas.setFont(font, size)
    canvas.setFillColor(Color(*color))
    
    line_height = size * line_spacing
    current_y = y
    
    # Combine all statements into one paragraph
    if strip_codes:
        # Remove "P210: ", "H225: " etc. prefixes
        import re
        clean_statements = []
        for s in statements:
            clean = re.sub(r'^[PH]\d+(\+[PH]\d+)*:\s*', '', s)
            clean_statements.append(clean)
        full_text = " ".join(clean_statements)
    else:
        full_text = " ".join(statements)
    
    # Word-wrap the combined text
    words = full_text.split()
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        test_width = stringWidth(test_line, font, size)
        
        if test_width <= width:
            current_line.append(word)
        else:
            # Draw current line and start new one
            if current_line:
                line_text = " ".join(current_line)
                canvas.drawString(x, current_y - size, line_text)
                current_y -= line_height
            current_line = [word]
    
    # Draw final line
    if current_line:
        line_text = " ".join(current_line)
        canvas.drawString(x, current_y - size, line_text)
        current_y -= line_height
    
    return current_y
```

## 5.7 Complete Column 3 Implementation

```python
def draw_column_3(canvas, sku_data):
    """
    Draw the right column with GHS pictograms and ALL hazard/precautionary statements.
    
    This column contains ALL legally required GHS elements.
    Uses dense small text to fit everything.
    """
    
    x = COLUMN_3_LEFT
    y = MAIN_TOP
    col_width = COLUMN_3_WIDTH
    
    # Skip this column entirely if not hazcom applicable
    if not sku_data.hazcom_applicable:
        return
    
    # 1. GHS PICTOGRAMS (standard format, no decorative cards)
    pictogram_ids = [p.value if hasattr(p, 'value') else p for p in sku_data.ghs_pictograms]
    
    ghs_height = draw_ghs_pictograms_standard(
        canvas, pictogram_ids,
        x, y,
        size=GHS_PICTOGRAM_SIZE,
        gap=GHS_GRID_GAP
    )
    
    y -= ghs_height + 8  # Space after pictograms
    
    # 2. SIGNAL WORD
    if sku_data.signal_word:
        signal = sku_data.signal_word.value if hasattr(sku_data.signal_word, 'value') else str(sku_data.signal_word)
        
        canvas.setFont(SIGNAL_WORD_FONT, SIGNAL_WORD_SIZE)
        
        if signal.upper() == "DANGER":
            canvas.setFillColor(Color(*SIGNAL_WORD_COLOR_DANGER))
        else:
            canvas.setFillColor(Color(*SIGNAL_WORD_COLOR_WARNING))
        
        canvas.drawString(x, y - SIGNAL_WORD_SIZE, signal.upper())
        y -= SIGNAL_WORD_SIZE + 6
    
    # 3. HAZARD STATEMENTS (H-codes)
    # Draw as dense paragraph with SMALL font
    if sku_data.hazard_statements:
        y = draw_dense_text_block(
            canvas, 
            sku_data.hazard_statements,
            x, y, col_width,
            H_STATEMENT_FONT, H_STATEMENT_SIZE, H_STATEMENT_COLOR,
            line_spacing=1.0,
            strip_codes=False  # Keep H-codes visible: "H225: Highly flammable..."
        )
        y -= 4  # Small gap before P-statements
    
    # 4. PRECAUTIONARY STATEMENTS (P-codes)
    # This is where the dense text really matters
    if sku_data.precaution_statements:
        # Add "See SDS" note at end
        p_statements = list(sku_data.precaution_statements)
        p_statements.append("See SDS for complete precautionary information.")
        
        y = draw_dense_text_block(
            canvas,
            p_statements,
            x, y, col_width,
            P_STATEMENT_FONT, P_STATEMENT_SIZE, P_STATEMENT_COLOR,
            line_spacing=1.0,
            strip_codes=True  # Remove P-codes, just show text
        )
    
    # 5. SUPPLIER INFORMATION (at bottom of column)
    supplier_y = MAIN_BOTTOM + 4
    
    canvas.setFont(SUPPLIER_FONT, SUPPLIER_SIZE)
    canvas.setFillColor(Color(*SUPPLIER_COLOR))
    
    canvas.drawString(x, supplier_y + 16, COMPANY_INFO['name'])
    canvas.drawString(x, supplier_y + 10, COMPANY_INFO['address'])
    canvas.drawString(x, supplier_y + 4, COMPANY_INFO['phone'])
```

---

# PART 6: FOOTER BAR SPECIFICATION

## 6.1 Visual Appearance
Simple dark bar at bottom with emergency contact and optional website.

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Emergency: CHEMTEL 1-800-255-3924                    alliancechemical.com │
└────────────────────────────────────────────────────────────────────────────┘
```

## 6.2 Specifications

```python
# FOOTER COLORS
FOOTER_BACKGROUND_COLOR = (0.1, 0.1, 0.12)  # Dark gray, almost black

# FOOTER TEXT
FOOTER_FONT = "Helvetica"
FOOTER_BOLD_FONT = "Helvetica-Bold"
FOOTER_SIZE = 7
FOOTER_TEXT_COLOR = (0.9, 0.9, 0.9)  # Light gray/white
FOOTER_ACCENT_COLOR = (0, 0.7, 0.55)  # Teal for "Emergency:" label
```

## 6.3 Implementation

```python
def draw_footer(canvas, sku_data):
    """Draw the dark footer bar with emergency contact."""
    
    # 1. Dark background
    canvas.setFillColor(Color(*FOOTER_BACKGROUND_COLOR))
    canvas.rect(0, FOOTER_BOTTOM, LABEL_WIDTH, FOOTER_HEIGHT, fill=1, stroke=0)
    
    # 2. Emergency contact (left side)
    text_y = FOOTER_BOTTOM + (FOOTER_HEIGHT / 2) - 3
    
    # "Emergency:" in teal
    canvas.setFont(FOOTER_BOLD_FONT, FOOTER_SIZE)
    canvas.setFillColor(Color(*FOOTER_ACCENT_COLOR))
    canvas.drawString(MARGIN_LEFT, text_y, "Emergency:")
    
    # Phone number in white
    emergency_label_width = stringWidth("Emergency: ", FOOTER_BOLD_FONT, FOOTER_SIZE)
    canvas.setFillColor(Color(*FOOTER_TEXT_COLOR))
    canvas.setFont(FOOTER_FONT, FOOTER_SIZE)
    canvas.drawString(MARGIN_LEFT + emergency_label_width, text_y, 
                      f"CHEMTEL {sku_data.chemtel_number}")
    
    # 3. Website (right side)
    canvas.setFillColor(Color(*FOOTER_TEXT_COLOR))
    canvas.drawRightString(LABEL_WIDTH - MARGIN_RIGHT, text_y, 
                           COMPANY_INFO['website'])
```

---

# PART 7: COMPLETE RENDERER CLASS

## 7.1 Main Renderer Structure

```python
class ScientificLabelRenderer:
    """
    Renders chemical labels in Sigma-Aldrich scientific style.
    
    Key characteristics:
    - 3-column layout
    - Solid color header (no gradient)
    - Standard GHS pictograms (no decorative cards)
    - Dense small text for statements
    - White background throughout
    - Minimal visual effects
    """
    
    def __init__(self, sku_data: SKUData):
        self.data = sku_data
        self.c = None
    
    def render(self, output_path: Path, lot_number: str = None) -> Path:
        """Render the label to PDF."""
        
        if lot_number:
            self.data.lot_number = lot_number
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(output_path), pagesize=(LABEL_WIDTH, LABEL_HEIGHT))
        
        # White background (implicit - PDF default)
        
        # Draw all sections
        self._draw_header()
        self._draw_column_1()
        self._draw_column_2()
        self._draw_column_3()
        self._draw_footer()
        
        self.c.save()
        return output_path
    
    def _draw_header(self):
        draw_header(self.c, self.data)
    
    def _draw_column_1(self):
        draw_column_1(self.c, self.data)
    
    def _draw_column_2(self):
        draw_column_2(self.c, self.data)
    
    def _draw_column_3(self):
        draw_column_3(self.c, self.data)
    
    def _draw_footer(self):
        draw_footer(self.c, self.data)
```

---

# PART 8: CRITICAL DIFFERENCES FROM CURRENT DESIGN

## 8.1 What to REMOVE (Current Alliance Style)

| Element | Current | Scientific Style |
|---------|---------|------------------|
| Header gradient | Brushed metal effect | Solid color |
| GHS card borders | Teal glow + dark cards | NO cards, standard GHS |
| Shadow effects | Drop shadows everywhere | NO shadows |
| Glow effects | Teal glow on accents | NO glow |
| Signal word | Large pill badge | Simple bold text |
| P-statement size | 6-7pt | 4-5pt (smaller) |
| P-statement format | May truncate | ALL statements shown |
| Layout | 2 columns | 3 columns |
| DOT info | Fancy badge | Simple text |
| Data block | Dark floating card | Simple text list |

## 8.2 What to ADD/CHANGE

| Element | Change |
|---------|--------|
| Column 3 | New dedicated hazard column |
| Text density | Much smaller, tighter spacing |
| GHS pictograms | Smaller (32pt vs 52pt) |
| P-statements | ALL must be visible |
| Format | Paragraphs, not bullets |
| Decorative lines | Add to header |
| CAS/SKU layout | Vertical stack in Column 1 |

---

# PART 9: TESTING CHECKLIST

After implementation, verify:

## 9.1 Visual Tests
- [ ] Header is solid color (no gradient)
- [ ] 3-column layout is visible
- [ ] GHS pictograms have standard red diamond (no teal)
- [ ] No shadows or glow effects anywhere
- [ ] Text is legible at 5pt size

## 9.2 Content Tests
- [ ] Product name visible
- [ ] All GHS pictograms displayed
- [ ] Signal word displayed
- [ ] ALL H-statements visible
- [ ] ALL P-statements visible
- [ ] "See SDS for complete information" at end
- [ ] CAS number visible
- [ ] SKU visible
- [ ] Lot number visible
- [ ] Net contents (US and metric)
- [ ] DOT info (if applicable)
- [ ] Emergency contact number
- [ ] Supplier name and address

## 9.3 Compliance Tests
- [ ] Meets OSHA HazCom 2012 requirements
- [ ] GHS pictograms are standard format
- [ ] All required elements present

---

# PART 10: FILE STRUCTURE

## 10.1 New Files to Create

```
src/
├── templates/
│   └── scientific_style.py    # New template module
├── label_renderer_scientific.py  # New renderer class
└── config_scientific.py       # Constants for scientific style
```

## 10.2 Files to Modify

```
src/
├── config.py          # Add scientific style constants
├── cli.py             # Add --style flag to choose template
├── components/
│   └── ghs.py         # Add standard GHS renderer (no cards)
└── utils/
    └── text_fitting.py  # Add dense_paragraph function
```

---

# APPENDIX A: COMPLETE COLOR REFERENCE

```python
# SCIENTIFIC STYLE COLOR PALETTE

COLORS_SCIENTIFIC = {
    # BACKGROUNDS
    "white": (1, 1, 1),
    "header_teal": (0/255, 180/255, 150/255),  # #00B496
    "footer_dark": (26/255, 26/255, 31/255),   # #1A1A1F
    
    # TEXT
    "text_black": (0, 0, 0),
    "text_dark": (0.1, 0.1, 0.1),
    "text_gray": (0.4, 0.4, 0.4),
    "text_light_gray": (0.6, 0.6, 0.6),
    "text_white": (1, 1, 1),
    
    # ACCENTS
    "accent_teal": (0, 0.7, 0.55),
    "danger_red": (0.8, 0, 0),
    "warning_orange": (0.9, 0.6, 0),
    
    # GHS
    "ghs_red": (1, 0, 0),
    
    # LINES
    "separator_light": (0.8, 0.8, 0.8),
    "separator_dark": (0.3, 0.3, 0.3),
}
```

---

# APPENDIX B: FONT SIZE REFERENCE

```python
# ALL FONT SIZES FOR SCIENTIFIC STYLE

FONT_SIZES_SCIENTIFIC = {
    # HEADER
    "company_name": 11,
    
    # COLUMN 1 (Identifiers)
    "product_code": 11,
    "sku": 9,
    "lot": 9,
    "cas": 7,
    "mol_weight": 7,
    "qr_label": 5,
    
    # COLUMN 2 (Product Info)
    "product_name": 12,
    "grade": 9,
    "contains": 7,
    "warning": 7,
    "net_contents_us": 14,
    "net_contents_metric": 9,
    "dot_info": 8,
    "small_text": 7,
    
    # COLUMN 3 (GHS)
    "signal_word": 8,
    "h_statement": 5,  # CRITICAL: Very small
    "p_statement": 5,  # CRITICAL: Very small
    "supplier": 5,
    
    # FOOTER
    "footer": 7,
    
    # LABELS (above values)
    "label": 6,
}
```

---

# END OF SPECIFICATION

This document provides complete specifications for recreating a Sigma-Aldrich style
scientific chemical label. Follow each section exactly for accurate implementation.