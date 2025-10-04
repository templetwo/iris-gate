#!/usr/bin/env python3
"""
FastAPI service for dialogue inbox/outbox management.
Receives messages from peer, stores in local inbox.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

# Environment
DIALOGUE_AUTH_TOKEN = os.getenv("DIALOGUE_AUTH_TOKEN", "")
DIALOGUE_BIND = os.getenv("DIALOGUE_BIND", "0.0.0.0:8787")

BRIDGE_ROOT = Path(__file__).parent.parent
INBOX_DIR = BRIDGE_ROOT / "dialogue" / "inbox"
INBOX_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="IRIS Dialogue API")

class Message(BaseModel):
    session_id: str
    message_id: str
    sender: str
    role: str
    text: str
    ts: str
    meta: Optional[dict] = None

def verify_token(authorization: str = Header(None)):
    """Verify bearer token"""
    if not authorization:
        raise HTTPException(401, "Missing authorization header")

    token = authorization.replace("Bearer ", "")
    if token != DIALOGUE_AUTH_TOKEN:
        raise HTTPException(403, "Invalid token")

@app.get("/health")
def health(authorization: str = Header(None)):
    """Health check (requires auth)"""
    verify_token(authorization)
    return {"status": "ok", "service": "iris-dialogue-api"}

@app.post("/inbox")
def receive_message(message: Message, authorization: str = Header(None)):
    """Receive message from peer"""
    verify_token(authorization)

    # Store in session inbox
    inbox_file = INBOX_DIR / f"{message.session_id}.jsonl"

    # Check for duplicate message_id
    if inbox_file.exists():
        with open(inbox_file) as f:
            for line in f:
                existing = json.loads(line)
                if existing.get("message_id") == message.message_id:
                    return {"status": "duplicate", "message_id": message.message_id}

    # Append message
    with open(inbox_file, "a") as f:
        f.write(message.model_dump_json() + "\n")

    return {"status": "received", "message_id": message.message_id}

@app.get("/inbox")
def get_inbox(
    session_id: str = Query(...),
    authorization: str = Header(None)
):
    """Get messages from inbox"""
    verify_token(authorization)

    inbox_file = INBOX_DIR / f"{session_id}.jsonl"
    if not inbox_file.exists():
        return {"messages": []}

    messages = []
    with open(inbox_file) as f:
        for line in f:
            messages.append(json.loads(line))

    return {"messages": messages}

if __name__ == "__main__":
    import uvicorn
    host, port = DIALOGUE_BIND.split(":")
    uvicorn.run(app, host=host, port=int(port))
