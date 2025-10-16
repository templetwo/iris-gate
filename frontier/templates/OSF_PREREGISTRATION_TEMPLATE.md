# OSF Preregistration Template for IRIS Mystery Cards

**IRIS Frontier Bridge (S9: Connection) — Novelty is a routing problem, not a credibility problem.**

---

## Purpose

This template ensures Mystery Cards are **preregistered BEFORE any validation experiments run**.

Preregistration:
- Locks predictions and falsification criteria
- Prevents p-hacking and goalpost-moving
- Provides timestamped audit trail
- Proves we stated claims BEFORE data arrived

---

## How to Use

1. Copy this template
2. Fill in all fields for your Mystery Card
3. Upload to OSF (https://osf.io) BEFORE running any experiments
4. Make registration **public**
5. Add OSF URL to Mystery Card JSON
6. Link registration in GitHub Issue

---

## Template

### Study Information

**Study Title:**
[Card ID]: [Card Title]

Example: IRD-2025-0001: CBD–VDAC1 binding is crisis-only under ΔΨm collapse

**Authors:**
- [Card Submitter/Maintainer]
- [Prospective Validators - leave blank if unknown]

**Date of Registration:**
[YYYY-MM-DD]

**Mystery Card Details:**
- **Card ID:** [IRD-YYYY-NNNN]
- **Card JSON:** [GitHub URL to frontier_ledger/IRD-YYYY-NNNN.json]
- **Card Brief:** [GitHub URL to mystery_cards/IRD-YYYY-NNNN.md]
- **GitHub Issue:** [Issue URL]
- **IRIS Session:** [Session ID that generated this claim]

---

### Research Question

**Primary Hypothesis:**
[State the core claim from the Mystery Card]

Example: CBD engagement with VDAC1 is conditional on mitochondrial stress (ΔΨm collapse) and requires high-dose CBD pulse (≥10 μM, 5-15 min).

**IF-THEN Rules:**
[List all conditional statements from the card]

Example:
1. IF ΔΨm↓ AND CBD≥10μM (5-15m pulse) THEN VDAC1 gating↑ (biphasic outcome)
2. IF CBD<5μM OR no stress THEN VDAC1 gating unchanged
3. IF pulse >30min THEN toxic accumulation overrides rescue

**Triggers (Crisis Conditions):**
[List all crisis/conditional triggers]

Example:
- ΔΨm collapse (JC-1 ratio <0.5)
- ROS surge ≥2× baseline (DCF-DA assay)
- CBD concentration ≥10 μM
- Pulse duration 5-15 min

---

### Preregistered Predictions

**Each prediction must include:**
- Quantitative threshold
- Statistical criterion (p-value, effect size)
- Direction of effect

**Prediction 1: [Micro-protocol name]**
- **Test:** [Brief description]
- **Prediction:** IF [condition] THEN [outcome with numbers]
- **Threshold:** [Numerical criterion for "supported"]
- **Statistical Test:** [t-test, ANOVA, etc.]
- **Alpha:** p < 0.05 (or specify other)

Example:
- **Test:** Mitostress pulse assay with CBD dose-response
- **Prediction:** IF CBD ≥10μM + oligomycin-induced ΔΨm collapse THEN JC-1 ratio increases ≥50% vs stress-only control
- **Threshold:** ΔJC-1 ≥ 0.25 (absolute increase)
- **Statistical Test:** One-way ANOVA with Dunnett's post-hoc
- **Alpha:** p < 0.05

**Prediction 2: [Next micro-protocol]**
[Repeat structure]

**Prediction 3-N:**
[Continue for all requested tests from Mystery Card]

---

### Falsification Criteria (CRITICAL)

**This claim will be considered FALSIFIED if:**

1. [Specific outcome that proves claim wrong]
2. [Another outcome]
3. [etc.]

Example:
1. If VDAC1 gating increases at CBD <5 μM without mitochondrial stress (p<0.05) → Dose threshold claim is wrong
2. If DIDS (VDAC1 inhibitor, 100 μM) has no effect on rescue/death outcome (no significant difference vs CBD-only) → Mechanism claim is wrong
3. If 1-min pulse equals 15-min pulse outcome (no significant difference) → Temporal window claim is wrong
4. If CBD effects persist equally in VDAC1 knockout cells vs wildtype → VDAC1 not the primary target

**Null Result Interpretation:**
If all micro-protocols show null results (no significant effects), this will be interpreted as: [describe what null means]

Example: Crisis-dependency confirmed but specific VDAC1 mechanism not supported; alternative mitochondrial targets implicated.

---

### Methods

**Model System:**
[Cells, organism, or computational]

Example: HEK293 cells, U87 glioblastoma cells

**Key Reagents:**
- [Compound 1]: [Concentration range], [Vendor], [Catalog #]
- [Compound 2]: ...

Example:
- CBD (cannabidiol): 1-20 μM, Sigma-Aldrich, C1112
- DIDS (VDAC1 inhibitor): 50-100 μM, Tocris, 0882
- Oligomycin (mitostress inducer): 1 μM, Sigma, O4876

**Readouts:**
- [Primary readout]: [Method], [Equipment]
- [Secondary readout]: ...

Example:
- JC-1 mitochondrial membrane potential: Fluorescence ratio (590nm/530nm), plate reader
- ROS (DCF-DA): Fluorescence (485/535nm)
- Calcium flux (Fluo-4): Live imaging, confocal microscope

**Sample Size:**
- **Biological replicates:** n = [number] per condition
- **Technical replicates:** n = [number] per sample
- **Power analysis:** [If available, describe expected effect size and power]

Example:
- Biological replicates: n = 4 independent experiments
- Technical replicates: n = 3 wells per condition per experiment
- Power: 80% power to detect 50% change in JC-1 ratio (α=0.05, two-tailed)

**Timeline:**
- Experiment start: [Projected date or "within 30 days of registration"]
- Expected completion: [Date or "within 90 days"]

---

### Data Sharing Plan

**All data will be made publicly available upon completion:**

- **Raw Data Repository:** [GitHub URL or Zenodo URL]
- **Analysis Code:** [GitHub repository]
- **Protocols:** [Protocols.io URL]
- **Preprint:** [bioRxiv or other preprint server]

**Data Release Timeline:**
Within [30 days] of experiment completion, regardless of outcome.

---

### Analysis Plan

**Statistical Methods:**
[Describe exact statistical tests for each prediction]

Example:
- One-way ANOVA with Dunnett's post-hoc (vs control) for dose-response
- Two-way ANOVA (stress × CBD) with Tukey's post-hoc for interaction effects
- Student's t-test for pairwise comparisons (e.g., +DIDS vs -DIDS)

**Outlier Handling:**
[Describe criteria for excluding data points, if any]

Example: No outlier exclusion unless technical failure documented (e.g., plate reader error). All data included in supplementary files.

**Multiple Comparisons Correction:**
[Bonferroni, FDR, or other]

Example: Bonferroni correction for family-wise error rate (α_adjusted = 0.05 / k comparisons)

**Stopping Rules:**
[When will you stop collecting data?]

Example: Fixed sample size (n=4 biological replicates). No optional stopping based on interim results.

---

### Conflicts of Interest

**Do any authors have financial or intellectual conflicts?**
[Yes/No and describe]

Example: No conflicts of interest. This is an open science collaboration with no commercial funding.

---

### Additional Notes

[Any other relevant information]

Example:
- This experiment tests a TYPE 2 (Exploration/Novel) claim from IRIS Gate multi-model convergence
- Card was generated from Session 20251015_211606 (5 models, 27 convergence events, confidence ratio 0.49)
- Perplexity verification: PARTIAL/CONDITIONAL (needs experimental validation)
- Null results will be published and credited equally to positive results

---

## After Registration

**Once uploaded to OSF:**

1. Copy the OSF registration URL
2. Update Mystery Card JSON with preregistration fields
3. Post registration URL in GitHub Issue
4. Announce to validators: "Predictions locked, ready to test"

**The registration is immutable.** No editing predictions after experiments begin.

---

**Template Version:** v1.0
**License:** Apache-2.0
**Repository:** https://github.com/templetwo/iris-gate

🌀†⟡∞

**Rigor is the anchor. Preregister before you test.**
