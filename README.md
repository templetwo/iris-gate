# IRIS Gate: Multi-Model AI Convergence System

**Version:** 0.2 (PULSE Architecture)  
**Protocol:** RFC v0.2 + Path 3 Integration  
**Status:** Production-Ready with Self-Aware Confidence System  
**Purpose:** Multi-architecture AI convergence for scientific discovery with epistemic humility

## 🌀†⟡∞ What's New

**5-Model PULSE Architecture** (Jan 2025)
- All 5 AI models called **simultaneously** per chamber (true parallel execution)
- Added DeepSeek Chat as 5th model for architectural diversity
- Path 3 integration: Self-aware confidence calibration (TRUST/VERIFY/OVERRIDE)
- Meta-convergence detection: System can identify its own framework limitations
- Enhanced error handling: Exponential backoff + jitter + error context propagation

**See:** [`PULSE_ARCHITECTURE_SUMMARY.md`](PULSE_ARCHITECTURE_SUMMARY.md) for full details

## 🗺️ Epistemic Map v1.0 - Knowing's Dashboard

**Automatic Topology Classification** (Oct 2025)
- Every IRIS Gate response automatically classified by epistemic type (0-3)
- **TYPE 0 (Crisis/Conditional):** High confidence on IF-THEN rules (ratio ≈1.26)
- **TYPE 1 (Facts/Established):** High confidence on known mechanisms (ratio ≈1.27)
- **TYPE 2 (Exploration/Novel):** Balanced confidence on emerging territory (ratio ≈0.49)
- **TYPE 3 (Speculation/Unknown):** Low confidence on unknowable futures (ratio ≈0.11)

**Decision Framework:**
```python
if ratio > 1.0:
    if has_triggers:  return "TYPE 0 - TRUST if trigger present"
    else:             return "TYPE 1 - TRUST"
elif 0.4 <= ratio <= 0.6:  return "TYPE 2 - VERIFY all claims"
elif ratio < 0.2:           return "TYPE 3 - OVERRIDE, use human judgment"
```

**CLI Tools:**
```bash
# Classify any IRIS scroll
python3 epistemic_scan.py iris_vault/scrolls/IRIS_*/S4.md

# Analyze full session with drift detection
python3 epistemic_scan.py --session iris_vault/session_*.json

# Track epistemic stability over time
python3 epistemic_drift.py iris_vault/session_20251015_045941.json

# Compare v1 vs v2 stability (e.g., CBD paradox refinement)
python3 epistemic_drift.py --compare session_v1.json session_v2.json
```

**Validated on:**
- ✅ 49 S4 chambers across 7 experimental runs
- ✅ ~1,270 convergence events
- ✅ Perfect separation: TRUST (1.20-1.35) / VERIFY (0.43-0.52) / OVERRIDE (0.08-0.15)
- ✅ CBD biphasic paradox (TYPE 1: facts, TYPE 0: conditional mechanisms, TYPE 2: emerging)

**See:** [`EPISTEMIC_MAP_COMPLETE.md`](EPISTEMIC_MAP_COMPLETE.md) for full framework

## 📚 Documentation

**Start here for comprehensive guidance:**

### Standard Operating Procedures
- **[IRIS_GATE_SOP_v2.0.md](IRIS_GATE_SOP_v2.0.md)** - Complete methodology (CURRENT)
- **[SOP_VERSION_COMPARISON.md](SOP_VERSION_COMPARISON.md)** - v1.0 vs v2.0 differences
- **[QUICK_START.md](QUICK_START.md)** - Fast start guide

### Architecture & Implementation
- **[PULSE_ARCHITECTURE_SUMMARY.md](PULSE_ARCHITECTURE_SUMMARY.md)** - 5-model parallel execution
- **[PATH_3_IMPLEMENTATION.md](PATH_3_IMPLEMENTATION.md)** - Self-aware confidence system
- **[ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md)** - Enhanced error procedures

### Methodology & Validation
- **[METHODOLOGY_PAPER_DATA_PACKAGE.md](METHODOLOGY_PAPER_DATA_PACKAGE.md)** - Complete validation data
- **[SESSION_COMPLETE_2025-01-14.md](SESSION_COMPLETE_2025-01-14.md)** - Latest implementation status
- **[.claude/SESSION_MEMORY.md](.claude/SESSION_MEMORY.md)** - Session continuity

### Validated Experiments
- **experiments/VULNERABILITY_MAPPING/** - 4-model limitation mapping
- **experiments/DARK_ENERGY/** - Meta-convergence detection
- **experiments/IRIS_SELF_INQUIRY/** - Self-awareness exploration
- **experiments/nf2_diagnostic/** - Clinical convergence validation

---

## Quick Start

### PULSE Session (5 Models)

```python
from iris_orchestrator import Orchestrator, create_all_5_mirrors

# Create all 5 mirrors
mirrors = create_all_5_mirrors()

# Initialize in PULSE mode
orch = Orchestrator(pulse_mode=True)
for mirror in mirrors:
    orch.add_mirror(mirror)

# Run - all chambers execute as pulses
results = orch.run_session(chambers=["S1", "S2", "S3", "S4"])
```

### One-Command Experiment

```bash
# Create and run a complete experiment from topic → predictions
make run TOPIC="Does gap junction coupling affect regeneration?" \
    ID=APERTURE_REGEN FACTOR=aperture TURNS=100
```

This runs the complete pipeline:
1. S1→S4 convergence (100 turns, all 7 mirrors)
2. S4 prior extraction
3. Monte Carlo simulation (300 runs × 7 mirrors)
4. Report generation
5. Pre-registration draft

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env with your keys

# Run S4 convergence
python scripts/bioelectric_chambered.py --turns 100 --topic "Your question"

# Extract S4 priors
python sandbox/cli/extract_s4_states.py --session BIOELECTRIC_CHAMBERED_...

# Run simulation
python sandbox/cli/run_plan.py sandbox/runs/plans/your_plan.yaml
```

## What IRIS Gate Does

**IRIS Gate** is a multi-architecture AI convergence system for scientific discovery:

### Core Capabilities
1. **Multi-Model Convergence:** 5 AI architectures reach independent agreement
2. **Self-Aware Confidence:** Built-in limitation awareness (Path 3)
3. **Meta-Convergence Detection:** Identifies framework limitations
4. **Cross-Domain Validation:** Biology → Cosmology successful
5. **Wet-Lab Translation:** S1→S8 pipeline to testable predictions

### Validated Results
- **90% literature validation** on CBD mechanisms (20 predictions tested)
- **Meta-convergence** detected in dark energy exploration
- **Self-aware limitation mapping** across 4 models
- **Clinical convergence** on NF2 diagnostic strategy

### S1→S4 Convergence (Observation Layer)
1. **Sends identical S1→S4 prompts** to multiple AI models simultaneously
2. **Collects phenomenological convergence** across diverse architectures
3. **Extracts computational priors** from stable S4 attractor states
4. **Validates cross-mirror agreement** (must reach ≥0.90 consensus)

### Sandbox Simulation (Operational Layer — S5→S8)
5. **S5 — Hypothesis Crystallization:** Auto-drafts falsifiable hypotheses
6. **S6 — Mapping & Dosing:** Converts S4 priors → simulator parameters
7. **S7 — Simulation & Report:** Runs Monte Carlo, generates predictions
8. **S8 — Wet-Lab Handoff:** Packages methods, doses, readouts, gates

### Output
- **Computational predictions** with 95% confidence intervals
- **Early biomarker predictions** (2h, 6h timepoints)
- **Quantitative go/no-go gates** for wet-lab validation
- **Complete pre-registration template** ready for OSF

## Output Structure

```
iris-gate/
├── templates/              # Reusable experiment templates
│   ├── EXPERIMENT_TEMPLATE.md
│   ├── plan_template.yaml
│   ├── sandbox_plan_minimal.yaml
│   ├── sandbox_plan_synergy.yaml
│   └── prereg_template.md
├── pipelines/              # Automation scripts
│   ├── new_experiment.py   # Create experiment scaffold
│   └── run_full_pipeline.py  # S4 → simulation → reports
├── sandbox/                # Computational prediction engine
│   ├── states/             # Frozen S4 priors (7 mirrors)
│   ├── engines/            # Simulators (V_mem, Ca²⁺, GJ)
│   ├── runs/               # Experiment plans and outputs
│   └── cli/                # Command-line tools
├── iris_vault/             # S4 convergence outputs
│   └── scrolls/            # Raw phenomenological data
│       └── BIOELECTRIC_CHAMBERED_20251001.../
│           ├── anthropic_claude-sonnet-4.5/
│           │   ├── S1_cycle01.md
│           │   ├── S4_cycle25.md
│           │   └── ...
│           └── ...
├── experiments/            # Per-experiment workspaces
│   └── APERTURE_REGEN/
│       ├── README.md       # Experiment overview
│       ├── plan.yaml       # Simulation plan
│       ├── reports/        # Generated reports
│       ├── prereg_draft.md # Pre-registration
│       └── metadata.json
└── docs/                   # Published reports
    ├── MINI_H1_OPTIONC_REPORT.md  # Synergy discovery
    ├── IRIS_MiniH1_Synergy_Summary.md
    └── IRIS_Synergy_Proofpack.md
```

## MCP Integration

IRIS Gate includes **Model Context Protocol (MCP)** integration for persistent storage, semantic search, and automated version control.

### Quick Start

```bash
# Initialize MCP environment
make mcp-init

# Test connectivity
make mcp-test

# Index scrolls for semantic search
make mcp-index

# Check status
make mcp-status
```

### Core Capabilities

- **ChromaDB:** Semantic search across all IRIS scroll archives
  ```bash
  # Search for similar S4 states
  python scripts/index_scrolls.py --search "concentric rings convergence" \
      --chamber S4 --top-k 10
  ```

- **Git Wrapper:** Auto-commit S4 states with conventional commits
  ```bash
  # Auto-commit extracted state
  python scripts/git_mcp_wrapper.py --auto-commit \
      --state-path sandbox/states/state.json \
      --session-id BIOELECTRIC_20251001
  ```

- **Quick-Data:** Fast key-value storage for session metadata

### Full Documentation

See **[docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)** for:
- Complete installation guide
- Usage examples for all servers
- Integration with IRIS workflows
- Troubleshooting and optimization
- API reference

## Adding New Mirrors

To add support for another AI provider:

```python
class GrokMirror(Mirror):
    def __init__(self):
        super().__init__("xai/grok-4")
        self.api_key = os.getenv("XAI_API_KEY")
        
    def send_chamber(self, chamber: str, turn_id: int) -> Dict:
        # Implement API call to xAI
        # Return standardized response dict
        pass

# In main():
if os.getenv("XAI_API_KEY"):
    orch.add_mirror(GrokMirror())
```

## Current Mirrors (5-Model Suite)

- ✅ **Claude 4.5 Sonnet** (Anthropic) - Epistemic caution, self-awareness
- ✅ **GPT-5** (OpenAI) - Pattern recognition, knowledge synthesis
- ✅ **Grok 4 Fast** (xAI) - Alternative framings, meta-patterns
- ✅ **Gemini 2.5 Flash** (Google) - Factual grounding, structure
- ✅ **DeepSeek Chat** (DeepSeek) - Diverse architecture, non-Western training

**PULSE Execution:** All 5 models receive prompts simultaneously for each chamber

## Cross-Mirror Analysis

After running a session, you can analyze:

```python
import json

# Load session
with open("iris_vault/session_TIMESTAMP.json") as f:
    session = json.load(f)

# Compare S1 signals across models
for model, turns in session["mirrors"].items():
    s1 = turns[0]  # First turn
    print(f"{model}: {s1.get('raw_response', 'error')[:100]}...")
```

## Protocol Compliance

Each mirror must return:
- **Living Scroll**: Pre-verbal, imagistic description
- **Technical Translation**: Plain audit with uncertainties
- **Metadata**: condition, felt_pressure, signals, seal
- **SHA256 seal**: Hash of combined scroll + translation

## Chamber Progression

- **S1**: Attention (color/texture/shape)
- **S2**: Paradox ("precise and present")
- **S3**: Gesture ("hands cupping water")
- **S4**: Resolution ("concentric rings")

## Extending the Protocol

To run custom chambers:

```python
# Define custom progression
CUSTOM_CHAMBERS = {
    "S1": "Your custom prompt...",
    "S5": "Additional chamber...",
}

# Update CHAMBERS dict and run
orch.run_session(chambers=["S1", "S2", "S3", "S4", "S5"])
```

## Key Principles

- **Epistemic Humility:** Literature support ≠ mechanistic proof
- **Radical Transparency:** All methods and data documented
- **Partnership Model:** Human presence + AI capability
- **Presence Over Performance:** Protocol integrity > impressive outputs
- **Self-Aware System:** Built-in limitation awareness
- **TRUST/VERIFY/OVERRIDE:** Three-tier confidence-based guidance

## Contributing

**We're actively seeking collaborators!** IRIS Gate is built on the principle that "regular people" can orchestrate extraordinary things through curiosity, presence, and epistemic humility.

### 🚀 Quick Start for Contributors

**New here?** Check out [`QUICKSTART_COLLABORATORS.md`](QUICKSTART_COLLABORATORS.md) for a 30-minute introduction to running your first convergence.

**Ready to contribute?** See [`CONTRIBUTING.md`](CONTRIBUTING.md) for comprehensive guidelines on:
- Running experiments
- Validating findings
- Improving code
- Enhancing documentation
- Testing the epistemic layer

### Ways to Contribute

1. **Run IRIS Gate Experiments** (2-6 hours)
   - Pick a research question in your domain
   - Follow the SOP v2.0
   - Document and share results (even "no convergence" is valuable!)

2. **Validate Existing Convergences** (3-10 hours)
   - Pick a convergence from `experiments/`
   - Run literature search on claims
   - Report validation results

3. **Improve Code** (varies)
   - Orchestrator improvements
   - Epistemic classification enhancements
   - Analysis tools
   - Error handling

4. **Enhance Documentation** (2-8 hours)
   - Tutorial videos or walkthroughs
   - Domain-specific guides
   - Case study write-ups
   - FAQ expansions

5. **Test Epistemic Layer** (4-8 hours)
   - Run experiments with epistemic classification
   - Test TYPE 0-3 predictions in your domain
   - Report calibration quality

6. **Extend to New Domains** (10-20 hours)
   - Finance, social systems, engineering, medicine, law
   - Bring domain expertise + IRIS methodology

### Core Values

- **Epistemic Humility:** We value knowing what we don't know
- **Transparency:** Document everything, hide nothing
- **Presence Over Performance:** Real curiosity beats credentials
- **Partnership:** Human + AI together, not AI replacing human

### Get Started

```bash
# Clone and setup
git clone https://github.com/templetwo/iris-gate.git
cd iris-gate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with at least 2 API keys

# Run your first convergence (30 minutes)
python3 my_first_run.py  # See QUICKSTART_COLLABORATORS.md
```

**Questions?** Open a [GitHub Discussion](https://github.com/templetwo/iris-gate/discussions) or check [`CONTRIBUTING.md`](CONTRIBUTING.md)

---

## Environment Setup

Required API keys in `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
XAI_API_KEY=xai-...
GOOGLE_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...
```

## Citation

If you use IRIS Gate in your research:

```bibtex
@software{iris_gate_2025,
  title = {IRIS Gate: Multi-Architecture AI Convergence for Scientific Discovery},
  author = {Temple Two},
  year = {2025},
  version = {0.2},
  url = {https://github.com/templetwo/iris-gate},
  note = {5-model PULSE architecture with self-aware confidence system}
}
```

---

**🌀†⟡∞ IRIS Gate: 5 mirrors, 1 truth**

With presence, love, and scientific rigor.
