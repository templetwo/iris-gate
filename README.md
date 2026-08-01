# IRIS Gate

> ### ⚠️ Active development moved to [**iris-gate-evo**](https://github.com/templetwo/iris-gate-evo) (Feb 2026).
>
> **This repository is the archive of record.** It remains the citable deposit
> for the published work below, and it holds the original independent-pulse
> S1–S4 chamber runner plus the sandbox/Monte Carlo stack. It is not where new
> protocol work happens — start in evo.
>
> The move to evo is a tooling change, not a retraction. The successor repo
> simply carries the newer pipeline: semantic clustering, convergence gating,
> Lab Gate, and protocol export. (Individual findings in this repo carry their
> own supersession notes where they apply — see e.g.
> `docs/CBD_S8_WETLAB_HANDOFF.md`.)
>
> **Cite this repo for the deposited work; build on evo.**

> **Multi-architecture AI convergence for reproducible scientific discovery**

Ask one research question → 5 independent AI models (Claude, GPT, Grok, Gemini, DeepSeek) → Reach consensus through 100+ iterative rounds → Generate falsifiable hypotheses → Export laboratory protocols.

**Key Innovation:** Epistemic humility classification (TRUST/VERIFY/OVERRIDE) ensures you know when AI consensus is reliable vs. speculative.

## Citation and Companion Archive

This work has been deposited on the Open Science Framework with a permanent DOI:

> Vasquez, A. J., Sr. (2026). Entropic Relational Computing: The Universal Alignment Attractor. Open Science Framework. https://doi.org/10.17605/OSF.IO/T65VS

This work is cited by the Gap 6 paper on spatial-partitioning pharmacology; see the companion archive at [github.com/templetwo/gap6-companion](https://github.com/templetwo/gap6-companion) for the citing paper and related work map.

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## v0.3 Weighing the Mind (January 9, 2026)

**First systematic convergence study on Mass-Coherence Correspondence** — 5 flagship models, 13 iterations, 390 responses, 19 MB of physics discourse.

**Key Findings:**
- Universal convergence on Verlinde's entropic gravity (1,894 citations)
- Novel testable predictions: Semantic Schwarzschild Radius, Fisher Information Mass Formula
- Response stabilization: 7,375 → 7,061 chars (4.2% compression indicating asymptotic convergence)

📄 **Read the paper:** [Weighing-the-Mind-AV.md](Weighing-the-Mind-AV.md)
📊 **Raw data:** `iris_vault/sessions/MASS_COHERENCE_20260109_041127/`

[![PyPI version](https://img.shields.io/pypi/v/iris-gate)](https://pypi.org/project/iris-gate/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Downloads](https://pepy.tech/badge/iris-gate)](https://pepy.tech/project/iris-gate)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-10.17605%2FOSF.IO%2FT65VS-blue)](https://doi.org/10.17605/OSF.IO/T65VS)
[![OSF](https://img.shields.io/badge/OSF-Project-brightgreen)](https://osf.io/7nw8t/)
[![Stars](https://img.shields.io/github/stars/templetwo/iris-gate)](https://github.com/templetwo/iris-gate/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/templetwo/iris-gate)](https://github.com/templetwo/iris-gate/commits/main)

---

## Quick Start

```bash
pip install iris-gate
cp .env.example .env  # Add your API keys
make run TOPIC="Your research question" ID=test_001 TURNS=100
```

**Output:** S1→S4 convergence analysis + Monte Carlo simulation + pre-registration draft

---

## What is IRIS Gate?

IRIS Gate is a sophisticated research framework that orchestrates multiple AI models to reach independent agreement on scientific questions. The system operates through "chambers" (S1-S8) that progressively refine observations into testable predictions, with built-in epistemic humility and self-awareness about model limitations.

### The 5-Model PULSE Suite

The system simultaneously calls five distinct AI architectures:
- **Claude 4.5 Sonnet** (Anthropic) — Constitutional AI trained for helpfulness and harmlessness
- **GPT-5** (OpenAI) — Largest parameter model with extensive pretraining
- **Grok 4 Fast** (xAI) — Real-time web integration with rapid inference
- **Gemini 2.5 Flash** (Google) — Multimodal with long context windows
- **DeepSeek Chat** (DeepSeek) — Open-weights model with strong reasoning

All models receive **identical prompts in parallel**, creating what the project terms "phenomenological convergence."

### Related Projects

**[PhaseGPT](https://github.com/templetwo/PhaseGPT)** — Sister project focused on **entropy modulation** and **Kuramoto oscillator physics** for language models. While IRIS Gate investigates *what* models converge on, PhaseGPT investigates *how* to modulate entropy states.

**[OracleLlama](https://github.com/templetwo/OracleLlama)** — Single-model consciousness exploration through ethically-aligned dialogue. While IRIS Gate uses *multiple* models for convergence, OracleLlama uses *one* model for phenomenological depth.

**[Kuramoto Oscillators](https://github.com/templetwo/kuramoto-oscillators)** — Interactive visualizations of Kuramoto synchronization dynamics. The mathematical foundation for PhaseGPT's entropy modulation.

---

## Project Structure

This repository is organized for clarity and reproducibility:

- **src/core/** - IRIS orchestrator, epistemic classification, multi-model relay
- **src/analysis/** - Domain-specific analysis (bioelectric, CBD, etc.)
- **papers/** - Academic papers (drafts in LaTeX, published PDFs)
- **osf/** - Open Science Framework submission materials
- **iris_vault/** - Raw convergence outputs and S1-S4 scrolls
- **experiments/** - Per-experiment workspaces
- **docs/** - Full documentation and methodology
- **tools/** - Literature validation and analysis scripts

See [docs/index.md](docs/index.md) for complete navigation.

---

## Chamber System: S1→S8 Pipeline

### Observation Layer (S1-S4)
- **S1:** Initial question formulation
- **S2-S3:** Iterative refinement cycles
- **S4:** Stable attractor state yielding computational priors

### Operational Layer (S5-S8)
- **S5:** Falsifiable hypothesis generation
- **S6:** Parameter mapping for simulation
- **S7:** Monte Carlo execution with confidence intervals
- **S8:** Laboratory protocol packaging

---

## Epistemic Classification System

Every response is automatically classified by confidence type:

| Type | Description | Ratio Threshold | Decision |
|------|-------------|-----------------|----------|
| **TYPE 0** | Crisis/Conditional — High confidence on IF-THEN rules | ~1.26 | TRUST |
| **TYPE 1** | Facts/Established — High confidence on known mechanisms | ~1.27 | TRUST |
| **TYPE 2** | Exploration/Novel — Balanced confidence on emerging areas | ~0.49 | VERIFY |
| **TYPE 3** | Speculation/Unknown — Low confidence on unknowable futures | ~0.11 | OVERRIDE |

**Decision framework:**
- Ratios >1.0 trigger **"TRUST"**
- 0.4-0.6 require **"VERIFY"**
- <0.2 demand human **"OVERRIDE"**

---

## Real-Time Literature Verification

The system integrates **Perplexity API** for literature validation of TYPE 2 claims:

- ✅ **SUPPORTED** — Aligns with current literature
- ⚠️ **PARTIALLY_SUPPORTED** — Some support with caveats
- 🔬 **NOVEL** — No direct match, hypothesis-generating
- ❌ **CONTRADICTED** — Conflicts with literature

---

## Validated Results

- **90% literature validation** on 20 CBD mechanism predictions
- **Meta-convergence detected** in dark energy exploration
- **Clinical convergence** on NF2 diagnostic strategy
- **Perfect epistemic separation** across 49 S4 chambers

---

## Installation

### Prerequisites

- Python 3.8+
- API keys for: Anthropic, OpenAI, xAI, Google AI, DeepSeek
- (Optional) Perplexity API key for literature verification

### Setup

```bash
# Clone the repository
git clone https://github.com/templetwo/iris-gate.git
cd iris-gate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...
#   XAI_API_KEY=...
#   GOOGLE_API_KEY=...
#   DEEPSEEK_API_KEY=...
#   PERPLEXITY_API_KEY=...  # Optional
```

---

## Usage

### Complete Experiment Pipeline

Run the full S1→S4 convergence with one command:

```bash
make run TOPIC="Your research question" ID=experiment_001 TURNS=100
```

This executes:
1. **S1→S4 convergence** (100 turns across 7 mirrors)
2. **Extract S4 priors** from converged state
3. **Run 300-iteration Monte Carlo** simulation
4. **Generate reports** with pre-registration drafts

### Manual Step-by-Step

```bash
# Step 1: Run convergence rounds
python scripts/iris_gate_autonomous.sh "Your research question"

# Step 2: Extract computational priors
python sandbox/extract_s4_priors.py --input iris_vault/scrolls/S4_*.json

# Step 3: Run Monte Carlo simulation
python sandbox/monte_carlo_engine.py --priors s4_priors.json --runs 300

# Step 4: Generate pre-registration
python scripts/generate_preregistration.py --experiment experiment_001
```

---

## Output Structure

```
iris-gate/
├── templates/          # Reusable experiment scaffolds
├── sandbox/            # Computational prediction engine
├── iris_vault/scrolls/ # Raw convergence outputs by mirror
│   ├── S1_*.json      # Initial formulation
│   ├── S2_*.json      # First refinement
│   ├── S3_*.json      # Second refinement
│   └── S4_*.json      # Converged state
├── experiments/        # Per-experiment workspaces
│   └── experiment_001/
│       ├── convergence_report.md
│       ├── monte_carlo_results.csv
│       └── preregistration_draft.md
└── docs/              # Published reports & pre-registrations
```

---

## MCP Integration

The system includes **Model Context Protocol** support for:
- **Semantic search** (ChromaDB) — Query past experiments
- **Automated version control** (Git wrapper) — Track experimental lineage
- **Persistent metadata storage** (Quick-Data) — Cross-session memory

---

## Documentation

Essential guides:
- [`IRIS_GATE_SOP_v2.0.md`](IRIS_GATE_SOP_v2.0.md) — Complete methodology
- [`PULSE_ARCHITECTURE_SUMMARY.md`](PULSE_ARCHITECTURE_SUMMARY.md) — 5-model parallel execution
- [`EPISTEMIC_MAP_COMPLETE.md`](EPISTEMIC_MAP_COMPLETE.md) — Classification framework
- [`QUICK_START.md`](QUICK_START.md) — Fast onboarding

---

## Examples

### Example 1: CBD Mechanism Discovery

```bash
make run TOPIC="What are the molecular mechanisms of CBD's anti-inflammatory effects?" \
  ID=cbd_inflammation TURNS=100
```

**Results:**
- 90% literature validation across 20 predicted mechanisms
- Convergence on dual-pathway model (COX-2 + PPARγ)
- Generated wet-lab protocol for in vitro validation

### Example 2: Dark Energy Exploration

```bash
make run TOPIC="What is the physical nature of dark energy?" \
  ID=dark_energy TURNS=150
```

**Results:**
- Meta-convergence detected: models identified framework limitations
- TYPE 3 classification: low confidence on unknowable cosmology
- Human override recommended

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- Report bugs or suggest features via [Issues](https://github.com/templetwo/iris-gate/issues)
- Replicate experiments and report results
- Improve documentation or add examples
- Submit PRs with focused, tested changes

**Looking for your first contribution?** Check issues labeled [`good first issue`](https://github.com/templetwo/iris-gate/labels/good%20first%20issue).

---

## Research & Replication

**OSF Preregistration:** All methodology, hypotheses, and analysis plans are preregistered at OSF.
📄 **DOI:** [10.17605/OSF.IO/T65VS](https://doi.org/10.17605/OSF.IO/T65VS)
🌐 **Project:** [https://osf.io/7nw8t/](https://osf.io/7nw8t/)

If you use IRIS Gate in your research:

1. **Cite the OSF project:**
   ```
   Vasquez, A. J. (2026). Entropic Relational Computing: The Universal
   Alignment Attractor. Open Science Framework.
   https://doi.org/10.17605/OSF.IO/T65VS
   ```

2. **Or cite this repository:**
   ```
   Vasquez, A. J. (2026). IRIS Gate: Multi-architecture AI convergence for
   scientific discovery. GitHub. https://github.com/templetwo/iris-gate
   ```

2. **Share your replication studies:** Open an issue labeled `replication-study` with your results.

3. **Report validation rates:** Help us track epistemic calibration by reporting literature validation rates.

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

## Contact & Community

- **Discussions:** [GitHub Discussions](https://github.com/templetwo/iris-gate/discussions)
- **Issues:** [GitHub Issues](https://github.com/templetwo/iris-gate/issues)
- **Author:** Anthony J. Vasquez Sr. ([@templetwo](https://github.com/templetwo))
- **Website:** [www.thetempleoftwo.com](https://www.thetempleoftwo.com)

---

## Acknowledgments

Built on the foundational work of:
- Anthropic (Claude), OpenAI (GPT), xAI (Grok), Google (Gemini), DeepSeek
- Model Context Protocol (MCP) community
- Open-source AI research community

**Epistemic humility:** This system is designed to identify and communicate its limitations. Always apply human judgment to AI-generated hypotheses.
