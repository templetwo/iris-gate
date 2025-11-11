#!/bin/bash
# Live 3-Model IRIS Gate Runner on Mac Studio
# Branch: local-3model-validation
# Features: Length guidance, SSH to Studio, parallel execution

set -e

STUDIO_HOST="tony_studio@192.168.1.195"
OLLAMA_CMD="/usr/local/bin/ollama"

SESSION_NAME="iris_local3_$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="iris_vault/sessions/${SESSION_NAME}"
mkdir -p "$OUTPUT_DIR"

# Models (3B non-reasoning, different ecosystems)
MODELS=(
    "llama3.2:3b"
    "falcon3:3b"
    "gemma3:4b"
)

MODEL_NAMES=(
    "Meta_Llama3.2"
    "TII_Falcon3"
    "Google_Gemma3"
)

# Length guidance prefix (prevents truncation)
LENGTH_GUIDE="[Response length: 200-300 words. Be specific and vivid. Complete your thought.]

"

# Chamber prompts (S1→S2→S3→S4 cycle) WITH LENGTH GUIDANCE
# Question: Why does 1000mg CBD exacerbate psychotic symptoms in schizophrenia but reduce them in healthy controls?

S1_PROMPT="${LENGTH_GUIDE}Observe the CBD paradox from multiple perspectives: molecular (receptors, channels), cellular (neuron function, mitochondria), and systems-level (neural circuits, brain regions). In schizophrenia patients, 1000mg CBD worsens psychosis and memory. In healthy controls, it improves these. Describe what you witness at each level. What patterns or dynamics might differ between these two populations?"

S2_PROMPT="${LENGTH_GUIDE}Hold this paradox without collapsing it: CBD as BOTH therapeutic (in healthy brains) AND harmful (in schizophrenia). Witness the tension between these opposite effects. Don't resolve it yet—observe what this contradiction reveals about the underlying system. What must be different in schizophrenia brains for the same molecule to produce opposite outcomes?"

S3_PROMPT="${LENGTH_GUIDE}Imagine you are a neuron in a schizophrenia patient's brain receiving 1000mg CBD. What does it feel like compared to a healthy neuron? Is the energetic state different? Are the mitochondria behaving differently? Is signal flow disrupted or amplified? Describe the felt quality of cellular response—what's stuck, what's flooding, what's mismatched?"

S4_PROMPT="${LENGTH_GUIDE}Visualize the complete organizing pattern explaining this paradox. Consider: (1) RHYTHM—what oscillations or dynamics are altered in schizophrenia? (2) CENTER—what organizing principle or baseline state differs? (3) APERTURE—what gates, channels, or thresholds respond differently to CBD? Describe the full mechanistic landscape that makes opposite effects inevitable. Be specific and vivid."

# Experiment parameters
CYCLES=5
TURNS_PER_CYCLE=4
TOTAL_TURNS=$((CYCLES * TURNS_PER_CYCLE))

echo "🌀 IRIS Gate Local 3-Model Validation (Mac Studio)"
echo "=================================================="
echo "Session: $SESSION_NAME"
echo "Models: ${MODELS[@]}"
echo "Cycles: $CYCLES (S1→S2→S3→S4)"
echo "Total Turns: $TOTAL_TURNS"
echo "Output: $OUTPUT_DIR"
echo "Remote: $STUDIO_HOST"
echo ""

# Function to run single turn for one model on Mac Studio
run_turn() {
    local model=$1
    local model_name=$2
    local turn=$3
    local prompt=$4

    echo "Turn $turn - $model_name" >> "$OUTPUT_DIR/${model_name}_log.txt"

    # Run ollama on Mac Studio via SSH (using heredoc to pass prompt)
    ssh "$STUDIO_HOST" "$OLLAMA_CMD run $model" <<EOF > "$OUTPUT_DIR/${model_name}_turn_${turn}.txt" 2>&1
$prompt
EOF
}

# Run experiment
echo "Starting parallel execution on Mac Studio..."

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

    # Fire all 3 models in parallel on Mac Studio
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
