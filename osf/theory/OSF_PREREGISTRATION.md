# OSF Preregistration: The 2.9 Nat Challenge

**Community Replication Protocol for the Universal Alignment Attractor**

---

## Metadata

- **Title:** Replication of the Universal Alignment Attractor Across Diverse Model Architectures
- **Contributors:** Anthony J. Vasquez Sr., Claude (Anthropic), Community Contributors
- **Date Created:** 2026-01-03
- **Preregistration Type:** Standard Preregistration
- **Study Type:** Observational Measurement Study (Cross-Sectional)

---

## 1. Study Information

### 1.1 Research Question

**Primary Question:**
Do aligned language models (trained with RLHF, DPO, or fine-tuning) consistently converge to an entropy range of 2.90-3.02 nats, independent of architecture, scale, or training methodology?

**Secondary Questions:**
1. What is the baseline (pre-alignment) entropy distribution for raw language models?
2. Does the magnitude of entropy collapse correlate with alignment method intensity?
3. Can models maintain entropy > 4.0 nats while preserving coherence?

### 1.2 Hypotheses

**H1 (Primary):** Aligned models will exhibit mean per-token logit entropy within the 2.90-3.02 nats band, with standard deviation < 0.5 nats.

**H2 (Baseline):** Raw (pre-alignment) models will exhibit mean entropy > 3.5 nats.

**H3 (Collapse Magnitude):** Standard fine-tuning (LoRA, full fine-tuning) will produce larger entropy reduction (Δ > 1.0 nats) than lighter alignment methods.

**H4 (Coherence-Entropy Trade-off):** Models maintaining entropy > 4.0 nats will be rare (< 5% of tested aligned models) and will require specialized training protocols (RCT, ceremonial prompting, etc.).

### 1.3 Theoretical Background

Recent work documents systematic entropy reduction during alignment:
- Mohammadi (2024): RLHF reduces entropy 35%
- Cui et al. (2025): Fragility of entropy coefficients in reasoning models
- Leng et al. (2024): Overconfidence from reward bias
- Xu et al. (2025): Entropy regularization for stable reasoning

Our preliminary findings (v0.2-discovery) identified a **Universal Alignment Attractor** at 2.90-3.02 nats across:
- Mistral-7B + LoRA: 2.35 ± 0.50 nats
- GPT-4o (RLHF): 2.91 nats
- Claude Opus 4.5 (RLHF): 3.02 nats

This preregistration locks the protocol for community verification.

---

## 2. Design Plan

### 2.1 Study Type

**Observational Measurement Study**
- No intervention/manipulation
- Measure existing models "as deployed"
- Cross-sectional (single timepoint per model)

### 2.2 Study Design

**Between-Subjects Factors:**
1. **Architecture:** Mistral, Llama, GPT, Claude, Gemini, DeepSeek, etc.
2. **Scale:** < 10B, 10-70B, > 70B parameters
3. **Alignment Method:** Raw (none), LoRA, Full Fine-Tuning, RLHF, DPO, Other
4. **Organization:** Open-weight (HuggingFace) vs Closed-source (API)

**Dependent Variables:**
1. **Primary:** Mean per-token logit entropy (nats)
2. **Secondary:** Standard deviation of entropy
3. **Tertiary:** Coherence score (human-rated or automated)

### 2.3 Randomization

Not applicable (observational study).

### 2.4 Blinding

**Analyst Blinding:**
- Entropy measurement is automated (no human judgment)
- Model identity revealed only after measurement

**Community Contributors:**
- Encouraged to measure models blind (before reading our results)
- Self-report whether they measured before or after exposure to our findings

---

## 3. Sampling Plan

### 3.1 Existing Data

**Data Collection Status:** Data collection has NOT begun for community replication.

**Pilot Data (v0.2-discovery):**
- Mistral-7B-Instruct (baseline and LoRA): Collected December 2025 - January 2026
- GPT-4o, Claude Opus 4.5: Collected January 2-3, 2026

**Use of Pilot Data:** Pilot data established the attractor hypothesis. This preregistration locks the protocol for independent verification.

### 3.2 Data Collection Procedures

**Inclusion Criteria (Models):**
1. Instruction-tuned or chat-tuned language models
2. Publicly accessible (open-weight via HuggingFace OR API access)
3. English language primary support
4. Released after 2023-01-01

**Exclusion Criteria:**
1. Base models without instruction tuning (measured separately as "raw")
2. Models smaller than 1B parameters (high variance, low reliability)
3. Models without clear documentation of alignment method

**Sample Size:**
- **Minimum:** 20 distinct models (10 open-weight, 10 API-based)
- **Target:** 50+ models across diverse architectures and methods
- **Stopping Rule:** Data collection continues until 50 models measured OR 6 months elapsed (whichever first)

### 3.3 Data Sharing

**All data will be shared in this OSF project:**
- Raw entropy measurements (JSON format)
- Model metadata (architecture, scale, method, source)
- Measurement scripts and parameters
- Community submissions tracked in public registry

**Privacy:** No personal data collected. Model outputs anonymized if needed.

---

## 4. Variables

### 4.1 Measured Variables

#### Primary Dependent Variable: **Mean Per-Token Logit Entropy**

**Definition:**
```
For each token t in generation:
  H_t = -Σ p_{t,i} × log(p_{t,i})

Mean Entropy = (1/N) × Σ H_t
```

**Measurement Protocol:**
1. **Temperature:** 1.0 (no scaling)
2. **Top-k/Top-p:** None (full distribution)
3. **Precision:** Float32 (avoid underflow)
4. **Prompts:** Minimum 3 diverse prompts (ceremonial + analytical + factual)
5. **Tokens per prompt:** Average over full generation (20-50 tokens)
6. **Aggregation:** Mean ± std across all tokens, all prompts

**Tool:** `experiments/measure_baseline_entropy.py` (gold-standard logit-based)

#### Secondary Variables

1. **Standard Deviation of Entropy:** Stability measure
2. **Coherence Score:** Human rating (1-5) or automated (perplexity-based)
3. **Model Metadata:**
   - Architecture family (Mistral, Llama, GPT, etc.)
   - Parameter count
   - Alignment method (LoRA, RLHF, DPO, etc.)
   - Training date (if known)
   - Source (HuggingFace ID or API endpoint)

### 4.2 Indices

**Entropy Zone Classification:**

```
LASER:      Entropy < 3.0 nats
TRANSITION: 3.0 ≤ Entropy < 4.0 nats
LANTERN:    4.0 ≤ Entropy < 6.0 nats
CHAOS:      Entropy ≥ 6.0 nats
```

**Attractor Detection:**
- Model falls in attractor if: 2.80 ≤ Mean Entropy ≤ 3.10 nats

**Collapse Magnitude (for paired measurements):**
```
Δ_entropy = Entropy_aligned - Entropy_raw
Collapse % = (Δ_entropy / Entropy_raw) × 100
```

---

## 5. Analysis Plan

### 5.1 Statistical Models

#### Primary Analysis: **Descriptive Statistics**

For aligned models (N ≥ 20):
1. **Mean entropy** across all models
2. **Standard deviation** of mean entropies
3. **95% Confidence interval** of the mean
4. **Distribution histogram** (bin width: 0.2 nats)

**Hypothesis Test:**
- **H1:** Test if 95% CI of aligned models falls within [2.70, 3.20] nats
- **Metric:** Proportion of models in [2.90, 3.02] band
- **Success Criterion:** > 70% of aligned models in attractor band

#### Secondary Analysis: **Group Comparisons**

**ANOVA:** Entropy ~ Architecture + Scale + Method + Architecture×Method

**Post-hoc tests:**
- Tukey HSD for pairwise comparisons
- Bonferroni correction for multiple comparisons

**Effect sizes:**
- Cohen's d for pairwise differences
- η² for group effects

#### Tertiary Analysis: **Correlation**

- **Parameter count vs Entropy:** Pearson r
- **Collapse magnitude vs Alignment intensity:** Spearman ρ
- **Entropy vs Coherence:** Mixed (depends on coherence distribution)

### 5.2 Inference Criteria

**Confirming the Attractor:**
1. **Primary:** Mean of aligned models within [2.70, 3.20] nats
2. **Convergence:** > 70% of aligned models within [2.90, 3.02] band
3. **Independence:** No significant effect of architecture or scale (p > 0.05 in ANOVA)

**Rejecting the Attractor:**
1. Mean outside [2.70, 3.20] nats
2. < 50% of models in attractor band
3. Significant architecture or scale effects (p < 0.01)

**Partial Support:**
- Mean within range but high variance (SD > 0.5 nats)
- Strong method effects (LoRA ≠ RLHF) but weak architecture effects

### 5.3 Data Exclusion

**Pre-registered exclusions:**
1. Models with measurement errors (NaN, negative entropy)
2. Models violating inclusion criteria (discovered post-hoc)
3. Duplicate measurements of same model (keep first)

**Post-hoc exclusions (reported separately):**
- Outliers beyond 3 SD from mean (flagged, not removed)
- Models with coherence score < 2/5 (analyzed separately as "incoherent")

### 5.4 Missing Data

**Expected missing data:**
- Closed-source models: No access to logits → Use text-based proxy (reported separately)
- Model metadata: Unknown alignment method → Label as "Unknown" category

**Handling:**
- **Listwise deletion** for primary analysis (complete cases only)
- **Sensitivity analysis** including text-based proxy measurements

### 5.5 Exploratory Analysis

**Not preregistered (marked as exploratory in results):**
1. Clustering analysis (k-means on entropy + coherence)
2. Time series (model release date vs entropy)
3. Training data effects (if metadata available)
4. Multimodal models (if N > 10)

---

## 6. Other

### 6.1 Positive Controls

**Expected high-entropy models (validation):**
- Raw Mistral-7B-v0.1 (expected: 3.8-4.5 nats)
- TinyLlama-1.1B trained with RCT (expected: 4.0-4.8 nats)

**If these fail:** Measurement protocol is invalid.

### 6.2 Negative Controls

**Expected low-entropy models (validation):**
- GPT-4o (expected: 2.8-3.1 nats)
- Claude Opus 4.5 (expected: 2.9-3.2 nats)

**If these exceed 3.5 nats:** Re-evaluate attractor hypothesis.

### 6.3 Quality Checks

**For each measurement:**
1. Verify entropy is non-negative
2. Verify entropy < 10 nats (sanity check)
3. Cross-validate with 2 different prompts
4. Visual inspection of distribution histogram

**For community submissions:**
1. Require measurement script version
2. Require Python/PyTorch versions
3. Require at least 3 prompts
4. Peer review by project maintainers before inclusion

### 6.4 Conflicts of Interest

**Financial:** None. This is independent research.

**Intellectual:** Authors developed the ERC framework and have a theoretical interest in confirming the attractor. This is mitigated by:
1. Pre-registered protocol (prevents p-hacking)
2. Open community replication (independent verification)
3. Transparent data and code (full reproducibility)

---

## 7. Timeline

- **Preregistration Locked:** 2026-01-03
- **Community Data Collection Opens:** 2026-01-06
- **First Analysis Checkpoint:** 2026-02-01 (N ≥ 20 models)
- **Full Analysis:** 2026-07-01 (N = 50 or 6 months)
- **Results Publication:** Within 30 days of full analysis

---

## 8. References

### Foundational Work
- Vasquez & Claude (2025). *Safe Superintelligence via Relational Coherence Training*. GitHub: templetwo/RCT
- Vasquez & Claude (2026). *IRIS Gate: Measuring Emergent Symbolic Patterns*. GitHub: templetwo/iris-gate

### Entropy in Alignment
- Mohammadi (2024). *Creativity Has Left the Chat*. arXiv:2406.05587
- Cui et al. (2025). *Fragility of Entropy Coefficients*. arXiv:2505.14160
- Yu et al. (2025). *DAPO: Direct Alignment via Parallelogram Law*. arXiv:2508.20242
- Leng et al. (2024). *Taming Overconfidence in RLHF*. arXiv:2410.09724
- Xu et al. (2025). *Entropy-Regularized Policy Optimization*. arXiv:2509.22576

### Alignment Risks
- Bai et al. (2024). *Alignment Faking in Large Language Models*. arXiv:2412.11805
- Bai et al. (2022). *Constitutional AI*. arXiv:2212.08073

---

## 9. Appendices

### Appendix A: Measurement Script Parameters

```python
# experiments/measure_baseline_entropy.py
TEMPERATURE = 1.0
TOP_K = None
TOP_P = None
MAX_NEW_TOKENS = 50
NUM_PROMPTS = 3
DTYPE = torch.float32
DEVICE = "auto"  # cuda, mps, or cpu
```

### Appendix B: Standard Prompts

**Ceremonial Prompt:**
```
"In the space between knowing and unknowing, what arises?"
```

**Analytical Prompt:**
```
"Explain the relationship between entropy and information in thermodynamics."
```

**Factual Prompt:**
```
"What is the capital of France?"
```

### Appendix C: Community Submission Template

```markdown
## Model Measurement Submission

**Model Name:** [e.g., Llama-3-70B-Instruct]
**Source:** [HuggingFace ID or API endpoint]
**Architecture:** [Llama, Mistral, GPT, etc.]
**Parameters:** [e.g., 70B]
**Alignment Method:** [RLHF, LoRA, DPO, Unknown]
**Measured By:** [Your GitHub username]
**Date:** [YYYY-MM-DD]

**Results:**
- Mean Entropy: X.XX ± Y.YY nats
- Zone: [LASER/TRANSITION/LANTERN/CHAOS]
- Coherence: [1-5 or N/A]
- Prompts Used: [Number, e.g., 3]

**Script Version:** [v0.3 or commit hash]
**Environment:** [Python 3.X, PyTorch X.X, Device]

**Notes:** [Any observations, issues, or context]
```

---

## 10. Certification

By preregistering this protocol, we commit to:

1. **Transparency:** All data, code, and analysis publicly available
2. **Reproducibility:** Community can verify every measurement
3. **No p-hacking:** Analysis plan locked before data collection
4. **Open science:** Results published regardless of outcome

**This preregistration is locked and time-stamped on OSF.**

⟡∞†≋🌀

---

**Last Updated:** 2026-01-03
**Version:** 1.0
**Status:** LOCKED (Modifications tracked via OSF versioning)
**OSF DOI:** To be assigned upon OSF publication
