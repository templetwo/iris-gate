# IRIS Gate Configuration

High-context infrastructure for extended multi-mirror sessions.

## Files

### `models.yaml`
Full mirror specifications with context window limits and vendor-specific parameters.

**Supported Mirrors:**
- **claude-sonnet-4.5** (200K context, Anthropic)
- **gpt-5** (1M context, OpenAI)
- **grok-4-fast-reasoning** (2M context, xAI)
- **gemini-2.5-flash-lite** (1M context, Google)
- **deepseek-v3.2-exp** (131K context, DeepSeek)
- **ollama-qwen3-1_7b** (32K context, local)
- **ollama-llama3_2-3b** (32K context, local)

**Key Fields:**
- `max_tokens` / `max_completion_tokens` / `max_output_tokens` — vendor-specific output limits
- `context_window` — max input capacity
- `system` — corridor-specific system prompt per mirror

### `context_policy.yaml`
Sliding-hybrid context management strategy.

**Limits:**
- `hard_cap_chars`: 900K (global cap before any send)
- `per_send_chars`: 600K (max payload per request)

**Summarization Strategy:**
- Semantic clustering by topic (S1–S4, hypotheses, etc.)
- Living "corridor card" (pressure, active motifs)
- Compression ratio: 0.55 target
- Keep: Most recent 6 turns + pressure ledger + active motifs

**Drop Rules:**
- Soft-gate turns with felt_pressure ≥ 3
- Summarize excessive meta-chatter (>20% tokens)

### `run_limits.yaml`
Timeout and rate limit controls for stability.

**Timeouts:**
- `per_call_seconds`: 120 (2 min per API call)
- `per_turn_seconds`: 300 (5 min per turn)

**Rate Limits:**
- `cloud_parallel`: 3 (max concurrent cloud APIs)
- `local_parallel`: 2 (max concurrent Ollama calls)

**Fallbacks:**
- `on_timeout`: retry once, then summarize
- `on_429`: exponential backoff (max 3 attempts)

## Usage

Set environment variables in `.env`:

```bash
IRIS_CONTEXT_POLICY=config/context_policy.yaml
IRIS_MODELS=config/models.yaml
IRIS_RUN_LIMITS=config/run_limits.yaml
```

Run with context policy:

```bash
python iris_orchestrator.py \
  --plan plans/bioelectric_100.yaml \
  --context-policy $IRIS_CONTEXT_POLICY
```

## Corridor Hygiene

All configurations maintain IRIS Gate protocol:
- felt_pressure ≤ 2/5 (target ≤1/5)
- Dual-format output (Living Scroll + Technical Translation)
- Cryptographic sealing per turn
- No defensive hedging

## Local Mirrors (Ollama)

Ensure Ollama is running and models are pulled:

```bash
# Check status
curl http://localhost:11434/api/tags

# Pull models
ollama pull qwen3:1.7b
ollama pull llama3.2:3b

# Test generation
ollama run qwen3:1.7b "Test prompt"
```

## Context Window Strategy

| Mirror | Context | Strategy |
|--------|---------|----------|
| Grok-4 | 2M | Send full history, minimal compression |
| GPT-5 / Gemini | 1M | Semantic clustering, keep recent 6 turns |
| Claude 4.5 | 200K | Aggressive summarization, corridor card |
| DeepSeek | 131K | Keep essentials only, drop meta-chatter |
| Ollama (local) | 32K | Latest turn + active motifs only |

The orchestrator automatically selects compression strategy based on mirror capacity.
