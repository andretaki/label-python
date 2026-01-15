# Sigma-Aldrich Label Analysis & Recreation Specification

## Overview
This document provides a comprehensive analysis of the Sigma-Aldrich chemical label design for recreation in the Alliance Chemical label generator.

---

## LAYOUT STRUCTURE

### Overall Dimensions
- Standard lab label: approximately 4" x 3" (estimate from image)
- Horizontal orientation
- White background with colored header band

### Grid Layout (3-Column Design)
```
┌─────────────────────────────────────────────────────────────────────┐
│ [GREEN HEADER BAR - Full Width]                          [LOGO]    │
├───────────────┬─────────────────────────┬───────────────────────────┤
│               │                         │                           │
│   LEFT COL    │      CENTER COL         │       RIGHT COL           │
│   (~20%)      │       (~40%)            │        (~40%)             │
│               │                         │                           │
│  Identifiers  │   Product Info          │   GHS + Statements        │
│  & Codes      │   & Warnings            │   (DENSE TEXT)            │
│               │                         │                           │
└───────────────┴─────────────────────────┴───────────────────────────┘
```

---

## SECTION A: GREEN HEADER BAR

### Specifications
- **Color**: Sigma-Aldrich Green (#00805A or similar forest green)
- **Height**: ~12-15% of total label height
- **Width**: 100% (full width)
- **Position**: Top edge

### Contents (Left to Right)
1. White vertical accent lines (decorative)
2. Company logo (right side) - "Supelco" in white

### Alliance Adaptation
- Use **Alliance Teal** (#00D4AA) instead of green
- Place Alliance logo on left
- Add "ALLIANCE CHEMICAL" text

---

## SECTION B-D: LEFT COLUMN (Identifiers)

### Element H: Catalog/Product Code
- **Content**: "1002846698" (large, bold)
- **Font Size**: ~12pt bold
- **Label**: "PCode" above in small text (~6pt)

### Element I: SKU/Batch Code  
- **Content**: "SLBX2192"
- **Label**: "Source" above
- **Font Size**: ~10pt

### Element J: Expiration Date
- **Content**: "31/05/21"
- **Format**: DD/MM/YY
- **Label**: "Exp. Date (DD/MM/YY)"
- **Font Size**: ~10pt

### Element K: Chemical Formula
- **Content**: "C₁₇H₂₁NO₄ · HCl"
- **Uses subscript formatting**
- **Font Size**: ~8pt

### Element L: Molecular Data
- **Line 1**: "M = 339.81 g/mol" (molecular weight)
- **Line 2**: "CAS-No: 53-21-4"
- **Font Size**: ~7pt

### Element M: Storage Temperature
- **Visual Icon**: Thermometer with "2°C" to "8°C" range
- **Size**: ~15x15pt icon
- **Shows min/max temperature visually**

### Element N: QR Code
- **Size**: ~40x40pt
- **Position**: Bottom of left column
- **Links to**: Product page or SDS

---

## SECTION C-D: CENTER COLUMN (Product Info)

### Product Name Block
- **Main Name**: "Cocaine hydrochloride solution" (bold, ~11pt)
- **Description**: "1.0 mg/mL in methanol, analytical standard, for drug analysis" (~8pt, regular)
- **Multi-language**: German translation below

### Warnings Block (Element labeled with warning triangle)
- **Contains Statement**: "(Contains: Methanol, Cocaine hydrochloride)"
- **Allergen Warning**: "May produce an allergic reaction. Safety datasheet is available. TK# 18-49"
- **Use Restriction**: "For R&D use only. Not for drug, household, or other uses."

### Origin Block
- **Text**: "Made in USA"
- **Font Size**: ~8pt

### Website
- **URL**: "sigmaaldrich.com"
- **Font Size**: ~7pt

---

## SECTION E-G: RIGHT COLUMN (GHS Hazard Block)

### THIS IS THE CRITICAL COMPLIANCE SECTION

### GHS Pictograms (Elements A-E in image header)
**Arranged in 2 rows of 3:**
```
┌─────┐ ┌─────┐ ┌─────┐
│ 🔥  │ │ ⚠️  │ │ ☠️  │
│GHS02│ │GHS07│ │GHS06│
└─────┘ └─────┘ └─────┘
┌─────┐ ┌─────┐ ┌─────┐
│ 💀 │ │ 🏥  │ │ 🌊  │
│GHS06│ │GHS08│ │GHS09│
└─────┘ └─────┘ └─────┘
```

- **Size**: ~28-32pt each
- **Standard GHS red diamond frame**
- **NO decorative borders** - just standard GHS format
- **Grid**: 3 columns x 2 rows with minimal spacing

### Signal Word
- **Text**: "EN Danger" (language prefix)
- **Position**: Top of text block, before statements
- **Style**: Bold, same size as body text

### Hazard & Precautionary Statements (Element G - Dense Text Block)
**THIS IS KEY - They show EVERYTHING in tiny text:**

- **Font Size**: ~4-5pt (very small!)
- **Line Spacing**: ~1.0 (tight)
- **Languages**: English, German, Spanish, French, Dutch (multi-language)
- **Format**: Continuous paragraph, not bulleted
- **Contains**:
  - All H-statements (hazard)
  - All P-statements (precautionary)
  - All in one dense block

**Example Text Style:**
```
EN Danger Highly flammable liquid and vapor. Toxic if swallowed, in contact 
with skin or if inhaled. Causes damage to organs (Eyes). Keep away from 
heat, hot surfaces, sparks, open flames and other ignition sources. No 
smoking. Wear protective gloves/protective clothing. IF SWALLOWED: 
Immediately call a POISON CENTER/doctor. Rinse mouth. IF ON SKIN: 
Wash with plenty of water. Call a POISON CENTER/doctor if you feel 
unwell. IF INHALED: Remove person to fresh air and keep comfortable for 
breathing. Call a POISON CENTER/doctor...
```

### Supplier Information (Element U)
- **Position**: Bottom right
- **Content**: 
  - "SIGMA-ALDRICH, Co., 3050 Spruce Street, St. Louis, MO 63103 USA +1-314-771-5765"
  - "SIGMA-ALDRICH CHEMIE GmbH, Riedstr. 2, 89555 Steinheim, Germany +49 7329 970"
  - "Affiliates of Merck KGaA, Darmstadt, Germany"
- **Font Size**: ~5pt

---

## COLOR PALETTE

| Element | Color | Hex (Approx) |
|---------|-------|--------------|
| Header Bar | Forest Green | #00805A |
| Background | White | #FFFFFF |
| Primary Text | Black | #000000 |
| Secondary Text | Dark Gray | #333333 |
| GHS Diamonds | Red border | #FF0000 |
| Accent Lines | White on green | #FFFFFF |

### Alliance Adaptation Colors
| Element | Color | Hex |
|---------|-------|-----|
| Header Bar | Alliance Teal | #00D4AA |
| Background | White | #FFFFFF |
| Primary Text | Near Black | #0D0D0F |
| Secondary Text | Dark Gray | #505058 |
| GHS Diamonds | Standard Red | #FF0000 |

---

## TYPOGRAPHY

### Font Family
- **Primary**: Arial or Helvetica (sans-serif)
- **Monospace**: For codes/numbers

### Font Sizes (Approximate)
| Element | Size |
|---------|------|
| Product Code (H) | 12pt bold |
| Product Name | 11pt bold |
| Description | 8pt regular |
| Identifiers (I,J,K,L) | 7-8pt |
| GHS Statements | 4-5pt |
| Supplier Info | 5pt |

---

## CRITICAL REQUIREMENTS FOR RECREATION

### 1. Dense P-Statement Block
```python
# The key is TINY text with ALL statements
P_STATEMENT_FONT_SIZE = 4.5  # Very small!
P_STATEMENT_LINE_SPACING = 1.0  # Tight
P_STATEMENT_FORMAT = "paragraph"  # Not bullets

# Include ALL statements, not truncated
# Add "See SDS for complete information" at end
```

### 2. GHS Grid (Not Floating Cards)
```python
# Standard GHS diamonds, no decorative borders
GHS_SIZE = 30  # Smaller than current
GHS_GRID = (3, 2)  # 3 columns, 2 rows
GHS_SPACING = 2  # Minimal spacing
GHS_STYLE = "standard"  # Red diamond, white background, NO teal border
```

### 3. Left Column Data Stack
```python
# Vertical stack of identifiers
LEFT_COLUMN_ELEMENTS = [
    ("PCode", product_code, 12, "bold"),
    ("Source", sku, 10, "regular"),
    ("Exp. Date", expiry, 8, "regular"),
    ("", formula, 8, "regular"),  # Chemical formula
    ("M =", molecular_weight, 7, "regular"),
    ("CAS-No:", cas_number, 7, "regular"),
    ("storage_icon", temp_range, 15, "icon"),
    ("qr_code", sds_url, 40, "image"),
]
```

### 4. Header Bar Style
```python
# Simple colored bar, no gradient
HEADER_STYLE = "solid_color"  # Not gradient
HEADER_COLOR = ALLIANCE_TEAL
HEADER_HEIGHT = 40  # Points
LOGO_POSITION = "left"
COMPANY_TEXT_POSITION = "center"
```

---

## IMPLEMENTATION INSTRUCTIONS FOR CLAUDE CODE

### Task 1: Create New Layout Template
```
Create a new label layout called "sigma_style" or "scientific_style" with:
- 3-column layout (20% / 40% / 40%)
- Solid color header bar (not gradient)
- White background throughout
- No dark cards or floating panels
```

### Task 2: Redesign GHS Section
```
Replace current GHS card styling with:
- Standard GHS pictograms (red diamond, white background)
- NO teal borders or glow effects
- Smaller size (30pt vs 52pt)
- Grid layout: 3 columns x 2 rows
- Minimal spacing between pictograms
```

### Task 3: Dense Text Block for Statements
```
Create a new text renderer that:
- Uses 4.5pt font for P-statements
- Line spacing of 1.0 (single-spaced)
- Formats as continuous paragraph
- Fits ALL statements in available space
- Adds language prefix if needed (EN, DE, etc.)
```

### Task 4: Left Column Data Stack
```
Create vertical stack of:
- Product/Catalog code (large)
- SKU/Source code
- Lot number
- Expiration date (if applicable)
- CAS number
- Molecular weight (if applicable)
- Storage temperature icon (if applicable)
- QR code at bottom
```

### Task 5: Simplify Visual Effects
```
REMOVE:
- Gradient backgrounds
- Glow effects
- Drop shadows on cards
- Teal borders on GHS

KEEP:
- Clean lines
- Solid colors
- High contrast text
```

---

## FILE CHANGES REQUIRED

### 1. src/config.py
- Add new template "scientific_style"
- Add color constants for solid header
- Reduce GHS_CARD_SIZE to 30
- Add LEFT_COLUMN_WIDTH constant

### 2. src/components/ghs.py
- Add `draw_ghs_pictogram_standard()` function
- Remove card styling for scientific template
- Create grid layout function

### 3. src/label_renderer.py
- Create new `ScientificLabelRenderer` class
- Or add template switching logic
- Implement 3-column layout
- Implement dense text block

### 4. src/utils/text_fitting.py
- Add `render_dense_paragraph()` function
- Support 4pt minimum font
- Single-spaced line height option

---

## SAMPLE OUTPUT STRUCTURE

```
┌────────────────────────────────────────────────────────────────────┐
│ [TEAL BAR] ALLIANCE CHEMICAL                      [LOGO]          │
├────────────┬─────────────────────────┬─────────────────────────────┤
│ PCode      │                         │ ┌───┐┌───┐┌───┐            │
│ 850123456  │ Isopropyl Alcohol       │ │GHS││GHS││GHS│            │
│            │ 99% ACS Reagent Grade   │ │02 ││07 ││   │            │
│ SKU        │                         │ └───┘└───┘└───┘            │
│ AC-IPA-99  │ Highly flammable liquid │                            │
│            │ and vapor. For          │ DANGER                     │
│ LOT        │ industrial use.         │                            │
│ TEST-001   │                         │ Highly flammable liquid    │
│            │ Contains: Isopropanol   │ and vapor. Causes serious  │
│ CAS-No:    │                         │ eye irritation. May cause  │
│ 67-63-0    │                         │ drowsiness or dizziness.   │
│            │ 55 Gallons              │ Keep away from heat, hot   │
│ ┌────┐     │ 208 L                   │ surfaces, sparks, open     │
│ │ QR │     │                         │ flames. No smoking. Keep   │
│ │CODE│     │ DOT: UN1219, Class 3    │ container tightly closed.  │
│ └────┘     │ Packing Group II        │ Ground/bond container...   │
│            │                         │                            │
├────────────┴─────────────────────────┴─────────────────────────────┤
│ Emergency: CHEMTEL 1-800-255-3924  │  alliancechemical.com        │
└────────────────────────────────────────────────────────────────────┘
```

---

## VALIDATION CHECKLIST

Before considering the label complete, verify:

- [ ] All GHS pictograms displayed (standard format)
- [ ] Signal word present (DANGER/WARNING)
- [ ] ALL H-statements visible
- [ ] ALL P-statements visible (even if tiny)
- [ ] "See SDS for complete information" included
- [ ] Supplier name and address
- [ ] Emergency contact number
- [ ] Product identifier matches SDS
- [ ] CAS number (if single substance)
- [ ] Net contents (quantity)

---

## NOTES

1. **Legibility vs. Compliance**: Sigma-Aldrich uses ~4pt text to fit everything. This is legally compliant but hard to read. Consider offering both "readable" and "compliant" versions.

2. **Multi-language**: Sigma-Aldrich includes multiple languages. For US-only distribution, English only is acceptable.

3. **Label Size**: The dense layout works better on larger labels (4x6"). On smaller labels (4x3"), may need to prioritize elements.

4. **QR Code as Escape Valve**: The QR code linking to full SDS allows the tiny text to be supplemented digitally.