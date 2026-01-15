"""Shopify Admin API importer for SKU JSON stubs."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from src.importers.shopify import (
    DEFAULT_OUTPUT_DIR,
    GRADE_OPTION_KEYWORDS,
    SIZE_OPTION_KEYWORDS,
    SizeInfo,
    build_import_record,
    find_size,
    normalize_unit,
    normalize_upc,
    parse_size_from_text,
)


DEFAULT_API_VERSION = "2024-01"


@dataclass
class ShopifyConfig:
    store: str
    access_token: str
    api_version: str = DEFAULT_API_VERSION


def normalize_store_domain(store: str) -> str:
    store = store.strip()
    if store.startswith("http://") or store.startswith("https://"):
        store = urlparse(store).netloc
    return store.strip().rstrip("/")


def get_env_config(store: Optional[str], api_version: Optional[str]) -> ShopifyConfig:
    env_store = store or os.getenv("SHOPIFY_STORE", "")
    access_token = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
    if not env_store:
        raise ValueError("SHOPIFY_STORE is required")
    if not access_token:
        raise ValueError("SHOPIFY_ACCESS_TOKEN is required")
    return ShopifyConfig(
        store=normalize_store_domain(env_store),
        access_token=access_token,
        api_version=api_version or os.getenv("SHOPIFY_API_VERSION", DEFAULT_API_VERSION),
    )


def fetch_json(url: str, access_token: str) -> tuple[dict, str]:
    request = Request(
        url,
        headers={
            "X-Shopify-Access-Token": access_token,
            "Accept": "application/json",
        },
    )
    with urlopen(request) as response:
        payload = response.read().decode("utf-8")
        link_header = response.headers.get("Link", "")
    return json.loads(payload), link_header


def parse_next_link(link_header: str) -> str:
    if not link_header:
        return ""
    for part in link_header.split(","):
        sections = [segment.strip() for segment in part.split(";")]
        if not sections:
            continue
        url = sections[0].strip("<>")
        if any(section == 'rel="next"' for section in sections[1:]):
            return url
    return ""


def iter_products(config: ShopifyConfig, limit: int = 250) -> Iterable[dict]:
    base_url = (
        f"https://{config.store}/admin/api/{config.api_version}/products.json"
    )
    params = f"limit={limit}&fields=id,title,variants,options"
    next_url = f"{base_url}?{params}"
    while next_url:
        payload, link_header = fetch_json(next_url, config.access_token)
        for product in payload.get("products", []):
            yield product
        next_url = parse_next_link(link_header)


def option_value_by_keywords(product: dict, variant: dict, keywords: Iterable[str]) -> str:
    options = product.get("options") or []
    for index, option in enumerate(options, 1):
        name = (option.get("name") or "").strip().lower()
        value = (variant.get(f"option{index}") or "").strip()
        if not name or not value:
            continue
        if value.lower() == "default title":
            continue
        if any(keyword in name for keyword in keywords):
            return value
    return ""


def option_values(product: dict, variant: dict) -> list[str]:
    values: list[str] = []
    options = product.get("options") or []
    for index in range(1, len(options) + 1):
        value = (variant.get(f"option{index}") or "").strip()
        if value and value.lower() != "default title":
            values.append(value)
    return values


def size_from_variant_weight(variant: dict) -> Optional[SizeInfo]:
    weight = variant.get("weight")
    unit = variant.get("weight_unit")
    if not weight or not unit:
        return None
    normalized = normalize_unit(str(unit))
    if normalized not in {"lb", "kg", "g"}:
        return None
    return SizeInfo(quantity=float(weight), unit=normalized, source="variant weight")


def import_shopify_api(
    store: Optional[str] = None,
    api_version: Optional[str] = None,
    output_dir: Optional[Path] = None,
    overwrite: bool = False,
    allow_missing: bool = False,
) -> tuple[int, list[dict[str, str]]]:
    config = get_env_config(store, api_version)
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    skipped: list[dict[str, str]] = []
    created = 0

    for product in iter_products(config):
        product_name = (product.get("title") or "").strip()
        if not product_name:
            skipped.append({"id": str(product.get("id", "")), "reason": "missing title"})
            continue

        for variant in product.get("variants") or []:
            sku = (variant.get("sku") or "").strip()
            if not sku:
                skipped.append(
                    {
                        "product_id": str(product.get("id", "")),
                        "variant_id": str(variant.get("id", "")),
                        "reason": "missing sku",
                    }
                )
                continue

            variant_title = (variant.get("title") or "").strip()
            if variant_title.lower() == "default title":
                variant_title = ""

            grade = option_value_by_keywords(product, variant, GRADE_OPTION_KEYWORDS)
            if not grade and variant_title:
                if not parse_size_from_text(variant_title):
                    grade = variant_title

            size_candidates: list[str] = []
            size_option = option_value_by_keywords(product, variant, SIZE_OPTION_KEYWORDS)
            if size_option:
                size_candidates.append(size_option)
            size_candidates.extend(option_values(product, variant))
            if variant_title:
                size_candidates.append(variant_title)
            size_candidates.append(product_name)
            size_candidates.append(sku)

            size = find_size(size_candidates)
            if not size:
                size = size_from_variant_weight(variant)

            upc = normalize_upc(str(variant.get("barcode") or ""))

            record, missing = build_import_record(
                sku=sku,
                product_name=product_name,
                size=size,
                upc=upc,
                grade=grade,
                sds_url="",
            )

            required_missing = [item for item in missing if item in {"size", "upc_gtin12"}]
            if required_missing and not allow_missing:
                skipped.append(
                    {
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
