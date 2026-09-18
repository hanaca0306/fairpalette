"""FairPalette attribution manifest primitives."""

from .diffusers import AdapterAttribution, DiffusersAttributionSession
from .manifest import AttributionManifest, Contributor, ManifestValidationError
from .registry import (
    CreatorRecord,
    CreatorRegistry,
    ModuleRegistration,
    RegistryValidationError,
)
from .royalties import RoyaltyAllocation, calculate_royalties

__all__ = [
    "AdapterAttribution",
    "AttributionManifest",
    "Contributor",
    "CreatorRecord",
    "CreatorRegistry",
    "DiffusersAttributionSession",
    "ManifestValidationError",
    "ModuleRegistration",
    "RegistryValidationError",
    "RoyaltyAllocation",
    "calculate_royalties",
]
