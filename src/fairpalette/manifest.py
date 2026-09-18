"""Models for FairPalette attribution manifests."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


class ManifestValidationError(ValueError):
    """Raised when manifest data violates the FairPalette v0.1 contract."""


def _required_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ManifestValidationError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True, slots=True)
class Contributor:
    """A creator-owned module participating in one generation."""

    artist_id: str
    module_id: str
    applied_weight: float
    license: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required_text(self.artist_id, "artist_id")
        _required_text(self.module_id, "module_id")
        if isinstance(self.applied_weight, bool) or not isinstance(
            self.applied_weight, (int, float)
        ):
            raise ManifestValidationError("applied_weight must be a number")
        if self.applied_weight <= 0:
            raise ManifestValidationError("applied_weight must be greater than zero")
        if self.license is not None:
            _required_text(self.license, "license")


@dataclass(frozen=True, slots=True)
class AttributionManifest:
    """A portable record of declared participation in a generation pipeline."""

    generation_id: str
    base_model: str
    contributors: Sequence[Contributor]
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    metadata: Mapping[str, Any] = field(default_factory=dict)
    spec_version: str = "0.1"

    def __post_init__(self) -> None:
        _required_text(self.generation_id, "generation_id")
        _required_text(self.base_model, "base_model")
        if self.spec_version != "0.1":
            raise ManifestValidationError("spec_version must be '0.1'")
        if not self.contributors:
            raise ManifestValidationError("contributors must contain at least one entry")
        if not all(isinstance(item, Contributor) for item in self.contributors):
            raise ManifestValidationError("contributors must contain Contributor objects")

        module_ids = [item.module_id for item in self.contributors]
        if len(module_ids) != len(set(module_ids)):
            raise ManifestValidationError("module_id values must be unique per manifest")

        try:
            parsed = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise ManifestValidationError("timestamp must be an ISO 8601 datetime") from exc
        if parsed.tzinfo is None:
            raise ManifestValidationError("timestamp must include a timezone")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable manifest."""

        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the manifest as stable UTF-8 JSON text."""

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, sort_keys=True)

    def write(self, path: str | Path) -> Path:
        """Write the manifest to disk and return the resolved output path."""

        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(f"{self.to_json()}\n", encoding="utf-8")
        return output.resolve()
