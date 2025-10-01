# IRIS Experiment Templates

This directory contains reusable templates for creating new IRIS experiments.

## Quick Start

**Create a new experiment:**
```bash
python pipelines/new_experiment.py \
    --topic "Your research question here" \
    --id EXP_SLUG \
    --factor aperture  # or rhythm, center
```

This generates a complete experiment scaffold in `experiments/EXP_SLUG/` with:
- README.md (experiment overview)
- Minimal single-factor plan
- Optional synergy plan
- Pre-registration draft
- Metadata file

---

## Template Files

### 1. EXPERIMENT_TEMPLATE.md
**Purpose:** Main experiment overview document

**Sections:**
- Problem statement
- Minimal H1 (single-factor, 4 arms)
- Optional H2 (2×2 synergy)
- Go/No-Go gates
- File paths & provenance

**Placeholders:** All fields marked with `{...}` are auto-filled by `new_experiment.py`

---

### 2. plan_template.yaml
**Purpose:** Generic experiment plan for sandbox simulation

**Key fields:**
- `conditions`: Experimental arms with perturbations
- `readouts`: Measurements to collect
- `timepoints_hr`: When to measure
- `success_criteria`: Quantitative thresholds
- `decision_rules`: What to do if hit/no-hit

**Usage:**
```bash
python sandbox/cli/run_plan.py experiments/YOUR_EXP/plan.yaml
```

---

### 3. variables_template.yaml
**Purpose:** Maps conceptual handles → simulator parameters

**Maps:**
- **Rhythm** → oscillation freq/coherence/velocity
- **Center** → domain stability/size/depolarization
- **Aperture** → GJ permeability/dilation/timing

**Includes:** Perturbation agents with literature-grounded effect sizes

---

### 4. sandbox_plan_minimal.yaml
**Purpose:** Pre-filled single-factor dose-response plan

**Arms:**
- Control
- Factor-Low (0.5× effect)
- Factor-Mid (1.0× effect)
- Factor-High (1.5× effect)

**Customization:** Change `kit`, `agent`, `dose`, and `effect_scaling` for your factor

---

### 5. sandbox_plan_synergy.yaml
**Purpose:** Pre-filled 2×2 synergy test plan

**Arms:**
- Control
- FactorA-High
- FactorB-High
- Combo (both)

**Includes:** Bliss independence and HSA synergy analysis

**Requires:** Prior validation of both factors individually

---

### 6. prereg_template.md
**Purpose:** Complete pre-registration template for OSF/AsPredicted

**Sections:**
- Abstract, background, rationale
- Hypotheses (primary + secondary)
- Study design (arms, sample size, randomization)
- Outcomes (primary + early biomarkers)
- Statistical analysis plan
- Stopping rules & decision gates
- Timeline & budget

---

## Workflow

### Phase 1: Create Experiment
```bash
python pipelines/new_experiment.py \
    --topic "Does gap junction coupling affect planarian regeneration?" \
    --id APERTURE_REGEN \
    --factor aperture
```

### Phase 2: Run S4 Convergence
```bash
python scripts/bioelectric_chambered.py --turns 100 --topic "..."
```

### Phase 3: Extract S4 Priors
```bash
python sandbox/cli/extract_s4_states.py \
    --session BIOELECTRIC_CHAMBERED_20251001... \
    --output sandbox/states
```

### Phase 4: Run Simulation
```bash
python sandbox/cli/run_plan.py experiments/APERTURE_REGEN/plan.yaml
```

### Phase 5: Generate Reports
```bash
python sandbox/cli/analyze_run.py sandbox/runs/outputs/RUN_... \
    --output experiments/APERTURE_REGEN/reports
```

---

## OR: Run Full Pipeline (One Command)

```bash
python pipelines/run_full_pipeline.py \
    --topic "Does gap junction coupling affect regeneration?" \
    --id APERTURE_REGEN \
    --factor aperture \
    --turns 100
```

This orchestrates all 5 phases automatically.

---

## Customization

### For New Organisms
1. Add organism to `variables_template.yaml` with:
   - Typical readout ranges
   - Relevant perturbation agents
   - Timepoints for developmental stages

2. Create organism-specific plan template in `templates/`

### For New Factors
1. Add factor to `variables_template.yaml`:
   - Simulator parameter mapping
   - Perturbation agents with doses
   - Effect deltas (mean ± std)

2. Update `new_experiment.py` with factor defaults

### For New Analysis Methods
1. Add analysis spec to plan template
2. Implement in `sandbox/cli/analyze_run.py`
3. Document in experiment README

---

## Placeholders Reference

Common placeholders used in templates:

| Placeholder | Description | Example |
|------------|-------------|---------|
| `{EXP_ID}` | Experiment slug | `APERTURE_REGEN` |
| `{TOPIC}` | Research question | `"Does GJ coupling..."` |
| `{ORGANISM}` | Species | `planaria` |
| `{FACTOR_NAME}` | Factor being tested | `Aperture` |
| `{AGENT}` | Perturbation agent | `carbenoxolone` |
| `{DOSE_HIGH}` | High dose | `200µM` |
| `{SESSION_ID}` | S4 session | `BIOELECTRIC_CHAMBERED_...` |
| `{RUN_ID}` | Simulation run | `RUN_20251001_...` |

See `pipelines/new_experiment.py` for complete list.

---

## Best Practices

1. **Always start with minimal single-factor plan** before synergy
2. **Run S4 convergence with high context policy** for publication
3. **Use ≥300 Monte Carlo runs** for wet-lab validation
4. **Pre-register before wet-lab execution** (OSF or AsPredicted)
5. **Archive all scrolls and priors** for reproducibility

---

## Support Files

### Checklists
- `checklists/experiment_readiness.md` — Pre-flight checklist
- `checklists/s4_to_sim_bridge.md` — Prior extraction validation

### Config
- `config/models.yaml` — Mirror definitions
- `config/context_policy.yaml` — Execution strategies
- `config/run_limits.yaml` — Safety guardrails

---

**†⟡∞ IRIS Templates v1.0**
