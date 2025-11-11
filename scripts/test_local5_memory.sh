#!/bin/bash
# Single-Turn Memory Test for 5-Model Architecture
# Purpose: Gauge memory draw on Mac Studio before full experiment
# Models: Llama3.2, Falcon3, Gemma3, Hermes3, Granite3-MoE

set -e

STUDIO_HOST="tony_studio@192.168.1.195"
OLLAMA_CMD="/usr/local/bin/ollama"

SESSION_NAME="iris_test5_$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="iris_vault/tests/${SESSION_NAME}"
mkdir -p "$OUTPUT_DIR"

# Models (5 ecosystems)
MODELS=(
    "llama3.2:3b"
    "falcon3:3b"
    "gemma3:4b"
    "hermes3:latest"
    "granite3-moe:3b"
)

MODEL_NAMES=(
    "Meta_Llama3.2"
    "TII_Falcon3"
    "Google_Gemma3"
    "Nous_Hermes3"
    "IBM_Granite3"
)

# Length guidance
LENGTH_GUIDE="[Response length: 200-300 words. Be specific and vivid. Complete your thought.]

"

# Test with S4 prompt (full mechanistic convergence)
TEST_PROMPT="${LENGTH_GUIDE}Visualize the complete organizing pattern explaining the CBD/schizophrenia paradox. Consider: (1) RHYTHM—what oscillations or dynamics are altered? (2) CENTER—what organizing principle differs? (3) APERTURE—what gates or thresholds respond differently to CBD? Describe the full mechanistic landscape. Be specific and vivid."

echo "🌀 IRIS Gate 5-Model Memory Test"
echo "================================="
echo "Session: $SESSION_NAME"
echo "Models: ${MODEL_NAMES[@]}"
echo "Test: Single S4 turn (CBD paradox)"
echo "Output: $OUTPUT_DIR"
echo ""

# Capture memory before
echo "📊 Memory before test:"
ssh "$STUDIO_HOST" "vm_stat | grep 'Pages free\|Pages active\|Pages inactive'"
echo ""

# Function to run single model with live output
run_model() {
    local model=$1
    local model_name=$2
    local start_time=$(date +%s)

    echo "▶ Starting $model_name..."

    # Run with live streaming output
    ssh "$STUDIO_HOST" "$OLLAMA_CMD run $model" <<EOF | tee "$OUTPUT_DIR/${model_name}_output.txt"
$TEST_PROMPT
EOF

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "✓ $model_name complete (${duration}s)" | tee -a "$OUTPUT_DIR/${model_name}_timing.txt"
    echo ""
}

echo "🔥 Firing all 5 models in parallel..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Fire all 5 in parallel with live output
for i in "${!MODELS[@]}"; do
    run_model "${MODELS[$i]}" "${MODEL_NAMES[$i]}" &
done

# Wait for all to complete
wait

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Memory after test:"
ssh "$STUDIO_HOST" "vm_stat | grep 'Pages free\|Pages active\|Pages inactive'"
echo ""

echo "✅ Memory test complete!"
echo ""
echo "Results: $OUTPUT_DIR"
echo ""
echo "Quick analysis:"
for model_name in "${MODEL_NAMES[@]}"; do
    file="$OUTPUT_DIR/${model_name}_output.txt"
    if [ -f "$file" ]; then
        has_rhythm=$(grep -qiE "rhythm|oscillat|wave|pulse" "$file" && echo "✓" || echo "✗")
        has_center=$(grep -qiE "center|core|baseline|organizing" "$file" && echo "✓" || echo "✗")
        has_aperture=$(grep -qiE "aperture|gate|threshold|channel" "$file" && echo "✓" || echo "✗")
        echo "  $model_name: R=$has_rhythm C=$has_center A=$has_aperture"
    fi
done
echo ""
