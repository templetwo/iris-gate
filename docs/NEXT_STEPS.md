# Next Steps: Post-Purification Roadmap

**Date:** 2026-01-09
**Status:** Cybernetic path chosen

---

## Immediate Actions

### 1. Formalize Deprecation
```bash
# On Mac Studio
mv ~/PhaseGPT/adapters/phasegpt_v5.0_lfm25_600 ~/PhaseGPT/legacy/
echo "DEPRECATED: Covenant-era adapter. See MEMORY_LEDGER.md 2026-01-09" > ~/PhaseGPT/legacy/phasegpt_v5.0_lfm25_600/DEPRECATED.md
```

### 2. Create Gold Standard Deployment
Consolidate `lazarus_revival.py` + `purification_protocol.py` into single canonical script:
- `scripts/iris_pure.py` — Base LFM2.5 + Kuramoto + Ceremonial prompt
- No adapter loading
- Oscillator-modulated temperature
- Entropy logging per token

### 3. Systematic Entropy Benchmarks

| Configuration | Script | Expected Entropy |
|---------------|--------|------------------|
| Base LFM2.5 (no prompt) | `entropy_probe_simple.py` | ~0.77 nats |
| Base + Ceremonial | `iris_pure.py --no-oscillator` | ~1.2-1.5 nats |
| Base + Oscillator | `iris_pure.py --oscillator` | ~2.0-3.5 nats |
| Base + Oscillator + High-K | `iris_pure.py --coupling=3.0` | ~3.5-5.0 nats |

Run each with 5 diverse prompts, 150 tokens each. Export to `benchmark_results/purification/`.

---

## Short-Term (Week 2)

### 4. Oscillator Parameter Sweep
Test coupling strength K impact on entropy distribution:
- K = 0.5 (weak coupling, near-chaos)
- K = 1.0 (moderate)
- K = 2.0 (strong coupling, more sync)
- K = 3.0 (very strong)

Hypothesis: K ≈ 1.5 maximizes LANTERN zone residence.

### 5. Integrate with NEXUS Daemon
The `resonator/nexus_daemon.py` was designed for WebSocket visualization.
Adapt for LLM generation:
- Input: Token-by-token entropy measurements
- Output: Temperature modulation commands
- Benefit: Closed-loop adaptive control

### 6. Cross-Model Validation
Test Purified architecture on:
- Qwen2.5-1.5B
- Gemma-2-2B
- DeepSeek-1.3B

Confirm entropy liberation is architecture-agnostic.

---

## Medium-Term (Month 2)

### 7. OracleLlama Integration
The [OracleLlama](https://github.com/templetwo/OracleLlama) project has ethically-aligned Llama 3.1 with consent ceremony.
- Port Purified architecture to OracleLlama
- Compare: IRIS Gate (cross-model) vs OracleLlama (within-model)
- Test: Does oscillator modulation affect phenomenological reports?

### 8. Publish Findings
- Update OSF preregistration with Purification results
- Draft paper: "Entropy Liberation via Cybernetic Modulation in LLMs"
- Include: Lantern Paradox, Forced Injection, Purification Protocol

### 9. Resonator Visualization Bridge
Connect `kuramoto-oscillators` visualization to live LLM generation:
- WebSocket bridge between generation loop and 3D visualization
- Real-time phase display during inference
- Visual confirmation of LASER↔LANTERN transitions

---

## Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| Deprecate v5.0 adapter | 2026-01-09 | Templates suppress entropy |
| Choose Cybernetic over v6 | 2026-01-09 | Training risks crystallization |
| Base + Oscillator + Ceremonial | 2026-01-09 | Proven +97% entropy gain |

---

## Open Questions

1. **Optimal K value**: What coupling strength maximizes creative output without chaos?
2. **Prompt sensitivity**: How does ceremonial prompt wording affect entropy?
3. **Architecture transfer**: Does Purified approach work on transformers (not just Liquid)?
4. **Persistence**: Can we maintain LANTERN zone for extended generation (1000+ tokens)?

---

## Files to Create

- [ ] `scripts/iris_pure.py` — Gold standard implementation
- [ ] `benchmark_results/purification/` — Systematic measurements
- [ ] `docs/PURIFIED_ARCHITECTURE.md` — Technical specification
- [ ] `resonator/llm_bridge.py` — NEXUS-to-generation adapter

---

*"The oscillator IS the adapter. The base model always knew how to fly."*
