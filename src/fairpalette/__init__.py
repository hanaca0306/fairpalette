"""FairPalette attribution manifest primitives."""

from .diffusers import AdapterAttribution, DiffusersAttributionSession
from .export import (
    AssetDescriptor,
    MetadataBundle,
    describe_asset,
    export_metadata_bundle,
)
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
    "AssetDescriptor",
    "AttributionManifest",
    "Contributor",
    "CreatorRecord",
    "CreatorRegistry",
    "DiffusersAttributionSession",
    "ManifestValidationError",
    "MetadataBundle",
    "ModuleRegistration",
    "RegistryValidationError",
    "RoyaltyAllocation",
    "calculate_royalties",
    "describe_asset",
    "export_metadata_bundle",
]
