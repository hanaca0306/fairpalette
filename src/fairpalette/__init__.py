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
from .session import (
    AttributionSession,
    AttributionSessionError,
    AttributionSessionManager,
    SessionState,
)

__all__ = [
    "AdapterAttribution",
    "AssetDescriptor",
    "AttributionManifest",
    "AttributionSession",
    "AttributionSessionError",
    "AttributionSessionManager",
    "Contributor",
    "CreatorRecord",
    "CreatorRegistry",
    "DiffusersAttributionSession",
    "ManifestValidationError",
    "MetadataBundle",
    "ModuleRegistration",
    "RegistryValidationError",
    "RoyaltyAllocation",
    "SessionState",
    "calculate_royalties",
    "describe_asset",
    "export_metadata_bundle",
]
