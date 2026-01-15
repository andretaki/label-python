"""Shopify CSV import helper for creating SKU JSON stubs."""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from src.config import DATA_DIR

SIZE_PATTERN = re.compile(
    r"(?P<qty>\d+(?:\.\d+)?)\s*[- ]*\s*(?P<unit>"
    r"gal|gallon|gallons|qt|quart|quarts|l|liter|litre|liters|litres|ml|"
    r"lb|lbs|pound|pounds|kg|kilogram|kilograms|g|gram|grams)"
)

DEFAULT_OUTPUT_DIR = DATA_DIR / "skus"

SIZE_OPTION_KEYWORDS = ("size", "volume", "weight", "package", "container")
GRADE_OPTION_KEYWORDS = ("grade", "concentration", "purity", "strength")


@dataclass
class SizeInfo:
    quantity: float
    unit: str
    source: str


def normalize_key(key: Optional[str]) -> str:
    if not key:
        return ""
    return " ".join(key.strip().lower().split())


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row.items():
        norm_key = normalize_key(key)
        if not norm_key:
            continue
        normalized[norm_key] = (value or "").strip()
    return normalized


def get_first(row: dict[str, str], keys: Iterable[str]) -> str:
    for key in keys:
        value = row.get(key, "").strip()
        if value:
            return value
    return ""


def pick_option_value(row: dict[str, str], keywords: Iterable[str]) -> str:
    for i in range(1, 4):
        name = row.get(f"option{i} name", "").strip().lower()
        value = row.get(f"option{i} value", "").strip()
        if not name or not value:
            continue
        if any(keyword in name for keyword in keywords):
            return value
    return ""


def parse_size_from_text(text: str) -> Optional[tuple[float, str]]:
    if not text:
        return None
    match = SIZE_PATTERN.search(text.lower())
    if not match:
        return None
    quantity = float(match.group("qty"))
    unit = normalize_unit(match.group("unit"))
    return quantity, unit


def find_size(candidates: Iterable[str]) -> Optional[SizeInfo]:
    for candidate in candidates:
        result = parse_size_from_text(candidate)
        if result:
            quantity, unit = result
            return SizeInfo(quantity=quantity, unit=unit, source=candidate)
    return None


def normalize_unit(unit: str) -> str:
    unit = unit.lower()
    if unit in {"gal", "gallon", "gallons"}:
        return "gal"
    if unit in {"qt", "quart", "quarts"}:
        return "qt"
    if unit in {"l", "liter", "litre", "liters", "litres"}:
        return "l"
    if unit == "ml":
        return "ml"
    if unit in {"lb", "lbs", "pound", "pounds"}:
        return "lb"
    if unit in {"kg", "kilogram", "kilograms"}:
        return "kg"
    if unit in {"g", "gram", "grams"}:
        return "g"
    return unit


def truncate(value: float, decimals: int) -> float:
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def format_number(value: float, decimals: int) -> str:
    text = f"{value:.{decimals}f}"
    return text.rstrip("0").rstrip(".")


def format_gallons(quantity: float) -> str:
    if math.isclose(quantity, 1.0, abs_tol=0.01):
        return "1 Gallon"
    return f"{format_number(quantity, 2)} Gallons"


def format_quarts(quantity: float) -> str:
    if math.isclose(quantity, 1.0, abs_tol=0.01):
        return "1 Quart"
    return f"{format_number(quantity, 2)} Quarts"


def format_pounds(quantity: float) -> str:
    return f"{format_number(quantity, 2)} lb"


def format_liters_from_gallons(gallons: float) -> str:
    liters = gallons * 3.78541
    if liters >= 100:
        return f"{int(math.floor(liters))} L"
    liters = truncate(liters, 2)
    return f"{format_number(liters, 2)} L"


def format_liters_from_quarts(quarts: float) -> str:
    liters = quarts * 0.946353
    liters = truncate(liters, 2)
    return f"{format_number(liters, 2)} L"


def format_kg_from_pounds(pounds: float) -> str:
    kg = pounds * 0.453592
    kg = round(kg, 2)
    return f"{format_number(kg, 2)} kg"


def format_volume_from_liters(liters: float) -> tuple[str, str]:
    gallons = liters / 3.78541
    return format_gallons(gallons), f"{format_number(liters, 2)} L"


def format_weight_from_kg(kg: float) -> tuple[str, str]:
    pounds = kg / 0.453592
    return format_pounds(pounds), f"{format_number(kg, 2)} kg"


def map_package_type(quantity: float, unit: str) -> str:
    if unit == "gal":
        return map_gallon_package(quantity)
    if unit == "qt":
        if math.isclose(quantity, 1.0, abs_tol=0.05):
            return "quart_1"
        return "unknown"
    if unit == "l":
        gallons = quantity / 3.78541
        return map_gallon_package(gallons)
    if unit == "ml":
        gallons = (quantity / 1000) / 3.78541
        return map_gallon_package(gallons)
    if unit == "lb":
        return map_pound_package(quantity)
    if unit == "kg":
        pounds = quantity / 0.453592
        return map_pound_package(pounds)
    if unit == "g":
        pounds = (quantity / 1000) / 0.453592
        return map_pound_package(pounds)
    return "unknown"


def map_gallon_package(gallons: float) -> str:
    if math.isclose(gallons, 1.0, abs_tol=0.1):
        return "gallon_1"
    if math.isclose(gallons, 2.5, abs_tol=0.1):
        return "gallon_2.5"
    if math.isclose(gallons, 5.0, abs_tol=0.2):
        return "gallon_5"
    if math.isclose(gallons, 55.0, abs_tol=0.5):
        return "drum_55gal"
    if math.isclose(gallons, 275.0, abs_tol=1.0):
        return "tote_275gal"
    if math.isclose(gallons, 330.0, abs_tol=1.0):
        return "tote_330gal"
    return "unknown"


def map_pound_package(pounds: float) -> str:
    if math.isclose(pounds, 25.0, abs_tol=0.5):
        return "bag_25lb"
    if math.isclose(pounds, 50.0, abs_tol=0.5):
        return "bag_50lb"
    return "unknown"


def build_net_contents(size: SizeInfo) -> tuple[str, str]:
    quantity = size.quantity
    unit = size.unit
    if unit == "gal":
        return format_gallons(quantity), format_liters_from_gallons(quantity)
    if unit == "qt":
        return format_quarts(quantity), format_liters_from_quarts(quantity)
    if unit == "l":
        return format_volume_from_liters(quantity)
    if unit == "ml":
        return format_volume_from_liters(quantity / 1000)
    if unit == "lb":
        return format_pounds(quantity), format_kg_from_pounds(quantity)
    if unit == "kg":
        return format_weight_from_kg(quantity)
    if unit == "g":
        return format_weight_from_kg(quantity / 1000)
    return "", ""


def normalize_upc(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 13 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 12:
        return digits
    return ""


def build_import_record(
    sku: str,
    product_name: str,
    size: Optional[SizeInfo],
    upc: str,
    grade: str,
    sds_url: str,
) -> tuple[dict[str, object], list[str]]:
    missing: list[str] = []
    if not size:
        missing.append("size")
        package_type = "unknown"
        net_us = ""
        net_metric = ""
    else:
        package_type = map_package_type(size.quantity, size.unit)
        net_us, net_metric = build_net_contents(size)
        if package_type == "unknown":
            missing.append("package_type")
    if not upc:
        missing.append("upc_gtin12")

    record: dict[str, object] = {
        "sku": sku,
        "product_name": product_name,
        "grade_or_concentration": grade or None,
        "package_type": package_type,
        "net_contents_us": net_us,
        "net_contents_metric": net_metric,
        "cas_number": None,
        "upc_gtin12": upc or "000000000000",
        "hazcom_applicable": False,
        "ghs_pictograms": [],
        "signal_word": None,
        "hazard_statements": [],
        "precaution_statements": [],
        "dot_regulated": False,
        "un_number": None,
        "proper_shipping_name": None,
        "hazard_class": None,
        "packing_group": None,
        "nfpa_health": None,
        "nfpa_fire": None,
        "nfpa_reactivity": None,
        "nfpa_special": None,
        "sds_url": sds_url or None,
    }
    return record, missing


def import_shopify_csv(
    csv_path: Path,
    output_dir: Optional[Path] = None,
    overwrite: bool = False,
    allow_missing: bool = False,
) -> tuple[int, list[dict[str, str]]]:
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    skipped: list[dict[str, str]] = []
    created = 0

    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, 2):
            normalized = normalize_row(row)
            sku = get_first(normalized, ("variant sku", "sku"))
            if not sku:
                skipped.append({"row": str(index), "reason": "missing sku"})
                continue

            product_name = get_first(normalized, ("title", "product title"))
            if not product_name:
                skipped.append({"row": str(index), "sku": sku, "reason": "missing title"})
                continue

            variant_title = normalized.get("variant title", "")
            if variant_title.lower() == "default title":
                variant_title = ""

            grade = pick_option_value(normalized, GRADE_OPTION_KEYWORDS)
            if not grade and variant_title:
                if not parse_size_from_text(variant_title):
                    grade = variant_title

            size_candidates = []
            size_option = pick_option_value(normalized, SIZE_OPTION_KEYWORDS)
            if size_option:
                size_candidates.append(size_option)
            for key in ("option1 value", "option2 value", "option3 value"):
                value = normalized.get(key, "")
                if value:
                    size_candidates.append(value)
            if variant_title:
                size_candidates.append(variant_title)
            size_candidates.append(product_name)
            size_candidates.append(sku)

            size = find_size(size_candidates)
            upc = normalize_upc(get_first(normalized, ("variant barcode", "barcode", "upc", "gtin")))
            sds_url = get_first(normalized, ("sds url", "sds_url", "sds"))

            record, missing = build_import_record(
                sku=sku,
                product_name=product_name,
                size=size,
                upc=upc,
                grade=grade,
                sds_url=sds_url,
            )

            required_missing = [item for item in missing if item in {"size", "upc_gtin12"}]
            if required_missing and not allow_missing:
                skipped.append(
                    {
                        "row": str(index),
                        "sku": sku,
                        "reason": f"missing {', '.join(required_missing)}",
                    }
                )
                continue

            if missing:
                record["needs_review"] = True
                record["import_notes"] = missing
                if size:
                    record["import_size_source"] = size.source

            output_path = output_dir / f"{sku}.json"
            if output_path.exists() and not overwrite:
                skipped.append(
                    {
                        "row": str(index),
                        "sku": sku,
                        "reason": "already exists",
                    }
                )
                continue

            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(record, out, indent=2, ensure_ascii=True)
                out.write("\n")

            created += 1

    return created, skipped
