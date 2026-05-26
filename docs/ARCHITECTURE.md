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
