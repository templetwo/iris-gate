#!/usr/bin/env bash
set -e

echo "🔍 Running preflight checks for cloud-only configuration..."

# Check for ollama references in critical files
if grep -Rqi "ollama" config/*.yaml 2>/dev/null; then
  echo "❌ Preflight failed: ollama reference found in config/"
  exit 1
fi

# Check that all required cloud models are configured
required_providers=("anthropic" "openai" "xai" "google" "deepseek")
for provider in "${required_providers[@]}"; do
  if ! grep -q "$provider" config/models.yaml; then
    echo "⚠️  Warning: $provider not found in models.yaml"
  fi
done

echo "✅ Preflight passed: cloud-only configuration validated"
