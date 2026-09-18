"""Portable creator and module registry primitives."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from .diffusers import AdapterAttribution


class RegistryValidationError(ValueError):
    """Raised when creator registry data violates the v0.1 contract."""


def _required_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise RegistryValidationError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True, slots=True)
class CreatorRecord:
    """A creator identity referenced by registered modules."""

    creator_id: str
    display_name: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required_text(self.creator_id, "creator_id")
        _required_text(self.display_name, "display_name")
        if not isinstance(self.metadata, Mapping):
            raise RegistryValidationError("creator metadata must be a mapping")


@dataclass(frozen=True, slots=True)
class ModuleRegistration:
    """An attributed module registered with explicit active consent."""

    module_id: str
    creator_id: str
    license: str
    active: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required_text(self.module_id, "module_id")
        _required_text(self.creator_id, "creator_id")
        _required_text(self.license, "license")
        if not isinstance(self.active, bool):
            raise RegistryValidationError("active must be a boolean")
        if not isinstance(self.metadata, Mapping):
            raise RegistryValidationError("module metadata must be a mapping")


@dataclass(frozen=True, slots=True)
class CreatorRegistry:
    """A versioned collection of creators and their attributed modules."""

    creators: Sequence[CreatorRecord]
    modules: Sequence[ModuleRegistration]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    registry_version: str = "0.1"

    def __post_init__(self) -> None:
        if self.registry_version != "0.1":
            raise RegistryValidationError("registry_version must be '0.1'")
        if not all(isinstance(item, CreatorRecord) for item in self.creators):
            raise RegistryValidationError("creators must contain CreatorRecord objects")
        if not all(isinstance(item, ModuleRegistration) for item in self.modules):
            raise RegistryValidationError(
                "modules must contain ModuleRegistration objects"
            )
        if not isinstance(self.metadata, Mapping):
            raise RegistryValidationError("registry metadata must be a mapping")

        creator_ids = [item.creator_id for item in self.creators]
        if len(creator_ids) != len(set(creator_ids)):
            raise RegistryValidationError("creator_id values must be unique")

        module_ids = [item.module_id for item in self.modules]
        if len(module_ids) != len(set(module_ids)):
            raise RegistryValidationError("module_id values must be unique")

        known_creators = set(creator_ids)
        unknown = sorted(
            {item.creator_id for item in self.modules if item.creator_id not in known_creators}
        )
        if unknown:
            raise RegistryValidationError(
                f"modules reference unknown creators: {', '.join(unknown)}"
            )

    def active_adapter_attribution(self) -> dict[str, AdapterAttribution]:
        """Return active module registrations in Diffusers session format."""

        return {
            item.module_id: AdapterAttribution(
                artist_id=item.creator_id,
                license=item.license,
                metadata=item.metadata,
            )
            for item in self.modules
            if item.active
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable registry document."""

        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, sort_keys=True)

    def write(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(f"{self.to_json()}\n", encoding="utf-8")
        return output.resolve()

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "CreatorRegistry":
        """Validate and construct a registry from parsed JSON data."""

        if not isinstance(payload, Mapping):
            raise RegistryValidationError("registry document must be an object")
        try:
            creators_data = payload["creators"]
            modules_data = payload["modules"]
            if not isinstance(creators_data, list) or not isinstance(modules_data, list):
                raise RegistryValidationError("creators and modules must be arrays")
            creators = [CreatorRecord(**item) for item in creators_data]
            modules = [ModuleRegistration(**item) for item in modules_data]
            return cls(
                creators=creators,
                modules=modules,
                metadata=payload.get("metadata", {}),
                registry_version=payload.get("registry_version", ""),
            )
        except RegistryValidationError:
            raise
        except (KeyError, TypeError) as exc:
            raise RegistryValidationError(f"invalid registry document: {exc}") from exc

    @classmethod
    def read(cls, path: str | Path) -> "CreatorRegistry":
        """Load a UTF-8 JSON registry document from disk."""

        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RegistryValidationError(f"could not read registry: {exc}") from exc
        return cls.from_dict(payload)
