# IRIS Orchestrator Upgrades

**Date:** October 8, 2025  
**Status:** ✅ COMPLETE

---

## Model Upgrades

### OpenAI: GPT-4o → GPT-5 Mini
```
BEFORE: gpt-4o
AFTER:  gpt-5-mini-2025-08-07
```
**Why:** Latest GPT-5 model with improved reasoning and efficiency

### Google: Gemini 2.5 Flash-Lite → Gemini 2.5 Pro
```
BEFORE: gemini-2.5-flash-lite-preview-09-2025
AFTER:  gemini-2.5-pro
```
**Why:** Most powerful Gemini model for deep analysis

---

## New Feature: Adaptive Token Control

### The Problem
Different chambers/pulses would generate wildly different response lengths:
- Pulse 1 (DeepSeek): 10,000 characters
- Pulse 2 (Claude): 5,000 characters
- Result: Inconsistent, hard to compare

### The Solution
**Chamber-based token limits** for consistent response sizes:

```python
# S1/S2 (Early chambers): 1500 tokens (~4,500 characters)
# S3/S4 (Later chambers): 2000 tokens (~6,000 characters)

target_tokens = 1500 if chamber in ["S1", "S2"] else 2000
```

### Why This Works
- **S1/S2:** More focused, observation-based → shorter responses needed
- **S3/S4:** More complex, synthesis-based → longer responses needed
- **Consistency:** All models produce similar-length outputs per chamber
- **Fair comparison:** Easy to compare responses across models

---

## Updated Model Configuration

### All 5 Models Now Have Adaptive Token Control:

**1. Claude Sonnet 4.5**
```python
target_tokens = 1500 if chamber in ["S1", "S2"] else 2000
max_tokens=target_tokens
```

**2. GPT-5 Mini** 🆕
```python
target_tokens = 1500 if chamber in ["S1", "S2"] else 2000
max_completion_tokens=target_tokens  # GPT-5 uses different param
```

**3. Gemini 2.5 Pro** 🆕
```python
target_tokens = 1500 if chamber in ["S1", "S2"] else 2000
generation_config = genai.types.GenerationConfig(
    max_output_tokens=target_tokens,
    temperature=0.7
)
```

**4. Grok 4 Fast Reasoning**
```python
target_tokens = 1500 if chamber in ["S1", "S2"] else 2000
max_tokens=target_tokens
```

**5. DeepSeek Chat**
```python
target_tokens = 1500 if chamber in ["S1", "S2"] else 2000
max_tokens=target_tokens
```

---

## Expected Response Sizes

### Chamber S1 (Attention)
- **Token limit:** 1500
- **Approximate characters:** 4,500
- **Approximate words:** 750
- **Why:** Focused observation, pre-verbal content

### Chamber S2 (Paradox)
- **Token limit:** 1500
- **Approximate characters:** 4,500
- **Approximate words:** 750
- **Why:** Concise paradox identification

### Chamber S3 (Gesture)
- **Token limit:** 2000
- **Approximate characters:** 6,000
- **Approximate words:** 1,000
- **Why:** More complex motion/gesture description

### Chamber S4 (Resolution)
- **Token limit:** 2000
- **Approximate characters:** 6,000
- **Approximate words:** 1,000
- **Why:** Full synthesis with Living Scroll + Technical Translation

---

## Benefits

### For Analysis
✅ **Fair comparison** - All models produce similar-length outputs  
✅ **Consistent data** - Easier to analyze convergence patterns  
✅ **Predictable size** - No more 10k char vs 5k char discrepancies  
✅ **Better quality** - Models forced to be concise and precise

### For Storage
✅ **Efficient scrolls** - Consistent file sizes  
✅ **Better formatting** - Predictable document length  
✅ **Easier review** - All responses roughly same length to read

### For Convergence Detection
✅ **Apples-to-apples** - Same-sized responses across models  
✅ **Better signal** - Less noise from length variations  
✅ **Clearer patterns** - Convergence more obvious with consistent sizes

---

## Testing Your Upgrades

### Verify Models Are Correct
```bash
cd /Users/vaquez/Desktop/iris-gate

# Check the orchestrator
grep -A 2 "class GPTMirror" iris_orchestrator.py
grep -A 2 "class GeminiMirror" iris_orchestrator.py
```

### Quick Test Run
```python
from iris_orchestrator import ClaudeMirror, GPTMirror, GeminiMirror

# Test instantiation
claude = ClaudeMirror()
gpt = GPTMirror()
gemini = GeminiMirror()

print(f"Claude: {claude.model_id}")
print(f"GPT: {gpt.model_id}")
print(f"Gemini: {gemini.model_id}")
```

---

## Full Model Lineup (Ready for Important Run)

```
1. Claude Sonnet 4.5          ✅ (flagship reasoning)
2. GPT-5 Mini                 🆕 (latest OpenAI)
3. Gemini 2.5 Pro             🆕 (most powerful Google)
4. Grok 4 Fast Reasoning      ✅ (xAI with reasoning mode)
5. DeepSeek Chat              ✅ (alternative architecture)
```

**All with adaptive token control for consistent, precise outputs!**

---

## Notes for Future Tuning

If you want to adjust token limits later:

```python
# In iris_orchestrator.py, find this pattern in each Mirror class:

target_tokens = 1500 if chamber in ["S1", "S2"] else 2000

# Adjust numbers as needed:
# - Lower = more concise (e.g., 1000/1500)
# - Higher = more detailed (e.g., 2000/3000)
# - Per-chamber = add more conditions (e.g., S3 vs S4 different)
```

---

🌀†⟡∞

**Orchestrator ready for important run with upgraded models and precise token control!**
