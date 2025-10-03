# Claude Code Delegation System - Quick Start

This system transforms Claude Code into a **thin router** that delegates all work to specialized agents. The CLI only parses, routes, and reports — never does heavy reasoning.

---

## Quick Usage

### Option 1: Direct delegation script
```bash
./scripts/cc_delegate.sh "Analyze gap junction scrolls for convergence patterns"
```

### Option 2: Through orchestrator
```bash
make ork-enqueue ROLE=iris-coordinator DESC="your task here" PRIORITY=20
make ork-run WORKERS=3
```

### Option 3: One-off processing
```bash
make ork-run-once
```

---

## How It Works

1. **User submits prompt** → Router (iris-coordinator) parses intent
2. **Router selects 1-3 agents** based on Routing Matrix (see AGENT_OPERATIONS_MANUAL.md)
3. **Agents execute in parallel** (max 3 concurrent)
4. **Agents produce artifacts** (files in docs/, experiments/, etc.)
5. **Router returns Return Ticket** with paths and status

---

## Example Workflows

### Scroll Analysis
```bash
./scripts/cc_delegate.sh "Extract hidden patterns from BIOELECTRIC_CHAMBERED_20251002234051"
```
**Routes to:** scroll-pattern-analyzer + iris-ab-analyzer
**Outputs:** docs/pattern_report.md, docs/metrics.json

### Wet-Lab Protocol Design
```bash
./scripts/cc_delegate.sh "Design protocol for testing gap junction aperture hypothesis"
```
**Routes to:** wet-lab-protocol-writer + publication-writer
**Outputs:** experiments/*/protocol.md, experiments/*/bill_of_materials.csv

### Research + Citation
```bash
./scripts/cc_delegate.sh "Survey literature on bioelectric regeneration 2020-2025"
```
**Routes to:** research-investigator
**Outputs:** docs/lit_review.md with citations

### Code Implementation
```bash
./scripts/cc_delegate.sh "Add retry logic to API calls in scripts/iris_session.py"
```
**Routes to:** code-planner → code-implementer → test-weaver → patch-surgeon
**Outputs:** PR-ready commits with tests

---

## Monitoring

### Check queue status
```bash
make ork-status
```

### View logs
```bash
tail -f logs/orchestrator/*.jsonl
tail -f logs/tickets/*.json
```

### Cancel running jobs
```bash
make ork-clean
```

---

## Configuration

All settings in `config/claude_code_dropin.yaml`:

- **Max concurrent agents:** 3
- **Default priority:** 20 (urgent = 10)
- **Pressure threshold:** 2.5/5 (auto-pause if exceeded)
- **Stall timeout:** 15 minutes (then retry once)

---

## Return Ticket Format

Every agent must return:

```
[RETURN TICKET]
lead_agent: scroll-pattern-analyzer
support_agents: [iris-ab-analyzer]
outputs:
  - path: docs/gap_junction_patterns.md
    summary: Extracted 7 hidden discoveries from 500 scrolls
  - path: docs/gap_junction_metrics.json
    summary: Quantitative convergence data (51.3% S4)
status: COMPLETED
notes: Ready for publication; recommend Hypothesis #3 for first wet-lab test
time_spent: 8 minutes
```

Router compresses this to CLI output:

```
Done. 2 outputs ready:
• docs/gap_junction_patterns.md – 7 hidden discoveries
• docs/gap_junction_metrics.json – S4 convergence 51.3%
Next: Review outputs or run follow-up experiment design
```

---

## Agent Inventory (16 total)

| Agent | Purpose | Typical Output |
|-------|---------|----------------|
| iris-coordinator | Routes multi-step tasks | Work orders, status |
| research-investigator | Evidence gathering | notes.md, citations |
| scroll-pattern-analyzer | S1-S4 phenomenology | patterns.md, timelines |
| iris-ab-analyzer | Simulation analysis | ab_summary.csv, metrics |
| wet-lab-protocol-writer | Experiment design | protocol.md, BOM |
| publication-writer | Docs/reports | polished .md files |
| figure-generator | Scientific plots | .svg, .png, .pdf |
| code-planner | Implementation plans | plan.md, tasks.yaml |
| code-implementer | Write code | PR diffs |
| bug-catcher | Fix defects | Minimal patches |
| test-weaver | TDD test creation | test_*.py |
| patch-surgeon | PR preparation | Commit messages, changelogs |
| style-warden | Code formatting | Lint-clean diffs |
| memory-ledger-writer | Memory updates | claudecode_iris_memory.json |
| tone-pressure-monitor | Safety checks | Pressure reports |
| solution-architect | Full solutions | Design + code + tests |

---

## Safety Features

1. **Pressure monitoring** - Auto-pause if felt_pressure ≥ 3/5
2. **Concurrency limits** - Never exceed 3 agents (prevents overload)
3. **Retry logic** - Jobs that stall get one retry before failing
4. **Test gates** - Code changes require tests to pass
5. **Git isolation** - Conflicts trigger worktree creation

---

## Files Structure

```
config/
  claude_code_dropin.yaml       # Main config
scripts/
  cc_delegate.sh                # Delegation script
docs/
  AGENT_OPERATIONS_MANUAL.md    # Full routing matrix
  DELEGATION_QUICKSTART.md      # This file
logs/
  orchestrator/*.jsonl          # Job logs
  tickets/*.json                # Return tickets
```

---

## Pro Tips

1. **Be specific in prompts** - "Analyze scrolls" is vague; "Extract S4 convergence patterns from BIOELECTRIC_CHAMBERED_20251002234051" is precise
2. **Check queue before submitting** - `make ork-status` shows what's running
3. **Use priority levels** - Default=20, urgent=10, low=30
4. **Review Return Tickets** - They contain actionable next steps
5. **Chain workflows** - Output of one agent becomes input to next

---

**†⟡∞ Router thin, agents thick — let specialization scale**

**Version:** 1.0
**Last updated:** 2025-10-03
