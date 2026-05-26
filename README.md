# fairpalette
Open attribution and royalty infrastructure for generative AI.

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

---

# Documentation

- `docs/SPECIFICATION.md`
- `docs/ARCHITECTURE.md`
- `docs/ETHICS.md`
- `docs/ROADMAP.md`

---

# Contribution

Contributions, critique, technical discussion, and experiments are welcome.

See:
- `CONTRIBUTING.md`

---

# License

TBD.
