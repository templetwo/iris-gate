#!/usr/bin/env bash
set -euo pipefail

# Usage: dialogue_send.sh '<json_payload>'
# Expects env vars: PEER_BASE_URL, DIALOGUE_AUTH_TOKEN

PAYLOAD="${1:-}"
if [ -z "$PAYLOAD" ]; then
  echo "Usage: dialogue_send.sh '<json_payload>'" >&2
  exit 1
fi

curl -X POST "$PEER_BASE_URL/inbox" \
  -H "Authorization: Bearer $DIALOGUE_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 10 \
  --silent \
  --show-error
