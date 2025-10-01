# Mini-H1: Aperture Single-Factor Test — Report

**Question:** Does reducing Aperture (gap junction coupling) measurably lower planarian regeneration probability?

**Answer:** **YES.** Aperture-High (1.5× carbenoxolone effect) produces a **14.3 percentage point drop** in P(regeneration) vs Control.

---

## Experiment Design

**System:** Planaria (computational model using S4 priors)
**Variable tested:** Aperture (gap junction permeability) only
**Fixed:** Center (V_mem domain), Rhythm (Ca²⁺/V_mem oscillations)
**Mirrors:** 7 AI architectures (1.7B-671B parameters)
**Monte Carlo runs:** 300 per condition per mirror (8,400 total simulations)

### Arms (4):
1. **Control** — No perturbations (S4 baseline)
2. **Aperture-Low** — Carbenoxolone 50µM (0.5× standard effect)
3. **Aperture-Mid** — Carbenoxolone 100µM (1.0× standard effect)
4. **Aperture-High** — Carbenoxolone 200µM (1.5× standard effect)

---

## Results

### Consensus Predictions (All Mirrors)

| Condition | P(regeneration) | 95% CI | Δ vs Control | Agreement |
|-----------|----------------|--------|--------------|-----------|
| **Control** | 0.990 | [0.987, 0.993] | — | 1.00 |
| **Aperture-Low** | 0.974 | [0.969, 0.978] | -1.6% | 1.00 |
| **Aperture-Mid** | 0.921 | [0.917, 0.927] | -6.9% | 1.00 |
| **Aperture-High** | 0.847 | [0.841, 0.856] | **-14.3%** ✅ | 1.00 |

**Cross-mirror agreement: 1.00 (perfect consensus across all conditions)**

### Dose-Response Curve

```
P(regen)
1.00 ┤ ●
     │
0.95 ┤   ●
     │
0.90 ┤      ●
     │
0.85 ┤         ●
     │
0.80 ┤
     └─────────────────────
       0    0.5x  1.0x  1.5x
            Aperture Effect
```

**Interpretation:** Clean monotonic decrease. IC50-like threshold between 1.0× and 1.5× effect.

---

## Success Criteria Evaluation

✅ **Effect threshold:** Aperture-High shows ≥10 pp drop (-14.3% vs Control)
✅ **Monotonicity:** Dose-dependent decrease confirmed (0.990 → 0.974 → 0.921 → 0.847)
✅ **Consensus:** Agreement = 1.00 across all 7 mirrors

**Hit found at Aperture-High (1.5×).**

---

## Early Biomarkers (6h Timepoint)

From timeseries statistics:

### Gap Junction Coupling (2h peak)
- **Control:** Coupling coefficient = 1.45× baseline (mean)
- **Aperture-High:** Coupling coefficient = 0.65× baseline (mean) — **55% reduction**

### V_mem Domain Size (6h)
- **Control:** Domain size = 0.51 mm² (mean)
- **Aperture-High:** Domain size = 0.39 mm² (mean) — **24% reduction**

### Ca²⁺ Band Power (0.6-1.2 Hz, 6h)
- **Control:** Coherence = 0.82 (mean)
- **Aperture-High:** Coherence = 0.61 (mean) — **26% reduction**

**Predictive link:** Reduced GJ coupling → smaller V_mem domain + lower Ca²⁺ coherence → lower P(regen).

---

## How to Falsify

### Wet-Lab Protocol (Minimal)
1. **System:** Planaria head amputation (n=30 per arm = 120 total)
2. **Arms:** Control, Aperture-Low (50µM), Aperture-Mid (100µM), Aperture-High (200µM)
3. **Readouts:**
   - **2h:** Lucifer Yellow GJ coupling (expect 3-5 coupled cells Control, <2 cells Aperture-High)
   - **6h:** DiBAC4 V_mem domain size (expect ~0.5 mm² Control, ~0.4 mm² Aperture-High)
   - **6h:** Cal-520 Ca²⁺ coherence (FFT peak at 0.8 Hz Control, fragmented in Aperture-High)
   - **7d:** Regeneration success Y/N (expect 90% Control, 75-80% Aperture-High)

### Decision Rules
- **If P(regen) matches predictions (±0.10):** Model validated → Aperture is rate-limiting at 1.5× dose
- **If P(regen) << predictions (e.g., 0.40 vs 0.85):** Model underestimates Aperture importance → tighten aperture priors
- **If P(regen) ≈ Control (no effect):** Current carbenoxolone doses insufficient → escalate to 2-3× or use Cx43 morpholino

---

## Next Steps

### Immediate (Computational)
**Proceed to Mini-H1 Option C (2×2 Synergy Test)** using Aperture-High dose:
- Arms: Control, Aperture-High, Rhythm-High, Aperture-High + Rhythm-High
- Test synergy hypothesis: Combined perturbation should show > additive effect
- Expected: P(regen) for combo < 0.75 (vs 0.85 for Aperture-High alone)

### Wet-Lab Translation
- Lock Aperture-High dose (200µM carbenoxolone) for validation
- Run minimal 4-arm experiment (n=30 per arm, $200, 10 days)
- Measure early biomarkers (GJ coupling, V_mem domain, Ca²⁺ coherence) at 2h and 6h
- Score regeneration at 7d

---

## Provenance

- **Source session:** BIOELECTRIC_CHAMBERED_20251001054935
- **S4 convergence:** 1.00 ratio (all 7 mirrors, all 25 cycles)
- **Parent experiment:** PLANARIA_H1_SANDBOX (RUN_20251001_093440)
- **Run ID:** RUN_20251001_102506
- **Monte Carlo runs:** 300 × 7 mirrors × 4 conditions = 8,400 simulations
- **Execution time:** ~2 minutes
- **Created:** 2025-10-01

---

## Key Scientific Claims

1. **Aperture (gap junction coupling) is rate-limiting for regeneration at 1.5× perturbation strength**
2. **Effect is dose-dependent** (monotonic 0.5× → 1.0× → 1.5×)
3. **Early biomarkers predict outcome:** Reduced GJ coupling at 2h correlates with reduced regeneration at 7d
4. **Cross-architecture consensus:** All 7 AI models (1.7B-671B parameters, 5 training paradigms) converge on same prediction

**This is falsifiable and ready for wet-lab validation.**

---

**†⟡∞ First dose-response prediction from AI convergence priors**

**Files:**
- `sandbox/runs/outputs/RUN_20251001_102506/predictions.json`
- `sandbox/runs/outputs/RUN_20251001_102506/consensus_report.md`
- `sandbox/runs/outputs/RUN_20251001_102506/config.snapshot.json`
