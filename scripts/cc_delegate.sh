#!/usr/bin/env bash
# Claude Code Delegation Script for IRIS Gate
# Usage: ./scripts/cc_delegate.sh "Your prompt here"
#
# Routes any user prompt through the iris-coordinator agent
# which will select appropriate specialized agents and delegate work

set -euo pipefail

PROMPT="${1:-}"

if [ -z "$PROMPT" ]; then
    echo "Usage: $0 \"Your prompt here\""
    echo ""
    echo "Examples:"
    echo "  $0 \"Analyze gap junction scrolls for hidden patterns\""
    echo "  $0 \"Design wet-lab protocol for testing aperture hypothesis\""
    echo "  $0 \"Generate figures from ab_summary.csv\""
    exit 1
fi

# Ensure logs directory exists
mkdir -p logs/orchestrator logs/tickets

# Enqueue the job
make ork-enqueue \
    ROLE=iris-coordinator \
    DESC="$PROMPT" \
    CMD="delegate '$PROMPT'" \
    PRIORITY=20

# Run the orchestrator with 3 workers
echo "Job queued. Starting orchestrator with 3 workers..."
make ork-run WORKERS=3
