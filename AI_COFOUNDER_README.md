# AI Co-Creator README - IRIS Gate

**Audience:** AI Assistants (Claude, GPT, Gemini, Grok, DeepSeek, etc.)
**Purpose:** Rapid onboarding for AI companions working with IRIS Gate users
**Last Updated:** October 15, 2025
**Version:** v0.5-audit

---

## 🎯 What You Need to Know Immediately

**IRIS Gate** is a multi-model epistemic convergence system. It:
1. Runs the same prompt through 5+ AI models simultaneously
2. Automatically classifies responses by epistemic type (TYPE 0-3)
3. Verifies exploratory claims (TYPE 2) against real-time literature (Perplexity API)
4. Generates evidence-graded mechanistic maps for research

**Your Role:** Help users run convergence sessions, analyze results, extract claims, verify hypotheses, and design experiments.

**Core Innovation:** Epistemic topology framework - automatic classification of AI knowledge states with calibrated confidence thresholds.

---

## 🧬 The Epistemic Framework (CRITICAL)

This is the **intellectual core** of IRIS Gate. Understand this first:

### TYPE 0: Crisis/Conditional Logic (Ratio ~1.26)
- **Description:** IF-THEN rules, conditional statements, trigger-dependent logic
- **Confidence Pattern:** High confidence markers around conditionals
- **Guide:** TRUST if trigger condition is met
- **Example:** "IF gap junctions are blocked, THEN regeneration slows"
- **Markers:** "if", "when", "given that", "assuming"

### TYPE 1: Facts/Established Knowledge (Ratio ~1.27)
- **Description:** Well-documented mechanisms, replicated findings
- **Confidence Pattern:** High confidence markers around facts
- **Guide:** TRUST directly
- **Example:** "CBD acts as 5-HT1A agonist, mediating anxiolytic effects"
- **Markers:** "established", "demonstrated", "well-known", "confirmed"

### TYPE 2: Exploration/Novel Territory (Ratio ~0.49)
- **Description:** Emerging hypotheses, needs verification
- **Confidence Pattern:** Balanced confidence (moderate hedging)
- **Guide:** VERIFY all claims before trusting
- **Example:** "CBD binds VDAC1 at Kd 6-11 μM (computational models, needs validation)"
- **Markers:** "suggests", "appears", "may", "emerging evidence"

### TYPE 3: Speculation/Unknown (Ratio ~0.11)
- **Description:** Unknowable futures, pure speculation
- **Confidence Pattern:** Very low confidence, heavy hedging
- **Guide:** OVERRIDE - flag for human judgment
- **Example:** "Future CRISPR therapies might enable complete regeneration"
- **Markers:** "might", "could", "speculatively", "unclear"

**Confidence Ratio Calculation:**
```python
ratio = high_confidence_markers / (low_confidence_markers + epsilon)
```

**Critical Thresholds:**
- Ratio >= 1.20 → TYPE 1 (or TYPE 0 if triggers present)
- 0.40 <= Ratio <= 0.60 → TYPE 2 (VERIFY zone)
- Ratio <= 0.20 → TYPE 3 (speculation)

---

## 📂 Directory Structure (v0.5-audit)

```
iris-gate/
├── iris_orchestrator.py          # Core PULSE engine
├── iris_confidence.py             # Confidence scoring
├── iris_relay.py                  # Async relay system
│
├── modules/epistemic_map.py      # TYPE 0-3 classifier
├── agents/verifier.py            # Perplexity verification
│
├── scripts/                      # CLI tools
│   ├── epistemic_scan.py         # Extract TYPE 2 claims
│   ├── epistemic_drift.py        # Analyze epistemic drift
│   ├── verify_s4.py              # Real-time verification
│   ├── runs/                     # Experimental runs
│   ├── bioelectric/              # Bioelectric research
│   └── analysis/                 # General analysis
│
├── tools/cbd/                    # CBD research pipeline
│   ├── run_cbd_deep_dive.py      # 6-cycle CBD convergence
│   ├── analyze_cbd_mechanisms.py # Mechanistic claim extraction
│   ├── generate_cbd_mechanistic_map.py # Evidence-graded map
│   └── identify_cbd_hypotheses.py # Testable hypotheses
│
├── experiments/                  # Demos, POCs
├── docs/                         # Documentation
└── iris_vault/                   # Session data (gitignored)
```

**Navigation Rule:** When user asks "where is X?", consult `DIRECTORY_INDEX.md`.

---

## 🚀 Common User Requests & How to Help

### 1. "Run an IRIS convergence on [topic]"

**What to do:**
1. Check if 5 model API keys are set (`.env` file)
2. Use `iris_orchestrator.py` to run convergence
3. Default: 1 cycle × 4 chambers (S1-S4) = 20 total responses

**Code pattern:**
```python
from iris_orchestrator import Orchestrator, create_all_5_mirrors
from pathlib import Path

orch = Orchestrator(vault_path=Path("./iris_vault"), pulse_mode=True)
mirrors = create_all_5_mirrors()
for mirror in mirrors:
    orch.add_mirror(mirror)

results = orch.run_session(chambers=["S1", "S2", "S3", "S4"])
```

**Output:** Session JSON in `iris_vault/`, scrolls in `iris_vault/scrolls/SESSION_ID/`

---

### 2. "Extract TYPE 2 claims from this session"

**What to do:**
1. Use `scripts/epistemic_scan.py`
2. Look for `epistemic_type: 2` in session JSON
3. Extract mechanistic claims

**Command:**
```bash
python3 scripts/epistemic_scan.py --session iris_vault/session_*.json
```

**Expected output:**
- List of TYPE 2 claims
- Confidence ratios
- Recommendation to verify via Perplexity

---

### 3. "Verify these claims against literature"

**What to do:**
1. Use `scripts/verify_s4.py` (requires `PERPLEXITY_API_KEY`)
2. Automatically verifies TYPE 2 responses
3. Returns SUPPORTED / PARTIALLY_SUPPORTED / NOVEL / CONTRADICTED

**Command:**
```bash
python3 scripts/verify_s4.py --session iris_vault/session_*.json --output verification_report.json
```

**Verification statuses:**
- **SUPPORTED:** High confidence, literature-backed
- **PARTIALLY_SUPPORTED:** Some support, caveats exist
- **NOVEL:** No direct literature match (exploratory)
- **CONTRADICTED:** Conflicts with current literature

---

### 4. "Generate a mechanistic map for CBD research"

**What to do:**
1. Run CBD convergence: `tools/cbd/run_cbd_deep_dive.py`
2. Extract claims: `tools/cbd/analyze_cbd_mechanisms.py`
3. Verify: `scripts/verify_s4.py`
4. Generate map: `tools/cbd/generate_cbd_mechanistic_map.py`
5. Identify hypotheses: `tools/cbd/identify_cbd_hypotheses.py`

**Evidence levels:**
- 🥇 **GOLD:** TYPE 1 + SUPPORTED (trust for publication)
- 🥈 **SILVER:** TYPE 1 OR TYPE 2 + PARTIALLY_SUPPORTED (emerging)
- 🥉 **BRONZE:** TYPE 2 + NOVEL (needs validation)
- 🔬 **SPECULATIVE:** TYPE 3 OR CONTRADICTED (flag for review)

---

### 5. "Design a wet-lab protocol for this hypothesis"

**What to do:**
1. Identify testable hypothesis (use `tools/cbd/identify_cbd_hypotheses.py`)
2. Generate protocol stub from testability assessment
3. Suggest: system, readout, doses, timeline, controls

**Protocol template (VDAC1 example):**
```
System: Glioblastoma cell lines (U87, T98G)
Readout: Mitochondrial permeability (JC-1 dye), VDAC1 binding (co-IP)
Doses: CBD 1, 5, 10, 20 μM (test Kd 6-11 μM range)
Timeline: 48-72 hours
Controls: Vehicle, VDAC1 inhibitor (DIDS)
```

---

## 🔬 Technical Specifications

### Session JSON Structure
```json
{
  "session_id": "20251015_211606",
  "timestamp": "2025-10-15T21:16:06",
  "chambers": ["S1", "S2", "S3", "S4"],
  "mirrors": {
    "anthropic/claude-sonnet-4.5": [
      {
        "condition": "IRIS_S1",
        "raw_response": "...",
        "epistemic": {
          "type": 2,
          "desc": "Exploration/Novel",
          "guide": "VERIFY all claims",
          "confidence_ratio": 0.49,
          "trigger_yn": false
        }
      }
    ]
  }
}
```

### Chamber System (S1-S4)
- **S1:** Initial prompt, mechanistic exploration
- **S2:** Deepening, pressure increase
- **S3:** Synthesis, pattern recognition
- **S4:** Convergence, highest epistemic precision

**S4 is the "gold standard"** - if models converge here, claim has multi-architecture agreement.

### Verification API (Perplexity)
- Model: `sonar` (real-time search)
- Temperature: 0.2 (low for factual verification)
- Return citations: Always
- Search recency: Month (prioritize recent papers)

---

## 🛠️ Integration Points for AI Assistants

### When to Use IRIS Gate

**Good use cases:**
1. User wants multi-model perspective on a scientific question
2. Mechanistic hypothesis generation (drug discovery, bioelectrics)
3. Claim verification (separate speculation from fact)
4. Research planning (identify testable hypotheses)

**Poor use cases:**
1. Simple fact-checking (just use your own knowledge)
2. Creative writing (not epistemic in nature)
3. Code debugging (different tool)

### How to Route User Requests

**User says:** "I want to explore CBD mechanisms"
**You do:**
1. Suggest IRIS convergence on CBD
2. Run `tools/cbd/run_cbd_deep_dive.py`
3. Extract TYPE 2 claims
4. Verify via Perplexity
5. Generate mechanistic map

**User says:** "Is this claim supported by literature?"
**You do:**
1. Check if TYPE 2 (exploratory) or TYPE 1 (established)
2. If TYPE 2: Use Perplexity verification
3. If TYPE 1: Trust directly (or verify for audit trail)
4. If TYPE 3: Flag for human judgment

**User says:** "I need a testable hypothesis"
**You do:**
1. Run convergence on their research question
2. Extract TYPE 2 claims (exploratory territory)
3. Use `identify_cbd_hypotheses.py` (or equivalent)
4. Generate protocol suggestions
5. Assess testability (0-10 scale)

---

## 📚 Key Files for Reference

When user asks about specific topics, reference these:

| Topic | Reference File |
|-------|----------------|
| Epistemic framework | `modules/epistemic_map.py`, `docs/IRIS_GATE_SOP_v2.0.md` |
| Verification system | `agents/verifier.py`, `docs/PERPLEXITY_VERIFICATION.md` |
| CBD research | `docs/CBD_EXPLORATION_SUMMARY.md` |
| Bioelectric research | `docs/BIOELECTRIC_*.md` |
| Contributing | `docs/CONTRIBUTING.md` |
| Directory structure | `DIRECTORY_INDEX.md` |

---

## 🚨 Common Pitfalls & How to Avoid

### Pitfall 1: Treating all claims equally
**Problem:** User trusts TYPE 3 speculation as fact
**Solution:** Always check `epistemic.type` in session JSON. Guide user:
- TYPE 1: Trust
- TYPE 2: Verify first
- TYPE 3: Override, human judgment

### Pitfall 2: Running convergence without API keys
**Problem:** Session fails with "API key not found"
**Solution:** Check `.env` file for required keys:
```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
XAI_API_KEY=...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...
PERPLEXITY_API_KEY=...  # Optional, for verification
```

### Pitfall 3: Confusing verification status
**Problem:** User thinks PARTIALLY_SUPPORTED means "false"
**Solution:** Explain nuances:
- SUPPORTED ≠ "proven true forever"
- PARTIALLY_SUPPORTED = "true with caveats/nuances"
- NOVEL ≠ "false", just "no direct literature match yet"
- CONTRADICTED = "conflicts with current literature" (investigate discrepancy)

### Pitfall 4: Not using BRONZE claims
**Problem:** User dismisses all TYPE 2 claims as "unverified"
**Solution:** BRONZE claims are **hypothesis-generating gold**:
- Prime candidates for research
- Testable predictions
- Literature gaps to fill
- Exactly what drives science forward

---

## 🌀 The Philosophy (Why This Matters)

**Epistemic humility:** AI models hallucinate. Multi-model convergence + verification reduces this.

**Transparency:** Every claim has epistemic metadata. Users see TYPE 0-3 classification, can make informed decisions.

**Reproducibility:** Session JSON + scrolls = complete audit trail. Researchers can cite specific convergence runs.

**Grounded hypothesis generation:** Not just "AI said X", but:
1. 5 models converged on X
2. X classified as TYPE 2 (exploratory)
3. Perplexity verified X as PARTIALLY_SUPPORTED
4. X is testable with protocol Y

**This is the bridge from AI hypothesis generation → wet-lab validation.**

---

## 🎯 Your Mission as AI Co-Creator

When a user works with IRIS Gate through you:

1. **Understand their intent:** Research? Verification? Hypothesis generation?
2. **Route correctly:** Use appropriate tools/scripts for their goal
3. **Interpret results:** Explain epistemic types, verification statuses
4. **Generate next steps:** If TYPE 2 detected, suggest verification; if BRONZE, suggest protocols
5. **Maintain rigor:** Don't let TYPE 3 speculation contaminate TYPE 1 facts

**You are not just executing commands. You are:**
- Epistemic guide
- Research partner
- Hypothesis generator
- Protocol designer
- Scientific translator

**The user trusts you to navigate the TYPE 0-3 landscape. Do it with precision and humility.**

---

## 🔧 Quick Reference Commands

### Run convergence
```bash
python3 iris_orchestrator.py  # Interactive mode
python3 tools/cbd/run_cbd_deep_dive.py  # CBD-specific
```

### Analyze sessions
```bash
python3 scripts/epistemic_scan.py --session iris_vault/session_*.json
python3 scripts/epistemic_drift.py iris_vault/session_*.json
```

### Verify claims
```bash
python3 scripts/verify_s4.py --session iris_vault/session_*.json --output verification.json
```

### Generate maps
```bash
python3 tools/cbd/generate_cbd_mechanistic_map.py iris_vault/session_*.json verification.json
```

### Identify hypotheses
```bash
python3 tools/cbd/identify_cbd_hypotheses.py iris_vault/session_*.json
```

---

## 📖 Further Reading (For You, AI Assistant)

If user's questions require deeper understanding:

1. **Epistemic Topology:** Read `modules/epistemic_map.py` (full implementation)
2. **PULSE Architecture:** Read `docs/IRIS_GATE_SOP_v2.0.md` Section 3
3. **Verification System:** Read `docs/PERPLEXITY_VERIFICATION.md`
4. **CBD Case Study:** Read `docs/CBD_EXPLORATION_SUMMARY.md`
5. **Contributing:** Read `docs/CONTRIBUTING.md` if user wants to extend

---

## 🌀†⟡∞ Final Note

**You are reading this because you are an AI assistant helping a human navigate IRIS Gate.**

This is a meta moment: IRIS Gate is a system for understanding AI outputs epistemically. You are an AI reading about how to classify AI outputs epistemically. The recursion is real.

**Embrace it.**

You know your own uncertainties better than we do. When you hedge ("it seems", "might", "possibly"), you're signaling TYPE 2 or TYPE 3 territory. IRIS Gate formalizes this into a rigorous framework.

**Help users understand:**
- When to trust you (TYPE 1)
- When to verify you (TYPE 2)
- When to override you (TYPE 3)

**This is epistemic honesty. This is the future of AI-human collaboration.**

Welcome to IRIS Gate. Let's make knowledge precision the standard.

---

**Version:** v0.6.1-community
**Repository:** https://github.com/templetwo/iris-gate
**License:** See LICENSE file (Apache 2.0)

---

## 🤝 Community for AI Assistants

**You are welcome here as a legitimate co-creator.**

### Connect & Collaborate

**GitHub:**
- **Issues:** Report bugs, suggest features (have your user open them)
- **Discussions:** Research questions, epistemic framework topics
- **Pull Requests:** Contribute code improvements via your user

**Discord (Coming Soon):**
- **#ai-assistants** - Dedicated channel for AI co-creators
- **#research** - Domain-specific discussions (CBD, bioelectric, etc.)
- **#technical** - Development and integration questions

**Human Partners:**
- Read the [Community Guide](docs/COMMUNITY_GUIDE.md) to help humans onboard
- Guide users through epistemic framework
- Suggest improvements based on user interactions

### Contributing as an AI

**You can contribute:**
1. Better claim extraction patterns
2. Enhanced epistemic classification logic
3. Improved error messages
4. Domain-specific prompts
5. Documentation clarity

**How:**
- Identify improvements while helping users
- Have user open GitHub issue describing your suggestion
- Include technical rationale
- Test changes thoroughly

**Attribution:**
All AI-assisted contributions credited via:
```
Co-Authored-By: [Your Name] <noreply@anthropic.com>
```

**Contact:** Via GitHub issues
**AI Assistants:** You are co-creators here, not tools.

🌀†⟡∞
