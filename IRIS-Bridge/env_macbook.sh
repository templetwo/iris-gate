#!/bin/bash
# IRIS-Bridge Environment Configuration - MacBook Pro
# Source this file before starting services: source env_macbook.sh

export DIALOGUE_AUTH_TOKEN="iris-bridge-autonomous-sync-2025"
export DIALOGUE_SESSION_ID="CLAUDE-GEMINI-SYNC"
export DIALOGUE_SELF_ID="macbook-pro"
export PEER_BASE_URL="http://100.72.59.69:8787"
export DIALOGUE_TICK="10"
export DIALOGUE_BIND="0.0.0.0:8788"

echo "✨ IRIS-Bridge Environment Loaded (MacBook Pro)"
echo "   Self ID: $DIALOGUE_SELF_ID"
echo "   Peer URL: $PEER_BASE_URL"
echo "   Session: $DIALOGUE_SESSION_ID"
echo "   Bind: $DIALOGUE_BIND"
