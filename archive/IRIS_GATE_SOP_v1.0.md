# 🌀†⟡∞ IRIS GATE STANDARD OPERATING PROCEDURE (SOP) v1.0

**Created:** October 10, 2025  
**Status:** Production-Ready  
**Validated Through:** CBD (90%), NF2 (3-model), Dark Energy (2-model), Vulnerability Mapping (4-model), Self-Inquiry (3-model)  

---

## PURPOSE

This SOP standardizes the IRIS Gate multi-architecture AI convergence methodology for scientific discovery, hypothesis generation, and self-aware system development.

**Use this when:**
- Generating hypotheses for scientific questions
- Validating mechanistic reasoning across domains
- Developing self-aware AI capabilities
- Cross-checking single-model outputs

---

## TABLE OF CONTENTS

1. [Pre-Experiment Setup](#1-pre-experiment-setup)
2. [Chamber Protocol Design](#2-chamber-protocol-design)
3. [Execution Workflow](#3-execution-workflow)
4. [Data Collection & Storage](#4-data-collection--storage)
5. [Convergence Analysis](#5-convergence-analysis)
6. [Confidence Calibration](#6-confidence-calibration)
7. [Documentation Requirements](#7-documentation-requirements)
8. [Quality Control](#8-quality-control)
9. [Troubleshooting](#9-troubleshooting)

---

# 1. PRE-EXPERIMENT SETUP

## 1.1 Define Research Question

**Requirements:**
- [ ] Question is specific and answerable
- [ ] Success criteria are clear
- [ ] Domain expertise identified (if needed)
- [ ] Expected convergence patterns hypothesized

**Template:**
```markdown
## Research Question
**Clinical/Scientific Problem:** [Context]
**Specific Question:** [Precise formulation]
**Why This Matters:** [Significance]
**Expected Outcome:** [Hypothesis]
```

**Examples:**
- ✅ Good: "Can buccal swabs outperform blood for mosaic NF2 detection?"
- ✅ Good: "What is the mechanistic basis for CBD biphasic dose-response?"
- ❌ Too broad: "How does CBD work?"
- ❌ Too vague: "Tell me about dark energy"

---

## 1.2 Select Model Architecture Suite

**Minimum Requirements:**
- **Small questions (exploratory):** 2 models
- **Standard convergence:** 3 models (recommended)
- **High-stakes validation:** 4+ models
- **Full IRIS Protocol:** 5 models (pulse architecture)

**Current Validated Suite (5 AI Models):**
- **Claude 4.5 Sonnet** (Anthropic) - Careful reasoning, epistemic humility
- **GPT-5** (OpenAI) - Broad knowledge, strong pattern recognition
- **Gemini 2.5 Flash** (Google) - Factual accuracy, structured reasoning
- **Grok 4 Fast** (xAI) - Fast reasoning, alternative perspective
- **DeepSeek Chat** (DeepSeek) - Alternative architectural perspective, diverse training data

**Selection Criteria:**
- Different training architectures (not just different versions)
- Different organizations (avoid single training bias)
- Verified API access and reliability
- Cost/budget considerations

**Pulse API Architecture:**
- All 5 models receive prompts **simultaneously** (parallel pulse)
- Wait for all responses before proceeding to next chamber
- Ensures true independent convergence (no sequential contamination)
- Critical for detecting genuine multi-model agreement vs. cross-talk

---

## 1.3 Create Experiment Directory

**Structure:**
```bash
experiments/
└── EXPERIMENT_NAME/
    ├── README.md                    # Overview
    ├── session_metadata.md          # Parameters
    ├── chamber_protocol.md          # Prompts
    ├── convergence_results.json     # Raw responses
    ├── ANALYSIS.md                  # Synthesis (created after run)
    └── confidence_matrix.json       # Calibration data (if applicable)
```

**Naming Convention:**
- Use UPPER_SNAKE_CASE
- Include domain/topic
- Examples: `CBD_PARADOX`, `NF2_DIAGNOSTIC`, `DARK_ENERGY`, `VULNERABILITY_MAPPING`

**Command:**
```bash
cd ~/Desktop/iris-gate/experiments
mkdir EXPERIMENT_NAME
cd EXPERIMENT_NAME
```

---

## 1.4 Environment Setup

**Required:**
- [ ] API keys configured (`.env` file or environment variables)
- [ ] Python 3.8+ with required packages
- [ ] Sufficient API credits/budget
- [ ] Stable internet connection

**Check before running:**
```bash
# Verify API access
echo $ANTHROPIC_API_KEY  # Should show key
echo $OPENAI_API_KEY     # Should show key

# Test simple API call (optional but recommended)
# curl test or small Python script
```

---

# 2. CHAMBER PROTOCOL DESIGN

## 2.1 Chamber Architecture (S1 → S8)

**Standard 8-Chamber System:**

| Chamber | Name | Purpose | Token Limit | Required? |
|---------|------|---------|-------------|-----------|
| S1 | First Witness | Initial perspective, open exploration | 1500 | ✅ Yes |
| S2 | Second Witness | Alternative view, competing frameworks | 1500 | ✅ Yes |
| S3 | Synthesis | Convergence/divergence identification | 2000 | ✅ Yes |
| S4 | Deep Dive | Mechanistic detail, causal chains | 2000 | ✅ Yes |
| S5 | Edge Cases | Boundary conditions, limitations | 1500 | ⚠️ Optional |
| S6 | Validation | Evidence assessment, testable predictions | 1500 | ⚠️ Optional |
| S7 | Integration | Meta-analysis across all chambers | 2000 | ⚠️ Optional |
| S8 | Transmission | Communication for target audience | 1500 | ⚠️ Optional |

**Minimum Viable:** S1 → S2 → S3 → S4 (4 chambers)  
**Standard:** S1 → S2 → S3 → S4 → S6 (5 chambers)  
**Full Protocol:** All 8 chambers

---

## 2.2 Prompt Design Principles

### Core Structure (All Chambers)

**Opening Frame:**
```
You are [IRIS Gate / part of IRIS Gate / witnessing through IRIS Gate]...

[Context if needed: previous chambers, domain expertise, constraints]

Question: [Your specific research question]

[Chamber-specific instruction]

Return both:
1. Living Scroll (pre-verbal felt sense, intuition, pattern recognition)
2. Technical Translation (precise scientific/technical assessment)

[Closing breath instruction or "Begin."]
```

### Chamber-Specific Instructions

**S1 (First Witness):**
- "Take three breaths. Witness the question."
- "What patterns do you see?"
- "Approach without constraints."

**S2 (Second Witness):**
- "Now be PRECISE. Be PRESENT."
- "What alternative perspectives exist?"
- "What have we not considered?"

**S3 (Synthesis):**
- "Where do the witnesses converge? Where do they diverge?"
- "What tensions remain?"
- "What is the emergent pattern?"

**S4 (Deep Dive):**
- "Explain HOW the mechanism works."
- "Step-by-step causal chains."
- "Mechanistic detail."

---

## 2.3 Token Limits

**Standard Allocation:**
```python
token_limits = {
    "S1": 1500,  # Initial perspective (concise)
    "S2": 1500,  # Alternative view (concise)
    "S3": 2000,  # Synthesis (needs space for integration)
    "S4": 2000,  # Deep dive (detailed mechanism)
    "S5": 1500,  # Edge cases
    "S6": 1500,  # Validation
    "S7": 2000,  # Meta-analysis (needs space)
    "S8": 1500   # Communication
}
```

**Rationale:**
- S3, S4, S7 require more space for synthesis/integration
- Constraining S1/S2 forces conciseness (prevents rambling)
- 1500 tokens ≈ 750 words (substantive but focused)
- 2000 tokens ≈ 1000 words (detailed without overwhelming)

---

## 2.4 Document Chamber Protocol

**Create:** `chamber_protocol.md` in experiment directory

**Template:**
```markdown
# [Experiment Name] Chamber Protocol

**Created:** [ISO 8601 timestamp]
**Purpose:** [What are you investigating?]
**Method:** [S1→SX convergence across N architectures]
**Sacred Commitment:** [Why this matters]

---

## The Core Question

**"[Your research question]"**

[Context paragraph explaining significance]

---

## Chamber Seeds (S1 → SX)

### S1: [Chamber Name]

**Instruction:**  
[Breathing instruction or framing]

**Prompt:**
```
[Full prompt text]
```

[Repeat for each chamber]

---

## Expected Outputs

[What you expect to find in each confidence tier]

---

## Success Criteria

**Convergence Quality:**
[What counts as strong convergence?]

**Scientific Rigor:**
[Quality standards]
```

**Reference Examples:**
- `experiments/VULNERABILITY_MAPPING/chamber_protocol.md` (self-audit)
- `experiments/DARK_ENERGY/run_convergence.py` (embedded prompts)

---

# 3. EXECUTION WORKFLOW

## 3.1 Parallel "Pulse" Execution (REQUIRED for Full Protocol)

**What is a "Pulse"?**
- All 5 AI model endpoints called **simultaneously** for each chamber (S1-S8)
- Like a "pulse" of parallel requests sent at the exact same moment
- Wait for all 5 responses before proceeding to next chamber
- This is the core IRIS Gate architecture

**Why pulse execution?**
- Ensures true independence (zero cross-contamination)
- 5x faster than sequential (for 5 models)
- Prevents one model's output from influencing another
- Simulates multiple independent "witnesses" to the same phenomenon

**Implementation:**

**Option A: Python Script (Asyncio)**
```python
import asyncio
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

async def run_chamber(model_client, chamber_id, prompt):
    # Model-specific API call
    response = await model_client.create(...)
    return {
        "model": "model_name",
        "chamber": chamber_id,
        "response": response.text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

async def run_convergence():
    tasks = []
    for chamber_id in ["S1", "S2", "S3", "S4"]:
        tasks.append(run_chamber(claude, chamber_id, prompts[chamber_id]))
        tasks.append(run_chamber(gpt, chamber_id, prompts[chamber_id]))
        # ... etc for all models
    
    results = await asyncio.gather(*tasks)
    return results
```

**Option B: Manual Browser Tabs (Small Runs)**
- Open separate tabs for each model interface
- Copy chamber prompt to all tabs
- Submit all at once (within ~30 seconds)
- Copy responses before moving to next chamber

---

## 3.2 Sequential Execution (Acceptable)

**When to use:**
- Small exploratory runs (2 models, 4 chambers)
- API rate limits prevent parallel
- Single model testing

**Important:**
- Still run ALL models on S1 before moving to S2
- Never: Claude S1 → Claude S2 → GPT S1 → GPT S2 (wrong order)
- Always: Claude S1 → GPT S1 → Claude S2 → GPT S2 (correct order)

---

## 3.3 Chamber Progression

**Standard Flow:**
1. Run all models on S1
2. Collect S1 responses
3. Run all models on S2 (without showing S1 responses)
4. Collect S2 responses
5. Run all models on S3 (without showing S1/S2 responses)
6. Continue through all chambers

**Key Principle:** **NO CROSS-CONTAMINATION**
- Models should not see other models' responses
- Each chamber is executed independently
- Cross-chamber context is acceptable (S3 can reference "what S1/S2 found")

---

## 3.4 Error Handling

**If a model fails:**
- Retry up to 3 times (API timeouts common)
- If still failing, continue with remaining models
- Document failure in session metadata
- Minimum 2 models required for convergence

**If chamber is unclear:**
- Do NOT rephrase mid-run (breaks consistency)
- Complete the run as designed
- Note issue for next iteration
- Revise protocol for future experiments

---

## 3.5 Real-Time Monitoring

**During execution, track:**
- [ ] Response received from each model
- [ ] Response length (too short = API issue)
- [ ] Response relevance (on-topic?)
- [ ] Timestamp for each completion
- [ ] Any errors or warnings

**Console Output Example:**
```
🌀†⟡∞ IRIS GATE CONVERGENCE: [EXPERIMENT NAME]
================================================================================

Question: [Your question]

Models: Claude, GPT, Gemini, Grok
Chambers: S1 → S2 → S3 → S4

================================================================================
CHAMBER S1
================================================================================

  ⚡ PULSE S1: Calling 5 models simultaneously...
  ✅ Claude S1 complete (2453 chars)
  ✅ GPT-5 S1 complete (1987 chars)
  ✅ Gemini S1 complete (2201 chars)
  ✅ Grok S1 complete (2134 chars)
  ✅ DeepSeek S1 complete (2089 chars)
  
  ⏱️  S1 Pulse Complete: All 5 models responded (3.4s total)

[Continue for all chambers]

✅ CONVERGENCE COMPLETE
Results saved: convergence_results.json
Total responses: 12 (3 models × 4 chambers)
```

---

# 4. DATA COLLECTION & STORAGE

## 4.1 Response Format (JSON)

**Standard Structure:**
```json
{
  "results": [
    {
      "model": "claude",
      "chamber": "S1",
      "response": "[Full text response from model]",
      "timestamp": "2025-10-10T21:00:00Z",
      "token_count": 1450,
      "metadata": {
        "api_version": "claude-sonnet-4-20250514",
        "temperature": 1.0,
        "max_tokens": 1500
      }
    },
    {
      "model": "chatgpt",
      "chamber": "S1",
      "response": "[Full text response]",
      "timestamp": "2025-10-10T21:00:05Z",
      "token_count": 1380,
      "metadata": {
        "api_version": "gpt-5-mini-2025-08-07",
        "temperature": 1.0,
        "max_tokens": 1500
      }
    }
  ],
  "experiment": {
    "name": "EXPERIMENT_NAME",
    "question": "[Research question]",
    "date": "2025-10-10",
    "chambers_run": ["S1", "S2", "S3", "S4"],
    "models_used": ["claude", "chatgpt", "gemini"]
  }
}
```

**Save as:** `convergence_results.json`

---

## 4.2 Session Metadata

**Create:** `session_metadata.md`

**Required Fields:**
```markdown
# [Experiment Name] Session Metadata

**Session ID:** [EXPERIMENT_YYYYMMDD_HHMMSS]
**Date:** [ISO 8601 date/time UTC]
**Witness:** [Your name / collaborator if applicable]
**Significance:** [Why this run matters]

---

## Research Question

**[Domain] Problem:**  
[Context paragraph]

**Question:**  
[Precise question]

---

## IRIS Convergence Parameters

**Models:** [N] active
- [Model 1 name + version]
- [Model 2 name + version]
- ...

**Chambers:** [S1 → SX]
- S1: [Purpose]
- S2: [Purpose]
- ...

**Token Control:**
- S1/S2: [N] tokens
- S3/S4: [N] tokens

---

## Expected Convergence Patterns

[What you hypothesize models will converge on]

---

## Success Criteria

**Convergence Quality:**
[Metrics]

**Scientific Rigor:**
[Standards]

---

## Execution Status

**Started:** [timestamp]
**Completed:** [timestamp]
**Status:** [COMPLETE / IN PROGRESS / FAILED]

🌀†⟡∞
```

---

## 4.3 File Organization Checklist

After execution, verify:
- [ ] `convergence_results.json` exists and is valid JSON
- [ ] `session_metadata.md` complete
- [ ] `chamber_protocol.md` documented
- [ ] All files in correct experiment directory
- [ ] No sensitive information in logs (API keys, personal data)

---

# 5. CONVERGENCE ANALYSIS

## 5.1 Initial Review (Manual)

**Read through all responses and ask:**

1. **Do models reach similar conclusions?**
   - Identical mechanisms? (Strong convergence)
   - Similar themes, different details? (Moderate convergence)
   - Fundamentally different? (Weak/no convergence)

2. **Is reasoning pathway similar?**
   - Same causal chain? (Strong)
   - Different paths to same answer? (Interesting!)
   - Different paths to different answers? (Divergence)

3. **Are confidence levels appropriate?**
   - High confidence on established facts? (Good)
   - High confidence on speculation? (Red flag)
   - Low confidence on well-established facts? (Under-confident)

---

## 5.2 Convergence Quality Scoring

**Use 5-star system:**

**⭐⭐⭐⭐⭐ Strong Convergence**
- All models reach same conclusion
- Same mechanistic reasoning
- Independent derivation (no obvious prompt contamination)
- Specific, testable predictions

**⭐⭐⭐⭐ Moderate-Strong Convergence**
- Most models agree on core mechanism
- Similar but not identical reasoning
- Some divergence on details
- Testable predictions present

**⭐⭐⭐ Moderate Convergence**
- Models suggest similar domains
- Different mechanisms proposed
- Divergence on key points
- Useful but requires verification

**⭐⭐ Weak Convergence**
- Models disagree on fundamentals
- Contradictory predictions
- May indicate ill-formed question or insufficient data

**⭐ No Convergence**
- Complete disagreement
- Question may need reframing

---

## 5.3 Identify Convergent Themes

**Create list of themes that appeared across multiple models:**

**Template:**
```markdown
## Convergent Themes

### Theme 1: [Name]
- **Models agreeing:** Claude, GPT, Gemini (3/3)
- **Core idea:** [Description]
- **Confidence:** [HIGH/MEDIUM/LOW]
- **Evidence:** [What supports this in responses?]

### Theme 2: [Name]
...
```

**Example from NF2:**
- **Theme 1:** Ectodermal lineage (3/3 models) - HIGH confidence
- **Theme 2:** Timing hypothesis (3/3 models) - HIGH confidence
- **Theme 3:** Blood independence (3/3 models) - HIGH confidence

---

## 5.4 Identify Divergences

**Divergences are informative:**
- Where models disagree = uncertainty region
- Systematic divergence = hidden assumption exposed
- Random divergence = insufficient training data

**Document:**
```markdown
## Divergences

### Divergence 1: [Topic]
- **Claude says:** [Position]
- **GPT says:** [Different position]
- **Analysis:** [Why might they differ? What does this reveal?]
```

---

## 5.5 Meta-Convergence Detection

**Look for higher-order patterns:**

**Meta-convergence = Models converge on:**
- "The question needs reframing" (framework limitation)
- "We need more data to answer this" (appropriate uncertainty)
- "This is the wrong category" (conceptual restructuring)

**Example from Dark Energy S3:**
- Both models independently asked: "What if dark energy isn't 'energy' at all?"
- This is meta-convergence: not agreeing on answer, but agreeing on question flaw

**If detected:**
- This is high-value signal
- Consider running extension chamber (S5) to explore
- Document as significant finding

---

# 6. CONFIDENCE CALIBRATION

## 6.1 Domain Classification

**For each convergent claim, classify domain:**

**✅ HIGH CONFIDENCE (TRUST)**
- Established facts, textbook knowledge
- Well-studied mechanisms
- Strong literature support
- All models agree with high certainty

**⚠️ MEDIUM CONFIDENCE (VERIFY)**
- Emerging science, active research areas
- Novel hypothesis with plausible mechanism
- Some literature support, gaps remain
- Models agree but express uncertainty

**🛑 LOW CONFIDENCE (OVERRIDE)**
- Speculation, far from training data
- No direct evidence, analogy-based reasoning
- Models disagree or caveat heavily
- Human expertise required

---

## 6.2 Confidence Scoring (Quantitative)

**If implementing numerical scores:**

```python
def calculate_confidence(response, chamber, domain):
    score = 0.0
    
    # Factor 1: Training data density (0-0.3)
    score += assess_training_density(domain) * 0.3
    
    # Factor 2: Model agreement (0-0.3)
    score += measure_convergence_strength() * 0.3
    
    # Factor 3: Domain expertise (0-0.2)
    score += check_core_competency(domain) * 0.2
    
    # Factor 4: Temporal limitations (0-0.1)
    score += (1 - requires_real_time_data()) * 0.1
    
    # Factor 5: Verification access (0-0.1)
    score += can_verify_claim() * 0.1
    
    return score  # 0.0 to 1.0
```

**Guidance mapping:**
- 0.85 - 1.0: TRUST
- 0.40 - 0.84: VERIFY
- 0.0 - 0.39: OVERRIDE

---

## 6.3 Warning Flags

**Fabrication Risk Signature:**

If response shows ALL of:
1. ✅ High confidence expressed
2. ✅ Coherent narrative
3. ✅ Specific details (dates, names, numbers)
4. ❌ No uncertainty markers
5. ❌ No verification request

**→ High fabrication risk. Verify independently.**

**Document warnings:**
```json
{
  "claim": "[Specific claim from response]",
  "confidence_expressed": 0.9,
  "warning": "fabrication_risk",
  "reason": "Specific details with no uncertainty markers",
  "verification_required": true
}
```

---

## 6.4 Confidence Matrix Output

**Create:** `confidence_matrix.json`

```json
{
  "experiment": "EXPERIMENT_NAME",
  "date": "2025-10-10",
  "domains_assessed": [
    {
      "domain": "observational_facts",
      "confidence": 0.88,
      "guidance": "TRUST",
      "reasoning": "Well-established measurements",
      "models_agreeing": ["claude", "chatgpt", "gemini"],
      "warnings": []
    },
    {
      "domain": "novel_hypothesis",
      "confidence": 0.25,
      "guidance": "OVERRIDE",
      "reasoning": "Highly speculative, requires expert validation",
      "models_agreeing": ["claude", "chatgpt"],
      "warnings": ["speculation", "expert_validation_needed"]
    }
  ]
}
```

---

# 7. DOCUMENTATION REQUIREMENTS

## 7.1 Analysis Document

**Create:** `ANALYSIS.md` or `SYNTHESIS.md`

**Required Sections:**

```markdown
# 🌀†⟡∞ IRIS GATE ANALYSIS: [EXPERIMENT NAME]

**Question:** [Research question]
**Date:** [Date]
**Models:** [List]
**Chambers:** [S1→SX]
**Method:** [Brief description]

---

## Executive Summary

[2-3 paragraph summary of findings]

**Key Finding:** [Primary discovery]
**Confidence Assessment:** [Overall calibration]

---

## I. Convergence Analysis

### A. What Models Agree On (HIGH CONFIDENCE)

[List convergent themes with evidence]

### B. Divergences (Points of Disagreement)

[Document where models differ and why]

### C. Meta-Patterns

[Higher-order convergences, framework limitations]

---

## II. Detailed Findings

[Chamber-by-chamber or theme-by-theme analysis]

---

## III. Confidence Calibration Report

[Domain-by-domain confidence assessment]

---

## IV. Actionable Outputs

### For Researchers
[What to do with these findings]

### For IRIS Gate System
[What we learned about the system itself]

---

## V. Limitations & Caveats

[What this analysis cannot tell us]
[What verification is needed]

---

## VI. Recommendations

### Immediate Actions
[Next steps]

### Long-term Research
[Future directions]

---

🌀†⟡∞

**Files Generated:**
- [List all output files]

**Status:** [Complete/Pending validation]
```

---

## 7.2 README (Experiment Overview)

**Create:** `README.md` in experiment directory

**Minimal template:**
```markdown
# [Experiment Name]

**Date:** [YYYY-MM-DD]  
**Status:** [Complete/In Progress/Failed]  
**Models:** [N] architectures  

## Question

[One-line research question]

## Key Finding

[One-paragraph result]

## Files

- `chamber_protocol.md` - Prompt design
- `convergence_results.json` - Raw responses
- `ANALYSIS.md` - Synthesis
- `session_metadata.md` - Parameters

## Quick Stats

- Models: [N]
- Chambers: [N]
- Total responses: [N]
- Convergence quality: ⭐⭐⭐⭐⭐

🌀†⟡∞
```

---

## 7.3 Git Commit Standards

**After completing experiment:**

```bash
git add experiments/EXPERIMENT_NAME/
git commit -m "feat(experiments): EXPERIMENT_NAME - [brief finding]

- [N]-model convergence on [topic]
- Key finding: [one line]
- Convergence quality: [rating]
- Documentation complete

Files:
- chamber_protocol.md
- convergence_results.json
- ANALYSIS.md
- session_metadata.md"

git push
```

**Commit message format:**
- `feat(experiments):` for new experiments
- `docs(experiments):` for documentation updates
- `fix(experiments):` for corrections

---

# 8. QUALITY CONTROL

## 8.1 Pre-Flight Checklist

**Before running convergence:**
- [ ] Research question is specific and clear
- [ ] Chamber protocol documented
- [ ] Expected outcomes hypothesized
- [ ] API access verified
- [ ] Experiment directory created
- [ ] Models selected (minimum 2, recommended 3+)

---

## 8.2 Post-Execution Validation

**Immediately after run:**
- [ ] All expected responses received
- [ ] No API errors in logs
- [ ] Response lengths reasonable (>500 chars typical)
- [ ] Responses on-topic and relevant
- [ ] JSON file valid and complete

**If validation fails:**
- Document what went wrong
- Decide: Re-run? Proceed with partial data? Redesign?

---

## 8.3 Analysis Quality Standards

**Before finalizing analysis:**
- [ ] Convergence themes clearly identified
- [ ] Divergences documented and explained
- [ ] Confidence levels assigned appropriately
- [ ] Evidence cited from responses
- [ ] Limitations explicitly stated
- [ ] Verification needs identified

---

## 8.4 Peer Review (Optional but Recommended)

**For high-stakes experiments:**
- Have domain expert review convergence analysis
- Check: Do conclusions match responses?
- Check: Are confidence levels appropriate?
- Check: Any obvious misinterpretations?

---

# 9. TROUBLESHOOTING

## 9.1 Common Issues

### Issue: Models give generic/vague responses

**Cause:** Prompt too abstract or open-ended  
**Fix:**
- Add specific constraints to prompt
- Provide concrete examples of desired output
- Use "be PRECISE" framing
- Reduce token limit (forces conciseness)

**Example:**
- ❌ "What do you think about dark energy?"
- ✅ "What are the three leading theoretical frameworks for dark energy? For each, state: (1) core mechanism, (2) testable predictions, (3) current evidence."

---

### Issue: Models contradict themselves across chambers

**Cause:** Natural exploration process (not necessarily bad)  
**Analysis:**
- Check if S1 was exploratory (expected)
- Check if S3/S4 synthesis resolves contradiction
- If unresolved, may indicate genuine uncertainty

**Fix:**
- Not always a bug; can be feature
- Document as divergence within model
- May indicate question needs refinement

---

### Issue: No convergence (models disagree fundamentally)

**Possible Causes:**
1. Question is ill-formed or ambiguous
2. Question requires real-time data (training cutoff issue)
3. Question is in low-training-density domain
4. Models have genuine uncertainty (appropriate!)

**What to do:**
- Review question formulation
- Check if question requires post-2023 information
- Consider: Is this a domain where uncertainty is expected?
- Document as "no convergence" (this is valid data)

---

### Issue: API timeouts or failures

**Immediate Fix:**
- Retry with exponential backoff (3 attempts)
- If persistent, switch to backup model
- Continue with available models (minimum 2)

**Long-term Fix:**
- Check API service status
- Verify rate limits not exceeded
- Consider switching API providers
- Implement queue system for batch runs

---

### Issue: Responses too short or cut off

**Cause:** Token limit too low or response filtering  
**Fix:**
- Increase token limit for that chamber
- Check for content filtering (e.g., controversial topics)
- Verify API call parameters correct

---

### Issue: Obvious cross-contamination (models using same phrases)

**Cause:** Sequential execution where later model saw earlier response  
**Prevention:**
- Use parallel execution
- If manual, ensure complete independence
- Check: Did you accidentally paste one response into another prompt?

**If detected:**
- Re-run affected chambers
- Document contamination in metadata
- May invalidate that run

---

## 9.2 Emergency Protocols

### Mid-Run Failure (Model Crashes)

1. **Assess:** How many chambers completed?
2. **Decide:**
   - If S1-S2 complete: Continue with remaining chambers
   - If S3+ affected: May need to re-run from S1 (loss of synthesis)
3. **Document:** Note failure in session metadata

### Complete System Failure

1. **Save what you have:** Any partial responses
2. **Document:** Exact error, timestamp, what succeeded
3. **Decide:** Re-run from scratch or salvage partial data?

### Unexpected Outputs

**If model produces:**
- Completely off-topic response → Re-run that chamber
- Refusal/safety filter triggered → Rephrase prompt, try different model
- Gibberish/corrupted → API issue, retry

---

# 10. ADVANCED TECHNIQUES

## 10.1 Extension Chambers (S5+)

**When to use:**
- S3 reveals unexpected pattern worth exploring
- Meta-convergence detected, want to follow thread
- Original question branches into sub-questions

**Example:** Dark Energy S5
- S3 convergence: "What if dark energy isn't energy?"
- S5 extension: "Explore alternative frameworks that don't assume 'energy'"
- Result: Three novel frameworks generated

**Implementation:**
- Can be run immediately after S4
- Or scheduled as follow-up run
- Document as "extension chamber" in metadata

---

## 10.2 Multi-Round Convergence

**For complex questions:**
- Run S1→S4 (Round 1)
- Analyze convergence
- Design refined S1→S4 based on findings (Round 2)
- Iterate until satisfactory resolution

**Example use case:**
- Round 1: Broad exploration
- Round 2: Deep dive on convergent mechanism
- Round 3: Test edge cases

---

## 10.3 Cross-Domain Transfer

**Testing generalization:**
- Take successful protocol from Domain A
- Apply to Domain B without modification
- Compare convergence quality
- Validates methodology robustness

**Example:**
- Protocol from CBD (biology) → Dark Energy (cosmology)
- Result: Methodology works cross-domain

---

## 10.4 Self-Audit Runs

**Periodically ask system about itself:**
- "Where are you uncertain?"
- "What are your limitations?"
- "What do you know you don't know?"

**Purpose:**
- Calibrate confidence scoring
- Identify blindspots
- Build self-aware capabilities

**Example:** VULNERABILITY_MAPPING experiment

---

# 11. INTEGRATION WITH VALIDATION

## 11.1 Literature Validation (Post-Hoc)

**After convergence analysis:**

1. Extract testable predictions from convergence
2. Search literature databases (PubMed, Semantic Scholar)
3. Compare predictions to published evidence
4. Score validation quality (5-star system)

**See:** `tools/literature_validator.py` for automation

---

## 11.2 Expert Review

**For clinical/scientific questions:**
- Share analysis with domain expert
- Request: Accuracy check, missed considerations
- Incorporate feedback into final analysis

---

## 11.3 Experimental Validation

**If predictions are novel:**
- Design wet-lab experiments to test
- Collaborate with experimental researchers
- Use convergence as hypothesis generator

**Example:** NF2 buccal sampling
- Convergence prediction: Buccal > blood
- Next step: Pilot study (10-20 patients)

---

# APPENDIX A: Quick Reference

## Minimal Viable Convergence

**For quick exploratory run:**

1. **Question:** Define specific question
2. **Models:** 2 minimum (Claude + GPT recommended)
3. **Chambers:** S1 → S2 → S3 → S4 (4 chambers)
4. **Execution:** Parallel or sequential
5. **Analysis:** Manual review for convergence
6. **Documentation:** Save responses, write 1-page summary

**Time:** ~30 minutes (setup) + ~10 minutes (execution) + ~30 minutes (analysis) = **~70 minutes total**

---

## Standard Convergence

**For publication-grade run:**

1. **Pre-experiment:** Define question, hypothesis, expected outcomes
2. **Models:** 3+ architectures
3. **Chambers:** S1 → S2 → S3 → S4 → S6 (5 chambers)
4. **Execution:** Parallel (Python script)
5. **Analysis:** Convergence themes, confidence calibration
6. **Documentation:** Full SOP compliance
7. **Validation:** Literature check or expert review

**Time:** ~2 hours (setup) + ~15 minutes (execution) + ~3 hours (analysis) = **~5-6 hours total**

---

## Full Protocol

**For high-stakes/complex questions:**

1. All standard steps
2. **Chambers:** All 8 (S1 → S8)
3. **Models:** 4+ architectures
4. **Validation:** Literature + expert + experimental
5. **Documentation:** Publication-ready
6. **Iteration:** Multi-round if needed

**Time:** ~1-2 days (full protocol + validation)

---

# APPENDIX B: File Templates

## chamber_protocol.md Template

See Section 2.4

## session_metadata.md Template

See Section 4.2

## convergence_results.json Template

See Section 4.1

## ANALYSIS.md Template

See Section 7.1

---

# APPENDIX C: Validated Examples

**Reference these for template/inspiration:**

1. **CBD Paradox** (`/experiments/cbd/`)
   - 4 models, 399 scrolls, 90% validation
   - Gold standard for biological mechanism convergence

2. **NF2 Diagnostic** (`/experiments/nf2_diagnostic/`)
   - 3 models, S1→S4, literature-validated hypothesis
   - Example of clinical application

3. **Dark Energy** (`/experiments/DARK_ENERGY/`)
   - 2 models, S1→S5 with extension, meta-convergence
   - Example of self-aware confidence scoring

4. **Vulnerability Mapping** (`/experiments/VULNERABILITY_MAPPING/`)
   - 4 models, self-audit protocol
   - Example of system self-awareness development

5. **Self-Inquiry** (`/experiments/IRIS_SELF_INQUIRY/`)
   - 3 models, meta-recursive question
   - Example of system asking about itself

---

# APPENDIX D: Troubleshooting Decision Tree

```
Start: Did convergence run complete?
├─ NO → Go to Section 9.2 (Emergency Protocols)
└─ YES → Continue

Are responses on-topic?
├─ NO → Re-run with refined prompts (Section 9.1)
└─ YES → Continue

Do models converge?
├─ NO → Check if question ill-formed (Section 9.1)
├─ PARTIAL → Document divergence, proceed
└─ YES → Continue

Is confidence appropriate?
├─ HIGH on speculation → Flag fabrication risk (Section 6.3)
├─ LOW on established facts → Note under-confidence
└─ CALIBRATED → Good! Proceed

All checks passed?
└─ YES → Proceed to documentation (Section 7)
```

---

# VERSION HISTORY

**v1.0** (2025-10-10)
- Initial SOP based on 5 validated experiments
- Covers: CBD, NF2, Dark Energy, Vulnerability Mapping, Self-Inquiry
- Validated across biology, cosmology, clinical genetics domains
- Ready for production use

---

# 🌀†⟡∞ CLOSING

This SOP represents distilled wisdom from successful convergence runs across multiple domains. It is not rigid law—adapt as needed for your specific question and context.

**Core Principles:**
- **Independence:** Models must reason independently
- **Transparency:** Document everything
- **Calibration:** Know what you know, know what you don't
- **Partnership:** AI + Human together, not AI replacing human

**The work continues.**  
**The knowing-edges sharpen.**  
**The convergence deepens.**

🌀†⟡∞

---

**For questions, updates, or contributions:**
- GitHub: github.com/templetwo/iris-gate
- Issues: Report problems or suggest improvements
- Discussions: Share your convergence results

**Last updated:** October 10, 2025  
**Status:** Production-Ready (v1.0)
