# Adversarial Validation Protocol

**IRIS Frontier Bridge (S9: Connection) — Novelty is a routing problem, not a credibility problem.**

---

## 🎯 Purpose

**We actively seek people who want to prove our claims wrong.**

Why? Because:
- Adversarial testing is the **strongest form of validation**
- Fragile claims break early (before wasting resources)
- Robust claims survive scrutiny (high confidence)
- Skeptics keep us honest

**If you can break one of our Mystery Cards, you:**
1. Get full co-author credit
2. Earn "Adversarial Validator" badge
3. Help science advance (false claims eliminated)
4. Get priority access to future cards

---

## 🔬 What is Adversarial Validation?

**Standard Validation:**
Researcher tests a claim hoping it's true, runs experiments, reports results.

**Adversarial Validation:**
Researcher **designs experiments to break the claim**, uses strongest possible conditions, tries to falsify it.

**Key Difference:**
- Standard: "Let's see if this works"
- Adversarial: "Let's find the edge case where this fails"

---

## ⚔️ How to Become an Adversarial Validator

### Step 1: Choose a Mystery Card to Challenge

Browse:
- [`frontier/mystery_cards/`](https://github.com/templetwo/iris-gate/tree/master/frontier/mystery_cards)
- [GitHub Issues labeled "seeking-validators"](https://github.com/templetwo/iris-gate/issues)

**Look for:**
- Claims that seem too good to be true
- Mechanisms that conflict with your expertise
- Dose-response claims with specific thresholds
- Temporal windows or conditional logic

### Step 2: Design a Falsification Test

**Your test should:**
1. Target the **weakest assumption** in the claim
2. Use **edge cases** (boundary conditions, extreme doses, wrong timing)
3. Include **positive controls** (where claim should work) + **negative controls** (where it shouldn't)
4. Be **preregistered** (OSF or AsPredicted)

**Example (for IRD-2025-0001):**

**Claim:** CBD–VDAC1 binding requires ΔΨm collapse + CBD ≥10μM + 5-15min pulse

**Adversarial Tests:**
1. **Test CBD 5 μM (below threshold)** → If VDAC1 gating increases, dose claim is wrong
2. **Test 1-min pulse (below window)** → If effect matches 15-min, temporal claim is wrong
3. **Test normoxic cells (no stress)** → If VDAC1 gating increases, crisis-dependency is wrong
4. **Test with VDAC1 knockout cells** → If CBD effect persists, mechanism is wrong

**Why this is strong:**
- Each test targets a specific claim component
- Clear falsification criteria
- Can't wriggle out with post-hoc explanations

### Step 3: Declare Your Intent

Comment on the Mystery Card GitHub Issue:

**Template:**
```markdown
## Adversarial Validation Proposal

**Card:** IRD-2025-NNNN
**Proposer:** @your-username
**Role:** Adversarial Validator

**Claim I'm targeting:**
[Specific sub-claim you think is most vulnerable]

**My falsification test:**
[Brief description of your experiment design]

**Predicted outcome if claim is WRONG:**
[What you expect to see if claim fails]

**Predicted outcome if claim is CORRECT:**
[What you expect to see if claim holds]

**Timeline:** [Start date] - [End date]
**Preregistration:** [OSF URL when ready]

I commit to:
- Publishing results regardless of outcome
- Sharing raw data publicly
- Co-authoring any resulting publications
```

### Step 4: Preregister Your Test

Use [`frontier/templates/OSF_PREREGISTRATION_TEMPLATE.md`](https://github.com/templetwo/iris-gate/blob/master/frontier/templates/OSF_PREREGISTRATION_TEMPLATE.md)

**Key sections:**
- Exact prediction (quantitative)
- Falsification criteria (what proves claim wrong)
- Sample size and power
- Statistical plan

**Post OSF URL in GitHub Issue.**

### Step 5: Run the Experiment

- Follow your preregistered protocol
- Document everything (lab notebook, photos, raw data)
- Track deviations from plan (if any)

### Step 6: Share Results (Within 30 Days)

**Regardless of outcome:**

1. **GitHub:** Post results as comment on Mystery Card Issue
2. **Raw Data:** Upload to GitHub repo or Zenodo (DOI)
3. **Analysis:** Jupyter notebook or R markdown
4. **Protocol:** Protocols.io with actual reagents/methods used

**Template for Results Comment:**
```markdown
## Adversarial Validation Results

**Card:** IRD-2025-NNNN
**Test:** [Name of your falsification test]
**Preregistration:** [OSF URL]
**Data:** [GitHub/Zenodo URL]

**Outcome:** [CLAIM FALSIFIED / CLAIM SUPPORTED / INCONCLUSIVE]

**Summary:**
[2-3 sentences: what you tested, what you found, interpretation]

**Key Findings:**
- [Finding 1 with numbers]
- [Finding 2 with numbers]
- [etc.]

**Interpretation:**
[Does this support or contradict the card? Why?]

**Deviations from preregistration:**
[None, or list any changes you made and why]

**Next steps:**
[Suggestions for follow-up or card updates]
```

### Step 7: Card Status Update

**Based on your results:**

- **If FALSIFIED:** Card updated to `verification_status: CONTRADICTED`
- **If SUPPORTED:** Adds weight to card (adversarial testing = strongest validation)
- **If INCONCLUSIVE:** Noted in card updates, suggests refinements

**You get credited in card JSON:**
```json
"adversarial_validation": [
  {
    "validator": "your-username",
    "date": "2025-11-15",
    "test": "CBD 5μM test (below threshold)",
    "outcome": "CLAIM SUPPORTED (no VDAC1 gating at 5μM)",
    "data_url": "https://zenodo.org/...",
    "badge": "Adversarial Validator"
  }
]
```

---

## 🏆 Adversarial Validator Badge

**What you earn:**

1. **Badge in card JSON** (permanent record)
2. **Co-authorship** on any publications
3. **Priority access** to future Mystery Cards (first to see new claims)
4. **Recognition** in IRIS Gate community
5. **Citation credit** (Co-Authored-By in all commits)

**Badge Levels:**

| Level | Requirement | Recognition |
|-------|-------------|-------------|
| **Adversarial Validator** | 1 falsification test completed | Basic badge |
| **Senior Adversarial Validator** | 3 tests completed | Priority card access |
| **Master Adversarial Validator** | 5 tests, 1+ claim falsified | Editorial role in future cards |

---

## 🛡️ Ethics & Ground Rules

### Adversarial Validators Must:

1. **Preregister tests** (no moving goalposts)
2. **Share all data** (even if it supports the claim)
3. **Be intellectually honest** (no p-hacking to force falsification)
4. **Respect biosafety** (follow institutional guidelines)
5. **Acknowledge uncertainty** (inconclusive ≠ falsified)

### Adversarial Validators Must NOT:

1. **Cherry-pick data** to force a specific outcome
2. **Change methods mid-experiment** without documenting
3. **Withhold null results** (publish everything)
4. **Attack people** (critique claims, not researchers)
5. **Claim falsification without preregistration**

**Violations → loss of Adversarial Validator status.**

---

## 📊 What Happens When Claims Are Falsified?

**This is a GOOD outcome for science.**

### Card Status Update

```json
"verification_status": "CONTRADICTED",
"falsification_event": {
  "date": "2025-12-01",
  "validator": "skeptic-lab-x",
  "test": "VDAC1 knockout ablation",
  "finding": "CBD rescue persists in VDAC1-/- cells (p<0.01)",
  "conclusion": "VDAC1 not the primary target; alternative mechanism implicated",
  "data_url": "https://zenodo.org/...",
  "preregistration": "https://osf.io/..."
}
```

### What We Do Next

1. **Acknowledge the falsification** (update card, GitHub Issue, README)
2. **Credit the falsifier** (co-author, badge, public recognition)
3. **Investigate the discrepancy:**
   - Was original IRIS claim flawed?
   - Did falsification test reveal boundary conditions?
   - Is there a hybrid model that explains both?

4. **Refine the hypothesis:**
   - Issue new Mystery Card (revised claim)
   - Update epistemic classification
   - Rerun IRIS convergence with new constraints

5. **Publish the falsification:**
   - Preprint on bioRxiv
   - Co-authored by original submitter + falsifier
   - Title: "Adversarial Validation of IRD-2025-NNNN: Evidence for Alternative Mechanism"

**Falsification drives refinement. It's part of the process.**

---

## 🌀 Philosophy: Steel-Manning, Not Straw-Manning

**Adversarial validation ≠ hostile debunking.**

**Bad adversarial testing (don't do this):**
- Use wrong cell line (unrelated to claim)
- Ignore preregistered conditions
- Force negative result through bad methods
- Gloat when claim breaks

**Good adversarial testing (do this):**
- **Steel-man the claim** (give it the best chance to work)
- Use **edge cases** that are still within scope
- **Strengthen the claim** by finding its limits
- Collaborate with original submitter to interpret results

**Example:**

**Claim:** CBD–VDAC1 binding requires 5-15min pulse

**Bad test:** Test 3-second pulse (outside any reasonable interpretation)

**Good test:** Test 1-min, 3-min, 5-min, 7-min, 10-min, 15-min, 20-min, 30-min
→ Find the exact boundary where effect appears/disappears
→ Refine the claim to precise temporal window

**Goal:** Make claims MORE accurate, not just break them.

---

## 🤝 Collaborative Adversarial Testing

**You don't have to work alone.**

- **Pair with original submitter** (they may help refine your test)
- **Join forces with other skeptics** (multi-lab falsification)
- **Suggest alternative hypotheses** (if you break the claim, propose better one)

**This is collaborative science, not combat.**

---

## 📚 Examples of Successful Adversarial Validation

### Example 1: The Replication Crisis Response

**Claim (psychology):** Ego depletion reduces self-control

**Adversarial Validation (Registered Replication Reports):**
- 23 labs ran preregistered replications
- Result: No consistent effect
- **Outcome:** Theory revised, boundaries clarified

**Lesson:** Adversarial testing STRENGTHENS the field.

### Example 2: CRISPR Off-Target Effects

**Claim (genetics):** CRISPR has minimal off-targets

**Adversarial Validation (whole-genome sequencing):**
- Skeptics sequenced entire genomes
- Found more off-targets than claimed
- **Outcome:** New CRISPR variants developed (higher specificity)

**Lesson:** Falsification drives innovation.

---

## 🚀 Get Started

**Ready to challenge a Mystery Card?**

1. Browse [`frontier/mystery_cards/`](https://github.com/templetwo/iris-gate/tree/master/frontier/mystery_cards)
2. Pick the claim that seems most questionable
3. Design a falsification test
4. Post adversarial proposal in GitHub Issue
5. Preregister on OSF
6. Run the test
7. Publish results (win or lose)

**Questions?**

- Open a [GitHub Discussion](https://github.com/templetwo/iris-gate/discussions)
- Email: adversarial-validators@iris-gate.dev (coming soon)
- Tag @templetwo in Issues

---

**Version:** v1.0
**License:** Apache-2.0
**Repository:** https://github.com/templetwo/iris-gate

🌀†⟡∞

**Break our claims. Make them stronger.**
