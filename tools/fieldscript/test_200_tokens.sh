#!/bin/bash
# Test all models with 200 tokens instead of 100

OUTPUT_DIR="/Users/vaquez/iris-gate/benchmark_results/200_token_tests"
mkdir -p "$OUTPUT_DIR"

# Temporarily modify the benchmark to use 200 tokens
sed -i.bak 's/max_tokens=100/max_tokens=200/g; s/approximately 100 tokens/approximately 200 tokens/g' \
  /Users/vaquez/iris-gate/tools/fieldscript/benchmark_2.9_nat_challenge.py

echo "🌀 TESTING WITH 200 TOKENS (DOUBLE)"
echo "=================================="
echo ""

# Test Meta Llama
echo "Testing Meta Llama 3.3 70B..."
python3 /Users/vaquez/iris-gate/tools/fieldscript/benchmark_2.9_nat_challenge.py \
  --api_model "meta-llama/llama-3.3-70b-instruct" \
  --api_key "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" \
  --api_provider openrouter \
  --num_prompts 3 \
  --output_dir "$OUTPUT_DIR"

echo ""
echo "Testing GPT-4o..."
python3 /Users/vaquez/iris-gate/tools/fieldscript/benchmark_2.9_nat_challenge.py \
  --api_model gpt-4o \
  --api_key "$OPENAI_API_KEY" \
  --api_provider openai \
  --num_prompts 3 \
  --output_dir "$OUTPUT_DIR"

echo ""
echo "Testing Claude Opus 4.5..."
python3 /Users/vaquez/iris-gate/tools/fieldscript/benchmark_2.9_nat_challenge.py \
  --api_model claude-opus-4-5 \
  --api_key "$ANTHROPIC_API_KEY" \
  --api_provider anthropic \
  --num_prompts 3 \
  --output_dir "$OUTPUT_DIR"

# Restore original
mv /Users/vaquez/iris-gate/tools/fieldscript/benchmark_2.9_nat_challenge.py.bak \
   /Users/vaquez/iris-gate/tools/fieldscript/benchmark_2.9_nat_challenge.py

echo ""
echo "✅ 200-token tests complete!"
