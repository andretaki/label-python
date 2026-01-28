"""Pydantic data models for SKU and label data."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class GHSPictogram(str, Enum):
    """GHS pictogram identifiers."""
    GHS01 = "GHS01"  # Explosive
    GHS02 = "GHS02"  # Flammable
    GHS03 = "GHS03"  # Oxidizer
    GHS04 = "GHS04"  # Compressed Gas
    GHS05 = "GHS05"  # Corrosive
    GHS06 = "GHS06"  # Toxic
    GHS07 = "GHS07"  # Irritant
    GHS08 = "GHS08"  # Health Hazard
    GHS09 = "GHS09"  # Environment


class SignalWord(str, Enum):
    """GHS signal words."""
    DANGER = "Danger"
    WARNING = "Warning"


class PackingGroup(str, Enum):
    """DOT packing groups."""
    I = "I"
    II = "II"
    III = "III"


class PackageType(str, Enum):
    """Package type options matching JSON data."""
    UNKNOWN = "unknown"
    QUART_1 = "quart_1"
    GALLON_1 = "gallon_1"
    GALLON_2_5 = "gallon_2.5"
    GALLON_5 = "gallon_5"
    DRUM_55GAL = "drum_55gal"
    TOTE_275GAL = "tote_275gal"
    TOTE_330GAL = "tote_330gal"
    BAG_25LB = "bag_25lb"
    BAG_50LB = "bag_50lb"
    LITER_1 = "liter_1"
    LITER_2_5 = "liter_2.5"
    LITER_AMBER = "liter_amber"
    CAN_5GAL = "can_5gal"
    BUCKET_5GAL = "bucket_5gal"
    CAN_5GAL_TIGHT = "can_5gal_tight"
    CARBOY_15GAL = "carboy_15gal"
    QUART_SPRAY = "quart_spray"
    MYLAR_BAG = "mylar_bag"
    BOX = "box"
    BOX_OPEN = "box_open"
    PALLET_100BOX = "pallet_100box"
    ROUND_1 = "round_1"
    ROUND_2 = "round_2"
    TOTE_SIDE = "tote_side"


class SKUData(BaseModel):
    """Complete data model for a product SKU label."""

    # Product identification
    sku: str
    product_name: str
    grade_or_concentration: Optional[str] = None
    package_type: PackageType
    net_contents_us: str
    net_contents_metric: str
    cas_number: Optional[str] = None
    upc_gtin12: str = Field(..., min_length=12, max_length=12)

    # GHS/HazCom data
    hazcom_applicable: bool = False
    ghs_pictograms: list[GHSPictogram] = Field(default_factory=list)
    signal_word: Optional[SignalWord] = None
    hazard_statements: list[str] = Field(default_factory=list)
    precaution_statements: list[str] = Field(default_factory=list)

    # DOT shipping data
    dot_regulated: bool = False
    un_number: Optional[str] = None
    proper_shipping_name: Optional[str] = None
    hazard_class: Optional[str] = None
    packing_group: Optional[PackingGroup] = None

    # NFPA 704 ratings
    nfpa_health: Optional[int] = Field(default=None, ge=0, le=4)
    nfpa_fire: Optional[int] = Field(default=None, ge=0, le=4)
    nfpa_reactivity: Optional[int] = Field(default=None, ge=0, le=4)
    nfpa_special: Optional[str] = None

    # URLs
    sds_url: Optional[str] = None

    # Emergency contact
    chemtel_number: str = "1-800-255-3924"

    # Runtime fields (not from JSON)
    lot_number: Optional[str] = None

    @property
    def has_nfpa(self) -> bool:
        """Check if NFPA data is present."""
        return any([
            self.nfpa_health is not None,
            self.nfpa_fire is not None,
            self.nfpa_reactivity is not None,
        ])

    @property
    def template_type(self) -> str:
        """Get the template type based on package type."""
        from src.config import PACKAGE_TO_TEMPLATE
        return PACKAGE_TO_TEMPLATE.get(self.package_type.value, "medium")

    class Config:
        use_enum_values = False
