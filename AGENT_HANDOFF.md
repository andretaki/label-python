# Agent Handoff: Label Print Station

## Project Overview

Web-based label printing system for Alliance Chemical. Allows warehouse operators to search products, enter lot numbers, and print labels directly to an Epson C7500 printer.

**Architecture:**
```
┌──────────────────────┐                      ┌─────────────────────────────┐
│  Next.js (Vercel)    │      Tailscale      │  Print Station PC           │
│  print-ui/           │      (secure)        │                             │
│  - Product search    │ ───────────────────► │  FastAPI agent (:8080)      │
│  - Lot selector      │   POST /print        │  src/print_agent/           │
│  - Print button      │                      │  - Generates PDF            │
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

## What's Been Completed

### 1. Print Agent (Python/FastAPI) ✅
Location: `src/print_agent/`

```
src/print_agent/
├── __init__.py      # Exports FastAPI app
├── main.py          # FastAPI server with /health and /print endpoints
├── printer.py       # SumatraPDF (Windows) and lp (Unix) wrapper
├── config.py        # Environment config (PRINTER_NAME, SUMATRA_PATH, etc.)
└── models.py        # Pydantic models (PrintRequest, PrintResponse, HealthResponse)
```

**Endpoints:**
- `GET /health` - Returns printer status
- `POST /print` - Accepts `{sku, lot_number, quantity}`, generates PDF, prints it

**Dependencies added to pyproject.toml:**
- `fastapi>=0.109`
- `uvicorn>=0.27`

**Tested:** Server starts, endpoints respond, PDF generation works, printing fails gracefully on systems without CUPS/SumatraPDF.

### 2. Web UI (Next.js 16 + Tailwind) ✅
Location: `print-ui/`

```
print-ui/
├── app/
│   ├── layout.tsx           # Header with nav (Print | History)
│   ├── page.tsx             # Main print interface
│   ├── globals.css          # Tailwind + custom animations
│   ├── history/page.tsx     # Print job audit log table
│   └── api/
│       ├── products/route.ts   # GET ?q=search or ?upc=123456789012
│       ├── print/route.ts      # POST - logs print job to database
│       ├── history/route.ts    # GET - fetch recent print jobs
│       └── agent/route.ts      # GET - proxy to agent health
├── components/
│   ├── AgentStatus.tsx      # Green/red status indicator (polls /health)
│   ├── ProductSearch.tsx    # Main search with barcode scanner support
│   ├── LotSelector.tsx      # Month/Year/Run letter dropdowns (MMYYAL)
│   ├── QuantityInput.tsx    # +/- spinner (1-100)
│   ├── PrintButton.tsx      # Large purple button with loading state
│   └── index.ts
├── lib/
│   ├── db.ts                # Drizzle + Neon connection
│   ├── schema.ts            # products + print_jobs tables
│   ├── agent.ts             # HTTP client for print agent
│   └── lot.ts               # MMYYAL lot number utilities
├── drizzle.config.ts
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── .env.local               # DATABASE_URL + PRINT_AGENT_URL (created)
└── .gitignore
```

**npm dependencies installed:** Next.js 16, React 18, Drizzle ORM, @neondatabase/serverless, Tailwind, TypeScript

### 3. Database (Neon PostgreSQL) ✅

**Connection:** Already configured in `print-ui/.env.local`

**Schema pushed:** Two tables created:
- `products` - 27 columns (sku, product_name, ghs_pictograms[], hazard_statements[], etc.)
- `print_jobs` - 10 columns (id, sku, lot_number, quantity, status, printed_at, etc.)

**Seed data:** One test product inserted: `AC-IPA-99-55` (Isopropyl Alcohol)

---

## What Remains To Do

### Immediate (to get it running):

1. **Start the print agent:**
   ```bash
   cd /home/andre/label-python
   .venv/bin/uvicorn src.print_agent.main:app --host 127.0.0.1 --port 8080
   ```

2. **Start the Next.js dev server:**
   ```bash
   cd /home/andre/label-python/print-ui
   npm run dev
   ```

3. **Open http://localhost:3000** and test the flow

### Known Issues to Fix:

1. **Next.js 16 compatibility** - The app was created with Next.js 14 patterns but npm updated to v16. May need to check for breaking changes in:
   - App Router patterns
   - Server Actions
   - Font loading

2. **Barcode scanner testing** - The ProductSearch component auto-submits when 12 digits are entered (barcode scanner behavior). Needs real hardware testing.

3. **Print agent CORS** - Currently allows localhost:3000. For production with Tailscale, need to add the Tailscale hostname.

### Future Work:

1. **Tailscale setup** - Install Tailscale on print station PC, configure Funnel or direct connect
2. **Vercel deployment** - Deploy print-ui to Vercel, set environment variables
3. **Product import script** - Migrate all products from Shopify/JSON to Postgres
4. **Operator authentication** - Track who printed what (printedBy field exists but unused)
5. **Print preview** - Optional PDF preview before printing

---

## Environment Variables

### print-ui/.env.local (already created):
```
DATABASE_URL=postgresql://neondb_owner:npg_mja0bvs8fSeF@ep-falling-hill-addubos2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
NEXT_PUBLIC_PRINT_AGENT_URL=http://localhost:8080
```

### Print Station (environment or .env):
```
PRINTER_NAME=Epson ColorWorks C7500
SUMATRA_PATH=C:\Program Files\SumatraPDF\SumatraPDF.exe
PRINT_AGENT_HOST=0.0.0.0
PRINT_AGENT_PORT=8080
```

---

## Quick Test Commands

```bash
# Test print agent health
curl http://localhost:8080/health

# Test print endpoint (will fail without printer but validates flow)
curl -X POST http://localhost:8080/print \
  -H "Content-Type: application/json" \
  -d '{"sku": "AC-IPA-99-55", "lot_number": "0126AL", "quantity": 1}'

# Query products from database
curl "http://localhost:3000/api/products?q=iso"

# Query by UPC
curl "http://localhost:3000/api/products?upc=850123456785"
```

---

## File Locations Summary

| Component | Location | Purpose |
|-----------|----------|---------|
| Print Agent | `src/print_agent/` | FastAPI server for printing |
| Web UI | `print-ui/` | Next.js frontend |
| Label Renderer | `src/label_renderer_organic.py` | PDF generation (unchanged) |
| Test SKU Data | `data/test_skus/AC-IPA-99-55.json` | Sample product JSON |
| DB Schema | `print-ui/lib/schema.ts` | Drizzle table definitions |

---

## How the Print Flow Works

1. User searches for product (types name or scans UPC barcode)
2. ProductSearch component queries `/api/products` → Postgres
3. User selects product, adjusts lot number (defaults to current month), sets quantity
4. User clicks Print button
5. PrintButton calls `printLabel()` from `lib/agent.ts`
6. Agent client POSTs to print agent at `localhost:8080/print`
7. Print agent calls `generate_organic_label(sku, lot_number)` → creates PDF in temp dir
8. Print agent calls `print_pdf(pdf_path, copies)` → SumatraPDF silent print
9. Agent returns success/failure
10. Web UI logs result to `/api/print` → Postgres print_jobs table
11. User sees success message (or error)

---

## To Continue This Work

1. Start both servers (commands above)
2. Test the full flow at http://localhost:3000
3. Fix any Next.js 16 compatibility issues that arise
4. Add more products to the database for testing
5. Set up Tailscale when ready for production
