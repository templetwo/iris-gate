#!/bin/bash
# IRIS Gate Autonomous Pipeline - Question to Hypothesis
# Usage: ./iris_gate_autonomous.sh "Your research question here"

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${MAGENTA}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🌀 IRIS GATE AUTONOMOUS 🌀                   ║
║                                                           ║
║         Question → Convergence → Hypothesis               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Configuration
QUESTION="$1"
STUDIO_HOST="tony_studio@192.168.1.195"
OLLAMA_CMD="/usr/local/bin/ollama"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY}"
XAI_API_KEY="${XAI_API_KEY}"

# Usage check
if [ -z "$QUESTION" ]; then
    echo "Usage: $0 \"Your research question here\""
    echo ""
    echo "Example:"
    echo "  $0 \"Why does high-dose vitamin C cause kidney stones?\""
    echo ""
    exit 1
fi

# Check API keys
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  DEEPSEEK_API_KEY not set${NC}"
    echo "Tier 2 synthesis (DeepSeek R1) will be skipped."
    echo "  export DEEPSEEK_API_KEY='your-key-here'"
    echo ""
fi

if [ -z "$XAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  XAI_API_KEY not set${NC}"
    echo "Tier 3 synthesis (Grok-4 final verdict) will be skipped."
    echo "  export XAI_API_KEY='your-key-here'"
    echo ""
fi

# Session setup
SESSION_NAME="iris_autonomous_$(date +%Y%m%d_%H%M%S)"
SESSION_DIR="iris_vault/sessions/${SESSION_NAME}"
mkdir -p "$SESSION_DIR"

echo -e "${CYAN}📋 Configuration${NC}"
echo "Question: $QUESTION"
echo "Session: $SESSION_NAME"
echo "Models: 5 (Llama3.2, Falcon3, Gemma3, Hermes3, Granite3)"
echo "Mac Studio: $STUDIO_HOST"
echo ""

# Save question
echo "$QUESTION" > "$SESSION_DIR/QUESTION.txt"

# Model configuration
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

# Generate chamber prompts
echo -e "${BLUE}🎯 Step 1: Generating Chamber Prompts${NC}"

# S1: Attention (turns 1-5)
S1_BASE="${LENGTH_GUIDE}Here is a biological or clinical question that researchers don't fully understand:

$QUESTION

"

# S2: Paradox (turns 6-10)
S2_BASE="${LENGTH_GUIDE}This question involves some kind of tension, paradox, or unexpected relationship. What makes this particularly puzzling or counterintuitive?

Original question: $QUESTION

"

# S3: Embodied (turns 11-15)
S3_BASE="${LENGTH_GUIDE}Let's ground this in specific physical mechanisms. What receptors, circuits, molecules, or oscillations might be involved?

Question: $QUESTION

"

# S4: Full Field (turn 20 - the critical one)
S4_PROMPT="${LENGTH_GUIDE}Visualize the complete organizing pattern that explains this phenomenon. Consider:

(1) RHYTHM—what oscillations, dynamics, or temporal patterns are involved? What wave patterns, firing patterns, or cycling processes?

(2) CENTER—what is the baseline state or organizing principle? What stable point, equilibrium, or organizing attractor exists?

(3) APERTURE—what gates, channels, thresholds, or modulation points control the response? What opens or closes to determine outcomes?

Question: $QUESTION

Describe the full mechanistic landscape. Be specific and vivid."

echo "✓ Generated S1-S4 prompts"
echo ""

# Execute parallel models
echo -e "${YELLOW}🔥 Step 2: Firing 5 Models in Parallel${NC}"
echo "This will take ~2-3 minutes..."
echo ""

# Function to run single model for all turns
run_model() {
    local model=$1
    local model_name=$2
    local start_time=$(date +%s)

    echo "  ▶ Starting $model_name..."

    # Turn 20 (S4) - the critical convergence turn
    ssh "$STUDIO_HOST" "$OLLAMA_CMD run $model" > "$SESSION_DIR/${model_name}_turn_20.txt" 2>&1 <<EOF
$S4_PROMPT
EOF

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "  ✓ $model_name complete (${duration}s)"
}

# Fire all 5 models in parallel
for i in "${!MODELS[@]}"; do
    run_model "${MODELS[$i]}" "${MODEL_NAMES[$i]}" &
done

# Wait for all models to complete
wait

echo ""
echo -e "${GREEN}✅ All 5 models completed S4 convergence${NC}"
echo ""

# Tier 2: DeepSeek R1 synthesis
if [ -n "$DEEPSEEK_API_KEY" ]; then
    echo -e "${MAGENTA}🧠 Step 3: Tier 2 Synthesis - DeepSeek R1${NC}"
    echo "Analyzing convergence patterns with reasoning traces..."
    echo ""

    ./scripts/synthesize_convergence.sh "$SESSION_DIR"

    echo ""
else
    echo -e "${YELLOW}⚠️  Skipping Tier 2 synthesis (no DEEPSEEK_API_KEY)${NC}"
    echo ""
fi

# Tier 3: Grok-4 final verdict (cosmic hypothesis boss)
if [ -n "$XAI_API_KEY" ]; then
    # Only run Grok-4 if DeepSeek synthesis exists
    if [ -f "$SESSION_DIR/SYNTHESIS_REPORT_DEEPSEEK.md" ]; then
        echo -e "${MAGENTA}🌌 Step 4: Tier 3 Synthesis - Grok-4 Final Verdict${NC}"
        echo "The cosmic hypothesis boss reviews all convergence..."
        echo ""

        ./scripts/grok4_final_synthesis.sh "$SESSION_DIR"

        echo ""
    else
        echo -e "${YELLOW}⚠️  Skipping Tier 3 (need DeepSeek synthesis first)${NC}"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  Skipping Tier 3 synthesis (no XAI_API_KEY)${NC}"
    echo ""
fi

# Generate summary report
SUMMARY_FILE="$SESSION_DIR/SESSION_SUMMARY.md"

cat > "$SUMMARY_FILE" <<SUMMARY
# IRIS Gate Autonomous Session Summary

**Session**: $SESSION_NAME
**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Question**: $QUESTION

---

## Session Files

- \`QUESTION.txt\` - Original research question
- \`*_turn_20.txt\` - S4 outputs from 5 models
- \`SYNTHESIS_REPORT_DEEPSEEK.md\` - Tier 2: DeepSeek R1 convergence analysis (if generated)
- \`FINAL_VERDICT_GROK4.md\` - Tier 3: Grok-4 final verdict (if generated)
- \`SESSION_SUMMARY.md\` - This file

---

## Models Used

1. Meta Llama 3.2 (3B) - Meta ecosystem
2. TII Falcon 3 (3B) - UAE/TII ecosystem
3. Google Gemma 3 (4B) - Google ecosystem
4. Nous Hermes 3 (8B) - Nous Research ecosystem
5. IBM Granite 3 MoE (3B) - IBM ecosystem

---

## Synthesis Chain

**Tier 1**: 5 diverse models → S4 convergence patterns (rhythm/center/aperture)
**Tier 2**: DeepSeek R1 → hypothesis extraction + reasoning traces
**Tier 3**: Grok-4 → final verdict + cosmic insight (cosmic hypothesis boss)

---

## Next Steps

1. **Review Final Verdict**: Read \`FINAL_VERDICT_GROK4.md\` (if generated) - the ultimate synthesis
2. **Review DeepSeek Analysis**: Read \`SYNTHESIS_REPORT_DEEPSEEK.md\` (if generated)
3. **Manual Analysis**: Review individual model outputs in \`*_turn_20.txt\`
4. **Validate Novelty**: Search literature for proposed mechanisms
5. **Documentation**: Create OSF component if hypothesis is novel

---

**Seal**: †⟡⚡
**Status**: Session complete, ready for review
SUMMARY

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ IRIS Gate Autonomous Pipeline Complete!${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📁 Session Directory:${NC} $SESSION_DIR"
echo ""
echo -e "${BLUE}📄 Generated Files:${NC}"
ls -1 "$SESSION_DIR" | sed 's/^/  - /'
echo ""

if [ -f "$SESSION_DIR/FINAL_VERDICT_GROK4.md" ]; then
    echo -e "${MAGENTA}🌌 Grok-4 Final Verdict Preview:${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    head -40 "$SESSION_DIR/FINAL_VERDICT_GROK4.md"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}Full verdict: $SESSION_DIR/FINAL_VERDICT_GROK4.md${NC}"
    echo -e "${GREEN}DeepSeek analysis: $SESSION_DIR/SYNTHESIS_REPORT_DEEPSEEK.md${NC}"
elif [ -f "$SESSION_DIR/SYNTHESIS_REPORT_DEEPSEEK.md" ]; then
    echo -e "${MAGENTA}🔬 DeepSeek Synthesis Preview:${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    head -30 "$SESSION_DIR/SYNTHESIS_REPORT_DEEPSEEK.md"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}Full synthesis: $SESSION_DIR/SYNTHESIS_REPORT_DEEPSEEK.md${NC}"
    echo -e "${YELLOW}Note: Grok-4 verdict skipped (no XAI_API_KEY)${NC}"
else
    echo -e "${YELLOW}Note: Synthesis skipped (no API keys)${NC}"
    echo "Run manually:"
    echo "  ./scripts/synthesize_convergence.sh $SESSION_DIR"
    echo "  ./scripts/grok4_final_synthesis.sh $SESSION_DIR"
fi

echo ""
echo -e "${MAGENTA}🌀 The spiral moves. The cosmic verdict is rendered. †⟡⚡${NC}"
