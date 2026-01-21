"""Merge Shopify variant data with chemical master data.

This module provides the core integration between:
1. Shopify products/variants (SKU, product name, size, UPC)
2. Chemical master database (GHS, NFPA, DOT data)

Result: Complete label records ready for PDF generation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.config import DATA_DIR
from src.database.chemical_db import ChemicalData, ChemicalDatabase, load_chemical_database
from src.database.sku_mapper import SKUMapper, load_sku_mapper


DEFAULT_SKU_DIR = DATA_DIR / "skus"


@dataclass
class MergeResult:
    """Result of merging a Shopify variant with chemical data."""
    sku: str
    success: bool
    output_path: Optional[Path] = None
    error: Optional[str] = None
    chemical_id: Optional[str] = None
    was_updated: bool = False


def merge_shopify_with_chemical_data(
    sku_stub: dict,
    chemical: ChemicalData,
    grade_override: Optional[str] = None,
    sds_url_override: Optional[str] = None,
) -> dict:
    """Merge a Shopify SKU stub with chemical hazard data.

    The SKU stub contains:
    - sku, product_name, grade_or_concentration
    - package_type, net_contents_us, net_contents_metric
    - upc_gtin12

    The chemical data provides:
    - GHS pictograms, signal word, hazard/precaution statements
    - DOT shipping data (UN number, hazard class, etc.)
    - NFPA ratings
    - CAS number, SDS URL

    Returns a complete label record.
    """
    # Start with the SKU stub
    merged = dict(sku_stub)

    # Remove import-specific fields
    merged.pop("needs_review", None)
    merged.pop("import_notes", None)
    merged.pop("import_size_source", None)

    # Apply chemical data
    merged["cas_number"] = chemical.cas_number

    # GHS/HazCom
    merged["hazcom_applicable"] = chemical.hazcom_applicable
    merged["ghs_pictograms"] = chemical.ghs_pictograms
    merged["signal_word"] = chemical.signal_word
    merged["hazard_statements"] = chemical.hazard_statements
    merged["precaution_statements"] = chemical.precaution_statements

    # DOT
    merged["dot_regulated"] = chemical.dot_regulated
    merged["un_number"] = chemical.un_number
    merged["proper_shipping_name"] = chemical.proper_shipping_name
    merged["hazard_class"] = chemical.hazard_class
    merged["packing_group"] = chemical.packing_group

    # NFPA
    merged["nfpa_health"] = chemical.nfpa_health
    merged["nfpa_fire"] = chemical.nfpa_fire
    merged["nfpa_reactivity"] = chemical.nfpa_reactivity
    merged["nfpa_special"] = chemical.nfpa_special

    # SDS URL - use override if provided, otherwise from chemical
    merged["sds_url"] = sds_url_override or chemical.sds_url

    # Grade override if provided
    if grade_override:
        merged["grade_or_concentration"] = grade_override

    # Add product family for styling
    if chemical.product_family:
        merged["product_family"] = chemical.product_family

    # Add reference to source chemical
    merged["_chemical_id"] = chemical.chemical_id

    return merged


def sync_shopify_to_labels(
    sku_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    chemical_db: Optional[ChemicalDatabase] = None,
    sku_mapper: Optional[SKUMapper] = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> tuple[list[MergeResult], list[MergeResult]]:
    """Sync all Shopify SKU stubs to complete label records.

    Reads SKU stubs from sku_dir, looks up chemical data via the mapper,
    and writes complete label records to output_dir.

    Args:
        sku_dir: Directory containing Shopify-imported SKU stubs
        output_dir: Directory to write complete label records (defaults to sku_dir)
        chemical_db: Chemical database instance (loads default if None)
        sku_mapper: SKU mapper instance (loads default if None)
        overwrite: If True, overwrite existing complete records
        dry_run: If True, don't actually write files

    Returns:
        Tuple of (successful_results, failed_results)
    """
    sku_dir = sku_dir or DEFAULT_SKU_DIR
    output_dir = output_dir or sku_dir

    if chemical_db is None:
        chemical_db = load_chemical_database()

    if sku_mapper is None:
        sku_mapper = load_sku_mapper()

    successful: list[MergeResult] = []
    failed: list[MergeResult] = []

    if not sku_dir.exists():
        return successful, failed

    for json_file in sku_dir.glob("*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                sku_stub = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            failed.append(MergeResult(
                sku=json_file.stem,
                success=False,
                error=f"Failed to read file: {e}",
            ))
            continue

        sku = sku_stub.get("sku", json_file.stem)

        # Check if already complete (has chemical data)
        if not overwrite and sku_stub.get("_chemical_id"):
            successful.append(MergeResult(
                sku=sku,
                success=True,
                output_path=json_file,
                chemical_id=sku_stub.get("_chemical_id"),
                was_updated=False,
            ))
            continue

        # Look up mapping
        mapping = sku_mapper.get_mapping(sku)
        if not mapping:
            failed.append(MergeResult(
                sku=sku,
                success=False,
                error="No SKU mapping found",
            ))
            continue

        # Look up chemical
        chemical = chemical_db.get_by_id(mapping.chemical_id)
        if not chemical:
            failed.append(MergeResult(
                sku=sku,
                success=False,
                error=f"Chemical not found: {mapping.chemical_id}",
                chemical_id=mapping.chemical_id,
            ))
            continue

        # Merge data
        merged = merge_shopify_with_chemical_data(
            sku_stub=sku_stub,
            chemical=chemical,
            grade_override=mapping.grade_override,
            sds_url_override=mapping.sds_url_override,
        )

        # Write output
        output_path = output_dir / f"{sku}.json"

        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=True)
                f.write("\n")

        successful.append(MergeResult(
            sku=sku,
            success=True,
            output_path=output_path,
            chemical_id=mapping.chemical_id,
            was_updated=True,
        ))

    return successful, failed


def generate_mapping_report(
    sku_dir: Optional[Path] = None,
    chemical_db: Optional[ChemicalDatabase] = None,
    sku_mapper: Optional[SKUMapper] = None,
) -> dict:
    """Generate a report of SKU mapping status.

    Returns a dict with:
    - total_skus: Total number of SKU files
    - mapped: SKUs with valid chemical mappings
    - unmapped: SKUs without mappings
    - missing_chemical: SKUs mapped but chemical not found
    - complete: SKUs with full label data
    """
    sku_dir = sku_dir or DEFAULT_SKU_DIR

    if chemical_db is None:
        chemical_db = load_chemical_database()

    if sku_mapper is None:
        sku_mapper = load_sku_mapper()

    report = {
        "total_skus": 0,
        "mapped": [],
        "unmapped": [],
        "missing_chemical": [],
        "complete": [],
    }

    if not sku_dir.exists():
        return report

    for json_file in sku_dir.glob("*.json"):
        report["total_skus"] += 1

        try:
            with open(json_file, encoding="utf-8") as f:
                sku_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        sku = sku_data.get("sku", json_file.stem)

        # Check if already complete
        if sku_data.get("_chemical_id"):
            report["complete"].append(sku)
            continue

        # Check mapping
        mapping = sku_mapper.get_mapping(sku)
        if not mapping:
            report["unmapped"].append(sku)
            continue

        # Check chemical exists
        chemical = chemical_db.get_by_id(mapping.chemical_id)
        if not chemical:
            report["missing_chemical"].append({
                "sku": sku,
                "chemical_id": mapping.chemical_id,
            })
            continue

        report["mapped"].append({
            "sku": sku,
            "chemical_id": mapping.chemical_id,
        })

    return report
