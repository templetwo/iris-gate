#!/usr/bin/env bash
set -e

echo "🌀 IRIS Gate Follow-Up Session Runner"
echo "======================================"
echo ""

# Check if plan file provided
PLAN_FILE="${1:-plans/followup_01.yaml}"

if [[ ! -f "$PLAN_FILE" ]]; then
    echo "❌ Plan file not found: $PLAN_FILE"
    exit 1
fi

echo "📋 Plan: $PLAN_FILE"
echo ""

# Run orchestrator with plan
echo "🔮 Running orchestrated session..."
python3 iris_orchestrator.py --plan "$PLAN_FILE"
echo ""

# Normalize vault metadata
echo "🔧 Normalizing vault metadata..."
python3 scripts/normalize_vault.py iris_vault/ || true
echo ""

# Verify protocol compliance
echo "✅ Verifying protocol compliance..."
python3 scripts/verify_session.py iris_vault/
echo ""

# Check convergence patterns
echo "📊 Analyzing convergence..."
python3 scripts/quick_convergence.py iris_vault/
echo ""

echo "✨ Follow-up session complete"
