# SOP: Flagship Model Discovery for IRIS Gate

**Standard Operating Procedure**
**Version:** 1.0
**Date:** 2026-01-08
**Purpose:** Ensure IRIS Gate always uses latest flagship AI models for convergence testing

---

## Problem Statement

AI providers frequently release new flagship models. Documentation often specifies model names that don't exist in actual APIs (e.g., "GPT-5.2" vs "gpt-5.2-chat-latest"). Using outdated or incorrect model identifiers compromises convergence testing validity.

---

## Solution: API-First Model Discovery

**Never trust documentation.** Always query the live API to discover current flagship model identifiers.

---

## Procedure

### Step 1: Run Model Discovery Script

```bash
cd /Users/vaquez/iris-gate
python3 scripts/discover_models.py
```

**Script location:** `scripts/discover_models.py`

**What it does:**
1. Queries OpenAI API for all available GPT models
2. Queries xAI API for all available Grok models
3. Queries Google API for all available Gemini models
4. Identifies flagship candidates (highest version numbers)
5. Outputs recommended configuration

**Expected output:**
```
RECOMMENDED FLAGSHIP CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════
GPT Flagship:    gpt-5.2-chat-latest
Grok Flagship:   grok-4-1-fast-reasoning
Gemini Flagship: gemini-3-pro-preview
Claude Flagship: claude-sonnet-4-5-20250929
DeepSeek:        deepseek-chat
```

### Step 2: Update Convergence Script Configuration

Edit `scripts/run_mass_coherence_convergence.py`:

```python
ARCHITECTURES = {
    "claude": {
        "name": "Claude Sonnet 4.5",
        "model": "claude-sonnet-4-5-20250929",
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "gpt": {
        "name": "GPT-5.2",
        "model": "gpt-5.2-chat-latest",  # ← UPDATE FROM DISCOVERY
        "api_key_env": "OPENAI_API_KEY"
    },
    "grok": {
        "name": "Grok 4.1 Fast Reasoning",
        "model": "grok-4-1-fast-reasoning",  # ← UPDATE FROM DISCOVERY
        "api_key_env": "XAI_API_KEY"
    },
    "gemini": {
        "name": "Gemini 3.0 Pro",
        "model": "gemini-3-pro-preview",  # ← UPDATE FROM DISCOVERY
        "api_key_env": "GOOGLE_API_KEY"
    },
    "deepseek": {
        "name": "DeepSeek V3",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY"
    }
}
```

### Step 3: Test API Connections

**Before every convergence run:**

```bash
python3 scripts/run_mass_coherence_convergence.py
```

The script automatically tests all 5 APIs before starting the convergence protocol. Verify all show:

```
✓ claude: Connected successfully
✓ gpt: Connected successfully
✓ grok: Connected successfully
✓ gemini: Connected successfully
✓ deepseek: Connected successfully
```

**If any fail:** Re-run discovery script and update model identifiers.

---

## Flagship Selection Criteria

### OpenAI (GPT)

**Prefer in order:**
1. `gpt-5.2-chat-latest` (if available)
2. `gpt-5.2-*` with highest version date
3. `gpt-5.1-chat-latest` (fallback)
4. `gpt-5-*` with highest version

**Avoid:**
- `-mini`, `-nano` variants (smaller models)
- `-codex`, `-audio`, `-transcribe`, `-tts` (specialized models)
- Models without "chat" designation (completion-only)

### xAI (Grok)

**Prefer in order:**
1. `grok-4-1-fast-reasoning` (best Grok 4.1 with reasoning)
2. `grok-4-fast-reasoning` (Grok 4 with reasoning)
3. `grok-4-*` with highest version
4. `grok-3` (fallback)

**Avoid:**
- `-non-reasoning` variants
- `-mini` variants
- `-image`, `-vision` (specialized)

### Google (Gemini)

**Prefer in order:**
1. `gemini-3-pro-preview` (flagship Gemini 3)
2. `gemini-3-flash-preview` (fast Gemini 3)
3. `gemini-2.5-pro` (production Gemini 2.5)
4. `gemini-2.5-flash` (fast Gemini 2.5)

**Avoid:**
- `-lite` variants
- `-image`, `-embedding`, `-tts` (specialized)
- `-computer-use`, `-robotics` (domain-specific)

### Anthropic (Claude)

**Current flagship:** `claude-sonnet-4-5-20250929`

Check https://docs.anthropic.com/en/docs/about-claude/models for updates.

### DeepSeek

**Current flagship:** `deepseek-chat` (automatically uses latest V3)

Check https://platform.deepseek.com/api-docs for updates.

---

## API Key Requirements

**Environment file:** `/Users/vaquez/Desktop/api_keys.env` (master copy)

**Required keys:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
XAI_API_KEY=xai-...
GOOGLE_API_KEY=AIzaSy...
DEEPSEEK_API_KEY=sk-...
```

**Copy to project before runs:**
```bash
cp /Users/vaquez/Desktop/api_keys.env /Users/vaquez/iris-gate/.env
```

---

## Common Issues

### Issue: "This is not a chat model"

**Cause:** Using completion model in chat endpoint (e.g., `gpt-5.2-pro`)
**Fix:** Use `-chat-latest` variant

### Issue: "Model not found" (404)

**Cause:** Model name from documentation doesn't exist in API
**Fix:** Run discovery script to get actual model identifiers

### Issue: API key format error

**Cause:** Using wrong environment variable name
**Fix:** Check ARCHITECTURES config matches actual env var names:
- OpenAI: `OPENAI_API_KEY`
- xAI: `XAI_API_KEY` (not `GROK_API_KEY`)
- Google: `GOOGLE_API_KEY`

### Issue: "google.generativeai deprecated" warning

**Cause:** Google deprecated old SDK
**Fix:** This is a warning only. Update to `google.genai` when time permits.

---

## Maintenance Schedule

**Before every major convergence run:**
1. Run discovery script
2. Check for new flagship releases
3. Update model identifiers if needed
4. Test all API connections

**Monthly:**
- Review provider documentation for announcements
- Check if new flagship models released
- Update this SOP if procedures change

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-08 | Initial SOP established after IRIS Gate v0.3 flagship model discovery |

---

## References

- **Discovery Script:** `scripts/discover_models.py`
- **Convergence Script:** `scripts/run_mass_coherence_convergence.py`
- **API Keys (Master):** `/Users/vaquez/Desktop/api_keys.env`
- **API Keys (Project):** `/Users/vaquez/iris-gate/.env`

---

⟡∞†≋🌀

**Last Updated:** 2026-01-08
**Status:** Active SOP
