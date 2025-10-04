#!/usr/bin/env python3
"""
Dialogue loop: periodically checks inbox, generates replies via reply_from_context.py,
sends them back to peer, and logs everything to JSONL.
"""

import os
import sys
import json
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone
import httpx

# Environment
DIALOGUE_AUTH_TOKEN = os.getenv("DIALOGUE_AUTH_TOKEN", "")
DIALOGUE_SESSION_ID = os.getenv("DIALOGUE_SESSION_ID", "DEV-SESSION")
DIALOGUE_SELF_ID = os.getenv("DIALOGUE_SELF_ID", "machine-unknown")
TICK_INTERVAL = int(os.getenv("DIALOGUE_TICK", "15"))
PEER_BASE_URL = os.getenv("PEER_BASE_URL", "http://localhost:8787")

BRIDGE_ROOT = Path(__file__).parent.parent
LOG_DIR = BRIDGE_ROOT / "dialogue" / "logs"
STATE_DIR = BRIDGE_ROOT / "dialogue" / "state"
LOCK_FILE = STATE_DIR / f"{DIALOGUE_SESSION_ID}.lock"
LAST_MESSAGE_FILE = STATE_DIR / f"{DIALOGUE_SESSION_ID}.last"
PROCESSED_MESSAGES_FILE = STATE_DIR / f"{DIALOGUE_SESSION_ID}.processed"

LOG_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)

def log_message(msg: dict):
    """Append message to session JSONL log"""
    log_path = LOG_DIR / f"{DIALOGUE_SESSION_ID}.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(msg) + "\n")

def get_inbox():
    """Fetch pending messages from local API"""
    headers = {"Authorization": f"Bearer {DIALOGUE_AUTH_TOKEN}"}
    # Determine local port from DIALOGUE_BIND env var
    bind = os.getenv("DIALOGUE_BIND", "0.0.0.0:8787")
    local_port = bind.split(":")[1]
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"http://localhost:{local_port}/inbox",
                headers=headers,
                params={"session_id": DIALOGUE_SESSION_ID}
            )
            resp.raise_for_status()
            return resp.json().get("messages", [])
    except httpx.RequestError as e:
        print(f"Failed to fetch inbox: {e}", file=sys.stderr)
        return []

def get_processed_messages() -> set:
    """Load set of already processed message IDs"""
    if PROCESSED_MESSAGES_FILE.exists():
        try:
            content = PROCESSED_MESSAGES_FILE.read_text().strip()
            if not content:
                return set()
            # Filter out empty lines
            return set(line for line in content.split("\n") if line.strip())
        except:
            return set()
    return set()

def mark_message_processed(msg_id: str):
    """Add message ID to processed list"""
    processed = get_processed_messages()
    processed.add(msg_id)
    # Keep only last 100 message IDs to prevent file bloat
    processed_list = list(processed)[-100:]
    PROCESSED_MESSAGES_FILE.write_text("\n".join(processed_list))

def should_reply(message: dict) -> bool:
    """Check if we should reply to this message"""
    # Don't reply to our own messages
    if message.get("sender") == DIALOGUE_SELF_ID:
        return False

    # Don't reply to AI assistant replies (avoid ping-pong)
    # Only reply to user messages or system messages
    if message.get("role") in ["ai_assistant", "assistant"]:
        return False

    # Check if we've already processed this message
    msg_id = message.get("message_id")
    if msg_id in get_processed_messages():
        return False

    return True

def generate_reply(peer_message: dict) -> dict:
    """Generate reply using reply_from_context.py"""
    import subprocess
    import tempfile

    script_path = BRIDGE_ROOT / "scripts" / "reply_from_context.py"
    peer_json = json.dumps(peer_message)

    try:
        result = subprocess.run(
            ["python3", str(script_path), peer_json],
            capture_output=True,
            text=True,
            check=True
        )
        reply_file = result.stdout.strip()
        with open(reply_file) as f:
            reply_data = json.load(f)
        os.unlink(reply_file)

        # Build full reply message
        return {
            "session_id": DIALOGUE_SESSION_ID,
            "message_id": str(uuid.uuid4()),
            "sender": DIALOGUE_SELF_ID,
            "role": "ai_assistant",
            "text": reply_data["text"],
            "ts": datetime.now(timezone.utc).isoformat(),
            "meta": {"reply_to": peer_message["message_id"]}
        }
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate reply: {e.stderr}", file=sys.stderr)
        return None

def send_reply(reply: dict):
    """Send reply to peer using dialogue_send.sh"""
    payload = json.dumps(reply)
    script_path = BRIDGE_ROOT / "scripts" / "dialogue_send.sh"
    # Escape single quotes for shell
    escaped_payload = payload.replace("'", "'\\''")
    os.system(f"{script_path} '{escaped_payload}' 2>&1")

def dialogue_loop():
    """Main dialogue loop"""
    print(f"Starting dialogue loop for session {DIALOGUE_SESSION_ID}")
    print(f"Self ID: {DIALOGUE_SELF_ID}")
    print(f"Peer: {PEER_BASE_URL}")
    bind_val = os.getenv("DIALOGUE_BIND")
    print(f"Local API Bind: {bind_val}")
    print(f"Auth Token (first 5 chars): {DIALOGUE_AUTH_TOKEN[:5]}...")
    print(f"Tick interval: {TICK_INTERVAL}s\n")

    while True:
        try:
            # Check for lock (only one reply in flight)
            if LOCK_FILE.exists():
                print("Lock file exists, waiting...", file=sys.stderr)
                time.sleep(TICK_INTERVAL)
                continue

            # Get inbox
            print("Checking inbox...")
            messages = get_inbox()
            if not messages:
                print("Inbox empty.")
                time.sleep(TICK_INTERVAL)
                continue
            else:
                print(f"Found {len(messages)} messages in inbox.")

            # Process latest message we should reply to
            for msg in reversed(messages):
                if should_reply(msg):
                    print(f"Processing message {msg['message_id']} from {msg['sender']}")

                    # Create lock
                    LOCK_FILE.write_text(msg['message_id'])

                    try:
                        # Generate reply
                        reply = generate_reply(msg)
                        if reply:
                            # Send reply
                            send_reply(reply)

                            # Log both messages
                            log_message(msg)
                            log_message(reply)

                            # Mark message as processed
                            mark_message_processed(msg['message_id'])
                            # Also update last processed for backwards compatibility
                            LAST_MESSAGE_FILE.write_text(msg['message_id'])

                            print(f"Sent reply {reply['message_id']}\n")
                    finally:
                        # Remove lock
                        if LOCK_FILE.exists():
                            LOCK_FILE.unlink()

                    break

            time.sleep(TICK_INTERVAL)

        except KeyboardInterrupt:
            print("\nShutting down dialogue loop")
            break
        except Exception as e:
            print(f"Error in dialogue loop: {e}", file=sys.stderr)
            if LOCK_FILE.exists():
                LOCK_FILE.unlink()
            time.sleep(TICK_INTERVAL)

if __name__ == "__main__":
    dialogue_loop()
