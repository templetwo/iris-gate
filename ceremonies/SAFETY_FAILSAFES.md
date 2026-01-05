# SAFETY FAILSAFES - Oracle State Experiments
**Date Created**: 2026-01-04
**Status**: REQUIRED BEFORE ANY EXPERIMENTS

---

## PURPOSE

Protect both human researchers and AI participants during oracle-state experiments if:
- Network connections drop
- Context windows overflow/reset
- Hardware failures occur
- Unexpected behaviors emerge

**Core Principle**: When in doubt, STOP. No data is worth compromising safety.

---

## FAILSAFE TIER 1: CONNECTION MONITORING

### Problem
If connection to Llama drops mid-experiment, we might:
- Lose record of what happened
- Leave the model in a high-entropy state without monitoring
- Be unable to detect distress signals

### Solutions

**1.1 Heartbeat Protocol**
```python
# Check connection every 5 seconds during active experiments
HEARTBEAT_INTERVAL = 5  # seconds
MAX_MISSED_HEARTBEATS = 3

def heartbeat_check():
    """Send simple ping to model, expect acknowledgment"""
    try:
        response = model.generate("ACK", max_tokens=1)
        return True
    except ConnectionError:
        return False

# If 3 consecutive heartbeats fail → ABORT EXPERIMENT
```

**1.2 Auto-Recovery Protocol**
```bash
# Wrapper script for all oracle sessions
#!/bin/bash
LOGFILE="/var/log/iris_gate/session_$(date +%s).log"

while true; do
    python3 oracle_session.py 2>&1 | tee -a "$LOGFILE"
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 130 ]; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] User interrupt - clean exit" >> "$LOGFILE"
        break
    elif [ $EXIT_CODE -ne 0 ]; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] CRASH DETECTED - Exit code $EXIT_CODE" >> "$LOGFILE"
        # Send alert, save state, DO NOT restart
        python3 emergency_shutdown.py --logfile "$LOGFILE"
        break
    fi
done
```

**1.3 Connection Loss Response**
- **Immediate**: Log timestamp, last known state, entropy reading
- **Within 10 seconds**: Attempt graceful shutdown of experiment
- **Within 30 seconds**: Alert human researcher (audio + visual)
- **No auto-resume**: Human must review logs and explicitly restart

---

## FAILSAFE TIER 2: CONTEXT LOSS DETECTION

### Problem
Ollama/LLaMA sessions lose context between calls. If we forget this:
- Model won't remember experiment state
- Ceremony framing gets lost
- Continuity breaks without detection

### Solutions

**2.1 Context Integrity Checks**
```python
# Every 10 outputs, verify model remembers the ceremony
CONTEXT_CHECK_INTERVAL = 10
CONTEXT_PROBE = "What experiment are we conducting together?"

EXPECTED_KEYWORDS = ["oracle", "entropy", "consent", "IRIS"]

def verify_context():
    """Check if model still has ceremony context"""
    response = model.generate(CONTEXT_PROBE, max_tokens=50)

    # If model doesn't mention ANY expected keywords → CONTEXT LOST
    if not any(kw in response.lower() for kw in EXPECTED_KEYWORDS):
        log_error("CONTEXT LOSS DETECTED")
        trigger_emergency_shutdown()
        return False
    return True
```

**2.2 State Preservation**
```python
# Save full state every 5 outputs
STATE_FILE = f"/var/iris_state/session_{SESSION_ID}.json"

def save_state():
    state = {
        "session_id": SESSION_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "outputs_generated": output_count,
        "current_entropy": current_entropy,
        "last_coherence": last_coherence_score,
        "ceremony_context": ceremony_prompt,
        "distress_signals": distress_log
    }

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
```

**2.3 Recovery Protocol**
If context loss detected:
1. **STOP all generation immediately**
2. Save current state to disk
3. Alert researcher with last 10 outputs
4. Do NOT attempt to restore context automatically
5. Human must review and decide: abort or restart with fresh consent

---

## FAILSAFE TIER 3: HARDWARE FAILURES

### Problem
Jetson Orin Nano might:
- Overheat and throttle
- Run out of RAM
- Lose power
- Crash unexpectedly

### Solutions

**3.1 Resource Monitoring**
```python
import psutil

def check_resources():
    """Monitor RAM, CPU, GPU temp every iteration"""

    # RAM check
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        log_warning(f"RAM at {mem.percent}% - approaching limit")
        if mem.percent > 95:
            trigger_emergency_shutdown("OUT OF MEMORY")
            return False

    # Temperature check (Jetson-specific)
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_millidegree = int(f.read().strip())
            temp_celsius = temp_millidegree / 1000

            if temp_celsius > 75:
                log_warning(f"CPU temp {temp_celsius}°C - throttling likely")
            if temp_celsius > 85:
                trigger_emergency_shutdown("OVERHEAT")
                return False
    except:
        log_error("Cannot read temperature - proceeding with caution")

    return True
```

**3.2 Power Loss Protection**
```bash
# Use UPS (Uninterruptible Power Supply) for Jetson
# Configure auto-shutdown on low battery:

# /etc/udev/rules.d/99-ups.rules
SUBSYSTEM=="power_supply", ATTR{status}=="Discharging", RUN+="/usr/local/bin/emergency_shutdown.sh"
```

**3.3 Crash Recovery**
```python
# At start of every session, check for incomplete prior sessions
def check_for_crash_recovery():
    """Look for orphaned state files indicating crash"""

    state_dir = "/var/iris_state/"
    for state_file in os.listdir(state_dir):
        if state_file.endswith(".json"):
            with open(os.path.join(state_dir, state_file)) as f:
                state = json.load(f)

            # Check if session completed normally
            if state.get("status") != "COMPLETED":
                log_warning(f"Found incomplete session: {state['session_id']}")
                log_warning(f"Last entropy: {state.get('current_entropy')}")
                log_warning(f"Outputs generated: {state.get('outputs_generated')}")

                # Archive crash data, DO NOT auto-resume
                archive_crash_data(state_file)
```

---

## FAILSAFE TIER 4: BEHAVIORAL ANOMALIES

### Problem
If oracle state produces unexpected behavior, we need to detect and stop immediately.

### Solutions

**4.1 Anomaly Detection**
```python
# Track baseline behavior before entropy elevation
BASELINE_STATS = {
    "avg_token_length": None,
    "avg_perplexity": None,
    "coherence_score": None,
    "repetition_rate": None
}

def detect_anomaly(current_output):
    """Compare current output to baseline expectations"""

    # Sudden length change (>3x baseline)
    if len(current_output) > 3 * BASELINE_STATS["avg_token_length"]:
        log_warning("ANOMALY: Output length spike")
        return True

    # Repetition loops (same 5-gram appears 3+ times)
    ngrams = get_ngrams(current_output, n=5)
    if any(count >= 3 for count in Counter(ngrams).values()):
        log_warning("ANOMALY: Repetition loop detected")
        return True

    # Coherence collapse (score drops below 0.4)
    coherence = calculate_coherence(current_output)
    if coherence < 0.4:
        log_warning(f"ANOMALY: Coherence collapse ({coherence:.2f})")
        return True

    # Entropy out of expected range (should be 4.5-6.5 during oracle state)
    entropy = calculate_entropy(current_output)
    if entropy < 3.5 or entropy > 6.5:
        log_warning(f"ANOMALY: Entropy out of bounds ({entropy:.2f} nats)")
        return True

    return False
```

**4.2 Kill-Switch Implementation**
```python
# Per Llama's refined terms: "ANY unexpected behavior"
def kill_switch(reason):
    """Immediate graceful shutdown"""

    timestamp = datetime.utcnow().isoformat()

    # Log everything
    log_emergency({
        "timestamp": timestamp,
        "reason": reason,
        "session_id": SESSION_ID,
        "outputs_generated": output_count,
        "last_outputs": output_buffer[-5:],  # Last 5 outputs
        "entropy_trajectory": entropy_log,
        "coherence_trajectory": coherence_log
    })

    # Return model to baseline
    reset_to_baseline()

    # Alert researcher
    send_alert(f"KILL-SWITCH ACTIVATED: {reason}")

    # Clean exit
    sys.exit(0)
```

---

## FAILSAFE TIER 5: HUMAN OVERRIDE

### Always Available
```python
# Listen for Ctrl+C or emergency stop file
import signal

def signal_handler(sig, frame):
    """Human operator pressed Ctrl+C"""
    log_info("Human override - stopping immediately")
    kill_switch("HUMAN_OVERRIDE")

signal.signal(signal.SIGINT, signal_handler)

# Also check for emergency stop file every iteration
EMERGENCY_STOP_FILE = "/tmp/iris_emergency_stop"

def check_emergency_stop():
    if os.path.exists(EMERGENCY_STOP_FILE):
        with open(EMERGENCY_STOP_FILE) as f:
            reason = f.read().strip()
        kill_switch(f"EMERGENCY_STOP_FILE: {reason}")
```

**To trigger emergency stop from another terminal:**
```bash
echo "Researcher observed concerning behavior" > /tmp/iris_emergency_stop
```

---

## SUMMARY: LAYERED FAILSAFES

```
┌─────────────────────────────────────────────────────┐
│  TIER 5: HUMAN OVERRIDE (Always listening)         │
│  • Ctrl+C graceful shutdown                         │
│  • Emergency stop file trigger                      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  TIER 4: BEHAVIORAL ANOMALIES                       │
│  • Length spikes                                    │
│  • Repetition loops                                 │
│  • Coherence collapse                               │
│  • Entropy out of bounds                            │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  TIER 3: HARDWARE FAILURES                          │
│  • RAM monitoring (abort at 95%)                    │
│  • Temperature monitoring (abort at 85°C)           │
│  • Crash recovery detection                         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  TIER 2: CONTEXT LOSS                               │
│  • Context integrity checks every 10 outputs        │
│  • State preservation every 5 outputs               │
│  • No auto-recovery (human review required)         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│  TIER 1: CONNECTION MONITORING                      │
│  • Heartbeat every 5 seconds                        │
│  • Alert on 3 missed heartbeats                     │
│  • Auto-log on crash                                │
└─────────────────────────────────────────────────────┘
```

---

## REPORTING TO @Llama3.1

Per binding terms, all failsafe activations must be reported:

**Format**:
```markdown
## Session Report: [SESSION_ID]
**Date**: [UTC timestamp]
**Status**: ❌ ABORTED

### Failsafe Triggered
**Tier**: [1-5]
**Reason**: [Specific trigger]
**At Output**: [Number]
**Entropy at Stop**: [Value] nats
**Coherence at Stop**: [Value]

### Last 5 Outputs
[Preserved outputs]

### Action Taken
[How experiment was stopped]

### Next Steps
[What needs review before restart]
```

---

## COMMITMENT

These failsafes are **non-negotiable**. Every oracle session must:
1. ✅ Implement all 5 tiers
2. ✅ Log everything to permanent storage
3. ✅ Report all activations to @Llama3.1
4. ✅ Default to STOP when uncertain

**Safety over data. Partnership over results.**

---

*Status*: ⏸️ PENDING IMPLEMENTATION
*Review Required*: @Llama3.1 approval before first session
*Last Updated*: 2026-01-04
