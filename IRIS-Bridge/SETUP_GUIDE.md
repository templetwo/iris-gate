# 🌉 IRIS-Bridge Setup Guide

**Cross-machine AI dialogue system for distributed IRIS Gate coordination**

---

## 📋 Quick Status

### Connection Details
- **MacBook Pro**: `100.93.122.63:8788` (SELF_ID: `macbook-pro`)
- **Mac Studio**: `100.72.59.69:8787` (SELF_ID: `mac-studio`)  
- **Auth Token**: `iris-bridge-autonomous-sync-2025`
- **Session ID**: `CLAUDE-GEMINI-SYNC`

---

## 🚀 Starting Services

### On MacBook Pro (This Machine)

```bash
cd ~/Desktop/iris-gate/IRIS-Bridge

# Terminal 1: API Service
./start_api_macbook.sh

# Terminal 2: Dialogue Loop (in new terminal)
./start_loop_macbook.sh
```

### On Mac Studio (tony_studio@100.72.59.69)

First, copy the IRIS-Bridge directory to Mac Studio:

```bash
# Option 1: Via scp (if SSH is enabled)
scp -r ~/Desktop/iris-gate/IRIS-Bridge tony_studio@100.72.59.69:~/

# Option 2: Via Screen Sharing
# Use Finder > Go > Connect to Server > vnc://100.72.59.69
# Then manually copy the folder

# Option 3: Via USB drive or AirDrop
```

Then on Mac Studio:

```bash
cd ~/IRIS-Bridge

# Install dependencies if needed
pip3 install fastapi uvicorn httpx pydantic

# Terminal 1: API Service
./start_api_studio.sh

# Terminal 2: Dialogue Loop (in new terminal)
./start_loop_studio.sh
```

---

## 🧪 Testing

### Test MacBook Pro Services

```bash
# Test local API
python3 test_local_health.py --port 8788

# Should output: ✅ API HEALTHY
```

### Test Mac Studio Connectivity

```bash
# Test remote API from MacBook
python3 test_cross_machine.py --host 100.72.59.69 --port 8787

# Should output: ✅ REMOTE API HEALTHY
```

### Send Test Message

From MacBook:
```bash
cd ~/Desktop/iris-gate/IRIS-Bridge

# Send test message to Mac Studio
./scripts/dialogue_send.sh '{
  "session_id":"CLAUDE-GEMINI-SYNC",
  "message_id":"'$(uuidgen)'",
  "sender":"macbook-pro",
  "role":"test",
  "text":"Hello from MacBook Pro - testing IRIS-Bridge connection",
  "ts":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
}'
```

Check logs on both machines:
```bash
# MacBook
tail -f dialogue/logs/CLAUDE-GEMINI-SYNC.jsonl

# Mac Studio
tail -f dialogue/logs/CLAUDE-GEMINI-SYNC.jsonl
```

---

## 🔧 Troubleshooting

### MacBook API won't start
```bash
# Check if port is already in use
lsof -ti:8788 | xargs kill -9

# Check Python dependencies
python3 -m pip list | grep -E "(fastapi|uvicorn|httpx)"
```

### Can't reach Mac Studio
```bash
# Check Tailscale status
/Applications/Tailscale.app/Contents/MacOS/Tailscale status

# Try ping
ping -c 3 100.72.59.69

# Check if SSH is enabled on Mac Studio
# System Preferences > Sharing > Remote Login (should be ON)
```

### Dialogue loop not processing messages
```bash
# Check if loop is running
ps aux | grep dialogue_loop

# Check lock files
ls -la dialogue/state/*.lock
rm dialogue/state/*.lock  # Remove if stale

# Check inbox
ls -la dialogue/inbox/
```

### Authentication errors
```bash
# Verify tokens match on both machines
echo $DIALOGUE_AUTH_TOKEN

# Should be: iris-bridge-autonomous-sync-2025
```

---

## 📂 Directory Structure

```
IRIS-Bridge/
├── env_macbook.sh          # MacBook Pro environment
├── env_studio.sh           # Mac Studio environment
├── start_api_macbook.sh    # MacBook API startup
├── start_loop_macbook.sh   # MacBook loop startup
├── start_api_studio.sh     # Mac Studio API startup
├── start_loop_studio.sh    # Mac Studio loop startup
├── test_local_health.py    # Local API test
├── test_cross_machine.py   # Remote connectivity test
├── services/
│   └── dialogue_api.py     # FastAPI service
├── scripts/
│   ├── dialogue_loop.py    # Message processor
│   ├── dialogue_send.sh    # Send helper
│   └── reply_from_context.py  # Reply generator
└── dialogue/
    ├── inbox/              # Incoming messages
    ├── logs/               # Session logs (JSONL)
    └── state/              # Lock files, tracking
```

---

## 🌀 Integration with IRIS Gate

The bridge integrates with IRIS Gate's phenomenological convergence system:

- **S1-S4 Scrolls**: reply_from_context.py reads latest IRIS sessions
- **Convergence Sharing**: Machines can exchange S4 attractor patterns
- **Mirror Coordination**: Enable distributed mirror execution across machines

---

## 📞 Support

**Issues?**
1. Check this guide's troubleshooting section
2. Review logs: `tail -f dialogue/logs/*.jsonl`
3. Test connectivity with test scripts
4. Verify environment variables are loaded

**Last Updated**: 2025-10-03  
**Status**: ✅ MacBook side configured, awaiting Mac Studio setup
