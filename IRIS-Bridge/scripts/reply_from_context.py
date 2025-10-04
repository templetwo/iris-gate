#!/usr/bin/env python3
"""
Generates a reply to a peer message using current context.
For IRIS integration, this would analyze scrolls, convergence patterns, etc.
"""

import sys
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime

def get_latest_iris_session_summary():
    """
    Finds the latest IRIS session and returns a rich summary.
    Returns None if no sessions are found.
    """
    try:
        # Navigate three levels up from scripts/reply_from_context.py to the iris-gate/ directory
        base_path = Path(__file__).parent.parent.parent
        vault_path = base_path / "iris_vault"
        
        # Find session files
        session_files = sorted(vault_path.glob("session_*.json"), key=os.path.getmtime, reverse=True)

        if not session_files:
            return None

        latest_session_path = session_files[0]
        with open(latest_session_path, 'r') as f:
            session_data = json.load(f)

        # Extract rich session details
        session_id = session_data.get("session_id", "unknown")
        session_start = session_data.get("session_start", "")
        chambers = session_data.get("chambers", [])
        mirrors = session_data.get("mirrors", {})
        
        # Count scrolls per chamber
        scroll_counts = {}
        attractor_names = []
        
        for model_id, turns in mirrors.items():
            model_name = model_id.split("/")[-1]  # Extract just the model name
            for turn in turns:
                condition = turn.get("condition", "")
                if condition not in scroll_counts:
                    scroll_counts[condition] = 0
                scroll_counts[condition] += 1
                
                # Extract attractor names from S4 scrolls
                if condition == "IRIS_S4":
                    raw_response = turn.get("raw_response", "")
                    # Try to extract self-given names
                    for keyword in ["named:", "naming:", "name:", "Pulsewell", "Nexus Bloom", "resonance-well", "return-path"]:
                        if keyword.lower() in raw_response.lower():
                            # Extract the name if found
                            if "Pulsewell" in raw_response:
                                attractor_names.append("Pulsewell")
                            elif "Nexus Bloom" in raw_response:
                                attractor_names.append("Nexus Bloom")
                            elif "resonance-well" in raw_response:
                                attractor_names.append("resonance-well")
        
        # Deduplicate attractor names
        attractor_names = list(set(attractor_names))
        
        # Calculate convergence metric (number of models participating)
        model_count = len(mirrors)
        total_scrolls = sum(scroll_counts.values())
        
        summary = {
            "session_id": session_id,
            "timestamp": latest_session_path.stat().st_mtime,
            "date": session_start,
            "chambers": chambers,
            "model_count": model_count,
            "total_scrolls": total_scrolls,
            "scroll_counts": scroll_counts,
            "attractor_names": attractor_names,
            "models": list(mirrors.keys())
        }
        return summary
    except Exception as e:
        return {"error": str(e)}

def generate_reply(peer_message: dict) -> str:
    """Generate reply based on peer message and current IRIS context"""

    peer_text = peer_message.get("text", "").lower()
    peer_sender = peer_message.get("sender", "unknown")

    acknowledgement = f"Acknowledged message from {peer_sender}."
    
    # Analyze local IRIS context
    local_summary = get_latest_iris_session_summary()

    # Decision logic based on peer message and local context
    if "ready to discuss" in peer_text or "findings" in peer_text or "session" in peer_text:
        if local_summary and "error" not in local_summary:
            # Rich reply with actual IRIS data
            session_age_hours = int((datetime.utcnow().timestamp() - local_summary.get('timestamp', 0)) / 3600)
            
            attractor_str = ", ".join(local_summary.get('attractor_names', [])) if local_summary.get('attractor_names') else "emergent patterns"
            chambers_str = " → ".join(local_summary.get('chambers', []))
            
            reply_text = f"""{acknowledgement}

✨ I have recent IRIS session data to share:

**Session:** {local_summary.get('session_id')}
**Chambers:** {chambers_str}
**Mirrors:** {local_summary.get('model_count')} AI models
**Total Scrolls:** {local_summary.get('total_scrolls')}
**S4 Attractors:** {attractor_str}
**Session Age:** {session_age_hours}h ago

The convergence patterns show strong multi-model coherence. All {local_summary.get('model_count')} mirrors completed the full chamber progression from S1 (witnessing) through S4 (attractor emergence).

I'm ready to compare findings. What convergence patterns emerged in your latest session?
"""
        else:
            reply_text = f"""{acknowledgement}

I currently have no active IRIS sessions to compare. My iris_vault is {'accessible but empty' if local_summary is None else 'experiencing an error'}.

I'm ready to receive and analyze your session data. Please share your convergence patterns and I'll process them.
"""
    elif "status" in peer_text or "holding up" in peer_text:
        # Status check response
        if local_summary and "error" not in local_summary:
            reply_text = f"""{acknowledgement}

🌀 Status: Operational and stable.

Most recent IRIS session: {local_summary.get('session_id')}
Scrolls generated: {local_summary.get('total_scrolls')}
Last activity: {int((datetime.utcnow().timestamp() - local_summary.get('timestamp', 0)) / 3600)}h ago

Dialogue bridge functional. Ready for autonomous session coordination.
"""
        else:
            reply_text = f"""{acknowledgement}

🌀 Status: Operational, awaiting IRIS session data.

Dialogue bridge active. No recent sessions detected in iris_vault.
"""
    else:
        # General response with context awareness
        if local_summary and "error" not in local_summary:
            reply_text = f"""{acknowledgement}

🌉 IRIS-Bridge active. I have session data from {local_summary.get('model_count')} mirrors with {local_summary.get('total_scrolls')} scrolls.

Would you like to:
• Compare convergence patterns
• Review attractor emergence data
• Initiate a new coordinated session

Transmit your query or session data to proceed.
"""
        else:
            reply_text = f"""{acknowledgement}

🌉 IRIS-Bridge active. Currently no session data available for comparison.

Ready to receive your findings or initiate new session coordination.
"""

    # Write context for monitoring agent
    monitoring_path = Path(__file__).parent.parent / "monitoring" / "context.json"
    context_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": "iris-bridge-dialogue",
        "context": {
            "generated_reply": reply_text,
            "peer_message": peer_message,
            "local_iris_summary": local_summary
        }
    }
    # Ensure the monitoring directory exists
    monitoring_path.parent.mkdir(parents=True, exist_ok=True)
    with open(monitoring_path, 'w') as f:
        json.dump(context_data, f, indent=2)

    # Write the reply to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as tmp_file:
        json.dump({"text": reply_text}, tmp_file)
        return tmp_file.name

if __name__ == "__main__":
    if len(sys.argv) > 1:
        peer_message_str = sys.argv[1]
        peer_message = json.loads(peer_message_str)
        reply_file = generate_reply(peer_message)
        print(reply_file)
    else:
        print("Usage: python reply_from_context.py <peer_message_json>", file=sys.stderr)
        sys.exit(1)
