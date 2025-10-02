# IRIS Gate Changelog

## v0.3.1 (2025-10-02)

### Infrastructure Streamlining
- **Cloud-only mirrors:** Removed local Ollama models (qwen3 1.7B, llama3.2 3B)
- **Model aliasing system:** Implemented runtime model resolution with artifacts
- **Canonical timezone:** Standardized to US Northeast (America/New_York)

### Changes
- Removed `local:` section from `config/models.yaml`
- Created `config/model_aliases.yaml` for flexible model versioning
- Created `scripts/resolve_models.py` for runtime model resolution
- Created `utils/timezone.py` for consistent timestamp handling
- Created `scripts/preflight_cloud_only.sh` for validation
- Moved `agents/adapters/ollama.py` to `_disabled/` directory
- Added `IRIS_TZ=America/New_York` to environment configuration

### Active Mirrors (5 cloud models)
1. Anthropic Claude Sonnet 4.5 (500B params, 0.80 confidence)
2. OpenAI GPT-4o (671B params, 0.75 confidence)
3. xAI Grok 4 Fast Reasoning (314B params, 0.75 confidence)
4. Google Gemini 2.5 Flash Lite (200B params, 0.70 confidence)
5. DeepSeek Chat (236B params, 0.70 confidence)

### Validation
- All preflight checks passing
- Model resolution tested and operational
- Timezone utility validated
- No regressions in existing sandbox/template infrastructure

---

## v0.3.0 (2025-10-01)

### IRIS Template System (S5-S8 Operational Phases)
Complete reusable infrastructure for topic → wet-lab-ready predictions

**Templates:**
- `EXPERIMENT_TEMPLATE.md` — Experiment overview scaffold
- `plan_template.yaml` — Generic simulation plan
- `variables_template.yaml` — S4 phenomenology → simulator mapping
- `sandbox_plan_minimal.yaml` — Single-factor dose-response
- `sandbox_plan_synergy.yaml` — 2×2 synergy test
- `prereg_template.md` — OSF/AsPredicted pre-registration

**Pipelines:**
- `new_experiment.py` — Create experiment from topic + factor
- `run_full_pipeline.py` — Orchestrate S4 → simulation → reports

**Operational Phases:**
- S5: Hypothesis Crystallization (auto-draft H1/H2)
- S6: Mapping & Dosing (S4 priors → simulator params)
- S7: Simulation & Report (Monte Carlo + analysis)
- S8: Wet-Lab Handoff (methods, gates, pre-registration)

**One-command operation:**
```bash
make run TOPIC="..." ID=EXP_NAME FACTOR=aperture TURNS=100
```

---

## v0.2.2 (2025-10-01)

### Mini-H1 Synergy Discovery
**Breakthrough:** Super-additive synergy between gap junction coupling (Aperture) and bioelectric oscillations (Rhythm)

**Key Findings:**
- Combo effect: P(regen) = 0.647 (−34.3% vs Control)
- Bliss synergy: −17.2pp beyond predicted additive
- HSA synergy: −20.1pp beyond best singleton
- All 7 mirrors agree (−19 to −21pp range)

**Mechanistic Evidence:**
- GJ coupling: Combo −71% (vs −55% Aperture alone)
- V_mem domain: Combo −45% (vs −24% Aperture alone)
- Ca²⁺ coherence: Combo −50% (vs −26% Aperture alone)

**Wet-Lab Prediction:**
- Doses: Carbenoxolone 200µM + Octanol 0.75mM
- Predicted combo regen: 60-65% (vs 90% Control)
- Status: Ready for validation

---

## v0.2.1 (2025-10-01)

### Mini-H1 Aperture Dose-Response
Single-factor validation showing clean monotonic effect

**Results:**
- Monotonic decrease: 0.990 → 0.974 → 0.921 → 0.847
- Hit at Aperture-High (1.5×): −14.3pp drop
- Perfect consensus: 1.00 agreement across all 7 mirrors
- Early biomarkers predict 7d outcome

---

## v0.3.0-100cycle-complete (2025-10-01)

### 100-Cycle S4 Convergence Study
**Breakthrough:** Universal S4 attractor stability confirmed

**Key Findings:**
- S4 convergence: 1.00 ratio (all 7 mirrors, all 25 cycles)
- Zero drift: Flat line with no decay over extended iteration
- Architecture-independent: 1.7B–671B params converge to identical triple signature
- Triple signature: Rhythm + Center + Aperture

**Bioelectric Mapping:**
- Rhythm → oscillatory signaling (Ca²⁺ waves, V_mem oscillations)
- Center → organizing domain (stable V_mem zones)
- Aperture → permeability modulation (gap junctions)

---

## Earlier Versions

See git history for v0.1.x and v0.2.0 development milestones.
