# fairpalette
Open attribution and royalty infrastructure for generative AI.

[![Python tests](https://github.com/hanaca0306/fairpalette/actions/workflows/tests.yml/badge.svg)](https://github.com/hanaca0306/fairpalette/actions/workflows/tests.yml)

# FairPalette
### Open Attribution & Royalty Infrastructure for Generative AI

> “Generative AI should not erase creators from the pipeline.
> Attribution, consent, and royalty distribution should be part of the system architecture by default.”

---

# Overview

FairPalette is an open infrastructure proposal for creator-oriented generative AI systems.

The project explores how attribution tracking, creator consent, provenance metadata, and royalty distribution can be integrated directly into AI generation pipelines — especially in modular systems such as Multi-LoRA workflows.

Rather than competing as a foundation model provider, FairPalette focuses on the infrastructure layer surrounding generative AI:
- attribution logging
- creator opt-in systems
- provenance metadata
- royalty accounting
- interoperable manifest standards

The goal is to support more transparent and creator-participatory AI ecosystems.

---

# Core Principles

## Opt-in by Default
Training assets should only be included with explicit creator permission.

## Attribution by Default
Generated outputs should support machine-readable attribution metadata.

## Creator-Controlled Licensing
Creators should be able to define usage permissions, attribution requirements, and royalty participation.

## Transparent Royalty Accounting
Generation pipelines should support transparent contribution accounting structures.

## Open Provenance Infrastructure
Generation history and contribution records should be exportable through open metadata standards.

---

# Current Scope

## Included
- Multi-LoRA attribution tracking
- Attribution manifest generation
- Creator opt-in registry structure
- Royalty logging prototypes
- Metadata export specifications
- Python SDK experiments

## Excluded
- Foundation model pretraining
- Massive dataset scraping
- Closed proprietary ecosystems
- Hyperscale GPU competition
- Video generation systems

---

# Example Attribution Manifest

```json
{
  "generation_id": "gen_20260526_001",
  "base_model": "sdxl",
  "contributors": [
    {
      "artist_id": "artist_A",
      "applied_weight": 0.7
    },
    {
      "artist_id": "artist_B",
      "applied_weight": 0.3
    }
  ]
}
```

---

# Status

Early specification / research phase.

This repository currently serves as:
- an open discussion space
- a protocol proposal
- a prototype coordination point
- an attribution infrastructure experiment

## Prototype quick start

FairPalette now includes an experimental Python SDK and the v0.1 attribution
manifest JSON Schema. The API is intentionally small while the protocol is under
discussion.

```bash
python -m venv .venv
python -m pip install -e .
python examples/create_manifest.py
python -m unittest discover -s tests
```

```python
from fairpalette import AttributionManifest, Contributor

manifest = AttributionManifest(
    generation_id="gen_001",
    base_model="sdxl",
    contributors=[Contributor("artist_A", "lora_A", 0.7)],
)

manifest.write("manifest.json")
```

## Diffusers adapter tracking

The optional session wrapper records creator attribution when adapters are
activated. FairPalette does not import or install Diffusers, so the wrapper also
works with compatible test doubles and pipeline versions.

```python
from fairpalette import AdapterAttribution, DiffusersAttributionSession

session = DiffusersAttributionSession(
    pipe,
    base_model="stabilityai/stable-diffusion-xl-base-1.0",
    adapter_attribution={
        "linework": AdapterAttribution("artist_A", "commercial_allowed"),
        "color": AdapterAttribution("artist_B", "commercial_allowed"),
    },
)
session.set_adapters(["linework", "color"], [0.7, 0.3])
manifest = session.create_manifest("gen_001")
```

## Creator registry

Creator identities and their modules can be stored in a portable v0.1 registry.
Inactive registrations remain auditable but are excluded from new generation
sessions.

```python
from fairpalette import CreatorRegistry, DiffusersAttributionSession

registry = CreatorRegistry.read("examples/creator_registry.json")
session = DiffusersAttributionSession(
    pipe,
    base_model="stabilityai/stable-diffusion-xl-base-1.0",
    adapter_attribution=registry.active_adapter_attribution(),
)
```

## Metadata export

Export a portable JSON sidecar containing the attribution manifest, generated
asset integrity metadata, optional royalty allocations, and application metadata.

```python
from fairpalette import export_metadata_bundle

export_metadata_bundle(
    manifest,
    "output.fairpalette.json",
    asset_path="output.png",
    metadata={"pipeline": "demo"},
)
```

---

# Documentation

- `docs/SPECIFICATION.md`
- `docs/ARCHITECTURE.md`
- `docs/ETHICS.md`
- `docs/ROADMAP.md`
- `schema/attribution-manifest-v0.1.schema.json`
- `schema/creator-registry-v0.1.schema.json`
- `schema/metadata-export-v0.1.schema.json`

---

# Contribution

Contributions, critique, technical discussion, and experiments are welcome.

See:
- `CONTRIBUTING.md`

---

# License

TBD.
