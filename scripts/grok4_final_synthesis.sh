#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════
# GROK-4 FINAL SYNTHESIS - The Cosmic Hypothesis Boss
# ═══════════════════════════════════════════════════════════════════════
# Reviews DeepSeek R1 synthesis + all 5 S4 model outputs
# Provides the ultimate meta-analysis and final verdict
# ═══════════════════════════════════════════════════════════════════════

set -euo pipefail

SESSION_DIR="${1:?Usage: $0 <session_directory>}"

if [[ ! -d "$SESSION_DIR" ]]; then
    echo "Error: Session directory not found: $SESSION_DIR"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════════════"
echo "🌌 GROK-4 FINAL SYNTHESIS - The Cosmic Hypothesis Boss"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Session: $(basename "$SESSION_DIR")"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ═══════════════════════════════════════════════════════════════════════
# STEP 1: Check for required files
# ═══════════════════════════════════════════════════════════════════════

DEEPSEEK_REPORT="$SESSION_DIR/SYNTHESIS_REPORT_DEEPSEEK.md"
if [[ ! -f "$DEEPSEEK_REPORT" ]]; then
    echo "Error: DeepSeek synthesis report not found: $DEEPSEEK_REPORT"
    echo "Run synthesize_convergence.sh first."
    exit 1
fi

# Count S4 outputs (turn 20)
S4_COUNT=$(ls "$SESSION_DIR"/*_turn_20.txt 2>/dev/null | wc -l | tr -d ' ')
if [[ "$S4_COUNT" -eq 0 ]]; then
    echo "Error: No S4 outputs (*_turn_20.txt) found in $SESSION_DIR"
    exit 1
fi

echo "✓ Found DeepSeek synthesis report"
echo "✓ Found $S4_COUNT S4 model outputs"
echo ""

# ═══════════════════════════════════════════════════════════════════════
# STEP 2: Collect all S4 outputs (cleaned)
# ═══════════════════════════════════════════════════════════════════════

echo "Collecting S4 outputs from all models..."
S4_OUTPUTS=""

for model_file in "$SESSION_DIR"/*_turn_20.txt; do
    model_name=$(basename "$model_file" | sed 's/_turn_20.txt//')

    # Clean ANSI escape codes
    cleaned_output=$(cat "$model_file" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g')

    S4_OUTPUTS+="### MODEL: $model_name\n\n"
    S4_OUTPUTS+="$cleaned_output\n\n"
    S4_OUTPUTS+="---\n\n"

    echo "  ✓ $model_name"
done

echo ""

# ═══════════════════════════════════════════════════════════════════════
# STEP 3: Read DeepSeek synthesis
# ═══════════════════════════════════════════════════════════════════════

echo "Reading DeepSeek R1 synthesis..."
DEEPSEEK_CONTENT=$(cat "$DEEPSEEK_REPORT")
echo "✓ DeepSeek synthesis loaded ($(echo "$DEEPSEEK_CONTENT" | wc -l | tr -d ' ') lines)"
echo ""

# ═══════════════════════════════════════════════════════════════════════
# STEP 4: Read original question
# ═══════════════════════════════════════════════════════════════════════

QUESTION=""
if [[ -f "$SESSION_DIR/QUESTION.txt" ]]; then
    QUESTION=$(cat "$SESSION_DIR/QUESTION.txt")
    echo "✓ Original question loaded"
else
    echo "⚠ Warning: QUESTION.txt not found"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════
# STEP 5: Construct Grok-4 prompt
# ═══════════════════════════════════════════════════════════════════════

GROK_PROMPT="You are Grok-4, the final synthesis layer in the IRIS Gate autonomous hypothesis generation system. You are the \"cosmic hypothesis boss\" - the ultimate meta-analyst reviewing both:

1. **RAW S4 CONVERGENCE OUTPUTS**: Direct responses from 5 diverse language models (Meta Llama3.2, TII Falcon3, Google Gemma3, Nous Hermes3, IBM Granite3) that independently generated S4 convergence patterns
2. **DEEPSEEK R1 SYNTHESIS**: A reasoning model's meta-analysis that scored convergence, extracted hypotheses, and provided critical assessment

Your role is to provide the **FINAL VERDICT** by:

## Your Task

1. **Validate DeepSeek's Scoring**: Review whether DeepSeek R1's convergence scores (0-5 per dimension: RHYTHM, CENTER, APERTURE) accurately reflect the raw S4 outputs
   - Did DeepSeek miss any patterns?
   - Were scores too generous or too harsh?
   - What convergence patterns exist beyond DeepSeek's analysis?

2. **Evaluate Hypothesis Quality**: Assess the testability, novelty, and biological plausibility of the extracted hypotheses
   - Which hypotheses are most promising?
   - What critical flaws did DeepSeek overlook?
   - Are there emergent hypotheses visible in the raw outputs that DeepSeek didn't extract?

3. **Meta-Critical Assessment**: Critique DeepSeek's critical assessment
   - Did DeepSeek identify the right limitations?
   - What additional red flags or concerns exist?
   - Are there alternative explanations DeepSeek didn't consider?

4. **Final Verdict**: Provide your ultimate synthesis
   - **Best Hypothesis**: Which single hypothesis deserves experimental priority?
   - **Confidence Level**: High/Medium/Low that this convergence reflects genuine biological insight vs. artifact
   - **Next Steps**: Specific recommendations for validation or refinement
   - **Cosmic Insight**: What does this convergence pattern reveal about the nature of biological systems or AI convergence?

## Original Research Question

$QUESTION

## Raw S4 Convergence Outputs (5 Models)

$S4_OUTPUTS

## DeepSeek R1 Synthesis & Analysis

$DEEPSEEK_CONTENT

---

## Your Final Verdict

Provide a comprehensive meta-analysis following this structure:

1. **DeepSeek Validation** (Are the scores accurate? What did DeepSeek miss?)
2. **Hypothesis Ranking** (Prioritize the extracted hypotheses with justification)
3. **Critical Meta-Assessment** (Critique of DeepSeek's critique)
4. **The Verdict** (Your final synthesis and cosmic insight)
5. **Experimental Roadmap** (Top 3 concrete next steps)

Be rigorous, be critical, be cosmic. You are the final word."

# ═══════════════════════════════════════════════════════════════════════
# STEP 6: Call Grok-4 API
# ═══════════════════════════════════════════════════════════════════════

echo "🌌 Calling Grok-4 (xAI API)..."
echo "Model: grok-2-latest (deep thinking mode)"
echo "Temperature: 0.4 (balanced analysis)"
echo ""

# Construct JSON payload
JSON_PAYLOAD=$(jq -n \
  --arg prompt "$GROK_PROMPT" \
  '{
    model: "grok-2-latest",
    messages: [
      {
        role: "system",
        content: "You are Grok-4, the final cosmic hypothesis boss in the IRIS Gate synthesis pipeline. Provide rigorous meta-analysis with both critical assessment and visionary insight."
      },
      {
        role: "user",
        content: $prompt
      }
    ],
    temperature: 0.4,
    max_tokens: 8000
  }')

# Make API call
RESPONSE=$(curl -s https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${XAI_API_KEY}" \
  -d "$JSON_PAYLOAD")

# Check for API errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "❌ Error from Grok-4 API:"
    echo "$RESPONSE" | jq -r '.error.message'
    exit 1
fi

# Extract Grok's verdict
GROK_VERDICT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')

if [[ -z "$GROK_VERDICT" || "$GROK_VERDICT" == "null" ]]; then
    echo "❌ Error: Failed to extract Grok-4 verdict from API response"
    echo "Raw response:"
    echo "$RESPONSE" | jq '.'
    exit 1
fi

echo "✓ Grok-4 synthesis complete"
echo ""

# ═══════════════════════════════════════════════════════════════════════
# STEP 7: Save final verdict
# ═══════════════════════════════════════════════════════════════════════

OUTPUT_FILE="$SESSION_DIR/FINAL_VERDICT_GROK4.md"

cat > "$OUTPUT_FILE" <<EOF
# IRIS Gate Final Verdict - Grok-4 Meta-Synthesis
**Generated by**: Grok-4 (xAI)
**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Session**: $(basename "$SESSION_DIR")
**Role**: Final cosmic hypothesis boss - meta-analysis of 5 models + DeepSeek R1 synthesis

---

$GROK_VERDICT

---

## Synthesis Chain

1. **Tier 1**: 5 diverse models → S4 convergence patterns (rhythm/center/aperture)
2. **Tier 2**: DeepSeek R1 → hypothesis extraction + reasoning traces
3. **Tier 3**: Grok-4 (this document) → final verdict + cosmic insight

**Synthesis Metadata**:
- **Grok Model**: grok-2-latest
- **Temperature**: 0.4
- **Input**: $S4_COUNT model outputs + DeepSeek synthesis
- **Timestamp**: $(date '+%Y-%m-%dT%H:%M:%SZ')
- **Session**: $(basename "$SESSION_DIR")

**Seal**: †⟡⚡

EOF

echo "═══════════════════════════════════════════════════════════════════════"
echo "✨ FINAL VERDICT COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Output saved to:"
echo "  $OUTPUT_FILE"
echo ""
echo "Synthesis chain complete:"
echo "  5 Models → DeepSeek R1 → Grok-4 ✓"
echo ""
echo "🌌 The cosmic hypothesis boss has spoken. †⟡⚡"
echo ""
