"""Optional attribution tracking for Diffusers-compatible pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .manifest import AttributionManifest, Contributor, ManifestValidationError


class AdapterPipeline(Protocol):
    """The small part of a Diffusers pipeline used by FairPalette."""

    def set_adapters(
        self,
        adapter_names: Sequence[str],
        adapter_weights: Sequence[float] | None = None,
    ) -> Any: ...


@dataclass(frozen=True, slots=True)
class AdapterAttribution:
    """Creator and licensing information registered for one adapter."""

    artist_id: str
    license: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def as_contributor(self, module_id: str, weight: float) -> Contributor:
        return Contributor(
            artist_id=self.artist_id,
            module_id=module_id,
            applied_weight=weight,
            license=self.license,
            metadata=self.metadata,
        )


class DiffusersAttributionSession:
    """Record declared adapter participation around ``set_adapters`` calls.

    The wrapped object only needs to expose the same ``set_adapters`` method as
    a Diffusers pipeline, so importing FairPalette does not require Diffusers.
    """

    def __init__(
        self,
        pipeline: AdapterPipeline,
        *,
        base_model: str,
        adapter_attribution: Mapping[str, AdapterAttribution],
    ) -> None:
        if not isinstance(base_model, str) or not base_model.strip():
            raise ManifestValidationError("base_model must be a non-empty string")
        if not adapter_attribution:
            raise ManifestValidationError("adapter_attribution must not be empty")
        if not all(
            isinstance(module_id, str)
            and module_id.strip()
            and isinstance(attribution, AdapterAttribution)
            for module_id, attribution in adapter_attribution.items()
        ):
            raise ManifestValidationError(
                "adapter_attribution must map module IDs to AdapterAttribution objects"
            )

        self.pipeline = pipeline
        self.base_model = base_model
        self.adapter_attribution = dict(adapter_attribution)
        self._active_contributors: tuple[Contributor, ...] = ()

    @property
    def active_contributors(self) -> tuple[Contributor, ...]:
        """Return the adapters recorded by the last successful activation."""

        return self._active_contributors

    def set_adapters(
        self,
        adapter_names: str | Sequence[str],
        adapter_weights: float | Sequence[float] | None = None,
    ) -> Any:
        """Activate adapters on the pipeline and record declared weights."""

        names = [adapter_names] if isinstance(adapter_names, str) else list(adapter_names)
        if not names:
            raise ManifestValidationError("adapter_names must not be empty")
        if len(names) != len(set(names)):
            raise ManifestValidationError("adapter_names must be unique")

        missing = [name for name in names if name not in self.adapter_attribution]
        if missing:
            raise ManifestValidationError(
                f"missing attribution registration for: {', '.join(missing)}"
            )

        if adapter_weights is None:
            weights = [1.0] * len(names)
        elif isinstance(adapter_weights, bool) or isinstance(adapter_weights, (int, float)):
            weights = [adapter_weights]
        else:
            weights = list(adapter_weights)
        if len(weights) != len(names):
            raise ManifestValidationError(
                "adapter_weights must contain one value per adapter"
            )

        contributors = tuple(
            self.adapter_attribution[name].as_contributor(name, weight)
            for name, weight in zip(names, weights)
        )

        result = self.pipeline.set_adapters(names, adapter_weights=weights)
        self._active_contributors = contributors
        return result

    def create_manifest(
        self,
        generation_id: str,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> AttributionManifest:
        """Create a manifest for the currently active adapter configuration."""

        if not self._active_contributors:
            raise ManifestValidationError(
                "set_adapters must succeed before creating a manifest"
            )
        return AttributionManifest(
            generation_id=generation_id,
            base_model=self.base_model,
            contributors=self._active_contributors,
            metadata={} if metadata is None else metadata,
        )
