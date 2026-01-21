"""SKU-to-chemical mapping system.

Maps Shopify SKUs (product variants) to chemicals in the master database.
This allows multiple SKUs (different sizes of the same product) to share
the same chemical hazard data.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.config import DATA_DIR


DEFAULT_MAPPINGS_FILE = DATA_DIR / "sku_mappings.json"


@dataclass
class SKUMapping:
    """Mapping from a SKU pattern to a chemical.

    Supports exact matches and pattern matching to handle SKU variations.
    """
    # The SKU or pattern to match
    sku_pattern: str

    # The chemical_id to link to
    chemical_id: str

    # Optional overrides for this specific SKU
    # (e.g., different grade, different SDS URL for this size)
    grade_override: Optional[str] = None
    sds_url_override: Optional[str] = None

    # If true, pattern is treated as a regex; otherwise exact match
    is_regex: bool = False

    def matches(self, sku: str) -> bool:
        """Check if this mapping matches the given SKU."""
        if self.is_regex:
            return bool(re.match(self.sku_pattern, sku))
        return self.sku_pattern == sku

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "sku_pattern": self.sku_pattern,
            "chemical_id": self.chemical_id,
        }
        if self.grade_override:
            result["grade_override"] = self.grade_override
        if self.sds_url_override:
            result["sds_url_override"] = self.sds_url_override
        if self.is_regex:
            result["is_regex"] = self.is_regex
        return result

    @classmethod
    def from_dict(cls, data: dict) -> SKUMapping:
        """Create from dictionary."""
        return cls(
            sku_pattern=data["sku_pattern"],
            chemical_id=data["chemical_id"],
            grade_override=data.get("grade_override"),
            sds_url_override=data.get("sds_url_override"),
            is_regex=data.get("is_regex", False),
        )


@dataclass
class SKUMappingRule:
    """Rule for auto-generating mappings from SKU patterns.

    E.g., "AC-IPA-{grade}-{size}" -> chemical "isopropyl-alcohol"
    """
    prefix: str
    chemical_id: str
    description: Optional[str] = None

    def matches(self, sku: str) -> bool:
        """Check if SKU starts with this prefix."""
        return sku.startswith(self.prefix)

    def to_dict(self) -> dict:
        result = {
            "prefix": self.prefix,
            "chemical_id": self.chemical_id,
        }
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, data: dict) -> SKUMappingRule:
        return cls(
            prefix=data["prefix"],
            chemical_id=data["chemical_id"],
            description=data.get("description"),
        )


class SKUMapper:
    """Maps SKUs to chemicals.

    Supports:
    1. Explicit mappings (SKU -> chemical_id)
    2. Prefix rules (SKU prefix -> chemical_id)
    3. Auto-detection from product name
    """

    def __init__(self, mappings_file: Optional[Path] = None):
        self.mappings_file = mappings_file or DEFAULT_MAPPINGS_FILE
        self._explicit_mappings: dict[str, SKUMapping] = {}  # exact SKU -> mapping
        self._regex_mappings: list[SKUMapping] = []
        self._prefix_rules: list[SKUMappingRule] = []

    def load(self) -> int:
        """Load mappings from file.

        Returns the total number of mappings loaded.
        """
        self._explicit_mappings.clear()
        self._regex_mappings.clear()
        self._prefix_rules.clear()

        if not self.mappings_file.exists():
            return 0

        with open(self.mappings_file, encoding="utf-8") as f:
            data = json.load(f)

        # Load explicit mappings
        for mapping_data in data.get("mappings", []):
            mapping = SKUMapping.from_dict(mapping_data)
            if mapping.is_regex:
                self._regex_mappings.append(mapping)
            else:
                self._explicit_mappings[mapping.sku_pattern] = mapping

        # Load prefix rules
        for rule_data in data.get("prefix_rules", []):
            self._prefix_rules.append(SKUMappingRule.from_dict(rule_data))

        return len(self._explicit_mappings) + len(self._regex_mappings) + len(self._prefix_rules)

    def save(self) -> None:
        """Save current mappings to file."""
        self.mappings_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "mappings": [
                m.to_dict() for m in list(self._explicit_mappings.values()) + self._regex_mappings
            ],
            "prefix_rules": [r.to_dict() for r in self._prefix_rules],
        }

        with open(self.mappings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=True)
            f.write("\n")

    def get_mapping(self, sku: str) -> Optional[SKUMapping]:
        """Find the mapping for a SKU.

        Checks in order:
        1. Exact match
        2. Regex patterns
        3. Prefix rules (creates implicit mapping)
        """
        # 1. Exact match
        if sku in self._explicit_mappings:
            return self._explicit_mappings[sku]

        # 2. Regex patterns
        for mapping in self._regex_mappings:
            if mapping.matches(sku):
                return mapping

        # 3. Prefix rules
        for rule in self._prefix_rules:
            if rule.matches(sku):
                return SKUMapping(
                    sku_pattern=sku,
                    chemical_id=rule.chemical_id,
                )

        return None

    def get_chemical_id(self, sku: str) -> Optional[str]:
        """Get the chemical_id for a SKU, if mapped."""
        mapping = self.get_mapping(sku)
        return mapping.chemical_id if mapping else None

    def add_mapping(self, mapping: SKUMapping, save: bool = True) -> None:
        """Add an explicit SKU mapping."""
        if mapping.is_regex:
            self._regex_mappings.append(mapping)
        else:
            self._explicit_mappings[mapping.sku_pattern] = mapping

        if save:
            self.save()

    def add_prefix_rule(self, rule: SKUMappingRule, save: bool = True) -> None:
        """Add a prefix rule."""
        self._prefix_rules.append(rule)
        if save:
            self.save()

    def list_unmapped_skus(self, skus: list[str]) -> list[str]:
        """Return SKUs that have no mapping."""
        return [sku for sku in skus if not self.get_mapping(sku)]

    def __len__(self) -> int:
        return len(self._explicit_mappings) + len(self._regex_mappings) + len(self._prefix_rules)


def load_sku_mapper(mappings_file: Optional[Path] = None) -> SKUMapper:
    """Load and return the SKU mapper."""
    mapper = SKUMapper(mappings_file)
    mapper.load()
    return mapper
