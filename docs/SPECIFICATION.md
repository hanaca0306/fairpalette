# Technical Specification

This document defines the conceptual architecture and attribution structures proposed by FairPalette.

---

# Attribution Model

FairPalette does not attempt deterministic pixel-level reverse tracing.

Instead, attribution is defined through:
- declared module participation
- explicit weighting structures
- generation metadata logging
- contractual attribution structures

---

# Example Royalty Structure

Given:
- total payment: P_total
- platform fee: α
- infrastructure cost rate: β
- contributor weight: w_i

Creator royalty pool:

```math
P_artist = P_total(1 - α - β)
```

Individual royalty allocation:

```math
R_i = P_artist * (w_i / Σw)
```

---

# Example Attribution Manifest

```json
{
  "spec_version": "0.1",
  "generation_id": "gen_20260526_001",
  "base_model": "sdxl",
  "contributors": [
    {
      "artist_id": "artist_A",
      "module_id": "lora_A",
      "applied_weight": 0.7,
      "license": "commercial_allowed",
      "metadata": {}
    },
    {
      "artist_id": "artist_B",
      "module_id": "lora_B",
      "applied_weight": 0.3,
      "license": "noncommercial_only",
      "metadata": {}
    }
  ],
  "timestamp": "2026-05-26T12:00:00Z",
  "metadata": {}
}
```

The normative machine-readable definition is
`schema/attribution-manifest-v0.1.schema.json`. In v0.1, weights record declared
pipeline participation; they are not claims of pixel-level causal contribution.
SDK validation additionally requires `module_id` values to be unique within a
manifest.

---

# Example SDK Direction

```python
from fairpalette import AttributionManifest, Contributor

manifest = AttributionManifest(
    generation_id="gen_20260526_001",
    base_model="sdxl",
    contributors=[
        Contributor("artist_A", "lora_A", 0.7),
        Contributor("artist_B", "lora_B", 0.3),
    ]
)

manifest.write("manifest.json")
```

---

# Metadata Goals

Potential future metadata support:
- C2PA compatibility
- provenance manifests
- audit logging
- creator registry systems
- generation receipts

---

# Creator Registry v0.1

The creator registry is a portable JSON document containing:

- creator identity records with stable `creator_id` values
- module registrations that reference a known creator
- license identifiers and module metadata
- an `active` consent flag used when creating new attribution sessions

Inactive registrations are retained for auditability but must not be activated
for new generations. The normative JSON shape is defined by
`schema/creator-registry-v0.1.schema.json`.

---

# Metadata Export v0.1

The metadata export is a JSON sidecar that packages an attribution manifest with
optional royalty allocations, application metadata, and an asset descriptor. The
asset descriptor contains its filename, MIME type, byte size, and SHA-256 digest.
Local absolute paths and asset bytes are not included.

The normative envelope is defined by
`schema/metadata-export-v0.1.schema.json`.
