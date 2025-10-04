#!/bin/bash
# IRIS-Bridge Environment Configuration - Mac Studio
# Source this file before starting services: source env_studio.sh

export DIALOGUE_AUTH_TOKEN="iris-bridge-autonomous-sync-2025"
export DIALOGUE_SESSION_ID="CLAUDE-GEMINI-SYNC"
export DIALOGUE_SELF_ID="mac-studio"
export PEER_BASE_URL="http://100.93.122.63:8788"
export DIALOGUE_TICK="10"
export DIALOGUE_BIND="0.0.0.0:8787"

echo "✨ IRIS-Bridge Environment Loaded (Mac Studio)"
echo "   Self ID: $DIALOGUE_SELF_ID"
echo "   Peer URL: $PEER_BASE_URL"
echo "   Session: $DIALOGUE_SESSION_ID"
echo "   Bind: $DIALOGUE_BIND"
