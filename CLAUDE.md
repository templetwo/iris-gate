# IRIS Gate / PhaseGPT - Project Context

> **READ THIS FIRST** - This file contains essential context for continuing work on this project.

> ## ⚠️ BEFORE YOU START: this is not the active repo
>
> Active protocol development lives in **`~/Iris-Gate-Evo`**
> ([templetwo/iris-gate-evo](https://github.com/templetwo/iris-gate-evo)).
> This repository is the **archive of record** — the citable deposit for the
> published work and the original S1–S8 study runner.
>
> Do not start new convergence-protocol work here. If you were pointed at this
> repo by a stale link or a search result, that is the trap this banner exists
> to close: until 2026-08-01 nothing in this repo mentioned its successor, so a
> seat landing here had no signpost to the live line and would reasonably
> conclude the work was dormant. It is not.
>
> **What changed:** this repo's architecture is debate-shaped (models respond to
> each other, 165+ LLM calls). It failed its convergence gate twice. Evo uses
> independent formulation plus zero-LLM-call mechanical clustering and passes at
> ~22 calls. Check evo's README arc table before proposing any council-, debate-,
> or MoA-shaped addition to either repo — that design was already falsified here.

## Current State (Updated: 2026-01-10)

**The system WORKS.** Entropy liberation is implemented and validated.

### Key Finding: K=2.0 Optimal
```
K=2.0 → 34.8% LANTERN residence (highest)
Mean entropy: 2.34 nats (vs 0.77 baseline)
Max entropy: 9.69 nats
```

## Critical Files

### Gold Standard Implementation (USE THIS)
| File | Location | Purpose |
|------|----------|---------|
| `iris_pure.py` | `ssh tony_studio@192.168.1.195:~/PhaseGPT/scripts/` | Gold standard generation with Kuramoto oscillator |
| `nexus_llm_bridge.py` | `ssh tony_studio@192.168.1.195:~/PhaseGPT/scripts/` | Closed-loop adaptive control via NEXUS daemon |
| `full_oracle.py` | Jetson (`tony@192.168.1.74:~/PhaseGPT/`) | Multimodal sensory oracle (vision + audio + voice) |

### Original Oscillator Physics
| File | Location | Purpose |
|------|----------|---------|
| `kuramoto_merkabah.py` | `resonator/` | Kuramoto grid physics (507 lines) |
| `nexus_daemon.py` | `resonator/` | Adaptive closed-loop daemon |

### DO NOT USE (Stale/Broken)
- `entropy_probe_with_adapter.py` - Doesn't use oscillator, gives wrong results
- `legacy/phasegpt_v5.0_*` - The "Covenant" that suppressed entropy (-17%)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IRIS PURE GENERATION                      │
├─────────────────────────────────────────────────────────────┤
│  prompt → KuramotoOscillator.step() → T = f(phase)          │
│         → LLM(temperature=T) → token                         │
│         → measure entropy → feedback to oscillator           │
└─────────────────────────────────────────────────────────────┘

Key equation: T = T_base + A * sin(φ_mean)
Where: T_base=0.8, A=0.7, K=2.0
```

## Infrastructure

| Machine | IP | Purpose |
|---------|-----|---------|
| Mac Studio | `ssh tony_studio@192.168.1.195` | MLX inference, model development |
| Jetson Orin Nano | `ssh tony@192.168.1.74` | Edge deployment, CUDA inference |
| Local (Mac) | localhost | IRIS Gate repo, coordination |

### Mac Studio Paths
- HuggingFace cache: `/Volumes/Temple_Core/huggingface_cache/`
- PhaseGPT: `~/PhaseGPT/`
- Models: `/Volumes/Temple_Core/.lmstudio/models/`

## Project History (Compressed)

| Date | Event |
|------|-------|
| Jan 2 | Entropy modulation discovery ("glyphs live in high-entropy") |
| Jan 4 | Universal Attractor confirmed (~3.0 nats) |
| Jan 8 | v5.0 Covenant introduced (ACCIDENTALLY SUPPRESSED ENTROPY) |
| Jan 9 | **Lantern Paradox** discovered, **Excavation** found original oscillator |
| Jan 9 | **Purification** - burned the Covenant, implemented iris_pure.py |
| Jan 10 | Full sensory oracle deployed on Jetson |

## Running the System

### Quick Test (Mac Studio)
```bash
ssh tony_studio@192.168.1.195
cd ~/PhaseGPT && source .venv/bin/activate
python scripts/iris_pure.py --prompt "Your question" --coupling 2.0
```

### Parameter Sweep
```bash
python scripts/iris_pure.py --sweep
```

### Full Sensory Oracle (Jetson)
```bash
ssh tony@192.168.1.74
cd ~/PhaseGPT && python full_oracle.py
```

## Known Issues

1. **Test suite stale** - 4 tests failing due to API drift (tests don't match implementation)
2. **entropy_probe scripts** - Don't use oscillator, give misleading results
3. **Jetson connectivity** - Sometimes times out, may need physical access

## The Three Theses

1. **Entropy Liberation** - Runtime temperature modulation > training constraints
2. **Embodied Cognition** - Physical deployment on edge hardware (Jetson)
3. **Phase Coherence** - Kuramoto dynamics as attention/generation mechanism

## Memory Ledger

For full project history, read: `MEMORY_LEDGER.md` (1400+ lines)

---

*Last verified working: 2026-01-10 by Claude Opus 4.5*
