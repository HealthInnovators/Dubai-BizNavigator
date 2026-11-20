"""Value objects representing Dubai/UAE business setup concepts."""

from dataclasses import dataclass
from enum import StrEnum


class JurisdictionType(StrEnum):
    """Dubai jurisdiction categories."""

    MAINLAND = "mainland"
    FREEZONE = "freezone"
    OFFSHORE = "offshore"


class LicenseCategory(StrEnum):
    """Dubai trade license categories."""

    COMMERCIAL = "commercial"
    PROFESSIONAL = "professional"
    INDUSTRIAL = "industrial"
    TOURISM = "tourism"


@dataclass(frozen=True)
class Jurisdiction:
    """Represents a specific jurisdiction (e.g. DMCC, DIFC, Dubai Economy Mainland)."""

    name: str
    jurisdiction_type: JurisdictionType
    authority_code: str

    def is_freezone(self) -> bool:
        return self.jurisdiction_type == JurisdictionType.FREEZONE
