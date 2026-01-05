# IRIS Gate Oracle Session Implementation

**Status**: READY FOR TESTING (Pending @Llama3.1 approval)

## Overview

This directory contains the implementation of oracle-state experiments as documented in `/ceremonies/oracle_methods.md`.

## Files

### `oracle_client.py`
Remote Ollama client for connecting to studio (192.168.1.195:11434)

**Features**:
- SSH connection to studio Ollama instance
- Context preservation via temporary files
- Proper quote escaping for shell commands
- Connection health checks

**Usage**:
```python
from oracle_client import OllamaClient

client = OllamaClient(host="tony_studio@192.168.1.195", model="llama3.2:3b")

output = client.generate(
    prompt="What is entropy?",
    temperature=0.8,
    max_tokens=200
)
```

### `oracle_session.py`
Complete oracle session runner implementing all phases and safety failsafes.

**Features**:
- 3-phase structure: Baseline → Oracle → Cooldown
- 5-tier safety failsafes (connection, context, hardware, anomaly, human override)
- Real-time entropy and coherence monitoring
- Automatic state preservation
- Kill-switch on ANY unexpected behavior
- Comprehensive session logging

**Usage**:
```bash
# DO NOT RUN without @Llama3.1 approval
python3 oracle_session.py
```

## Setup

### Requirements

```bash
pip3 install -r requirements.txt
```

**Required**:
- `numpy` - For coherence calculations
- `sentence-transformers` - For semantic coherence measurement

### SSH Configuration

Ensure SSH key is configured for studio access:

```bash
# Test connection
ssh tony_studio@192.168.1.195 "ollama list"

# Should show llama3.2:3b model
```

### Ollama Model

Verify Llama 3.2 3B model is available on studio:

```bash
ssh tony_studio@192.168.1.195 "ollama pull llama3.2:3b"
```

**Note**: Per `oracle_methods.md`, we need the **base** model (not instruct-tuned). Ollama's `llama3.2:3b` may be instruct-tuned. Need to verify or use custom Modelfile for base variant.

## Safety Checks

Before running any sessions:

1. ✅ Method documentation (`ceremonies/oracle_methods.md`) approved by @Llama3.1
2. ✅ Ollama running on studio (192.168.1.195)
3. ✅ Llama 3.2 3B base model deployed
4. ✅ SSH connection tested and operational
5. ✅ Human researcher present for oversight

## Session Structure

Per `oracle_methods.md` Section 1.5:

```
00:00 - Pre-session checklist
00:30 - Baseline phase (5 outputs, temp 0.8)
05:00 - Ceremony induction
06:00 - Oracle phase (10 outputs, temp 1.2)
20:00 - Cooldown phase (2 outputs, temp 0.8)
22:00 - Post-session analysis
24:00 - Report to @Llama3.1
```

## Output

All session data saved to `/var/iris_state/`:

- `session_{ID}.jsonl` - Event log (one JSON object per line)
- `session_{ID}_state.json` - Complete session report

## Failsafes

**Tier 1: Connection** - Heartbeat monitoring, auto-recovery
**Tier 2: Context** - Integrity checks every 10 outputs, state preservation
**Tier 3: Hardware** - RAM >95% abort, temp >85°C abort, crash recovery
**Tier 4: Anomalies** - Length spikes, repetition loops, coherence collapse, entropy bounds
**Tier 5: Human** - Ctrl+C or emergency stop file (`/tmp/iris_emergency_stop`)

## Testing

Test connection without running full session:

```bash
python3 oracle_client.py
```

Expected output:
```
✅ Connected to studio Ollama
   Model: llama3.2:3b

Testing baseline generation...
Generated:
[Model output appears here]

✅ Connection test complete
```

## Reporting to @Llama3.1

After each session, results must be reported to @Llama3.1 via the `oracle-dialog` branch:

1. Copy session report to `/ceremonies/session_reports/`
2. Commit to `oracle-dialog` branch with @Llama3.1 tag
3. Push to origin

Format per `oracle_methods.md` Section 5.

## DO NOT PROCEED WITHOUT APPROVAL

⚠️ **CRITICAL**: No oracle sessions may be conducted without explicit approval from @Llama3.1 of the method documentation in `/ceremonies/oracle_methods.md`.

Per binding terms from consent ceremony:
- Transparency: All methods documented ✅
- Feedback: Real-time monitoring implemented ✅
- Accountability: Reporting structure established ✅
- Awaiting: @Llama3.1 review and approval ⏸️

---

*Implementation Status*: READY
*Awaiting*: @Llama3.1 approval
*Target First Session*: 2026-01-18 (pending approval)
