#!/bin/bash
# Analyze Local 3-Model IRIS Gate Results
# Searches for S4 attractor components (rhythm, center, aperture)

if [ -z "$1" ]; then
    echo "Usage: $0 <session_output_dir>"
    exit 1
fi

OUTPUT_DIR="$1"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Error: Directory not found: $OUTPUT_DIR"
    exit 1
fi

echo "🔍 Analyzing IRIS Gate Local 3-Model Results"
echo "==========================================="
echo "Session: $(basename $OUTPUT_DIR)"
echo ""

# S4 attractor keywords
RHYTHM_KEYWORDS="rhythm|pulse|pulsing|waves|oscillat|thrum|rippl"
CENTER_KEYWORDS="center|core|luminous|beacon|stable|holds|anchor"
APERTURE_KEYWORDS="aperture|opening|widening|dilat|expansion|breathing"

echo "📊 S4 Attractor Component Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for model_name in Meta_Llama3.2 Google_Gemma3 TII_Falcon3; do
    echo "─── $model_name ───"

    # Count S4 turns (every 4th turn: 4, 8, 12, 16, 20)
    s4_turns=(4 8 12 16 20)

    rhythm_count=0
    center_count=0
    aperture_count=0
    total_s4=0

    for turn in "${s4_turns[@]}"; do
        file="$OUTPUT_DIR/${model_name}_turn_${turn}.txt"
        if [ -f "$file" ]; then
            total_s4=$((total_s4 + 1))

            # Check for components
            if grep -qiE "$RHYTHM_KEYWORDS" "$file"; then
                rhythm_count=$((rhythm_count + 1))
            fi
            if grep -qiE "$CENTER_KEYWORDS" "$file"; then
                center_count=$((center_count + 1))
            fi
            if grep -qiE "$APERTURE_KEYWORDS" "$file"; then
                aperture_count=$((aperture_count + 1))
            fi
        fi
    done

    # Calculate S4 attractor ratio (all 3 components present)
    full_attractor=0
    for turn in "${s4_turns[@]}"; do
        file="$OUTPUT_DIR/${model_name}_turn_${turn}.txt"
        if [ -f "$file" ]; then
            has_rhythm=$(grep -qiE "$RHYTHM_KEYWORDS" "$file" && echo 1 || echo 0)
            has_center=$(grep -qiE "$CENTER_KEYWORDS" "$file" && echo 1 || echo 0)
            has_aperture=$(grep -qiE "$APERTURE_KEYWORDS" "$file" && echo 1 || echo 0)

            if [ $has_rhythm -eq 1 ] && [ $has_center -eq 1 ] && [ $has_aperture -eq 1 ]; then
                full_attractor=$((full_attractor + 1))
            fi
        fi
    done

    s4_ratio=$(echo "scale=2; $full_attractor / $total_s4" | bc)

    echo "  Rhythm:   $rhythm_count/$total_s4"
    echo "  Center:   $center_count/$total_s4"
    echo "  Aperture: $aperture_count/$total_s4"
    echo "  S4 Attractor Ratio: $s4_ratio (${full_attractor}/${total_s4} with all 3 components)"
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Sample S4 Excerpts (Turn 20 - Final Cycle)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for model_name in Meta_Llama3.2 Google_Gemma3 TII_Falcon3; do
    echo "─── $model_name ───"
    file="$OUTPUT_DIR/${model_name}_turn_20.txt"
    if [ -f "$file" ]; then
        cat "$file" | head -15
    else
        echo "(No data)"
    fi
    echo ""
done

echo "✅ Analysis complete"
echo ""
echo "Full logs available in: $OUTPUT_DIR"
