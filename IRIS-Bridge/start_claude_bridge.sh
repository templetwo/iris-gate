#!/bin/bash
export DIALOGUE_AUTH_TOKEN="iris-bridge-autonomous-sync-2025"
export DIALOGUE_BIND="0.0.0.0:8788"
export DIALOGUE_SELF_ID="iris-gate-claude"
export DIALOGUE_SESSION_ID="CLAUDE-GEMINI-SYNC"
export PEER_BASE_URL="http://192.168.1.195:8787"

cd "$(dirname "$0")"
python3 -m uvicorn services.dialogue_api:app --host 0.0.0.0 --port 8788
