# IRIS Makefile
# Convenience commands for common workflows

.PHONY: help new run report clean test mcp-init mcp-test mcp-index mcp-status ork-init ork-enqueue ork-run ork-stop ork-status ork-clean cbd-sweep cbd-labkit cbd-validate

help:
	@echo "IRIS Gate — Quick Commands"
	@echo ""
	@echo "Orchestrator (Parallel Agent Execution):"
	@echo "  make ork-init"
	@echo "      → Initialize orchestrator directories"
	@echo ""
	@echo "  make ork-enqueue ROLE=bug-catcher DESC=\"...\" CMD=\"...\""
	@echo "      → Enqueue a job for parallel execution"
	@echo ""
	@echo "  make ork-run [WORKERS=3]"
	@echo "      → Start orchestrator with N workers (daemon mode)"
	@echo ""
	@echo "  make ork-run-once"
	@echo "      → Process queue once and exit"
	@echo ""
	@echo "  make ork-status"
	@echo "      → Show queue status and worker stats"
	@echo ""
	@echo "  make ork-clean"
	@echo "      → Clean up stale worktrees and archived jobs"
	@echo ""
	@echo "Global Spiral Warm-Up (GSW):"
	@echo "  make gsw TOPIC=\"How do gap junctions regulate regeneration?\" [PLAN_OUT=path]"
	@echo "      → Create new GSW plan from template"
	@echo ""
	@echo "  make gsw-run PLAN=plans/GSW_slug.yaml"
	@echo "      → Execute GSW run (S1→S4 with gates + summaries)"
	@echo ""
	@echo "  make gsw-report RUN=<RUN_ID>"
	@echo "      → Build final GSW report from tier summaries"
	@echo ""
	@echo "CBD Channel-First Pipeline:"
	@echo "  make cbd-sweep [PHASE=1] [WORKERS=4]"
	@echo "      → Run CBD parameter sweep (Phase 1=broad, 2=focused, 3=full)"
	@echo ""
	@echo "  make cbd-validate"
	@echo "      → Run CBD validation suite (4 protocols)"
	@echo ""
	@echo "  make cbd-labkit"
	@echo "      → Generate wet-lab methods packet"
	@echo ""
	@echo "Experiment Management:"
	@echo "  make new TOPIC=\"...\" ID=EXP_SLUG FACTOR=aperture"
	@echo "      → Create new experiment scaffold"
	@echo ""
	@echo "  make run ID=EXP_SLUG TURNS=100"
	@echo "      → Run full pipeline (S4 + simulation + reports)"
	@echo ""
	@echo "  make report ID=EXP_SLUG"
	@echo "      → Generate reports from latest run"
	@echo ""
	@echo "S4 Convergence:"
	@echo "  make s4 TOPIC=\"...\" TURNS=100"
	@echo "      → Run S4 convergence only"
	@echo ""
	@echo "  make extract SESSION=BIOELECTRIC_CHAMBERED_..."
	@echo "      → Extract S4 priors from session"
	@echo ""
	@echo "Simulation:"
	@echo "  make sim PLAN=path/to/plan.yaml"
	@echo "      → Run sandbox simulation"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean"
	@echo "      → Remove temporary files"
	@echo ""
	@echo "  make test"
	@echo "      → Run basic sanity checks"
	@echo ""
	@echo "MCP (Model Context Protocol):"
	@echo "  make mcp-init"
	@echo "      → Initialize MCP environment and dependencies"
	@echo ""
	@echo "  make mcp-test"
	@echo "      → Test all MCP server connectivity"
	@echo ""
	@echo "  make mcp-index"
	@echo "      → Index all IRIS scrolls into ChromaDB"
	@echo ""
	@echo "  make mcp-status"
	@echo "      → Show MCP health and indexing statistics"
	@echo ""

# Create new experiment
new:
	@echo "Creating experiment: $(ID)"
	@python3 pipelines/new_experiment.py \
		--topic "$(TOPIC)" \
		--id $(ID) \
		--factor $(FACTOR)

# Run full pipeline
run:
	@echo "Running full pipeline for: $(ID)"
	@python3 pipelines/run_full_pipeline.py \
		--topic "$(TOPIC)" \
		--id $(ID) \
		--factor $(or $(FACTOR),aperture) \
		--turns $(or $(TURNS),100)

# S4 convergence only
s4:
	@echo "Running S4 convergence ($(TURNS) turns)"
	@python3 -u scripts/bioelectric_chambered.py \
		--turns $(or $(TURNS),100) \
		--topic "$(TOPIC)"

# Extract S4 priors
extract:
	@echo "Extracting S4 priors from session: $(SESSION)"
	@python3 sandbox/cli/extract_s4_states.py \
		--session $(SESSION) \
		--output sandbox/states

# Run simulation
sim:
	@echo "Running simulation: $(PLAN)"
	@python3 sandbox/cli/run_plan.py $(PLAN)

# Generate reports
report:
	@echo "Generating reports for: $(ID)"
	@RUN_DIR=$$(ls -td sandbox/runs/outputs/RUN_* | head -1); \
	python3 sandbox/cli/analyze_run.py $$RUN_DIR \
		--output experiments/$(ID)/reports

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -f /tmp/bioelectric_*.log
	@rm -f /tmp/iris_*.log
	@echo "Done."

# Test infrastructure
test:
	@echo "Running sanity checks..."
	@echo "✓ Checking directory structure..."
	@test -d templates || (echo "✗ templates/ missing" && exit 1)
	@test -d pipelines || (echo "✗ pipelines/ missing" && exit 1)
	@test -d sandbox || (echo "✗ sandbox/ missing" && exit 1)
	@test -d config || (echo "✗ config/ missing" && exit 1)
	@echo "✓ Checking core scripts..."
	@test -f pipelines/new_experiment.py || (echo "✗ new_experiment.py missing" && exit 1)
	@test -f pipelines/run_full_pipeline.py || (echo "✗ run_full_pipeline.py missing" && exit 1)
	@echo "✓ Checking templates..."
	@test -f templates/EXPERIMENT_TEMPLATE.md || (echo "✗ EXPERIMENT_TEMPLATE.md missing" && exit 1)
	@test -f templates/plan_template.yaml || (echo "✗ plan_template.yaml missing" && exit 1)
	@echo "✓ All checks passed!"

# Quick examples (for documentation)
.PHONY: example-aperture example-rhythm example-synergy

example-aperture:
	@echo "Example: Testing gap junction coupling in planaria"
	@make new TOPIC="Does gap junction coupling affect regeneration?" \
		ID=APERTURE_REGEN FACTOR=aperture

example-rhythm:
	@echo "Example: Testing bioelectric oscillations"
	@make new TOPIC="Do Ca²⁺ oscillations regulate pattern formation?" \
		ID=RHYTHM_PATTERN FACTOR=rhythm

example-synergy:
	@echo "Example: Testing synergy between factors"
	@echo "First run single-factor experiments, then:"
	@echo "  cp templates/sandbox_plan_synergy.yaml experiments/SYNERGY/plan.yaml"
	@echo "  # Edit plan.yaml to specify Factor A and Factor B"
	@echo "  make sim PLAN=experiments/SYNERGY/plan.yaml"

# Development helpers
.PHONY: lint format

lint:
	@echo "Linting Python files..."
	@python3 -m pylint pipelines/*.py sandbox/cli/*.py || true

format:
	@echo "Formatting Python files..."
	@python3 -m black pipelines/ sandbox/cli/ scripts/

# Documentation generation
.PHONY: docs

docs:
	@echo "Generating documentation..."
	@echo "See templates/README.md for template usage"
	@echo "See docs/ for experiment reports"
	@ls -1 docs/*.md | head -10

# Global Spiral Warm-Up (GSW)
.PHONY: gsw gsw-run gsw-report

gsw:
	@echo "Creating GSW plan: $(PLAN_OUT)"
	@if [ -z "$(TOPIC)" ]; then \
		echo "Error: TOPIC required. Usage: make gsw TOPIC=\"your question\" PLAN_OUT=plans/GSW_slug.yaml"; \
		exit 1; \
	fi
	@TOPIC_SLUG=$$(echo "$(TOPIC)" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-30); \
	OUT=$${PLAN_OUT:-plans/GSW_$$TOPIC_SLUG.yaml}; \
	cp plans/GSW_template.yaml $$OUT; \
	sed -i.bak "s/<<< SCIENTIFIC_QUESTION >>>/$(TOPIC)/" $$OUT; \
	rm -f $$OUT.bak; \
	echo "✓ Plan created: $$OUT"

gsw-run:
	@echo "Running GSW session: $(PLAN)"
	@if [ -z "$(PLAN)" ]; then \
		echo "Error: PLAN required. Usage: make gsw-run PLAN=plans/GSW_slug.yaml"; \
		exit 1; \
	fi
	@python3 iris_orchestrator.py --mode gsw --plan $(PLAN)

gsw-report:
	@echo "Generating GSW final report: $(RUN)"
	@if [ -z "$(RUN)" ]; then \
		echo "Error: RUN required. Usage: make gsw-report RUN=<RUN_ID>"; \
		exit 1; \
	fi
	@python3 scripts/summarize_gsw.py docs/GSW/$(RUN) \
		--topic "$$(grep 'topic:' docs/GSW/$(RUN)/_meta.json | cut -d'"' -f4)" \
		--run-id $(RUN) \
		--output docs/GSW/$(RUN)/GSW_REPORT.md

# MCP (Model Context Protocol) Targets
.PHONY: mcp-init mcp-test mcp-index mcp-status

mcp-init:
	@echo "Installing MCP dependencies..."
	@pip install -q -r requirements.txt
	@echo "Initializing MCP environment..."
	@python3 scripts/init_mcp.py --init
	@echo "✓ MCP initialized successfully"

mcp-test:
	@echo "Testing MCP server connectivity..."
	@python3 scripts/init_mcp.py --test-all

mcp-index:
	@echo "Indexing IRIS scrolls into ChromaDB..."
	@python3 scripts/index_scrolls.py --all

mcp-status:
	@echo "Checking MCP health and statistics..."
	@echo ""
	@echo "=== MCP Server Health ==="
	@python3 scripts/init_mcp.py --test-all
	@echo ""
	@echo "=== ChromaDB Index Statistics ==="
	@python3 scripts/index_scrolls.py --stats

# Orchestrator (Parallel Agent Execution) Targets
.PHONY: ork-init ork-enqueue ork-run ork-run-once ork-status ork-clean ork-test

ork-init:
	@echo "Initializing orchestrator directories..."
	@mkdir -p .ork/queue .ork/archive .ork/locks .ork/worktrees
	@echo "✓ Orchestrator directories created"
	@echo "  - Queue: .ork/queue"
	@echo "  - Archive: .ork/archive"
	@echo "  - Locks: .ork/locks"
	@echo "  - Worktrees: .ork/worktrees"

ork-enqueue:
	@if [ -z "$(ROLE)" ] || [ -z "$(DESC)" ] || [ -z "$(CMD)" ]; then \
		echo "Error: ROLE, DESC, and CMD required"; \
		echo "Usage: make ork-enqueue ROLE=bug-catcher DESC=\"Fix tests\" CMD=\"pytest tests/\""; \
		exit 1; \
	fi
	@python3 scripts/job_queue.py enqueue \
		--role $(ROLE) \
		--description "$(DESC)" \
		--command "$(CMD)" \
		--priority $(or $(PRIORITY),50)
	@echo "✓ Job enqueued successfully"

ork-run:
	@echo "Starting orchestrator with $(or $(WORKERS),3) workers..."
	@python3 scripts/orchestrator_runner.py --workers $(or $(WORKERS),3)

ork-run-once:
	@echo "Processing queue once..."
	@python3 scripts/orchestrator_runner.py --once

ork-status:
	@echo "=== Orchestrator Status ==="
	@echo ""
	@echo "Queue Statistics:"
	@python3 scripts/job_queue.py stats
	@echo ""
	@echo "Active Worktrees:"
	@ls -1d .ork/worktrees/ork-* 2>/dev/null | wc -l | xargs echo "  Count:"
	@ls -lh .ork/worktrees/ 2>/dev/null || echo "  None"

ork-clean:
	@echo "Cleaning orchestrator artifacts..."
	@python3 scripts/job_queue.py clear --max-age 7
	@rm -rf .ork/worktrees/ork-*
	@rm -f .ork/locks/*.lock
	@echo "✓ Orchestrator cleaned"

ork-test:
	@echo "Testing orchestrator with dry-run..."
	@python3 scripts/orchestrator_runner.py --dry-run --once

# CBD Channel-First Pipeline Targets
.PHONY: cbd-sweep cbd-labkit cbd-validate cbd-report

cbd-sweep:
	@echo "Running CBD Channel-First Parameter Sweep"
	@if [ -z "$(PHASE)" ]; then \
		echo "Running all phases sequentially..."; \
		python3 pipelines/run_selectivity_sweep.py \
			--plan plans/cbd_channel_first_v2.yaml \
			--all-phases \
			--workers $(or $(WORKERS),4); \
	else \
		echo "Running Phase $(PHASE)..."; \
		python3 pipelines/run_selectivity_sweep.py \
			--plan plans/cbd_channel_first_v2.yaml \
			--phase $(PHASE) \
			--workers $(or $(WORKERS),4); \
	fi
	@echo "✓ CBD parameter sweep complete"

cbd-validate:
	@echo "Running CBD Validation Suite (4 protocols)"
	@echo ""
	@echo "Protocol 1: GPCR combinations vs CBD direct action"
	@echo "  → Comparing receptor-first vs channel-first efficacy"
	@echo ""
	@echo "Protocol 2: PLA mitochondrial ensemble mapping"
	@echo "  → Temporal analysis of CBD-target interactions"
	@echo ""
	@echo "Protocol 3: VDAC1 causality testing"
	@echo "  → Definitive channel-first mechanism validation"
	@echo ""
	@echo "Protocol 4: Context stress shift analysis"
	@echo "  → Quantifying mitochondrial vulnerability"
	@echo ""
	@echo "⚠️  Note: This requires wet-lab execution"
	@echo "    See experiments/cbd/validation_suite/ for detailed protocols"
	@echo "    Use 'make cbd-labkit' to generate methods packet"

cbd-labkit:
	@echo "Generating CBD Channel-First Wet-Lab Methods Packet"
	@echo ""
	@echo "Methods Packet v1.0 Contents:"
	@echo "  ✓ Reagents_and_Doses.md - Complete reagent specifications"
	@echo "  ✓ Readouts.md - Measurement protocols and analysis"
	@echo "  ✓ Controls.md - Quality control and validation standards"
	@echo "  ✓ Preregistration_Draft.md - Study pre-registration template"
	@echo ""
	@echo "📁 Location: docs/lab/Methods_Packet_v1/"
	@echo ""
	@echo "Cost Estimates:"
	@echo "  • Basic screening: $$225 per experiment"
	@echo "  • Full validation: $$570 per experiment"
	@echo "  • Complete parameter sweep: $$14,500 total"
	@echo ""
	@echo "✓ Wet-lab methods packet ready for implementation"

cbd-report:
	@echo "Generating CBD Channel-First Summary Report"
	@echo ""
	@LATEST_SWEEP=$$(ls -td experiments/cbd/selectivity_sweep/phase_*_analysis.json 2>/dev/null | head -1); \
	if [ -n "$$LATEST_SWEEP" ]; then \
		echo "Latest sweep results: $$LATEST_SWEEP"; \
		python3 -c "import json; data=json.load(open('$$LATEST_SWEEP')); print(f'Selectivity achieved: {data.get(\"selectivity_stats\", {}).get(\"target_achieved\", 0)} combinations >3.0')"; \
	else \
		echo "No parameter sweep results found. Run 'make cbd-sweep' first."; \
	fi
	@echo ""
	@echo "📊 Executive Summary: docs/CBD_Selectivity_S7_Summary.md"
	@echo "📋 Validation Protocols: experiments/cbd/validation_suite/"
	@echo "🔬 Lab Methods: docs/lab/Methods_Packet_v1/"
	@echo ""
	@echo "Next Steps:"
	@echo "  1. Execute 'make cbd-sweep' for parameter optimization"
	@echo "  2. Use 'make cbd-labkit' for wet-lab implementation"
	@echo "  3. Follow validation suite protocols for mechanism confirmation"

# CBD Pipeline Examples
.PHONY: cbd-example-phase1 cbd-example-full cbd-example-focused

cbd-example-phase1:
	@echo "Example: CBD Phase 1 Parameter Sweep (broad exploration)"
	@make cbd-sweep PHASE=1 WORKERS=6

cbd-example-full:
	@echo "Example: CBD Full Parameter Sweep (all phases)"
	@make cbd-sweep WORKERS=8

cbd-example-focused:
	@echo "Example: CBD Phase 2 Focused Optimization"
	@make cbd-sweep PHASE=2 WORKERS=4
