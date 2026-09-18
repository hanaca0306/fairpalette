"""Portable metadata sidecar export pipeline."""

from __future__ import annotations

import hashlib
import json
import mimetypes
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from .manifest import AttributionManifest, ManifestValidationError
from .royalties import RoyaltyAllocation


@dataclass(frozen=True, slots=True)
class AssetDescriptor:
    """Integrity and media information for a generated asset."""

    filename: str
    media_type: str | None
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class MetadataBundle:
    """A JSON-serializable export containing attribution and asset metadata."""

    manifest: AttributionManifest
    asset: AssetDescriptor | None = None
    royalties: Sequence[RoyaltyAllocation] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    format_version: str = "0.1"

    def __post_init__(self) -> None:
        if self.format_version != "0.1":
            raise ManifestValidationError("format_version must be '0.1'")
        if not isinstance(self.manifest, AttributionManifest):
            raise ManifestValidationError("manifest must be an AttributionManifest")
        if self.asset is not None and not isinstance(self.asset, AssetDescriptor):
            raise ManifestValidationError("asset must be an AssetDescriptor or None")
        if not all(isinstance(item, RoyaltyAllocation) for item in self.royalties):
            raise ManifestValidationError(
                "royalties must contain RoyaltyAllocation objects"
            )
        if not isinstance(self.metadata, Mapping):
            raise ManifestValidationError("metadata must be a mapping")

        manifest_modules = {
            item.module_id: item.artist_id for item in self.manifest.contributors
        }
        royalty_modules = [item.module_id for item in self.royalties]
        if len(royalty_modules) != len(set(royalty_modules)):
            raise ManifestValidationError("royalty module_id values must be unique")
        unknown = sorted(set(royalty_modules) - set(manifest_modules))
        if unknown:
            raise ManifestValidationError(
                f"royalties reference modules absent from manifest: {', '.join(unknown)}"
            )
        if any(item.amount < 0 for item in self.royalties):
            raise ManifestValidationError("royalty amounts cannot be negative")
        mismatched = sorted(
            item.module_id
            for item in self.royalties
            if manifest_modules.get(item.module_id) not in (None, item.artist_id)
        )
        if mismatched:
            raise ManifestValidationError(
                f"royalty artists do not match manifest: {', '.join(mismatched)}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Return the normative metadata bundle shape."""

        return {
            "format_version": self.format_version,
            "manifest": self.manifest.to_dict(),
            "asset": None if self.asset is None else asdict(self.asset),
            "royalties": [
                {
                    "artist_id": item.artist_id,
                    "module_id": item.module_id,
                    "amount": str(item.amount),
                }
                for item in self.royalties
            ],
            "metadata": dict(self.metadata),
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, sort_keys=True)

    def write(self, destination: str | Path) -> Path:
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(f"{self.to_json()}\n", encoding="utf-8")
        return output.resolve()


def describe_asset(path: str | Path) -> AssetDescriptor:
    """Hash a generated asset and return portable, non-path metadata."""

    asset_path = Path(path)
    if not asset_path.is_file():
        raise ManifestValidationError(f"asset does not exist or is not a file: {asset_path}")

    digest = hashlib.sha256()
    with asset_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)

    media_type, _ = mimetypes.guess_type(asset_path.name)
    return AssetDescriptor(
        filename=asset_path.name,
        media_type=media_type,
        size_bytes=asset_path.stat().st_size,
        sha256=digest.hexdigest(),
    )


def export_metadata_bundle(
    manifest: AttributionManifest,
    destination: str | Path,
    *,
    asset_path: str | Path | None = None,
    royalties: Sequence[RoyaltyAllocation] = (),
    metadata: Mapping[str, Any] | None = None,
) -> Path:
    """Build and write a FairPalette v0.1 metadata sidecar."""

    bundle = MetadataBundle(
        manifest=manifest,
        asset=None if asset_path is None else describe_asset(asset_path),
        royalties=royalties,
        metadata={} if metadata is None else metadata,
    )
    return bundle.write(destination)
