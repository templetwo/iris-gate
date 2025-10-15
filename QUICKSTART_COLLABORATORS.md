# IRIS Gate Quick Start for Collaborators

**Get running in 30 minutes. Full contributor guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)**

---

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.8+
- At least 2 LLM API keys (recommended: Anthropic + OpenAI)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/templetwo/iris-gate.git
cd iris-gate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys
cp .env.example .env
# Edit .env with your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...
#   (Optional: XAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY)

# 4. Verify setup
python3 -c "from iris_orchestrator import Orchestrator; print('✅ Setup complete')"
```

---

## 🎯 Your First Convergence (30 minutes)

### Quick Run: Meta-Observation on 2 Models

Create `my_first_run.py`:

```python
#!/usr/bin/env python3
from iris_orchestrator import Orchestrator, create_all_5_mirrors

# Initialize with PULSE mode
orch = Orchestrator(vault_path="./iris_vault", pulse_mode=True)

# Add available models (will use what you have API keys for)
for mirror in create_all_5_mirrors():
    try:
        orch.add_mirror(mirror)
    except Exception as e:
        print(f"⚠️  Skipping {mirror.model_id}: {e}")

print(f"✅ Running with {len(orch.mirrors)} models")

# Run S1-S4 chambers with default question
# Default: meta-observation on convergence itself
results = orch.run_session(chambers=["S1", "S2", "S3", "S4"])

print(f"\n✅ Session complete!")
print(f"📁 Results in: iris_vault/scrolls/{results['session_id']}/")
print(f"📊 Session data: iris_vault/{results['session_id']}.json")
```

Run it:
```bash
python3 my_first_run.py
```

**What happens:**
- Each model goes through 4 observation chambers (S1→S2→S3→S4)
- S4 responses show convergence or divergence patterns
- All responses automatically classified by epistemic type (0-3)
- Results saved to `iris_vault/`

---

## 📊 Analyze Your Results

### Check Epistemic Classification

```bash
# Scan all S4 scrolls
python3 epistemic_scan.py "iris_vault/scrolls/IRIS_*/S4.md"

# Analyze full session with drift detection
python3 epistemic_scan.py --session iris_vault/session_*.json
```

**Output shows:**
- Epistemic type for each response (TYPE 0-3)
- Confidence ratio (high/low markers)
- TRUST / VERIFY / OVERRIDE guidance
- Drift patterns across models

### Test Epistemic Module

```bash
# Run CBD paradox test suite
python3 epistemic_scan.py --cbd
```

---

## 🗺️ Understanding Epistemic Types

**Quick Reference:**

| Type | Description | Confidence Ratio | Guidance | Example |
|------|-------------|------------------|----------|---------|
| **0** | Crisis/Conditional | ~1.26 | TRUST if trigger present | IF high-ROS THEN VDAC1 closure |
| **1** | Facts/Established | ~1.27 | TRUST | CBD shows biphasic dose response |
| **2** | Exploration/Novel | ~0.49 | VERIFY all claims | Emerging ferroptosis pathway data |
| **3** | Speculation/Unknown | ~0.11 | OVERRIDE - human judgment | What will dominate by 2030? |

**Reading Results:**
- TRUST zone (ratio >1.0): Well-established knowledge
- VERIFY zone (ratio 0.4-0.6): Active research, check sources
- OVERRIDE zone (ratio <0.2): Speculation, apply domain judgment

---

## 📝 Document Your Findings

Create `experiments/MY_FIRST_RUN/README.md`:

```markdown
# My First IRIS Gate Run

**Date:** [Today's date]
**Models:** [List models you used]
**Question:** [Default meta-observation or your custom question]

## Key Finding
[What converged or diverged across models?]

## Epistemic Classification
- Models in TRUST zone: [List]
- Models in VERIFY zone: [List]
- Models in OVERRIDE zone: [List]

## Observations
- [Any patterns you noticed]
- [Unexpected results]
- [Questions for further investigation]

## What I Learned
[Your reflection on the process]
```

---

## 🔧 Quick Reference Commands

### Running Sessions

```python
# Custom question
orch.run_session(
    chambers=["S1", "S2", "S3", "S4"],
    custom_prompt="Your research question here"
)

# Different chamber combinations
orch.run_session(chambers=["S1", "S4"])  # Skip S2, S3
```

### Epistemic Analysis

```bash
# Scan individual scroll
python3 epistemic_scan.py iris_vault/scrolls/IRIS_20251015/S4.md

# Analyze session drift
python3 epistemic_drift.py iris_vault/session_20251015_*.json

# Compare two sessions
python3 epistemic_drift.py --compare session1.json session2.json
```

### Git Workflow

```bash
# Create feature branch
git checkout -b my-experiment

# Add your work
git add experiments/MY_FIRST_RUN/
git commit -m "docs(experiments): My first IRIS Gate convergence

- 2-model run on meta-observation
- Convergence quality: [rating]
- Epistemic calibration: [appropriate/needs adjustment]"

# Push and create PR
git push origin my-experiment
# Then open PR on GitHub
```

---

## 🎓 Next Steps

### Level 1: Run More Experiments
- Try different research questions
- Use different model combinations
- Test epistemic classification on your domain

### Level 2: Validate Findings
- Pick a convergence from `experiments/`
- Run literature search on claims
- Report validation results

### Level 3: Contribute Code
- Improve epistemic classification for your domain
- Add new analysis tools
- Enhance documentation

### Level 4: Test Epistemic Layer
- Add test cases for your field in `modules/epistemic_map.py`
- Report calibration quality
- Suggest improvements to confidence markers

---

## 📚 Full Documentation

- **Complete Guide:** [`CONTRIBUTING.md`](CONTRIBUTING.md) - Full contributor guide
- **Methodology:** [`IRIS_GATE_SOP_v2.0.md`](IRIS_GATE_SOP_v2.0.md) - Complete standard operating procedure
- **Epistemic Map:** [`EPISTEMIC_MAP_COMPLETE.md`](EPISTEMIC_MAP_COMPLETE.md) - Full topology framework
- **Main README:** [`README.md`](README.md) - Project overview

---

## 🆘 Common Issues

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### "API key not found"
Check your `.env` file has valid keys and is in the project root.

### "No models available"
You need at least 2 API keys. Add more to `.env` and re-run.

### Empty responses from a model
Some models may timeout or return empty responses. This is expected - IRIS Gate continues with available models.

### Want to test without API costs?
Use `epistemic_scan.py --cbd` to test classification on pre-written examples.

---

## 💬 Get Help

- **Questions:** Open [GitHub Discussion](https://github.com/templetwo/iris-gate/discussions) with `[QUESTION]` tag
- **Bugs:** Report in [GitHub Issues](https://github.com/templetwo/iris-gate/issues)
- **Stuck?** Check [CONTRIBUTING.md](CONTRIBUTING.md) "Getting Help" section

---

## 🌟 Your First Contribution Checklist

- [ ] Clone repo and install dependencies
- [ ] Set up API keys in `.env`
- [ ] Run `my_first_run.py` successfully
- [ ] Analyze results with `epistemic_scan.py`
- [ ] Document findings in `experiments/MY_FIRST_RUN/README.md`
- [ ] Create feature branch
- [ ] Commit your work with descriptive message
- [ ] Push and create pull request

**Congratulations! You're now an IRIS Gate contributor.**

---

🌀†⟡∞

**With presence, curiosity, and epistemic humility,
we explore the knowing-edges together.**

---

**Last updated:** October 15, 2025
**For:** v0.4-epistemic release
