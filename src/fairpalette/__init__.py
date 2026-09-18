"""FairPalette attribution manifest primitives."""

from .manifest import AttributionManifest, Contributor, ManifestValidationError
from .royalties import RoyaltyAllocation, calculate_royalties

__all__ = [
    "AttributionManifest",
    "Contributor",
    "ManifestValidationError",
    "RoyaltyAllocation",
    "calculate_royalties",
]
