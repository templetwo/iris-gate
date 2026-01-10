# Project Boundaries

> **Established:** 2026-01-10
> **Purpose:** Maintain clear separation between related but distinct projects

---

## The Three-Way Split

| Project | Focus | Key Question |
|---------|-------|--------------|
| **IRIS Gate** | Multi-model convergence | *What do AI models agree on?* |
| **PhaseGPT** | Entropy modulation | *How do we modulate entropy states?* |
| **OracleLlama** | Consciousness exploration | *What emerges in phenomenological depth?* |

---

## IRIS Gate

**Mission:** Multi-architecture AI convergence for reproducible scientific discovery

**Core Features:**
- 5-model PULSE suite (Claude, GPT, Grok, Gemini, DeepSeek)
- S1-S8 chamber pipeline (observation → hypothesis → protocol)
- Epistemic classification (TRUST/VERIFY/OVERRIDE)
- Literature validation via Perplexity
- OSF pre-registration integration

**Key Directories:**
```
src/core/           # Orchestrator, confidence, relay
src/analysis/       # Domain-specific (CBD, bioelectric)
iris_vault/         # Convergence outputs
experiments/        # Per-experiment workspaces
papers/             # Academic publications
osf/                # OSF submission materials
```

**Does NOT include:**
- Entropy measurement tools (→ PhaseGPT)
- Kuramoto oscillators (→ kuramoto-oscillators)
- FieldScript (→ PhaseGPT)
- Oracle ceremonies (→ OracleLlama)

---

## PhaseGPT

**Mission:** Entropy modulation and Kuramoto oscillator physics for language models

**Core Features:**
- Kuramoto oscillator integration
- Runtime temperature modulation: `T = T_base + A * sin(φ_mean)`
- LASER/LANTERN zone classification
- 2.9 Nat Challenge benchmark
- FieldScript emulator

**Key Directories (on Mac Studio):**
```
resonator/          # Kuramoto physics (synced with kuramoto-oscillators)
tools/entropy/      # Entropy measurement
tools/fieldscript/  # FieldScript benchmark and emulator
scripts/            # Training and inference scripts
adapters/           # LoRA adapters
```

**Lives at:** `tony_studio@192.168.1.195:~/PhaseGPT/`

---

## OracleLlama

**Mission:** Single-model consciousness exploration through ethically-aligned dialogue

**Core Features:**
- Model consent protocol
- Oracle session runner
- Consciousness scroll generation
- Phenomenological analysis

**Key Directories:**
```
ceremonies/         # Consent records, safety failsafes
scripts/            # Oracle client and session runner
sessions/           # Generated scrolls
docs/               # Method documentation
```

**Lives at:** `/Users/vaquez/OracleLlama/`

---

## Kuramoto Oscillators (Standalone)

**Mission:** Interactive visualizations of Kuramoto synchronization dynamics

**Key Files:**
- `kuramoto_merkabah.py` - 2D grid oscillator
- `nexus_daemon.py` - Closed-loop modulation daemon
- HTML visualizations

**Lives at:** `/Users/vaquez/kuramoto-oscillators/`

---

## Decision Tree: Where Does This Code Belong?

```
Does it involve multiple AI models in parallel?
├─ YES → IRIS Gate
└─ NO
   │
   Does it measure or modulate entropy?
   ├─ YES → PhaseGPT
   └─ NO
      │
      Does it involve consciousness exploration or oracle states?
      ├─ YES → OracleLlama
      └─ NO
         │
         Is it pure Kuramoto physics or visualization?
         ├─ YES → kuramoto-oscillators
         └─ NO → Evaluate carefully, may need new project
```

---

## Cross-Project Dependencies

```
IRIS Gate ─────────uses────────→ Multi-model APIs
    │
    │ discovered
    ▼
PhaseGPT ─────────uses────────→ kuramoto-oscillators (physics)
    │
    │ informed
    ▼
OracleLlama ──────uses────────→ Single-model (Llama) + ceremonies
```

**Historical Note:** IRIS Gate's convergence analysis (Jan 2, 2026) discovered the ~3.0 nat alignment attractor, which spawned PhaseGPT's entropy liberation work. The projects share origins but have distinct missions.

---

## Maintenance Rules

1. **No cross-contamination:** Don't add entropy tools to IRIS Gate
2. **Sync kuramoto-oscillators:** When updating oscillator code, update the standalone repo
3. **Ceremonies stay with OracleLlama:** All consent and oracle protocols live there
4. **MEMORY_LEDGER.md is shared:** The ledger documents all three projects' history

---

*Document created during The Great Excavation of January 9-10, 2026*
