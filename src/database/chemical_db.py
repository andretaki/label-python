"""Chemical master database for hazard and regulatory data.

This module provides the infrastructure for storing and retrieving chemical
hazard data (GHS, NFPA, DOT) that gets merged with Shopify product variants
to create complete label records.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.config import DATA_DIR


DEFAULT_CHEMICALS_DIR = DATA_DIR / "chemicals"


@dataclass
class ChemicalData:
    """Master record for a chemical's hazard and regulatory data.

    This data is independent of packaging/SKU - it represents the chemical
    itself and its inherent hazard properties.
    """
    # Identification
    chemical_id: str  # Unique identifier (e.g., "isopropyl-alcohol-99")
    chemical_name: str  # Display name (e.g., "Isopropyl Alcohol")
    cas_number: Optional[str] = None
    aliases: list[str] = field(default_factory=list)  # Alternative names

    # Product family (for label styling)
    product_family: Optional[str] = None  # e.g., "solvents", "acids", "bases"

    # GHS/HazCom data
    hazcom_applicable: bool = False
    ghs_pictograms: list[str] = field(default_factory=list)  # GHS01, GHS02, etc.
    signal_word: Optional[str] = None  # "Danger" or "Warning"
    hazard_statements: list[str] = field(default_factory=list)
    precaution_statements: list[str] = field(default_factory=list)

    # DOT shipping data
    dot_regulated: bool = False
    un_number: Optional[str] = None
    proper_shipping_name: Optional[str] = None
    hazard_class: Optional[str] = None
    packing_group: Optional[str] = None

    # NFPA 704 ratings
    nfpa_health: Optional[int] = None
    nfpa_fire: Optional[int] = None
    nfpa_reactivity: Optional[int] = None
    nfpa_special: Optional[str] = None

    # SDS reference
    sds_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "chemical_id": self.chemical_id,
            "chemical_name": self.chemical_name,
            "cas_number": self.cas_number,
            "aliases": self.aliases,
            "product_family": self.product_family,
            "hazcom_applicable": self.hazcom_applicable,
            "ghs_pictograms": self.ghs_pictograms,
            "signal_word": self.signal_word,
            "hazard_statements": self.hazard_statements,
            "precaution_statements": self.precaution_statements,
            "dot_regulated": self.dot_regulated,
            "un_number": self.un_number,
            "proper_shipping_name": self.proper_shipping_name,
            "hazard_class": self.hazard_class,
            "packing_group": self.packing_group,
            "nfpa_health": self.nfpa_health,
            "nfpa_fire": self.nfpa_fire,
            "nfpa_reactivity": self.nfpa_reactivity,
            "nfpa_special": self.nfpa_special,
            "sds_url": self.sds_url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ChemicalData:
        """Create from dictionary."""
        return cls(
            chemical_id=data["chemical_id"],
            chemical_name=data["chemical_name"],
            cas_number=data.get("cas_number"),
            aliases=data.get("aliases", []),
            product_family=data.get("product_family"),
            hazcom_applicable=data.get("hazcom_applicable", False),
            ghs_pictograms=data.get("ghs_pictograms", []),
            signal_word=data.get("signal_word"),
            hazard_statements=data.get("hazard_statements", []),
            precaution_statements=data.get("precaution_statements", []),
            dot_regulated=data.get("dot_regulated", False),
            un_number=data.get("un_number"),
            proper_shipping_name=data.get("proper_shipping_name"),
            hazard_class=data.get("hazard_class"),
            packing_group=data.get("packing_group"),
            nfpa_health=data.get("nfpa_health"),
            nfpa_fire=data.get("nfpa_fire"),
            nfpa_reactivity=data.get("nfpa_reactivity"),
            nfpa_special=data.get("nfpa_special"),
            sds_url=data.get("sds_url"),
        )


class ChemicalDatabase:
    """In-memory database of chemical hazard data.

    Loads chemical data from JSON files and provides lookup by:
    - chemical_id (primary key)
    - CAS number
    - aliases/alternative names
    """

    def __init__(self, chemicals_dir: Optional[Path] = None):
        self.chemicals_dir = chemicals_dir or DEFAULT_CHEMICALS_DIR
        self._by_id: dict[str, ChemicalData] = {}
        self._by_cas: dict[str, ChemicalData] = {}
        self._by_alias: dict[str, ChemicalData] = {}

    def load(self) -> int:
        """Load all chemical data from JSON files.

        Returns the number of chemicals loaded.
        """
        self._by_id.clear()
        self._by_cas.clear()
        self._by_alias.clear()

        if not self.chemicals_dir.exists():
            return 0

        for json_file in self.chemicals_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                chemical = ChemicalData.from_dict(data)
                self._index_chemical(chemical)
            except (json.JSONDecodeError, KeyError) as e:
                # Skip malformed files
                continue

        return len(self._by_id)

    def _index_chemical(self, chemical: ChemicalData) -> None:
        """Add a chemical to all lookup indexes."""
        self._by_id[chemical.chemical_id] = chemical

        if chemical.cas_number:
            self._by_cas[chemical.cas_number] = chemical

        # Index by normalized aliases
        for alias in chemical.aliases:
            normalized = self._normalize_name(alias)
            self._by_alias[normalized] = chemical

        # Also index by normalized chemical name
        normalized_name = self._normalize_name(chemical.chemical_name)
        self._by_alias[normalized_name] = chemical

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize a chemical name for matching."""
        return name.lower().strip().replace("-", " ").replace("_", " ")

    def get_by_id(self, chemical_id: str) -> Optional[ChemicalData]:
        """Look up by chemical_id."""
        return self._by_id.get(chemical_id)

    def get_by_cas(self, cas_number: str) -> Optional[ChemicalData]:
        """Look up by CAS number."""
        return self._by_cas.get(cas_number)

    def get_by_name(self, name: str) -> Optional[ChemicalData]:
        """Look up by chemical name or alias (fuzzy match)."""
        normalized = self._normalize_name(name)
        return self._by_alias.get(normalized)

    def search(self, query: str) -> Optional[ChemicalData]:
        """Search by any identifier (ID, CAS, or name).

        Tries in order: exact ID, CAS number, name/alias.
        """
        # Try exact ID match
        if query in self._by_id:
            return self._by_id[query]

        # Try CAS number
        if query in self._by_cas:
            return self._by_cas[query]

        # Try name/alias
        return self.get_by_name(query)

    def add(self, chemical: ChemicalData, save: bool = True) -> None:
        """Add a chemical to the database.

        If save=True, also writes to disk.
        """
        self._index_chemical(chemical)

        if save:
            self.chemicals_dir.mkdir(parents=True, exist_ok=True)
            output_path = self.chemicals_dir / f"{chemical.chemical_id}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chemical.to_dict(), f, indent=2, ensure_ascii=True)
                f.write("\n")

    def list_all(self) -> list[ChemicalData]:
        """Return all chemicals in the database."""
        return list(self._by_id.values())

    def __len__(self) -> int:
        return len(self._by_id)

    def __contains__(self, chemical_id: str) -> bool:
        return chemical_id in self._by_id


def load_chemical_database(chemicals_dir: Optional[Path] = None) -> ChemicalDatabase:
    """Load and return the chemical database."""
    db = ChemicalDatabase(chemicals_dir)
    db.load()
    return db
