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
  "generation_id": "gen_20260526_001",
  "base_model": "sdxl",
  "contributors": [
    {
      "artist_id": "artist_A",
      "applied_weight": 0.7,
      "license": "commercial_allowed"
    },
    {
      "artist_id": "artist_B",
      "applied_weight": 0.3,
      "license": "noncommercial_only"
    }
  ],
  "timestamp": "2026-05-26T12:00:00Z"
}
```

---

# Example SDK Direction

```python
from fairpalette import AttributionSession

session = AttributionSession(
    base_model="sdxl",
    contributors=[
        {"artist": "A", "weight": 0.7},
        {"artist": "B", "weight": 0.3}
    ]
)

image = session.generate(
    prompt="city pop anime illustration"
)

session.export_manifest()
session.calculate_royalties()
```

---

# Metadata Goals

Potential future metadata support:
- C2PA compatibility
- provenance manifests
- audit logging
- creator registry systems
- generation receipts
