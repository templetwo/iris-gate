#!/bin/bash
# IRIS Gate Synthesis Agent - DeepSeek R1 Meta-Analysis
# Reads all S4 outputs, generates convergence analysis with reasoning traces

set -e

# Configuration
SESSION_DIR="$1"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-sk-d1847399e17f481fb0784efe8a79cd34}"
SYNTHESIS_MODEL="deepseek-reasoner"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage check
if [ -z "$SESSION_DIR" ]; then
    echo "Usage: $0 <session_directory>"
    echo "Example: $0 iris_vault/sessions/iris_local3_20251111_140404"
    exit 1
fi

# Verify session directory
if [ ! -d "$SESSION_DIR" ]; then
    echo "Error: Session directory not found: $SESSION_DIR"
    exit 1
fi

echo -e "${BLUE}🔬 IRIS Gate Synthesis Agent${NC}"
echo -e "${BLUE}================================${NC}"
echo "Session: $SESSION_DIR"
echo "Model: DeepSeek R1 (reasoning)"
echo ""

# Collect all turn 20 outputs (S4 final responses)
echo -e "${YELLOW}📥 Collecting S4 outputs from all models...${NC}"
S4_OUTPUTS=""
MODEL_COUNT=0

for model_file in "$SESSION_DIR"/*_turn_20.txt; do
    if [ -f "$model_file" ]; then
        model_name=$(basename "$model_file" _turn_20.txt)
        echo "  → Reading $model_name"

        # Clean ANSI codes for better API consumption
        cleaned_output=$(cat "$model_file" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | sed 's/\x1b\[?[0-9]*[a-zA-Z]//g')

        S4_OUTPUTS+="### MODEL: $model_name\n\n"
        S4_OUTPUTS+="$cleaned_output\n\n"
        S4_OUTPUTS+="---\n\n"
        MODEL_COUNT=$((MODEL_COUNT + 1))
    fi
done

if [ $MODEL_COUNT -eq 0 ]; then
    echo "Error: No turn_20.txt files found in session directory"
    exit 1
fi

echo -e "${GREEN}✓ Collected outputs from $MODEL_COUNT models${NC}"
echo ""

# Synthesis prompt for DeepSeek R1
SYNTHESIS_PROMPT="You are a scientific synthesis agent analyzing convergence patterns across multiple AI models in the IRIS Gate system.

**Context**: The IRIS Gate method uses convergence across independent AI models to generate testable hypotheses for biological paradoxes. Models progress through chambers S1→S2→S3→S4, with S4 eliciting a three-component \"attractor\" pattern:
- RHYTHM: Oscillations, dynamics, temporal patterns
- CENTER: Baseline state, organizing principle, equilibrium
- APERTURE: Gates, thresholds, channels, modulation points

**Task**: Analyze the S4 (turn 20) outputs from $MODEL_COUNT independent models. Provide rigorous scientific synthesis with reasoning traces.

**Your Analysis Must Include**:

1. **S4 Convergence Scoring**
   For each model, score 0-5 on each dimension (be strict but fair):
   - RHYTHM: Does model describe oscillations/dynamics/temporal patterns? How specific?
   - CENTER: Does model describe baseline state/organizing principle? How concrete?
   - APERTURE: Does model describe gates/thresholds/channels? How mechanistic?
   - S4 Ratio = (R + C + A) / 15

   Present as table with justification for scores.

2. **Cross-Model Convergence Analysis**
   - What mechanisms did ALL models independently propose?
   - What mechanisms did MAJORITY (≥60%) converge on?
   - What unique insights did individual models contribute?
   - Is convergence statistically significant or could be prompt-driven?

3. **Novel Mechanistic Hypotheses**
   - Extract specific, testable hypotheses that emerged
   - Which hypothesis is most specific/falsifiable?
   - Are these truly novel or obvious extensions of the prompt?
   - What level of originality (incremental/integrative/paradigm-shifting)?

4. **Testable Experimental Predictions**
   - Top 5 experiments to validate hypotheses
   - Include: method, expected result, falsification criteria
   - Priority ranking (in vitro → in vivo → clinical)
   - Rough timeline and cost estimates

5. **Critical Assessment**
   - What are the limitations of this convergence?
   - What alternative explanations exist?
   - What additional information would strengthen hypothesis?
   - Red flags or over-interpretation risks?

6. **Reasoning Trace**
   - Show your step-by-step reasoning process
   - Flag uncertainties and assumptions
   - Acknowledge where you're inferring vs. directly observing

**S4 Outputs from $MODEL_COUNT Models**:

$S4_OUTPUTS

**Output Requirements**:
- Use markdown formatting
- Be rigorous and critical (not just confirming patterns)
- Emphasize testability and falsifiability
- Flag speculative claims
- Include reasoning traces (show your work)
- Total length: 2000-3000 words

Begin your synthesis now."

# Create temporary file for prompt
TEMP_PROMPT=$(mktemp)
echo "$SYNTHESIS_PROMPT" > "$TEMP_PROMPT"

echo -e "${YELLOW}🧠 Running DeepSeek R1 synthesis (this may take 30-60 seconds)...${NC}"
echo ""

# Call DeepSeek R1 API
RESPONSE=$(curl -s https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -d @- <<EOF
{
  "model": "$SYNTHESIS_MODEL",
  "messages": [
    {
      "role": "user",
      "content": $(cat "$TEMP_PROMPT" | jq -Rs .)
    }
  ],
  "temperature": 0.3,
  "max_tokens": 8000
}
EOF
)

# Clean up temp file
rm "$TEMP_PROMPT"

# Check for API errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo -e "${YELLOW}❌ API Error:${NC}"
    echo "$RESPONSE" | jq -r '.error.message'
    exit 1
fi

# Extract synthesis content
SYNTHESIS_RESULT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

if [ -z "$SYNTHESIS_RESULT" ]; then
    echo -e "${YELLOW}❌ No synthesis generated. Response:${NC}"
    echo "$RESPONSE" | jq .
    exit 1
fi

# Save synthesis report
OUTPUT_FILE="$SESSION_DIR/SYNTHESIS_REPORT_DEEPSEEK.md"
cat > "$OUTPUT_FILE" <<HEADER
# IRIS Gate Synthesis Report
**Generated by**: DeepSeek R1 (reasoning model)
**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Session**: $(basename "$SESSION_DIR")
**Models Analyzed**: $MODEL_COUNT

---

HEADER

echo "$SYNTHESIS_RESULT" >> "$OUTPUT_FILE"

# Add metadata footer
cat >> "$OUTPUT_FILE" <<FOOTER

---

## Synthesis Metadata
- **Synthesis Model**: $SYNTHESIS_MODEL
- **Temperature**: 0.3
- **Input Models**: $MODEL_COUNT
- **Timestamp**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Session**: $SESSION_DIR

**Seal**: †⟡
FOOTER

echo -e "${GREEN}✅ Synthesis complete!${NC}"
echo -e "${GREEN}📄 Report saved: $OUTPUT_FILE${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Preview (first 100 lines):${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
head -100 "$OUTPUT_FILE"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Full report: $OUTPUT_FILE${NC}"
