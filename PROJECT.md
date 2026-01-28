# Alliance Chemical Label Generator

## Project Overview

A system for generating regulatory-compliant chemical product labels (PDF) and printing them via a web-based warehouse station. Built for Alliance Chemical's product line.

**Core workflow:** Shopify product data + chemical hazard database → merged label JSON → PDF label → printed via warehouse station.

---

## Architecture

```
┌──────────────────────┐                      ┌─────────────────────────────┐
│  Next.js (Vercel)    │      Tailscale       │  Print Station PC           │
│  print-ui/           │      (secure)        │                             │
│  - Product search    │ ───────────────────► │  FastAPI agent (:8080)      │
│  - Lot selector      │   POST /print        │  src/print_agent/           │
│  - Barcode scanner   │                      │  - Generates PDF            │
│                      │ ◄─────────────────── │  - Prints via SumatraPDF    │
└──────────┬───────────┘   { success }        └─────────────────────────────┘
           │
           ▼
┌──────────────────────┐
│  Neon PostgreSQL     │
│  - products table    │
│  - print_jobs table  │
└──────────────────────┘
```

---

## Directory Structure

```
label-python/
├── src/                              # Python core
│   ├── cli.py                        # Typer CLI (generate, batch, import, db commands)
│   ├── config.py                     # Global configuration constants
│   ├── models.py                     # Pydantic data models (SKUData, ChemicalData, etc.)
│   ├── label_renderer.py             # Standard (frame) label renderer
│   ├── label_renderer_organic.py     # Organic/modern label style
│   ├── label_renderer_scientific.py  # Sigma-Aldrich 3-column style
│   ├── components/                   # Reusable label drawing components
│   │   ├── barcode.py                # UPC barcode generation
│   │   ├── dot.py                    # DOT shipping diamond
│   │   ├── ghs.py                    # GHS hazard pictograms
│   │   ├── ghs_frosted.py           # Frosted glass GHS variant
│   │   ├── nfpa.py                   # NFPA 704 fire diamond
│   │   └── qrcode.py                # QR code generation
│   ├── database/                     # Data layer
│   │   ├── chemical_db.py            # Chemical hazard data model + JSON loader
│   │   ├── sku_mapper.py             # SKU prefix → chemical ID mapping
│   │   └── merger.py                 # Combines Shopify product + hazmat → label JSON
│   ├── importers/                    # External data importers
│   │   ├── shopify.py                # CSV import from Shopify export
│   │   └── shopify_api.py            # Direct Shopify Admin API import
│   ├── print_agent/                  # FastAPI print server (runs on warehouse PC)
│   │   ├── main.py                   # /health and /print endpoints
│   │   ├── printer.py                # SumatraPDF (Windows) / lp (Unix) wrapper
│   │   ├── config.py                 # Printer env config
│   │   └── models.py                 # Request/response Pydantic models
│   └── utils/                        # Drawing utilities
│       ├── effects.py                # Visual effects (shadows, glows)
│       ├── gradients.py              # Gradient backgrounds
│       ├── organic_shapes.py         # Organic style shape helpers
│       └── text_fitting.py           # Text wrapping and dense paragraph rendering
│
├── print-ui/                         # Next.js 16 web frontend
│   ├── app/
│   │   ├── page.tsx                  # Main print interface
│   │   ├── layout.tsx                # App shell (header, nav)
│   │   ├── history/page.tsx          # Print job audit log
│   │   └── api/                      # API routes
│   │       ├── products/route.ts     # GET ?q=search or ?upc=barcode
│   │       ├── print/route.ts        # POST - logs print job to DB
│   │       ├── history/route.ts      # GET - fetch recent print jobs
│   │       └── agent/route.ts        # GET - proxy to print agent /health
│   ├── components/
│   │   ├── ProductSearch.tsx          # Search + barcode scanner auto-submit
│   │   ├── LotSelector.tsx            # Month/Year/Run dropdowns (MMYYAL format)
│   │   ├── QuantityInput.tsx          # Spinner (1-100)
│   │   ├── PrintButton.tsx            # Submit button with loading state
│   │   └── AgentStatus.tsx            # Print agent connectivity indicator
│   └── lib/
│       ├── db.ts                      # Drizzle + Neon connection
│       ├── schema.ts                  # products + print_jobs tables
│       ├── agent.ts                   # HTTP client for print agent
│       └── lot.ts                     # MMYYAL lot number utilities
│
├── data/
│   ├── chemicals/                    # Chemical hazard JSON files
│   ├── test_skus/                    # Sample SKU data for testing
│   └── sku_mappings.json             # SKU prefix → chemical ID rules
│
├── assets/
│   ├── ghs/                          # GHS pictogram PNGs (GHS01-GHS09)
│   └── logo.png                      # Alliance Chemical logo
│
├── fonts/                            # TTF fonts (Anton, Barlow, IBM Plex, etc.)
├── Alliance_Logo/                    # Brand assets (AI, EPS, PDF, PNG, JPEG)
│
├── pyproject.toml                    # Python project config + dependencies
├── requirements.txt                  # Python dependencies (pinned)
├── AGENT_HANDOFF.md                  # Print station handoff doc
├── SHOPIFY_INTEGRATION_PLAN.md       # Shopify integration plan + DB schema
├── labelspec.md                      # Scientific label design spec
└── prompt.md                         # Label design spec (organic style)
```

---

## Components

### 1. Label Renderer (Python/ReportLab)

Three label styles, all generating 6"x4" PDFs:

| Style | File | Description |
|-------|------|-------------|
| Standard | `label_renderer.py` | Frame-based layout with dark cards |
| Organic | `label_renderer_organic.py` | Modern design, diagonal header, Anton font |
| Scientific | `label_renderer_scientific.py` | Sigma-Aldrich 3-column, dense GHS text |

Each label includes:
- Company branding (header/footer)
- Product name, SKU, lot number, UPC barcode
- GHS pictograms, signal word, H/P-statements
- NFPA 704 fire diamond
- DOT shipping info (UN number, hazard class, packing group)
- QR code linking to SDS
- Net contents (US + metric)

### 2. CLI (`src/cli.py`)

Typer-based commands:

```bash
# Generate labels
python -m src.cli generate <sku> [--lot LOT] [--style organic|scientific|standard]
python -m src.cli batch "SKU1,SKU2,SKU3" [--lot-prefix PREFIX]

# Shopify import
python -m src.cli import-shopify <csv_file> [--overwrite] [--allow-missing]
python -m src.cli import-shopify-api [--store DOMAIN] [--overwrite]

# Database management
python -m src.cli db status
python -m src.cli db sync [--overwrite] [--dry-run]
python -m src.cli db add-chemical <id> <name> [--cas CAS]
python -m src.cli db add-mapping <sku> <chemical_id> [--prefix]
python -m src.cli db list-chemicals
python -m src.cli info <sku>
```

### 3. Print Agent (`src/print_agent/`)

FastAPI server running on the warehouse PC:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Printer status check |
| `/print` | POST | Generate PDF + print (accepts `{sku, lot_number, quantity}`) |

```bash
# Start the agent
uvicorn src.print_agent.main:app --host 0.0.0.0 --port 8080
```

### 4. Web UI (`print-ui/`)

Next.js 16 + React 18 + Tailwind. Deployed to Vercel.

**Features:**
- Product search by name or SKU
- UPC barcode scanner support (auto-submits on 12-digit input)
- Lot number selector (MMYYAL format: month/year/run letter)
- Quantity spinner (1-100)
- Print agent status indicator (polls /health)
- Print history audit log

```bash
# Start dev server
cd print-ui && npm run dev
```

---

## Data Flow

### Label Generation Pipeline

```
Shopify CSV/API  ──►  SKU Stub (JSON)  ──►  Merger  ──►  Label JSON  ──►  PDF
                           │                    ▲
                           ▼                    │
                      SKU Mapper  ──►  Chemical DB (JSON)
                   (sku_mappings.json)    (data/chemicals/)
```

1. **Import**: Shopify products → SKU stub JSON files (`data/skus/`)
2. **Map**: SKU prefix rules match stubs to chemical IDs (`data/sku_mappings.json`)
3. **Merge**: Combine Shopify data (name, size, UPC) + hazmat data (GHS, NFPA, DOT)
4. **Render**: Complete label JSON → PDF via chosen renderer style

### Print Flow

1. Warehouse operator searches product in web UI
2. Selects product, sets lot number + quantity
3. Clicks Print → POST to print agent via Tailscale
4. Agent generates PDF using `label_renderer_organic.py`
5. Agent sends PDF to Epson C7500 via SumatraPDF (Windows) or lp (Unix)
6. Result logged to PostgreSQL `print_jobs` table

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| PDF Generation | Python 3.11+, ReportLab |
| CLI | Typer |
| Print Server | FastAPI, Uvicorn |
| Frontend | Next.js 16, React 18, TypeScript |
| Styling | Tailwind CSS |
| Database | PostgreSQL (Neon), Drizzle ORM |
| Networking | Tailscale VPN (UI ↔ print agent) |
| Printer | Epson ColorWorks C7500 |
| Hosting | Vercel (frontend), local PC (print agent) |

---

## SKU Naming Convention

```
[COMPANY]-[CHEMICAL]-[GRADE]-[SIZE]

AC-IPA-99-1GAL    → Isopropyl Alcohol 99%, 1 Gallon
AC-IPA-99-55      → Isopropyl Alcohol 99%, 55 Gallon
AC-IPA-70-1GAL    → Isopropyl Alcohol 70%, 1 Gallon
AC-ACET-ACS-5GAL  → Acetone ACS Grade, 5 Gallon
AC-PA-10-5G       → Phosphoric Acid 10%, 5 Gallon
AC-NAHCO3-50      → Sodium Bicarbonate, 50 lb
AC-MO-FG-1G       → Mineral Oil Food Grade, 1 Gallon
```

---

## Environment Variables

### Python / Print Agent

```bash
PRINTER_NAME="Epson ColorWorks C7500"
SUMATRA_PATH="C:\Program Files\SumatraPDF\SumatraPDF.exe"
PRINT_AGENT_HOST=0.0.0.0
PRINT_AGENT_PORT=8080
```

### Shopify Import

```bash
SHOPIFY_STORE="your-store.myshopify.com"
SHOPIFY_ACCESS_TOKEN="shpat_xxxxxxxxxxxxx"
```

### Web UI (`print-ui/.env.local`)

```bash
DATABASE_URL="postgresql://..."
NEXT_PUBLIC_PRINT_AGENT_URL="http://localhost:8080"
```

---

## Regulatory Standards

Labels comply with:

- **OSHA HazCom 2012** (29 CFR 1910.1200) — GHS-aligned hazard communication
- **GHS Rev 7+** — Globally Harmonized System pictograms, signal words, H/P-statements
- **NFPA 704** — Fire diamond (health, flammability, reactivity, special)
- **DOT 49 CFR** — Proper shipping name, UN number, hazard class, packing group

---

## Implementation Status

### Completed

- [x] Three label renderer styles (standard, organic, scientific)
- [x] GHS pictogram rendering (standard + frosted variants)
- [x] NFPA 704 diamond component
- [x] DOT shipping info component
- [x] Barcode + QR code generation
- [x] CLI with generate, batch, import, and db commands
- [x] Shopify CSV and API importers
- [x] SKU → chemical mapping system
- [x] Data merger (Shopify + hazmat)
- [x] Print agent (FastAPI) with /health and /print
- [x] Web UI with product search, lot selector, barcode scanner
- [x] Print job history/audit log
- [x] Neon PostgreSQL schema (products + print_jobs)

### Pending

- [ ] PostgreSQL connector for hazmat database (need schema details)
- [ ] Bulk chemical import from external DB
- [ ] Tailscale production setup (UI ↔ print agent)
- [ ] Vercel deployment with environment variables
- [ ] Full product catalog import to Postgres
- [ ] Operator authentication (printedBy field exists, unused)
- [ ] Print preview before sending to printer
- [ ] Webhook listener for real-time Shopify product updates
- [ ] Multi-page batch PDF (multiple labels per sheet)

---

## Quick Start

```bash
# 1. Install Python dependencies
pip install -e .

# 2. Generate a test label
python -m src.cli generate AC-IPA-99-55 --style organic --lot 0126AL

# 3. Start the print agent
uvicorn src.print_agent.main:app --host 127.0.0.1 --port 8080

# 4. Start the web UI
cd print-ui && npm install && npm run dev

# 5. Open http://localhost:3000
```

---

## Related Documentation

| File | Purpose |
|------|---------|
| `AGENT_HANDOFF.md` | Print station setup, endpoints, deployment details |
| `SHOPIFY_INTEGRATION_PLAN.md` | Shopify import pipeline, SKU mapping, DB integration plan |
| `labelspec.md` | Scientific (Sigma-Aldrich) label design specification |
| `prompt.md` | Organic label design specification |
