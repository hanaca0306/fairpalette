# Architecture

---

# Conceptual Pipeline

```text
[ User Prompt ]
       │
       ▼
[ Base Model + Multi-LoRA Pipeline ]
       │
       ▼
[ Attribution Session Layer ]
       │
 ┌─────┼───────────────────┐
 ▼     ▼                   ▼
Manifest  Royalty Log   Provenance Metadata
```

---

# Proposed Tech Stack

## Frontend
- TypeScript
- Next.js
- TailwindCSS

## Backend
- Python
- FastAPI
- SQLAlchemy Async
- Redis Queue / Celery

## AI Layer
- PyTorch
- Hugging Face diffusers
- PEFT
- OpenCLIP (experimental)

## Infrastructure
- PostgreSQL
- Cloudflare R2
- Docker
- Kubernetes (future consideration)

---

# Multi-LoRA Direction

Example:

```python
pipe.set_adapters(
    ["LoRA_A", "LoRA_B"],
    adapter_weights=[0.7, 0.3]
)
```

The attribution layer records:
- active adapters
- weight values
- generation session metadata
- timestamps
- optional licensing data

## Diffusers Experiment

`DiffusersAttributionSession` wraps the narrow `set_adapters()` boundary rather
than taking a dependency on Diffusers itself. Registered creator and licensing
information is joined with the adapter names and weights only after the pipeline
accepts the configuration. A manifest can then be emitted for each generation.

This records declared pipeline participation. It does not claim that adapter
weights measure pixel-level causal contribution.

## Creator Registry

The v0.1 registry separates creator identity records from module registrations.
Each module points to one creator and carries its license, metadata, and active
consent state. Only active registrations are exposed to new attribution sessions;
inactive records remain in the registry for auditability.
