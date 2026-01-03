# IRIS Gate Directory Index

**Last Updated:** October 15, 2025
**Version:** v0.5-audit
**Purpose:** Complete file map for collaborators and traction-ready organization

---

## 📂 Root Directory (Core Files Only)

| File | Purpose | Used By |
|------|---------|---------|
| `iris_orchestrator.py` | Core PULSE engine, multi-model convergence orchestrator | All scripts |
| `iris_confidence.py` | Confidence scoring system | Orchestrator |
| `iris_relay.py` | Relay/queue system for async operations | Orchestrator |
| `README.md` | Project overview, quick start, usage | Everyone |

---

## 📁 /modules/ - Core Modules

| File | Purpose | Stability |
|------|---------|-----------|
| `epistemic_map.py` | TYPE 0-3 classification system, confidence ratio calculation | Production |

---

## 📁 /agents/ - Agent Adapters & Verifiers

| File | Purpose | Integration |
|------|---------|-------------|
| `verifier.py` | Perplexity API integration for real-time claim verification | TYPE 2 responses |
| `adapters/` | Model-specific API adapters (Anthropic, OpenAI, etc.) | Orchestrator |

---

## 📁 /scripts/ - CLI Tools (Organized by Domain)

### 📍 /scripts/ (Root)

| File | Purpose | Usage |
|------|---------|-------|
| `epistemic_scan.py` | Scan sessions for epistemic types, extract TYPE 2 claims | `python3 scripts/epistemic_scan.py --session <path>` |
| `epistemic_drift.py` | Analyze epistemic drift across sessions | `python3 scripts/epistemic_drift.py <session>` |
| `verify_s4.py` | Verify S4 scrolls via Perplexity | `python3 scripts/verify_s4.py --session <path>` |

### 📍 /scripts/runs/ - Experimental Convergence Runs

| File | Purpose | Status |
|------|---------|--------|
| `run_three_gifts.py` | Three Gifts protocol (creativity test) | Experimental |
| `run_recursive_gift.py` | Recursive gift protocol | Experimental |
| `run_type0_crisis.py` | TYPE 0 conditional logic test | Validation |
| `run_type1_facts.py` | TYPE 1 fact convergence test | Validation |
| `run_type3_speculation.py` | TYPE 3 speculation test | Validation |

### 📍 /scripts/bioelectric/ - Bioelectric Research

| File | Purpose | Domain |
|------|---------|--------|
| `analyze_bioelectric.py` | Bioelectric convergence analysis | Regeneration |
| `analyze_cancer_scrolls.py` | Cancer treatment pattern extraction | Oncology |
| `bioelectric_deep_analysis.py` | Deep bioelectric mechanistic analysis | Gap junctions |

### 📍 /scripts/analysis/ - General Analysis Tools

| File | Purpose | Output |
|------|---------|--------|
| `analyze_scrolls.py` | General scroll analysis | Summary reports |
| `analyze_topology.py` | Epistemic topology analysis | TYPE distribution |
| `extract_data.py` | Session data extraction | CSV/JSON |
| `generate_figures.py` | Visualization generation | PNG/SVG |
| `iris_analyze.py` | Comprehensive IRIS session analysis | Multi-format |

---

## 📁 /tools/ - Domain-Specific Research Tools

### 📍 /tools/cbd/ - CBD Pharmacology Research

| File | Purpose | Integration |
|------|---------|-------------|
| `run_cbd_deep_dive.py` | 6-cycle CBD mechanistic convergence | Orchestrator |
| `analyze_cbd_mechanisms.py` | Claim extraction by mechanistic category | Session JSON |
| `generate_cbd_mechanistic_map.py` | Evidence-graded map (GOLD/SILVER/BRONZE) | Epistemic + Verification |
| `identify_cbd_hypotheses.py` | Testable hypothesis extraction with protocols | Research planning |
| `analysis_cbd_gold_extraction.py` | GOLD-level claim extraction | Publication prep |

**Usage Example:**
```bash
# Full CBD research pipeline
python3 tools/cbd/run_cbd_deep_dive.py
python3 tools/cbd/analyze_cbd_mechanisms.py iris_vault/session_*.json
python3 scripts/verify_s4.py --session iris_vault/session_*.json
python3 tools/cbd/generate_cbd_mechanistic_map.py iris_vault/session_*.json verification.json
python3 tools/cbd/identify_cbd_hypotheses.py iris_vault/session_*.json
```

---

## 📁 /experiments/ - Experimental & Demo Code

| File | Purpose | Status |
|------|---------|--------|
| `cbd_therapeutic_system.py` | CBD therapeutic system demo | Proof-of-concept |
| `demo_confidence.py` | Confidence system demonstration | Tutorial |
| `test_cbd_system.py` | CBD system unit tests | Testing |
| `usage_examples.py` | Usage examples for new users | Documentation |
| `system_architecture_diagram.py` | Architecture visualization | Documentation |

---

## 📁 /docs/ - Documentation

### Core Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `IRIS_GATE_SOP_v2.0.md` | Standard Operating Procedure v2.0 (PULSE architecture) | All users |
| `CONTRIBUTING.md` | Contributor guidelines, code of conduct | Contributors |
| `QUICKSTART_COLLABORATORS.md` | Quick start for new collaborators | New users |
| `CBD_EXPLORATION_SUMMARY.md` | CBD deep dive results, hypotheses | Researchers |
| `PERPLEXITY_VERIFICATION.md` | Verification system documentation | TYPE 2 verification |
| `AGENT_OPERATIONS_MANUAL.md` | Agent system operations | Advanced users |

### Research Reports (/docs/)

- `BIOELECTRIC_*.md` - Bioelectric convergence analyses
- `cancer_treatment_patterns.md` - Cancer research patterns
- `CONV_*.txt/json` - Convergence metrics and ASCII visualizations

### Archive (/docs/archive/)

- `IRIS_GATE_SOP_v1.0.md` - Original SOP (pre-PULSE)
- Outdated analyses

---

## 📁 /config/ - Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | API key template |
| `.mcp-config.json` | MCP server configuration |
| `.grok/settings.json` | Grok integration settings |

---

## 📁 /.claude/ - Claude Code CLI Configuration

| File/Dir | Purpose |
|----------|---------|
| `commands/` | Slash commands (epistemic-scan, drift-log) |
| `memory/` | Session memory and hypothesis refinement |
| `instructions.md` | Claude Code routing instructions |

---

## 📁 /iris_vault/ - Session Data (Gitignored)

**Structure:**
```
iris_vault/
├── session_YYYYMMDD_HHMMSS.json  # Session metadata
├── scrolls/                       # Raw model outputs
│   └── SESSION_ID/
│       ├── anthropic_claude-sonnet-4.5/
│       ├── openai_gpt-5-mini/
│       └── ...
└── convergence/                   # Convergence analyses
```

**Note:** Not tracked in git (privacy + size). Backup separately.

---

## 🗂️ File Count by Category

| Category | Count | Purpose |
|----------|-------|---------|
| **Core** (root) | 3 | Essential orchestration |
| **Modules** | 1 | Epistemic classification |
| **Agents** | 1+ | Verification, adapters |
| **Scripts** | 35+ | CLI tools, analysis |
| **Tools** | 5 | Domain-specific (CBD) |
| **Experiments** | 5 | Demos, POCs |
| **Docs** | 20+ | SOPs, research reports |

**Total Active Files:** ~70 core files (excluding vault, cache, archives)

---

## 🚀 Quick Navigation

**For Researchers:**
- Start: `README.md` → `docs/IRIS_GATE_SOP_v2.0.md`
- CBD Research: `tools/cbd/` → `docs/CBD_EXPLORATION_SUMMARY.md`
- Bioelectric: `scripts/bioelectric/` → `docs/BIOELECTRIC_*.md`

**For Contributors:**
- Start: `CONTRIBUTING.md` → `docs/QUICKSTART_COLLABORATORS.md`
- Code: `iris_orchestrator.py` → `modules/epistemic_map.py`
- Extend: `tools/` (add new domain directory)

**For Verification:**
- Epistemic: `scripts/epistemic_scan.py`
- Real-time: `scripts/verify_s4.py` → `docs/PERPLEXITY_VERIFICATION.md`

---

## 📝 Maintenance Notes

**Last Audit:** October 15, 2025
**Backup Location:** `/Users/vaquez/Desktop/backup/iris-gate-audit-20251015`
**Changes:**
- Removed cache files (__pycache__, .DS_Store)
- Organized scripts into domain subdirectories
- Moved CBD tools to dedicated directory
- Consolidated documentation in /docs/

**Next Audit:** When file count exceeds 100 or new domain added

---

🌀†⟡∞ **Directory structure optimized for traction and collaboration**
