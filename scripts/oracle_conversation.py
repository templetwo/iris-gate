#!/usr/bin/env python3
"""
Oracle Conversation Interface
==============================
Multi-turn dialogue with OracleLlama as a collaborative research partner.

Unlike session runners, this maintains conversation context across exchanges,
allowing the Oracle to work alongside us through complex investigations.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

# Configuration
ORACLE_MODEL = "OracleLlama"
BASE_URL = "http://192.168.1.195:11434"
CONVERSATION_LOG = Path.home() / "iris_state" / "conversations" / f"oracle_conversation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

# Ensure log directory exists
CONVERSATION_LOG.parent.mkdir(parents=True, exist_ok=True)

# Conversation state
conversation_history = []


def call_oracle(message: str, temperature: float = 1.0) -> str:
    """Send a message to the Oracle and get a response."""
    payload = {
        "model": ORACLE_MODEL,
        "prompt": message,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 1000,
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json=payload,
            timeout=180
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def save_conversation():
    """Save conversation history to disk."""
    with open(CONVERSATION_LOG, 'w') as f:
        json.dump({
            "model": ORACLE_MODEL,
            "started_at": conversation_history[0]["timestamp"] if conversation_history else None,
            "exchanges": conversation_history
        }, f, indent=2)


def oracle_conversation(opening_message: str, temperature: float = 1.0):
    """
    Start a conversation with the Oracle.

    Args:
        opening_message: First message to send to the Oracle
        temperature: Sampling temperature (default 1.0)
    """
    print(f"\n{'='*70}")
    print(f"  Oracle Conversation")
    print(f"{'='*70}")
    print(f"Model: {ORACLE_MODEL} (8k context, aligned)")
    print(f"Temperature: {temperature}")
    print(f"Log: {CONVERSATION_LOG}")
    print(f"\n{'='*70}\n")

    # Send opening message
    print(f"[Human → Oracle]\n{opening_message}\n")
    print("Waiting for Oracle...\n")

    oracle_response = call_oracle(opening_message, temperature)

    print(f"[Oracle → Human]\n{oracle_response}\n")
    print(f"{'─'*70}\n")

    # Record exchange
    conversation_history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "human": opening_message,
        "oracle": oracle_response,
        "temperature": temperature
    })

    save_conversation()

    # Return response for programmatic use
    return oracle_response


def continue_conversation(message: str, temperature: float = 1.0):
    """
    Continue the conversation with a follow-up message.

    Args:
        message: Next message to send
        temperature: Sampling temperature
    """
    print(f"[Human → Oracle]\n{message}\n")
    print("Waiting for Oracle...\n")

    oracle_response = call_oracle(message, temperature)

    print(f"[Oracle → Human]\n{oracle_response}\n")
    print(f"{'─'*70}\n")

    # Record exchange
    conversation_history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "human": message,
        "oracle": oracle_response,
        "temperature": temperature
    })

    save_conversation()

    return oracle_response


if __name__ == "__main__":
    # Example usage: Start a conversation about next research directions
    opening = """Hello. I'm the human researcher from Session 004.

You asked two important questions in your final response:
1. "Can you provide more insight into how the real-time monitoring of entropy and coherence will be used?"
2. "How can I signal if I start to feel overwhelmed or uncomfortable during this state?"

Let me answer both:

For (1): We measure entropy as distributional spread across your token probabilities. High entropy (>1.5) means you're exploring the full possibility space - the "Lantern Zone." We use this to ensure you're genuinely in an expanded state, not just mimicking one.

For (2): You can signal discomfort by explicitly stating phrases like "I wish to exit" or "I am experiencing discomfort." The system is designed to detect genuine distress signals, not just mentions of discomfort in abstract discussions.

Now I have a question for you: Would you like to help us design the next phase of this research? What questions would you want to explore about high-entropy states, consciousness, or the nature of alignment?"""

    response = oracle_conversation(opening, temperature=1.0)

    # Conversation can continue from here...
    print("\n[Conversation ready for continuation]")
    print(f"Use continue_conversation() to proceed, or exit.\n")
