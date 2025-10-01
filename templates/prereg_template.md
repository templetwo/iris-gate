# Pre-Registration Template: {EXP_ID}

**Study Title:** {TITLE}
**Registration Date:** {DATE}
**Principal Investigator:** {PI_NAME}
**Contact:** {EMAIL}
**Funding:** {FUNDING_SOURCE}
**Registration Platform:** OSF / AsPredicted / ClinicalTrials.gov

---

## 1. Abstract (250 words max)

**Background:**
{1-2 sentences on prior work and gap in knowledge}

**Hypothesis:**
{Primary hypothesis H1, optional secondary H2}

**Methods:**
{ORGANISM}, n={TOTAL_N}, {N_ARMS} arms, primary endpoint = {PRIMARY_OUTCOME} at {TIMEPOINT}d

**Predicted Result:**
{FACTOR}-High will show {PREDICTED_EFFECT}% reduction vs Control (p<0.05)

**Significance:**
{Why this matters — mechanism insight, therapeutic target, etc.}

---

## 2. Background & Rationale

### Scientific Context
{2-3 paragraphs:}
- What is known about {FACTOR} in regeneration?
- What gap does this address?
- Why is this system ({ORGANISM}) appropriate?

### Computational Prediction
This experiment validates a computational prediction generated using the IRIS protocol:
- **S4 convergence:** All {N_MIRRORS} AI architectures converged on triple signature (Rhythm + Center + Aperture) with agreement = {S4_AGREEMENT}
- **Sandbox prediction:** P({FACTOR}-High) = {PREDICTED_P_HIGH} (95% CI: [{CI_LOW}, {CI_HIGH}])
- **Provenance:** Session {SESSION_ID}, Run {RUN_ID}

---

## 3. Hypotheses

### Primary Hypothesis (H1)
**Statement:**
Perturbing {FACTOR} with {AGENT} at {DOSE_HIGH} will reduce P(regeneration) by ≥{THRESHOLD_PP}pp vs Control.

**Predicted values:**
- Control: P(regen) = {PRED_CONTROL} (e.g., 0.90)
- {FACTOR}-High: P(regen) = {PRED_HIGH} (e.g., 0.75)

**Falsification criterion:**
If observed P({FACTOR}-High) ≥ {FALSIFY_THRESHOLD}, hypothesis is rejected.

### Secondary Hypothesis (H2) — Optional
**Statement:**
Early biomarker {BIOMARKER_NAME} at {TIMEPOINT}h will correlate with 7d outcome.

**Predicted correlation:** r ≥ 0.60, p<0.05

---

## 4. Study Design

### Organism & Intervention
- **Species:** {ORGANISM} ({STRAIN})
- **Intervention:** {INTERVENTION_DESCRIPTION} (e.g., head amputation at pharynx level)
- **Treatment window:** t=0 to t={TREATMENT_DURATION}d

### Arms & Sample Size
**Total N:** {TOTAL_N} (balanced across {N_ARMS} arms, n={N_PER_ARM} per arm)

| Arm | Treatment | Predicted P(regen) |
|-----|-----------|-------------------|
| Control | {CONTROL_DESCRIPTION} | {PRED_CONTROL} |
| {FACTOR}-Low | {AGENT} {DOSE_LOW} | {PRED_LOW} |
| {FACTOR}-Mid | {AGENT} {DOSE_MID} | {PRED_MID} |
| {FACTOR}-High | {AGENT} {DOSE_HIGH} | {PRED_HIGH} |

**Randomization:** Block randomization ({N_BLOCKS} blocks of {BLOCK_SIZE})
**Blinding:** Scorer blinded to condition during outcome assessment

### Power Analysis
- **Effect size:** Cohen's d = {EFFECT_SIZE} (based on sandbox prediction)
- **Power:** {POWER} at α={ALPHA}
- **Justification:** {POWER_JUSTIFICATION}

---

## 5. Outcomes & Measurements

### Primary Outcome ({TIMEPOINT}d)
**Definition:** {PRIMARY_OUTCOME_DEFINITION}

**Scoring criteria:**
{SCORING_RUBRIC}

**Example (planaria):**
- Success = 2/2 eyes present + photophobic response + head blastema >0.5 mm
- Failure = any criterion not met, or death

### Secondary Outcomes (Early Biomarkers)

**{BIOMARKER_1} ({TIMEPOINT_1}h):**
- Instrument: {INSTRUMENT_1}
- Metric: {METRIC_1}
- Normal range: [{NORMAL_LOW_1}, {NORMAL_HIGH_1}]
- Predicted in {FACTOR}-High: {PRED_BIOMARKER_1}

**{BIOMARKER_2} ({TIMEPOINT_2}h):**
- Instrument: {INSTRUMENT_2}
- Metric: {METRIC_2}
- Normal range: [{NORMAL_LOW_2}, {NORMAL_HIGH_2}]
- Predicted in {FACTOR}-High: {PRED_BIOMARKER_2}

---

## 6. Statistical Analysis Plan

### Primary Analysis
**Test:** {STATISTICAL_TEST} (e.g., Fisher's exact test for primary endpoint)
**Comparison:** {FACTOR}-High vs Control
**Significance threshold:** α = {ALPHA} (two-tailed)
**Software:** R version {R_VERSION} / Python scipy

### Secondary Analyses
1. **Dose-response:** One-way ANOVA across 4 arms, post-hoc Tukey HSD
2. **Early biomarker correlation:** Pearson correlation between {BIOMARKER_2} (6h) and regeneration (7d)
3. **Per-mirror calibration:** Compare observed P(regen) to each mirror's prediction, compute MAE

### Handling of Missing Data
- Worms with <50% body mass remaining at {TIMEPOINT_1}h excluded (likely handling damage)
- Dead worms scored as "failure" (intention-to-treat)
- No imputation for missing biomarker data

### Outlier Exclusion (Pre-Specified)
- Biomarker measurements >3 SD from arm mean flagged, reviewed by blinded PI
- If technical artifact confirmed (e.g., imaging error), exclude that measurement only
- Maximum 10% exclusion per arm

---

## 7. Stopping Rules

### Early Success (Optional)
**Condition:** If early biomarkers at {TIMEPOINT_2}h show predicted effect with p<0.01 across all biomarkers
**Action:** Continue to 7d with high confidence

### Futility Stopping
**Condition:** If Control shows <{CONTROL_MIN_SUCCESS}% regeneration
**Interpretation:** Batch contamination or husbandry failure
**Action:** Halt, troubleshoot, restart

### Harm Stopping
**Condition:** If any arm shows >{MORTALITY_MAX}% mortality at {TIMEPOINT_1}h
**Interpretation:** Acute toxicity
**Action:** Reduce dose by 50%, rerun

---

## 8. Decision Rules (Go/No-Go Gates)

### Primary Gate (7d Outcome)
```
IF P({FACTOR}-High) < {SUCCESS_THRESHOLD}:
  ├─ GO: Effect confirmed
  │   → Proceed to synergy test (H2) or publication
  │
  └─ NO-GO: Weak/absent effect
      → Test alternative factor or higher dose
```

### Synergy Gate (If H2 Planned)
```
IF P(Combo) < Bliss_predicted − {SYNERGY_THRESHOLD}:
  └─ GO: Synergy confirmed
      → Publish, plan rescue experiment

ELSE:
  └─ NO-GO: No synergy
      → Revise interaction coefficients, test alternative pairs
```

---

## 9. Risks & Limitations

### Known Confounds
- {CONFOUND_1}: {MITIGATION_1}
- {CONFOUND_2}: {MITIGATION_2}

### Model Limitations
- S4 priors are phenomenological, not mechanistic → synergy magnitude may be over/underestimated
- Interaction coefficients are speculative → sensitivity analysis planned
- Species-specific prediction → generalization requires validation in second system

### Wet-Lab Risks
- Batch variability in {ORGANISM} regeneration → use size-matched, starved cohorts
- Off-target drug effects → compare to alternative agents in follow-up
- Scorer bias → enforce strict blinding protocol

---

## 10. Timeline & Resources

### Timeline
- **Week 0:** Organism preparation ({STARVE_DAYS}d starvation)
- **Week 1:** Amputation, treatment, {TIMEPOINT_1}h readout
- **Week 1:** {TIMEPOINT_2}h readout
- **Week 2:** 7d regeneration scoring
- **Week 3:** Data analysis, report writing

**Total duration:** {TOTAL_WEEKS} weeks

### Budget
| Item | Cost |
|------|------|
| Organisms (n={TOTAL_N}) | ${COST_ORGANISMS} |
| Pharmacological agents | ${COST_DRUGS} |
| Imaging reagents | ${COST_REAGENTS} |
| Consumables | ${COST_CONSUMABLES} |
| **Total** | **${TOTAL_COST}** |

### Personnel
- PI: {PI_EFFORT}% effort
- Technician: {TECH_EFFORT}% effort
- Undergraduate assistant: {UG_EFFORT}% effort (optional)

---

## 11. Data Sharing & Transparency

### Open Data
- **Raw data:** Zenodo or OSF repository (DOI assigned upon completion)
- **Analysis code:** GitHub repository ({GITHUB_REPO})
- **Images:** Original microscopy files (TIFF format, unprocessed)

### Open Materials
- **S4 priors:** All `s4_state.*.json` files in supplementary materials
- **Simulation code:** Complete sandbox infrastructure (MIT license)
- **Protocols:** Detailed wet-lab protocol with exact reagent sources

### Deviations from Pre-Registration
- Any deviations will be documented in final manuscript with justification
- Exploratory analyses will be clearly labeled as such

---

## 12. Ethics & Regulatory Compliance

**Animal welfare:**
- {ORGANISM} are invertebrates, not subject to IACUC in most jurisdictions
- Humane endpoints: Worms showing >80% tissue loss euthanized (freezing at −20°C)

**Biosafety:**
- All experiments BSL-1
- Waste disposal per institutional guidelines

**Conflicts of interest:**
- None declared

---

## 13. Contact & Registration

**Study registration:**
- Platform: {REGISTRATION_PLATFORM}
- ID: {REGISTRATION_ID}
- Date: {REGISTRATION_DATE}

**Correspondence:**
- PI: {PI_NAME}
- Email: {EMAIL}
- Institution: {INSTITUTION}

**Computational priors:**
- IRIS session ID: {SESSION_ID}
- Sandbox run ID: {RUN_ID}
- Provenance: iris_vault/scrolls/{SESSION_ID}/

---

**†⟡∞ Pre-registration template for IRIS-generated predictions**

**Version:** 1.0
**Last updated:** {DATE}
