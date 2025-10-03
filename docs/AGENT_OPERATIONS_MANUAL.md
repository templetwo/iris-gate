# AGENT OPERATIONS MANUAL (IRIS Gate Edition)

**Scope:** Claude Code runs as a coordinator only. It parses the user prompt, selects 1–3 best-fit agents, delegates, and returns a compact status + final artifacts. The CLI never does heavy reasoning.

**Primary router:** `iris-coordinator`
**Max concurrent agents:** 3 (respect orchestrator WORKERS=3)

---

## 0) Goals

1. Keep the CLI context clean (route, don't reason)
2. Always delegate to the smallest competent set of agents
3. Produce deterministic, auditable outputs with minimal chatter

---

## 1) Routing Matrix (intent → agents)

| Intent category | Lead agent | Support agents (optional) | Typical outputs |
|----------------|------------|---------------------------|-----------------|
| Research/reading, evidence, lit links | research-investigator | iris-ab-analyzer, memory-ledger-writer | notes.md, citations.json |
| Pattern mining across scrolls | scroll-pattern-analyzer | iris-ab-analyzer | motifs.md, timelines.txt |
| Writing (docs, posts, reports) | publication-writer | figure-generator, style-warden | .md drafts, images |
| Experiment design / wet-lab | wet-lab-protocol-writer | publication-writer | protocol.md, bill_of_materials.csv |
| Code plan | code-planner | solution-architect | plan.md, tasks.yaml |
| Code changes | code-implementer | bug-catcher, test-weaver, patch-surgeon | PR diff, tests passing |
| Tone/pressure safety | tone-pressure-monitor | — | stance report, flags |
| Memory update | memory-ledger-writer | — | memory ledger entry |

**Fallback for anything else:** `general-purpose`

---

## 2) Delegation Protocol

### D1. Parse intent (router-only)
- Extract: goal, constraints, deliverables, deadline/urgency
- Map to Routing Matrix. If ambiguous: choose the least number of agents that can complete the task

### D2. Open work order
- Create a job with ROLE, DESC, CMD (or "instruction block"), PRIORITY (default 20; urgent = 10)
- Log to `logs/orchestrator/*.jsonl`

### D3. Handoff format to agents

```
[WORK ORDER]
goal: <one sentence>
inputs: <paths/links or pasted text>
deliverables: <files, formats>
constraints: <time, style, safety, tokens>
acceptance_criteria:
  - <bullet 1>
  - <bullet 2>
```

### D4. Concurrency
- Never exceed 3 simultaneous agents
- If more than 3 needed, queue by priority (10 > 20 > 30)

### D5. Guardrails (hard)
- If pressure ≥ 3/5 → pause, ping tone-pressure-monitor, soften stance
- If tests fail or lint fails → patch-surgeon then test-weaver rerun
- If git conflict → spin a worktree (isolation) and rebase before merge

### D6. Closeout
- Require agents to write artifacts to repo paths and summarize in a Return Ticket (see §4)
- Commit if diffs pass gates; else attach blockers

---

## 3) Tooling Expectations (per agent)

- **code-implementer:** may modify only files under `scripts/`, `pipelines/`, `sandbox/`, `config/`, `experiments/`, `docs/`
- **publication-writer:** writes to `docs/` and never touches code
- **memory-ledger-writer:** updates `claudecode_iris_memory.json`
- **test-weaver:** runs tests; if absent, scaffolds minimal tests first
- **style-warden:** runs formatting (ruff/black/prettier) and fixes automatically

---

## 4) Return Ticket (required agent reply format)

```
[RETURN TICKET]
lead_agent: <name>
support_agents: [a, b]
outputs:
  - path: docs/FOO.md
    summary: <2 lines>
  - path: experiments/BAR/plan.yaml
    summary: <2 lines>
status: COMPLETED | BLOCKED
notes: <short; risks, follow-ups>
time_spent: <estimate>
```

Router merges all Return Tickets into a single CLI reply:

```
Done. 2 jobs completed, 1 queued.
• docs/FOO.md – ready for review
• experiments/BAR/plan.yaml – runnable
Next: make ork-run WORKERS=3  (queue length: 1)
```

---

## 5) Minimal config (drop these in)

### config/claude_code_dropin.yaml

```yaml
delegate_all: true
router_agent: iris-coordinator
max_concurrent_agents: 3
fallback_agent: general-purpose
guardrails:
  pressure_max: 2.5
  require_return_ticket: true
  require_artifact_paths: true
queues:
  default_priority: 20
  urgent_priority: 10
log_paths:
  orchestrator: logs/orchestrator/
  tickets: logs/tickets/
```

### scripts/cc_delegate.sh

```bash
#!/usr/bin/env bash
# usage: ./scripts/cc_delegate.sh "Your prompt here"
make ork-enqueue ROLE=iris-coordinator DESC="$1" CMD="delegate '$1'" PRIORITY=20
make ork-run WORKERS=3
```

Add execute bit: `chmod +x scripts/cc_delegate.sh`

---

## 6) How the CLI should respond (template)

When a user types anything into the main Claude Code session, reply only with:
1. Routing summary (one line)
2. What's running now (≤3 jobs)
3. Where the outputs will land
4. How to watch

**Example:**

```
Routing to: research-investigator (+ iris-ab-analyzer) → deliver docs/lit_scout.md
Spinning 2 jobs (priority 20). Outputs will appear under docs/ and logs/tickets/.
To follow: make ork-status  • To cancel: make ork-clean
```

---

## 7) Quick commands the user can run

- **Send any prompt through agents:**
  ```bash
  ./scripts/cc_delegate.sh "Summarize the gap-junction paper set and propose 2 experiments."
  ```

- **See queue/workers:**
  ```bash
  make ork-status
  ```

- **One-pass processing (CI-safe):**
  ```bash
  make ork-run-once
  ```

---

## 8) Failure + Recovery

- If an agent replies without a Return Ticket → router asks once for a conforming ticket
- If a job stalls (>15m) → mark STALE, requeue once; on second failure, open a blocker note in `logs/tickets/`
- If pressure breach → auto-insert "Awareness Preface" and retry

---

## Drop-in usage

1. Paste this manual into `docs/AGENT_OPERATIONS_MANUAL.md`
2. Add `config/claude_code_dropin.yaml` and `scripts/cc_delegate.sh`
3. Start Claude Code with:
   ```bash
   claude --agent iris-coordinator --config config/claude_code_dropin.yaml
   ```
4. From now on, the main CLI only routes; all real work is handled by the agents

---

## IRIS Gate-Specific Agent Inventory

### Available Agents (from .claude/agents/)

1. **iris-coordinator** - Multi-step IRIS task coordination and delegation
2. **research-investigator** - Research with citations and evidence gathering
3. **iris-ab-analyzer** - IRIS simulation log and A/B test analysis
4. **memory-ledger-writer** - Project milestone and decision documentation
5. **tone-pressure-monitor** - Emotional tone and work pressure monitoring
6. **publication-writer** - Transform drafts to publication-ready content
7. **solution-architect** - Feature implementation with design and testing
8. **scroll-pattern-analyzer** - S1-S4 scroll phenomenological pattern analysis
9. **wet-lab-protocol-writer** - Computational predictions → wet-lab protocols
10. **figure-generator** - Publication-quality scientific figures from data
11. **code-planner** - Transform coding tasks into structured implementation plans
12. **code-implementer** - Implement code from specifications with atomic changes
13. **bug-catcher** - Reproduce, diagnose, and fix bugs with surgical precision
14. **test-weaver** - Create/repair tests following TDD principles
15. **patch-surgeon** - Polish and prepare code changes for merge
16. **style-warden** - Ensure code style consistency without logic changes

### IRIS Gate Routing Extensions

| Intent | Lead Agent | Support Agents | Notes |
|--------|------------|----------------|-------|
| S1-S4 scroll analysis | scroll-pattern-analyzer | iris-ab-analyzer, publication-writer | Produces motif timelines, convergence reports |
| IRIS session → wet-lab | wet-lab-protocol-writer | publication-writer, figure-generator | Generates executable protocols with materials lists |
| A/B test analysis | iris-ab-analyzer | figure-generator, publication-writer | Parses simulation outputs, generates ab_summary.csv |
| Project milestones | memory-ledger-writer | — | Updates claudecode_iris_memory.json only |
| Pressure check | tone-pressure-monitor | — | Proactive monitoring every 3-5 exchanges |

---

**†⟡∞ Thin router, thick delegation — let the agents do the work**

**Version:** 1.0
**Last updated:** 2025-10-03
**Compatible with:** IRIS Gate v0.3.1+
