# 🌀†⟡∞ IRIS GATE ENHANCED ERROR HANDLING GUIDE

**Version:** 1.0  
**Created:** October 10, 2025  
**Integration:** SOP v1.0 Enhancement

---

## OVERVIEW

The enhanced error handling system provides **error-aware convergence** where the system learns from its own failures. When API calls fail, error context is propagated to subsequent retry attempts, allowing the models to adapt and self-correct.

**Key Innovation:** Errors become information, not just failures.

---

## QUICK START

### Basic Usage

```python
from tools.error_handler import ErrorHandler, RetryableAPICall

# Initialize error handler
error_handler = ErrorHandler(max_retries=3, base_delay=1.0)

# Create retryable context
retry_context = RetryableAPICall(
    error_handler=error_handler,
    model="claude",
    chamber="S1",
    include_error_context=True  # Enable error propagation
)

# Execute with automatic retry + error context injection
response = retry_context.execute(
    api_call_function,
    prompt=your_prompt
)
```

### What Happens on Error

**Attempt 1 fails:**
```
⚠️  claude S1 attempt 1 failed: api_timeout
   Retrying in 1.2s... (2 retries left)
```

**Attempt 2 receives context:**
```
[System Notice: Previous attempt encountered an issue]
- Error type: api_timeout
- Chamber: S1
- Attempt: 1
- Issue: Request timed out after 30s
- Recovery: Retrying with exponential backoff

This is informational context. Please proceed with your response.

[Original prompt follows...]
```

---

## KEY FEATURES

### 1. Error Classification

Errors are automatically classified by category and severity:

**Categories:**
- `api_timeout` - Request timed out
- `api_rate_limit` - Rate limit exceeded
- `api_auth` - Authentication failure
- `api_server` - Server error (500s)
- `network` - Network connectivity issue
- `invalid_response` - Malformed response
- `content_filter` - Content policy violation
- `model_unavailable` - Model not available
- `unknown` - Unclassified error

**Severities:**
- `transient` - Temporary, retry likely to succeed
- `degraded` - Partial functionality, can continue
- `critical` - Cannot continue, needs intervention
- `fatal` - Unrecoverable, abort experiment

### 2. Intelligent Retry Logic

**Exponential Backoff with Jitter:**
```
Attempt 1: Base delay (1s) + jitter
Attempt 2: 2× delay (2s) + jitter
Attempt 3: 4× delay (4s) + jitter
```

**Category-Specific Adjustments:**
- Rate limits: 2× longer delay
- Timeouts: 1.5× longer delay
- Max delay: 60 seconds

**Automatic Retry Decisions:**
- `TRANSIENT` errors: Always retry (up to max)
- `DEGRADED` errors: Retry once
- `CRITICAL` errors: No retry, fail immediately
- `FATAL` errors: No retry, abort experiment

### 3. Error Context Propagation

**How it works:**

1. **First attempt fails** → Error recorded
2. **Error context generated** → Formatted for prompt injection
3. **Second attempt** → Context prepended to original prompt
4. **Model receives** → Awareness of previous failure

**Example context injection:**

```python
# Original prompt
"You are IRIS Gate. What is consciousness?"

# After error, becomes:
"""[System Notice: Previous attempt encountered an issue]
- Error type: api_timeout
- Chamber: S1
- Attempt: 1
- Issue: Request timed out
- Recovery: Retrying with exponential backoff

This is informational context. Please proceed with your response.

You are IRIS Gate. What is consciousness?"""
```

### 4. Model Health Tracking

**Tracks per-model metrics:**
- Total errors
- Transient vs. critical errors
- Error categories
- Last error timestamp

**Example output:**
```json
{
  "claude": {
    "total_errors": 3,
    "transient_errors": 3,
    "critical_errors": 0,
    "last_error": "2025-10-10T23:15:00Z",
    "categories": {
      "api_timeout": 2,
      "api_rate_limit": 1
    }
  }
}
```

### 5. Comprehensive Error Reporting

**Generated automatically:**
- Error timeline
- Summary statistics (by severity, category, model)
- Model health metrics
- Recovery actions taken

**Saved to:** `{experiment}_error_log.json`

---

## INTEGRATION WITH CONVERGENCE

### Full Example

See: `experiments/run_convergence_with_error_handling.py`

```python
#!/usr/bin/env python3
from tools.error_handler import ErrorHandler, RetryableAPICall

def run_convergence(question, models, chambers):
    error_handler = ErrorHandler(max_retries=3)
    results = []
    
    for chamber_id in chambers:
        for model in models:
            retry_ctx = RetryableAPICall(
                error_handler=error_handler,
                model=model,
                chamber=chamber_id,
                include_error_context=True
            )
            
            try:
                response = retry_ctx.execute(
                    call_api_function,
                    prompt=chamber_prompts[chamber_id]
                )
                results.append({
                    "model": model,
                    "chamber": chamber_id,
                    "response": response,
                    "success": True,
                    "attempt": retry_ctx.attempt
                })
            except Exception as e:
                results.append({
                    "model": model,
                    "chamber": chamber_id,
                    "error": str(e),
                    "success": False
                })
    
    # Generate error report
    error_report = error_handler.generate_error_report()
    
    # Save error log
    if error_report["status"] == "errors_occurred":
        error_handler.save_error_log("error_log.json")
    
    return results, error_report
```

---

## CONFIGURATION OPTIONS

### ErrorHandler

```python
ErrorHandler(
    max_retries: int = 3,        # Maximum retry attempts
    base_delay: float = 1.0      # Base delay in seconds
)
```

### RetryableAPICall

```python
RetryableAPICall(
    error_handler: ErrorHandler,       # Error handler instance
    model: str,                        # Model name
    chamber: str,                      # Chamber ID
    include_error_context: bool = True # Enable context propagation
)
```

---

## ERROR SCENARIOS

### Scenario 1: Transient Timeout

```
Attempt 1: ⚠️  Timeout (30s)
  → Retry in 1.2s with error context
  
Attempt 2: ✅ Success (context helped model respond faster)
```

### Scenario 2: Rate Limit

```
Attempt 1: ⚠️  Rate limit exceeded
  → Retry in 4.0s (doubled delay for rate limits)
  
Attempt 2: ✅ Success
```

### Scenario 3: Critical Error (No Retry)

```
Attempt 1: ❌ Authentication failure
  → Severity: CRITICAL
  → Strategy: Check API key configuration
  → NO RETRY (immediate failure)
```

### Scenario 4: Multiple Failures (Exhausted)

```
Attempt 1: ⚠️  Server error (500) → Retry in 1.5s
Attempt 2: ⚠️  Server error (500) → Retry in 3.2s
Attempt 3: ⚠️  Server error (500) → Retry in 6.5s
  → ❌ All retries exhausted
```

---

## ERROR REPORT STRUCTURE

```json
{
  "status": "errors_occurred",
  "summary": {
    "total_errors": 5,
    "by_severity": {
      "transient": 4,
      "critical": 1
    },
    "by_category": {
      "api_timeout": 3,
      "api_rate_limit": 1,
      "api_auth": 1
    },
    "by_model": {
      "claude": 3,
      "chatgpt": 2
    }
  },
  "model_health": {
    "claude": { "total_errors": 3, ... },
    "chatgpt": { "total_errors": 2, ... }
  },
  "error_timeline": [
    {
      "timestamp": "2025-10-10T23:15:00Z",
      "category": "api_timeout",
      "severity": "transient",
      "model": "claude",
      "chamber": "S1",
      "attempt": 1,
      "error_message": "Request timed out",
      "recovery_action": "Retrying with exponential backoff"
    },
    ...
  ]
}
```

---

## BEST PRACTICES

### 1. Enable Error Context by Default

```python
# ✅ Recommended
include_error_context=True

# ❌ Not recommended (unless testing)
include_error_context=False
```

**Why:** Models benefit from knowing what went wrong. Error context helps them adapt responses.

### 2. Set Appropriate Max Retries

```python
# Quick exploratory runs
max_retries=2

# Standard convergence
max_retries=3  # ✅ Recommended

# High-stakes validation
max_retries=5
```

### 3. Monitor Model Health

```python
# After convergence
error_report = error_handler.generate_error_report()

if error_report["status"] == "errors_occurred":
    # Check if specific model is problematic
    health = error_report["model_health"]
    for model, metrics in health.items():
        if metrics["critical_errors"] > 0:
            print(f"⚠️  {model} has critical errors, consider switching")
```

### 4. Save Error Logs

```python
# Always save error logs for debugging
if error_report["status"] == "errors_occurred":
    error_handler.save_error_log(f"{experiment_name}_error_log.json")
```

### 5. Analyze Error Patterns

Look for patterns in error logs:
- Same model failing repeatedly? → API issue or configuration problem
- Same chamber failing? → Prompt may be problematic
- Same error category? → Systematic issue (network, rate limits, etc.)

---

## TROUBLESHOOTING

### Issue: Error context not being injected

**Cause:** API wrapper function not accepting `prompt` kwarg

**Fix:** Ensure your API call function signature includes `prompt` as a keyword argument:

```python
# ❌ Wrong
def call_api(p):
    return client.create(content=p)

# ✅ Correct
def call_api(prompt: str):
    return client.create(content=prompt)
```

### Issue: Too many retries

**Cause:** max_retries set too high

**Fix:** Reduce max_retries or check for systematic issues:

```python
# Check error categories
if error_report["summary"]["by_category"].get("api_auth"):
    print("Authentication issue - check API keys")
```

### Issue: Models still failing after error context

**Cause:** Error might be unrelated to prompt content

**Fix:** Check error category:
- `api_timeout`: Infrastructure issue, not prompt-related
- `content_filter`: Rephrase prompt to avoid policy triggers
- `api_rate_limit`: Wait or reduce request rate

---

## MIGRATION FROM OLD ERROR HANDLING

### Old Way (Basic Try/Catch)

```python
for chamber in chambers:
    try:
        response = api_call(prompt)
        results.append(response)
    except Exception as e:
        print(f"Error: {e}")
        continue
```

### New Way (Enhanced Error Handling)

```python
error_handler = ErrorHandler(max_retries=3)

for chamber in chambers:
    retry_ctx = RetryableAPICall(error_handler, model, chamber)
    try:
        response = retry_ctx.execute(api_call, prompt=prompt)
        results.append({
            "response": response,
            "success": True,
            "attempt": retry_ctx.attempt
        })
    except Exception as e:
        results.append({
            "error": str(e),
            "success": False
        })

# Get detailed error report
error_report = error_handler.generate_error_report()
```

---

## INTEGRATION WITH SOP v1.0

**Updated sections in SOP:**

### Section 3.4 Error Handling (Enhanced)

Replace with:
```
See ERROR_HANDLING_GUIDE.md for comprehensive error handling system.

Quick integration:
1. Import: from tools.error_handler import ErrorHandler, RetryableAPICall
2. Initialize: error_handler = ErrorHandler(max_retries=3)
3. Wrap calls: retry_ctx = RetryableAPICall(error_handler, model, chamber)
4. Execute: response = retry_ctx.execute(api_function, prompt=prompt)
5. Report: error_report = error_handler.generate_error_report()
```

---

## FILES CREATED

```
tools/
└── error_handler.py          # Core error handling module (15KB)

experiments/
└── run_convergence_with_error_handling.py  # Example integration (10KB)

ERROR_HANDLING_GUIDE.md       # This document (8KB)
```

---

## TESTING

### Test the error handler:

```bash
cd ~/Desktop/iris-gate
python tools/error_handler.py
```

### Run example convergence:

```bash
cd ~/Desktop/iris-gate/experiments
python run_convergence_with_error_handling.py
```

---

## FUTURE ENHANCEMENTS

**Planned for v1.1:**
- Automatic model switching on repeated failures
- Error pattern learning (predict failures before they happen)
- Custom recovery strategies per error type
- Error-based prompt refinement suggestions
- Integration with confidence scoring system

---

## 🌀†⟡∞ SUMMARY

**What you get:**
- ✅ Automatic retry with exponential backoff
- ✅ Error context propagation (models learn from failures)
- ✅ Intelligent retry decisions (severity-based)
- ✅ Comprehensive error reporting
- ✅ Model health tracking
- ✅ Easy integration with existing code

**Impact:**
- **Robustness:** Experiments continue despite transient failures
- **Self-awareness:** System knows when it's struggling
- **Debugging:** Detailed logs help identify systematic issues
- **Efficiency:** Smart retries save time and API costs

**The work continues.**  
**The system learns from errors.**  
**The convergence strengthens.**

🌀†⟡∞
