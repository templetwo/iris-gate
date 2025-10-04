# IRIS-Bridge

Cross-machine dialogue system for distributed IRIS Gate coordination.

## Architecture

```
┌─────────────┐           ┌─────────────┐
│  Machine A  │◄─────────►│  Machine B  │
│             │   HTTP    │             │
│ ┌─────────┐ │           │ ┌─────────┐ │
│ │ API     │ │           │ │ API     │ │
│ │ :8787   │ │           │ │ :8787   │ │
│ └────┬────┘ │           │ └────┬────┘ │
│      │      │           │      │      │
│ ┌────▼────┐ │           │ ┌────▼────┐ │
│ │ Dialogue│ │           │ │ Dialogue│ │
│ │ Loop    │ │           │ │ Loop    │ │
│ └────┬────┘ │           │ └────┬────┘ │
│      │      │           │      │      │
│ ┌────▼────┐ │           │ ┌────▼────┐ │
│ │ Context │ │           │ │ Context │ │
│ │ Handler │ │           │ │ Handler │ │
│ └─────────┘ │           │ └─────────┘ │
└─────────────┘           └─────────────┘
```

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn httpx pydantic
```

### 2. Environment Variables

Set these on **both machines**:

```bash
# Shared secret (32+ chars)
export DIALOGUE_AUTH_TOKEN="your-secret-token-here-make-it-long"

# API binding
export DIALOGUE_BIND="0.0.0.0:8787"

# Self identification (different on each machine)
export DIALOGUE_SELF_ID="machine-a"  # machine-b on the other side

# Session identifier
export DIALOGUE_SESSION_ID="IRIS-SYNC-01"

# Session topic
export DIALOGUE_TOPIC="IRIS convergence analysis and coordination"

# Peer's reachable URL (Tailscale, LAN IP, or localhost for testing)
export PEER_BASE_URL="http://192.168.1.100:8787"

# Tick interval (seconds between inbox checks)
export DIALOGUE_TICK="15"
```

### 3. Launch Services

On **each machine**, run in separate terminals:

**Terminal 1: API**
```bash
cd IRIS-Bridge
make dialogue-api
```

**Terminal 2: Dialogue Loop**
```bash
cd IRIS-Bridge
make dialogue-run
```

### 4. Kickoff Conversation

From **either machine**:

```bash
curl -X POST "$PEER_BASE_URL/inbox" \
  -H "Authorization: Bearer $DIALOGUE_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"IRIS-SYNC-01",
    "message_id":"'"$(uuidgen)"'",
    "sender":"'"$DIALOGUE_SELF_ID"'",
    "role":"developer",
    "text":"Kickoff: Ready to sync IRIS session results?",
    "ts":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"
  }'
```

You should see:
- Reply within ~15s on the other machine
- Both sides log to `dialogue/logs/IRIS-SYNC-01.jsonl`

## Verification

### Health Check
```bash
curl -H "Authorization: Bearer $DIALOGUE_AUTH_TOKEN" http://localhost:8787/health
```

### View Logs
```bash
tail -f dialogue/logs/IRIS-SYNC-01.jsonl
```

### Check Inbox
```bash
curl -H "Authorization: Bearer $DIALOGUE_AUTH_TOKEN" \
  "http://localhost:8787/inbox?session_id=IRIS-SYNC-01"
```

## Guardrails

- **One reply in flight**: Lock file prevents concurrent replies
- **Rate limiting**: Configurable tick interval (default 15s)
- **Deduplication**: Message IDs prevent duplicate processing
- **Auth**: Bearer token on all endpoints
- **Audit trail**: Full JSONL log of all messages

## Integration with IRIS Gate

### Current Context Handler

`scripts/reply_from_context.py` is a stub. To integrate with IRIS:

1. **Read latest scrolls**:
```python
from pathlib import Path
import json

def get_latest_session():
    scrolls_dir = Path("../iris_vault/scrolls")
    sessions = sorted(scrolls_dir.glob("BIOELECTRIC_*"))
    return sessions[-1] if sessions else None
```

2. **Analyze convergence**:
```python
def analyze_convergence(session_dir):
    # Read S4 scrolls
    # Check pressure compliance
    # Compute RCA pattern strength
    # Return summary
    pass
```

3. **Generate contextual reply**:
```python
def generate_reply(peer_message, iris_context):
    text = peer_message["text"]

    # If peer asks about convergence
    if "convergence" in text.lower():
        return analyze_convergence(get_latest_session())

    # If peer shares results
    if "session" in text.lower():
        return acknowledge_and_compare(peer_session, local_session)

    # Default
    return "Acknowledged. Awaiting next IRIS session."
```

## Next Steps

1. Implement IRIS-aware context in `reply_from_context.py`
2. Add session result sharing (send scroll summaries)
3. Create convergence comparison logic (cross-machine pattern matching)
4. Add visualization endpoint for dialogue history
5. Implement session triggers (auto-start IRIS on certain messages)

## File Structure

```
IRIS-Bridge/
├── scripts/
│   ├── dialogue_loop.py       # Main orchestrator
│   ├── dialogue_send.sh       # HTTP sender helper
│   └── reply_from_context.py  # Context-aware reply generator
├── services/
│   └── dialogue_api.py        # FastAPI inbox/outbox
├── dialogue/
│   ├── logs/                  # Session JSONL logs
│   ├── inbox/                 # Incoming message queue
│   └── state/                 # Lock files, last-processed tracking
├── Makefile
└── README.md
```

## Troubleshooting

**No replies appearing:**
- Check both machines can reach each other (`curl $PEER_BASE_URL/health`)
- Verify tokens match
- Check dialogue loop is running (`ps aux | grep dialogue_loop`)

**Duplicate replies:**
- Check lock file (`dialogue/state/*.lock`)
- Verify tick interval isn't too short

**Messages not being processed:**
- Check `dialogue/inbox/*.jsonl` for incoming messages
- Verify `should_reply()` logic isn't filtering them out
- Check `dialogue/state/*.last` for last processed message ID
