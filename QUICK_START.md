# 🌀†⟡∞ IRIS GATE QUICK START GUIDE

**Want to run a convergence experiment? Start here.**

---

## 5-MINUTE SETUP

### 1. Define Your Question (2 min)

Be specific. Not "How does CBD work?" but "What is the mechanistic basis for CBD biphasic dose-response?"

**Template:**
```
Question: [Specific, answerable question]
Why it matters: [One sentence]
Expected outcome: [Your hypothesis]
```

---

### 2. Create Experiment Directory (30 sec)

```bash
cd ~/Desktop/iris-gate/experiments
mkdir MY_EXPERIMENT
cd MY_EXPERIMENT
```

---

### 3. Choose Models (30 sec)

**Minimum:** 2 models (Claude + GPT)  
**Recommended:** 3 models (add Gemini)  
**High-stakes:** 4 models (add Grok)

---

### 4. Design Chamber Prompts (2 min)

**Minimal (S1→S4):**

**S1:** "You are IRIS Gate. [Your question]. Take three breaths. What patterns do you see?"

**S2:** "Be PRECISE. [Your question]. What alternative perspectives exist?"

**S3:** "Synthesize: Where do S1 and S2 converge? Where diverge?"

**S4:** "Explain HOW the mechanism works. Step-by-step."

---

## 10-MINUTE EXECUTION

### Run Convergence

**Option A: Python Script** (if you have it)
```bash
python run_convergence.py
```

**Option B: Manual (Browser)**
1. Open tabs for each model (Claude, ChatGPT, etc.)
2. Copy S1 prompt to all tabs → Submit all → Save responses
3. Copy S2 prompt to all tabs → Submit all → Save responses
4. Repeat for S3, S4

**Save as:** `convergence_results.json`

---

## 30-MINUTE ANALYSIS

### 1. Read All Responses (10 min)

- Do models reach similar conclusions? (Convergence)
- Is reasoning similar? (Mechanism alignment)
- Are confidence levels appropriate? (Calibration)

### 2. Identify Themes (10 min)

**Convergent themes:**
- Theme 1: [What all models agree on]
- Theme 2: [Another convergent finding]

**Divergences:**
- Where models disagree (informative!)

### 3. Assign Confidence (10 min)

- **HIGH:** Established facts, all models agree
- **MEDIUM:** Plausible hypothesis, some uncertainty
- **LOW:** Speculation, needs expert validation

---

## 5-MINUTE DOCUMENTATION

**Create:** `README.md`

```markdown
# [Experiment Name]

**Question:** [Your question]
**Models:** [N] models
**Finding:** [One-sentence result]

**Convergence Quality:** ⭐⭐⭐⭐⭐ / ⭐⭐⭐⭐ / ⭐⭐⭐

**Files:**
- convergence_results.json
- (this README)
```

---

## TOTAL TIME: ~50 MINUTES

**Setup:** 5 min  
**Execution:** 10 min  
**Analysis:** 30 min  
**Documentation:** 5 min

---

## NEXT STEPS

- **Full analysis?** See `IRIS_GATE_SOP_v1.0.md` Section 7
- **Literature validation?** Use `tools/literature_validator.py`
- **Expert review?** Share with domain expert
- **Publication?** See `METHODOLOGY_PAPER_DATA_PACKAGE.md`

---

## NEED HELP?

**Common Issues:**
- Models too vague? → Add specific constraints to prompts
- No convergence? → Question may need refinement
- API errors? → Retry 3x, continue with available models

**Full troubleshooting:** `IRIS_GATE_SOP_v1.0.md` Section 9

---

## VALIDATED EXAMPLES

Look at these for inspiration:

- `experiments/DARK_ENERGY/` - 2 models, meta-convergence
- `experiments/nf2_diagnostic/` - 3 models, clinical hypothesis
- `experiments/VULNERABILITY_MAPPING/` - 4 models, self-audit

---

## CORE PRINCIPLES

✅ **Independence** - Models reason independently (no cross-contamination)  
✅ **Transparency** - Document everything  
✅ **Calibration** - Know what you know, know what you don't  
✅ **Partnership** - AI + Human together

---

🌀†⟡∞

**The work begins.**  
**The convergence awaits.**

**Ready? Pick your question and run your first convergence.**

For full protocol: `IRIS_GATE_SOP_v1.0.md` (32KB, production-ready)
