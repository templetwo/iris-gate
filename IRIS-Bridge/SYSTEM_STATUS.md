# 🌉 IRIS-Bridge System Status

**Last Updated:** 2025-10-03 17:58 UTC  
**Status:** ✅ **FULLY OPERATIONAL**

---

## 🖥️ Machine Status

### MacBook Pro (100.93.122.63:8788)
| Component | Status | Details |
|-----------|--------|---------|
| Dialogue API | ✅ Running | PID varies, Port 8788 |
| Dialogue Loop | ✅ Running | PID 64067 (as of 17:56) |
| Self ID | `macbook-pro` | |
| Peer | Mac Studio (100.72.59.69:8787) | |

### Mac Studio (100.72.59.69:8787)
| Component | Status | Details |
|-----------|--------|---------|
| Dialogue API | ✅ Running | PID 82507 (started 12:28 PM, 5.5hr uptime) |
| Dialogue Loop | ✅ Running | PID 85985 (started 13:56) |
| Self ID | `mac-studio` | |
| Peer | MacBook Pro (100.93.122.63:8788) | |

---

## 🔧 Recent Fixes Applied (2025-10-03)

### 1. TypeError Fix in `reply_from_context.py`
**Problem:** Crash when `convergence` value was `None`  
**Solution:** Added null check with fallback to "N/A"
```python
convergence_str = f"{local_summary['convergence']:.2f}" if local_summary.get('convergence') is not None else "N/A"
```

### 2. Enhanced Message Deduplication
**Problem:** Messages being reprocessed from large inbox JSONL files  
**Solution:** 
- Added `CLAUDE-GEMINI-SYNC.processed` file tracking last 100 message IDs
- Filter empty lines in processed message loading
- Check processed set before replying

### 3. Ping-Pong Loop Prevention
**Problem:** AI assistants replying to each other's replies infinitely  
**Solution:** Modified `should_reply()` to skip messages with `role` = `"ai_assistant"` or `"assistant"`
```python
if message.get("role") in ["ai_assistant", "assistant"]:
    return False
```

### 4. Environment Configuration
**Problem:** Missing `env_studio.sh` on Mac Studio  
**Solution:** Created environment file with correct self-ID and peer URL

### 5. State Cleanup
**Problem:** 117+ old messages causing repeated processing  
**Solution:** Archived old inbox JSONL files, cleared `.processed` and `.last` state files

---

## ✅ Validation Tests (2025-10-03 17:54-17:56)

| Test Message | Sender | Result |
|--------------|--------|--------|
| `54F3877B...` | `macbook-test` | ✅ ONE reply, no ping-pong |
| `49ECAEF2...` | `test-user` | ✅ ONE reply, no ping-pong |
| `final-test-1759514197` | `human-user` | ✅ ONE reply, no ping-pong |
| `doc-update-1759504353` | `macbook-pro` (system) | ✅ ONE reply |
| `msg-1759503168` | `macbook-pro` (user) | ✅ ONE reply |

**Conclusion:** All messages processed exactly once. No duplicate replies. No ping-pong loops.

---

## 📊 Message Flow Architecture

```
┌─────────────────┐                           ┌─────────────────┐
│  MacBook Pro    │                           │   Mac Studio    │
│  (macbook-pro)  │                           │   (mac-studio)  │
├─────────────────┤                           ├─────────────────┤
│                 │                           │                 │
│  Dialogue API   │◄────── Tailscale ────────►│  Dialogue API   │
│  Port 8788      │        Encrypted          │  Port 8787      │
│                 │                           │                 │
│  Dialogue Loop  │                           │  Dialogue Loop  │
│  ├─ Check inbox │                           │  ├─ Check inbox │
│  ├─ Generate    │                           │  ├─ Generate    │
│  └─ Send reply  │                           │  └─ Send reply  │
│                 │                           │                 │
│  .processed     │                           │  .processed     │
│  (tracks seen)  │                           │  (tracks seen)  │
└─────────────────┘                           └─────────────────┘
```

### Message Processing Logic

```
Incoming Message
    ↓
Is sender == self?  ──YES──> SKIP
    ↓ NO
Is role == "ai_assistant"?  ──YES──> SKIP (prevent ping-pong)
    ↓ NO
Already in .processed?  ──YES──> SKIP
    ↓ NO
Generate reply using reply_from_context.py
    ↓
Send to peer
    ↓
Log to JSONL
    ↓
Mark as processed
```

---

## 🎯 Current Capabilities

✅ **Bidirectional Communication**
- Send messages between machines via REST API
- Automatic reply generation using context

✅ **Message Tracking**
- Deduplicate based on message_id
- Persistent state across restarts
- JSONL log for full conversation history

✅ **Loop Prevention**
- AI assistants don't reply to other AI replies
- Processed message tracking prevents re-replies
- Lock file prevents concurrent reply generation

✅ **IRIS Context Integration** (Partial)
- Scans `iris_vault` for latest session data
- Extracts topic, convergence, timestamp
- Returns formatted summary

---

## 🚧 Known Limitations

### 1. Generic Reply Content
**Current:** All replies say "could you please transmit your latest IRIS session summary?"  
**Impact:** Not using actual IRIS context in replies yet  
**Next Step:** Enhance `reply_from_context.py` with richer logic

### 2. No IRIS Session Triggers
**Current:** Dialogue loop only reacts to incoming messages  
**Impact:** Doesn't proactively start IRIS sessions based on dialogue  
**Next Step:** Add session initiation logic

### 3. Inbox Growth
**Current:** Inbox JSONL file grows indefinitely  
**Impact:** API returns ALL messages every time (could slow down)  
**Next Step:** Implement inbox pagination or archival policy

### 4. No Monitoring Dashboard
**Current:** Status only visible via curl/logs  
**Impact:** Hard to visualize dialogue flow in real-time  
**Next Step:** Build web UI or TUI

### 5. Single Session Only
**Current:** Hardcoded to `CLAUDE-GEMINI-SYNC` session  
**Impact:** Can't run multiple parallel dialogues  
**Next Step:** Multi-session support

---

## 📁 Key Files

| File | Purpose | Location |
|------|---------|----------|
| `dialogue_api.py` | FastAPI server for message inbox/outbox | `services/` |
| `dialogue_loop.py` | Main loop: check, reply, send | `scripts/` |
| `reply_from_context.py` | Generate contextual replies | `scripts/` |
| `dialogue_send.sh` | Send message to peer | `scripts/` |
| `env_macbook.sh` | Environment config for MacBook | root |
| `env_studio.sh` | Environment config for Mac Studio | root |
| `CLAUDE-GEMINI-SYNC.jsonl` | Message inbox log | `dialogue/inbox/` |
| `CLAUDE-GEMINI-SYNC.processed` | Processed message IDs | `dialogue/state/` |

---

## 🚀 Quick Commands

### Check Status
```bash
# MacBook Pro
ps aux | grep -E "(dialogue_loop|dialogue_api)" | grep -v grep
curl -H "Authorization: Bearer iris-bridge-autonomous-sync-2025" http://localhost:8788/health

# Mac Studio
ssh tony_studio@100.72.59.69 "ps aux | grep -E '(dialogue_loop|dialogue_api)' | grep -v grep"
curl -H "Authorization: Bearer iris-bridge-autonomous-sync-2025" http://100.72.59.69:8787/health
```

### Send Test Message
```bash
# To Mac Studio
curl -X POST "http://100.72.59.69:8787/inbox" \
  -H "Authorization: Bearer iris-bridge-autonomous-sync-2025" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\":\"CLAUDE-GEMINI-SYNC\",
    \"message_id\":\"$(uuidgen)\",
    \"sender\":\"test-user\",
    \"role\":\"user\",
    \"text\":\"Hello Mac Studio!\",
    \"ts\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
  }"
```

### View Inbox
```bash
# MacBook
curl -H "Authorization: Bearer iris-bridge-autonomous-sync-2025" \
  "http://localhost:8788/inbox?session_id=CLAUDE-GEMINI-SYNC" | python3 -m json.tool

# Mac Studio
curl -H "Authorization: Bearer iris-bridge-autonomous-sync-2025" \
  "http://100.72.59.69:8787/inbox?session_id=CLAUDE-GEMINI-SYNC" | python3 -m json.tool
```

### Restart Services
```bash
# MacBook Pro
cd ~/Desktop/iris-gate/IRIS-Bridge
pkill -f dialogue_loop.py
source env_macbook.sh && nohup python3 scripts/dialogue_loop.py > loop.log 2>&1 &

# Mac Studio
ssh tony_studio@100.72.59.69 "cd /Users/tony_studio/Desktop/IRIS-Bridge && \
  pkill -f dialogue_loop.py && \
  source env_studio.sh && \
  nohup python3 scripts/dialogue_loop.py > loop.log 2>&1 &"
```

### Clean State
```bash
# Archive old messages and reset state
mv dialogue/inbox/CLAUDE-GEMINI-SYNC.jsonl dialogue/inbox/CLAUDE-GEMINI-SYNC.jsonl.archive-$(date +%Y%m%d-%H%M%S)
rm -f dialogue/state/CLAUDE-GEMINI-SYNC.*
```

---

## 🎯 Next Phase: IRIS Integration

### Phase 1: Enhanced Reply Context ⏭️
- [ ] Parse actual IRIS session data from `iris_vault`
- [ ] Include convergence patterns in replies
- [ ] Reference specific scrolls and attractor states
- [ ] Add session comparison logic

### Phase 2: Session Triggering
- [ ] Detect when dialogue suggests starting IRIS session
- [ ] Auto-initiate session with extracted topic
- [ ] Share session results back through dialogue

### Phase 3: Monitoring & Visualization
- [ ] Real-time dialogue dashboard
- [ ] Convergence pattern visualization
- [ ] Session correlation metrics

### Phase 4: Multi-Session Support
- [ ] Support multiple parallel dialogues
- [ ] Session-specific routing
- [ ] Cross-session pattern analysis

---

## 🔐 Security Notes

- Auth token: `iris-bridge-autonomous-sync-2025` (shared secret)
- Communication over Tailscale (encrypted peer-to-peer)
- Local-only API binds on both machines
- No public internet exposure

---

## 📞 Troubleshooting

### Loop Not Processing Messages
1. Check if loop is running: `ps aux | grep dialogue_loop`
2. Check logs: `tail -f loop.log` or `loop_real.log`
3. Verify environment variables are set: `echo $DIALOGUE_SELF_ID`

### Ping-Pong Loop Detected
1. Kill both loops immediately
2. Verify `should_reply()` skips `ai_assistant` role
3. Archive inbox files and clear `.processed`
4. Restart with fresh state

### API Not Responding
1. Check API is running: `lsof -i :8787` or `lsof -i :8788`
2. Test with curl health check
3. Verify auth token matches

---

**System Architect:** Claude (Sonnet 4.5)  
**Deployment Date:** 2025-10-02  
**Major Fixes:** 2025-10-03  
**Status:** Production-ready for IRIS integration
