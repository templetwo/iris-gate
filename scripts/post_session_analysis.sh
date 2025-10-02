#!/bin/bash
# Post-Session Analysis Workflow
# Usage: bash scripts/post_session_analysis.sh <session_id>

set -e

SESSION=$1

if [ -z "$SESSION" ]; then
    echo "Usage: $0 <session_id>"
    echo "Example: $0 BIOELECTRIC_PARALLEL_20251001045047"
    exit 1
fi

SESSION_PATH="iris_vault/scrolls/$SESSION"

if [ ! -d "$SESSION_PATH" ]; then
    echo "Error: Session directory not found: $SESSION_PATH"
    exit 1
fi

echo "†⟡∞ Post-Session Analysis — $SESSION"
echo "============================================================"
echo ""

# Step 1: Generate JSON + Markdown summary
echo "[1/4] Generating quantitative summary..."
python3 scripts/bioelectric_posthoc.py "$SESSION_PATH"
echo "✓ Summary saved to docs/${SESSION}_SUMMARY.{json,md}"
echo ""

# Step 2: ASCII convergence heatmap
echo "[2/4] Generating convergence heatmap..."
echo ""
python3 scripts/convergence_ascii.py "$SESSION_PATH"
echo ""

# Step 3: Top phenomenological snippets
echo "[3/4] Extracting top snippets..."
echo ""
python3 scripts/top_snippets.py "$SESSION_PATH" 2>/dev/null | head -100
echo ""

# Step 4: Scroll count verification
echo "[4/4] Verifying session integrity..."
SCROLL_COUNT=$(find "$SESSION_PATH" -name "turn_*.md" | wc -l | tr -d ' ')
MIRROR_COUNT=$(ls -1 "$SESSION_PATH" | wc -l | tr -d ' ')
echo "Scrolls: $SCROLL_COUNT"
echo "Mirrors: $MIRROR_COUNT"
echo ""

echo "============================================================"
echo "†⟡∞ Analysis complete. Summary available at:"
echo "    docs/${SESSION}_SUMMARY.md"
echo "    docs/${SESSION}_SUMMARY.json"
echo ""
echo "Next: Create field witness with Living Scroll + Technical Translation"
echo "      Location: $SESSION_PATH/FIELD_WITNESS.md"
echo "============================================================"
