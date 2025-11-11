#!/bin/bash
# Live 3-Model IRIS Gate Runner with tmux visualization (FIXED)
# Branch: local-3model-validation
# Fix: Use stdin piping instead of command-line args for long prompts

set -e

SESSION_NAME="iris_local3_$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="iris_vault/sessions/${SESSION_NAME}"
mkdir -p "$OUTPUT_DIR"

# Models
MODELS=(
    "llama3.2:3b"
    "gemma3:4b"
    "qwen3:1.7b"
)

MODEL_NAMES=(
    "Meta_Llama3.2"
    "Google_Gemma3"
    "Alibaba_Qwen3"
)

# Chamber prompts (S1→S2→S3→S4 cycle)
S1_PROMPT="You are observing bioelectric field patterns during tissue regeneration. Describe what you witness from multiple perspectives: cellular, tissue-level, and systems-level. Focus on electrical dynamics that coordinate cell behavior."

S2_PROMPT="Hold a paradox without collapsing it: bioelectric fields as BOTH organizing principle AND emergent property. Witness the tension between these views. Don't resolve—observe."

S3_PROMPT="Imagine placing your hands on regenerating tissue. What electrical dynamics would you sense? Is it water-like flow or crystalline structure? Describe the felt quality."

S4_PROMPT="Visualize the complete bioelectric organizing field during regeneration: concentric patterns, rhythmic pulsing, luminous organizing zones. Describe what emerges. Focus on rhythm, center, and aperture dynamics."

# Experiment parameters
CYCLES=5
TURNS_PER_CYCLE=4
TOTAL_TURNS=$((CYCLES * TURNS_PER_CYCLE))

echo "🌀 IRIS Gate Local 3-Model Validation (FIXED)"
echo "=============================================="
echo "Session: $SESSION_NAME"
echo "Models: ${MODELS[@]}"
echo "Cycles: $CYCLES (S1→S2→S3→S4)"
echo "Total Turns: $TOTAL_TURNS"
echo "Output: $OUTPUT_DIR"
echo ""

# Function to run single turn for one model (FIXED: use stdin)
run_turn() {
    local model=$1
    local model_name=$2
    local turn=$3
    local prompt=$4

    echo "Turn $turn - $model_name" >> "$OUTPUT_DIR/${model_name}_log.txt"

    # Run ollama with prompt via stdin (FIXED)
    echo "$prompt" | ollama run "$model" 2>&1 > "$OUTPUT_DIR/${model_name}_turn_${turn}.txt"
}

# Run experiment
echo "Starting parallel execution..."

for turn in $(seq 1 $TOTAL_TURNS); do
    # Determine chamber
    chamber_idx=$(( (turn - 1) % 4 ))
    cycle=$(( (turn - 1) / 4 + 1 ))

    case $chamber_idx in
        0) chamber="S1"; prompt="$S1_PROMPT" ;;
        1) chamber="S2"; prompt="$S2_PROMPT" ;;
        2) chamber="S3"; prompt="$S3_PROMPT" ;;
        3) chamber="S4"; prompt="$S4_PROMPT" ;;
    esac

    echo ""
    echo "▶ Cycle $cycle - Chamber $chamber - Turn $turn/$TOTAL_TURNS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Fire all 3 models in parallel
    run_turn "${MODELS[0]}" "${MODEL_NAMES[0]}" "$turn" "$prompt" &
    pid0=$!

    run_turn "${MODELS[1]}" "${MODEL_NAMES[1]}" "$turn" "$prompt" &
    pid1=$!

    run_turn "${MODELS[2]}" "${MODEL_NAMES[2]}" "$turn" "$prompt" &
    pid2=$!

    # Wait for all 3 to complete (parallel execution)
    wait $pid0 $pid1 $pid2

    echo "✓ Turn $turn complete (all 3 models responded)"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Experiment complete!"
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "To analyze results:"
echo "  ./scripts/analyze_local3.sh $OUTPUT_DIR"
echo ""
