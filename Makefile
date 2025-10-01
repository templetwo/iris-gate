# IRIS Makefile
# Convenience commands for common workflows

.PHONY: help new run report clean test

help:
	@echo "IRIS Gate — Quick Commands"
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
