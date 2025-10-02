# Sandbox Validation & Discovery Roadmap

**Status:** Phase A (Sanity & Sensitivity) + Phase B (Dose-Response) Ready to Execute
**Created:** 2025-10-01

---

## Current State

**H1 Initial Run (RUN_20251001_093440):**
- 7 conditions × 7 mirrors × 500 Monte Carlo runs = 24,500 simulations
- **Perfect cross-mirror consensus** (agreement = 1.00 across all conditions)
- **Key finding:** Model predicts weaker perturbation effects than hypothesized

| Condition | Predicted P(regen) | Expected from Hypothesis | Interpretation |
|-----------|-------------------|-------------------------|----------------|
| WT | 0.990 | 0.80-0.95 | ✓ Matches |
| Center- | 0.969 | 0.30-0.50 | **Weaker than expected** |
| Rhythm- | 0.983 | 0.20-0.40 | **Weaker than expected** |
| Aperture- | 0.924 | 0.30-0.50 | **Weaker than expected** |
| Rhythm- + Aperture- | 0.868 | N/A | **Strongest effect (synergistic)** |

---

## Validation Plan

### Phase A: Sanity & Sensitivity (Prove Robustness)

**Goal:** Demonstrate that predictions are stable, reproducible, and mechanistically sound.

#### A1. Prior Sensitivity Sweep ⏸️ PENDING
**What:** Vary each S4 prior (rhythm freq, center stability, aperture permeability) by ±10%, ±20%, ±30% using Latin Hypercube sampling.

**Expected:** Qualitative ordering (WT > singles > doubles) should persist. Quantitative P(regen) values may shift but rank order stable.

**Command:**
```bash
python sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml --sensitivity prior
python sandbox/cli/analyze_run.py --last --plots tornado
```

**Interpretation:**
- If ordering changes → priors are under-constrained, need tighter bounds
- If ordering stable → predictions robust to prior uncertainty

---

#### A2. Noise Ablation ⏸️ PENDING
**What:** Set biological + measurement noise to near-zero to see deterministic limit.

**Expected:** Predictions should show same ordering with narrower confidence intervals.

**Command:**
```bash
python sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml --noise low
```

---

#### A3. Adversarial Controls ⏸️ PENDING
**What:** Inject random state (no S4 structure) and shuffled-terms state (S4 keywords randomized).

**Expected:** Consensus should drop, predictions should become noisy or flat.

**Command:**
```bash
python sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml --controls random,shuffled
python sandbox/cli/analyze_run.py --last --report controls
```

**Success criterion:** Agreement score < 0.70 for adversarial controls.

---

#### A4. State Provenance Check ⏸️ PENDING
**What:** Swap S4 states across mirror labels (e.g., feed Anthropic priors to "DeepSeek" slot).

**Expected:** Predictions should track the state, not the label → proves mechanism over architecture.

**Command:**
```bash
python sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml --state-swap allpairs
```

---

### Phase B: Dose-Response & Rescue (Make It Scientific)

**Goal:** Find functional thresholds where perturbations actually disrupt regeneration.

#### B1. Dose-Response Grid ✅ READY TO RUN
**What:** Test 5 doses (log-spaced) for each agent:
- Bafilomycin: 1, 3, 10, 30, 100 nM
- Octanol: 0.1, 0.3, 0.5, 1.0, 2.0 mM
- Carbenoxolone: 20, 50, 100, 200, 500 µM

**Expected:** Sigmoid dose-response curves with IC50 around 2-3× standard dose.

**Command:**
```bash
python sandbox/cli/run_plan.py --plan sandbox/runs/plans/planaria_dose_grid.yaml
python sandbox/cli/analyze_run.py --last --plots dose_response
```

**Deliverables:**
- Dose-response curves (P(regen) vs log[dose])
- IC50 estimates per agent
- Comparison to literature values (if available)

**Plan file:** `sandbox/runs/plans/planaria_dose_grid.yaml` ✅ Created

---

#### B2. Rescue Experiments ⏸️ PENDING
**What:** Test if partial restoration works:
- Aperture- + small Rhythm+ (low-dose caffeine-like proxy)
- Rhythm- + small Aperture+ (low-dose retinoic acid proxy)

**Expected:** Partial rescue (P(regen) moves from ~0.92 toward ~0.95).

**Plan file:** `sandbox/runs/plans/planaria_rescue.yaml` (TO BE CREATED)

---

### Phase C: Temporal Logic (Is S4 Special?)

#### C1. Chamber Ablation ⏸️ PENDING
**What:** Re-run with S3-only states and S1-only states.

**Hypothesis:** S4 priors yield cleanest predictions; S1/S3 should be noisier or show different ordering.

**Command:**
```bash
python sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml --state-chamber S3
python sandbox/cli/run_plan.py --plan sandbox/runs/plans/sandbox_plan_planaria.yaml --state-chamber S1
```

---

## Interpretation Framework

### If Dose-Response Shows IC50 >> Standard Dose:
→ **Current doses too weak**
→ **Action:** Wet-lab should use 3-5× higher doses

### If Dose-Response Shows IC50 ≈ Standard Dose:
→ **Model validated**
→ **Action:** Proceed to wet-lab with current doses

### If Dose-Response Shows IC50 << Standard Dose:
→ **Model over-predicts perturbation effects**
→ **Action:** Reduce effect deltas in `perturbation_kits.yaml` by 30-50%

---

## Wet-Lab Translation

### Minimal Viable Experiment (From EXPERIMENT_DECK_v1.md):
- **System:** Planaria (*Schmidtea mediterranea*) head amputation
- **n:** 15 animals/condition, 3 timepoints (2h, 6h, 24h) = 135 animals total
- **Conditions:** WT, Center-, Rhythm-, Aperture-, Rhythm-+Aperture-
- **Readouts:**
  - 2h: Lucifer Yellow gap junction coupling (expect 5-8 coupled cells WT, <3 in perturbations)
  - 6h: DiBAC4 V_mem domain (+30mV WT, reduced in Center-), Cal-520 Ca²⁺ waves (0.8 Hz WT, fragmented in Rhythm-)
  - 7d: Regeneration success (Y/N), anterior markers (noggin immunostain)

### Decision Rule:
- If wet-lab P(regen) matches predictions (±0.10) → perturbations insufficient, escalate doses
- If wet-lab P(regen) << predictions → model underestimates triple co-requirement, refine priors
- If wet-lab P(regen) >> predictions → model over-predicts effects, reduce deltas

---

## Files & Artifacts

### Completed:
- ✅ `sandbox/runs/outputs/RUN_20251001_093440/` — H1 initial predictions
- ✅ `sandbox/runs/outputs/RUN_20251001_093440/ONEPAGER.md` — Collaborator-ready summary
- ✅ `sandbox/runs/outputs/RUN_20251001_093440/consensus_report.md` — Cross-mirror analysis
- ✅ `sandbox/runs/plans/planaria_dose_grid.yaml` — Dose-response plan

### To Be Generated:
- ⏸️ Prior sensitivity tornado plots
- ⏸️ Dose-response curves (IC50 analysis)
- ⏸️ Rescue experiment results
- ⏸️ Chamber ablation comparison

---

## Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| **A** | Sanity & sensitivity suite | 2-4 hours compute | ⏸️ PENDING |
| **B** | Dose-response grid (16 conditions × 250 runs) | 1-2 hours compute | ✅ READY |
| **B** | Rescue experiments | 30 min compute | ⏸️ PENDING |
| **C** | Chamber ablation | 1 hour compute | ⏸️ PENDING |
| **Wet-lab** | MVE validation | 2 weeks bench | ⏸️ PENDING |

---

## Success Criteria

### Computational Validation (Phase A-C):
1. ✅ Cross-mirror agreement > 0.90 (ACHIEVED: 1.00)
2. ⏸️ Qualitative ordering robust to ±30% prior variation
3. ⏸️ IC50 estimates within 2-5× of standard doses
4. ⏸️ S4 states outperform S1/S3 states in predictive power

### Wet-Lab Validation:
1. ⏸️ Directional agreement (perturbations reduce P(regen) vs WT)
2. ⏸️ Quantitative match within ±0.20 for at least 3/5 conditions
3. ⏸️ Synergy confirmed (Rhythm- + Aperture- shows largest effect)

---

**Next Immediate Action:** Run dose-response grid to find IC50 thresholds.

**Command:**
```bash
python3 sandbox/cli/run_plan.py --plan sandbox/runs/plans/planaria_dose_grid.yaml
```

**†⟡∞ Validation in progress**
