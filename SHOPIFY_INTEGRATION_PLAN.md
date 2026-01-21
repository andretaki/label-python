# Shopify Label Integration - Implementation Plan

## Overview

Automatically generate product labels for each Shopify product variant by combining:
1. **Shopify data** - SKU, product name, size, UPC, barcode
2. **Hazmat database** - GHS, NFPA, DOT regulatory data (from PostgreSQL)

---

## Current State

### Completed Infrastructure

| Component | File | Status | Description |
|-----------|------|--------|-------------|
| Shopify CSV Importer | `src/importers/shopify.py` | ✅ Done | Import from Shopify product export CSV |
| Shopify API Importer | `src/importers/shopify_api.py` | ✅ Done | Pull directly from Shopify Admin API |
| Chemical Database Schema | `src/database/chemical_db.py` | ✅ Done | Data model for hazmat info |
| SKU Mapper | `src/database/sku_mapper.py` | ✅ Done | Maps SKU prefixes → chemical IDs |
| Data Merger | `src/database/merger.py` | ✅ Done | Combines Shopify + hazmat → label JSON |
| CLI Commands | `src/cli.py` | ✅ Done | `db sync`, `db status`, etc. |

### Pending Work

| Component | Status | Blocker |
|-----------|--------|---------|
| PostgreSQL Connector | ❌ Pending | Need DB schema info |
| Bulk Chemical Import | ❌ Pending | Need DB schema info |
| Auto SKU Mapping Rules | ❌ Pending | Need to understand SKU naming patterns |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           SHOPIFY                                    │
│  ┌─────────────┐                                                    │
│  │  Products   │──── API or CSV Export ────┐                        │
│  │  Variants   │                           │                        │
│  └─────────────┘                           │                        │
└────────────────────────────────────────────│────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LABEL GENERATOR                                 │
│                                                                      │
│  ┌─────────────────┐      ┌─────────────────┐                       │
│  │ Shopify Importer│      │  SKU Mapper     │                       │
│  │                 │      │                 │                       │
│  │ - SKU           │      │ AC-IPA-99-* ──► │                       │
│  │ - Product Name  │      │ isopropyl-99    │                       │
│  │ - Size/Volume   │      │                 │                       │
│  │ - UPC/Barcode   │      │ AC-ACET-* ────► │                       │
│  │                 │      │ acetone         │                       │
│  └────────┬────────┘      └────────┬────────┘                       │
│           │                        │                                 │
│           │    ┌───────────────────┘                                │
│           │    │                                                     │
│           ▼    ▼                                                     │
│  ┌─────────────────┐      ┌─────────────────┐                       │
│  │     MERGER      │◄─────│ PostgreSQL DB   │                       │
│  │                 │      │                 │                       │
│  │ Shopify Data +  │      │ - GHS Pictograms│                       │
│  │ Hazmat Data =   │      │ - Signal Word   │                       │
│  │ Complete Label  │      │ - H-Statements  │                       │
│  │                 │      │ - P-Statements  │                       │
│  └────────┬────────┘      │ - NFPA Ratings  │                       │
│           │               │ - DOT Info      │                       │
│           │               │ - CAS Number    │                       │
│           ▼               └─────────────────┘                       │
│  ┌─────────────────┐                                                │
│  │ Label Renderer  │                                                │
│  │                 │                                                │
│  │ - Organic Style │                                                │
│  │ - Scientific    │                                                │
│  │ - Standard      │                                                │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│      [PDF Labels]                                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Step 1: Import Shopify Products

```bash
# Option A: From CSV export
python -m src.cli import-shopify products.csv --allow-missing

# Option B: From API (requires env vars)
export SHOPIFY_STORE="your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_xxxxx"
python -m src.cli import-shopify-api --allow-missing
```

**Output:** SKU stub files in `data/skus/`

Example stub (`data/skus/AC-IPA-99-1GAL.json`):
```json
{
  "sku": "AC-IPA-99-1GAL",
  "product_name": "Isopropyl Alcohol 99%",
  "package_type": "gallon_1",
  "net_contents_us": "1 Gallon",
  "net_contents_metric": "3.78 L",
  "upc_gtin12": "123456789012",
  "hazcom_applicable": false,
  "ghs_pictograms": [],
  "needs_review": true
}
```

### Step 2: Map SKUs to Chemicals

SKU mapping rules in `data/sku_mappings.json`:
```json
{
  "prefix_rules": [
    {
      "prefix": "AC-IPA-99-",
      "chemical_id": "isopropyl-alcohol-99",
      "description": "All 99% IPA variants"
    },
    {
      "prefix": "AC-IPA-70-",
      "chemical_id": "isopropyl-alcohol-70"
    },
    {
      "prefix": "AC-ACET-",
      "chemical_id": "acetone"
    }
  ]
}
```

### Step 3: Sync with Hazmat Database

```bash
# Check mapping status
python -m src.cli db status

# Sync Shopify stubs with chemical data
python -m src.cli db sync
```

**Output:** Complete label JSON files ready for PDF generation

### Step 4: Generate Labels

```bash
# Single label
python -m src.cli generate AC-IPA-99-1GAL --style organic

# Batch
python -m src.cli batch "AC-IPA-99-1GAL,AC-IPA-99-5GAL,AC-IPA-99-55GAL"
```

---

## PostgreSQL Integration (PENDING)

### Required Information

To connect to your hazmat database, I need:

#### 1. Connection Details
```
Host: _______________
Port: _______________ (default 5432)
Database: _______________
Username: _______________
Password: _______________ (or use env var)
SSL Required: Yes / No
```

#### 2. Table Structure

**Table name:** `_______________`

**Columns needed:**

| Data Field | Your Column Name | Example Value |
|------------|------------------|---------------|
| SKU Prefix | `_______________` | `AC-IPA-99` |
| Chemical Name | `_______________` | `Isopropyl Alcohol` |
| CAS Number | `_______________` | `67-63-0` |
| GHS Pictograms | `_______________` | `GHS02,GHS07` or separate columns? |
| Signal Word | `_______________` | `Danger` or `Warning` |
| Hazard Statements | `_______________` | How stored? (JSON array, comma-separated, separate table?) |
| Precautionary Statements | `_______________` | How stored? |
| NFPA Health | `_______________` | `1` (0-4) |
| NFPA Fire | `_______________` | `3` (0-4) |
| NFPA Reactivity | `_______________` | `0` (0-4) |
| NFPA Special | `_______________` | `null` or `W`, `OX`, etc. |
| DOT Regulated | `_______________` | `true/false` |
| UN Number | `_______________` | `UN1219` |
| Proper Shipping Name | `_______________` | `Isopropanol` |
| Hazard Class | `_______________` | `3` |
| Packing Group | `_______________` | `II` |
| SDS URL | `_______________` | URL to SDS PDF |

#### 3. Questions About Data Format

- [ ] Are GHS pictograms stored as a single comma-separated string or separate columns (ghs01, ghs02, etc.)?
- [ ] Are hazard/precautionary statements in a single text field, JSON array, or a related table?
- [ ] Is there a "product family" or category column (solvents, acids, etc.)?
- [ ] Are there multiple grades per chemical (99%, 70%, etc.) in separate rows or same row?

### Planned Implementation

Once schema is provided, I'll create:

```python
# src/database/postgres_connector.py

class PostgresChemicalDatabase:
    """Connect to PostgreSQL hazmat database."""

    def __init__(self, connection_string: str):
        ...

    def get_by_sku_prefix(self, prefix: str) -> ChemicalData:
        """Look up chemical by SKU prefix."""
        ...

    def sync_all(self) -> list[ChemicalData]:
        """Pull all chemicals for local caching."""
        ...
```

New CLI command:
```bash
# Sync from Postgres
python -m src.cli db sync --from-postgres

# Or with explicit connection
python -m src.cli db sync --postgres-url "postgresql://user:pass@host:5432/dbname"
```

---

## SKU Naming Convention

Based on your SKU prefix system, document the pattern here:

```
[COMPANY]-[CHEMICAL]-[GRADE]-[SIZE]

Examples:
  AC-IPA-99-1GAL    → Isopropyl Alcohol 99%, 1 Gallon
  AC-IPA-99-5GAL    → Isopropyl Alcohol 99%, 5 Gallon
  AC-IPA-70-1GAL    → Isopropyl Alcohol 70%, 1 Gallon
  AC-ACET-ACS-5GAL  → Acetone ACS Grade, 5 Gallon
```

**Mapping strategy:** Use prefix `AC-IPA-99-` to match chemical `isopropyl-alcohol-99`

---

## Environment Variables

```bash
# Shopify API (for import-shopify-api command)
export SHOPIFY_STORE="your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_xxxxxxxxxxxxx"

# PostgreSQL (when implemented)
export HAZMAT_DB_URL="postgresql://user:password@host:5432/database"
# Or separate vars:
export HAZMAT_DB_HOST="your-db-host.com"
export HAZMAT_DB_PORT="5432"
export HAZMAT_DB_NAME="hazmat"
export HAZMAT_DB_USER="readonly_user"
export HAZMAT_DB_PASSWORD="xxxxx"
```

---

## File Structure

```
label-python/
├── data/
│   ├── chemicals/           # Chemical hazmat data (JSON cache from Postgres)
│   │   └── isopropyl-alcohol-99.json
│   ├── skus/                # Shopify-imported SKU stubs + merged labels
│   │   └── AC-IPA-99-1GAL.json
│   └── sku_mappings.json    # SKU prefix → chemical ID mappings
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── chemical_db.py       # Chemical data model & JSON loader
│   │   ├── sku_mapper.py        # SKU → chemical mapping
│   │   ├── merger.py            # Combine Shopify + hazmat data
│   │   └── postgres_connector.py # (PENDING) PostgreSQL integration
│   ├── importers/
│   │   ├── shopify.py           # CSV import
│   │   └── shopify_api.py       # API import
│   └── cli.py                   # Command-line interface
└── output/                  # Generated PDF labels
```

---

## CLI Command Reference

### Shopify Import
```bash
# From CSV
python -m src.cli import-shopify <csv_file> [--overwrite] [--allow-missing]

# From API
python -m src.cli import-shopify-api [--store DOMAIN] [--overwrite] [--allow-missing]
```

### Database Management
```bash
# Check status of all SKUs
python -m src.cli db status

# Sync SKU stubs with chemical data
python -m src.cli db sync [--overwrite] [--dry-run]

# Add a chemical (creates stub for editing)
python -m src.cli db add-chemical <id> <name> [--cas CAS] [--family FAMILY]

# Add SKU mapping
python -m src.cli db add-mapping <sku> <chemical_id> [--prefix]

# List all chemicals
python -m src.cli db list-chemicals
```

### Label Generation
```bash
# Single label
python -m src.cli generate <sku> [--lot LOT] [--style organic|scientific|standard]

# Batch labels
python -m src.cli batch "SKU1,SKU2,SKU3" [--lot-prefix PREFIX]

# Show SKU info
python -m src.cli info <sku>
```

---

## Next Steps

### Immediate (When Ready)
1. [ ] Get PostgreSQL connection details
2. [ ] Get table schema / column names
3. [ ] Build PostgreSQL connector
4. [ ] Test with a few chemicals

### Future Enhancements
- [ ] Webhook listener for real-time Shopify product updates
- [ ] Web UI for mapping review
- [ ] Bulk label PDF generation (multiple labels per page)
- [ ] Integration with print queue

---

## Questions / Notes

_Add any questions or notes here as they come up:_

-

---

*Last updated: 2026-01-20*
