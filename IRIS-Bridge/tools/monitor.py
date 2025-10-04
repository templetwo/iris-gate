#!/usr/bin/env python3
"""
IRIS-Bridge Monitoring Dashboard
Simple real-time view of dialogue status across both machines
"""

import os
import sys
import time
import json
import httpx
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
AUTH_TOKEN = os.getenv("DIALOGUE_AUTH_TOKEN", "iris-bridge-autonomous-sync-2025")
SESSION_ID = "CLAUDE-GEMINI-SYNC"
MACBOOK_URL = "http://localhost:8788"
STUDIO_URL = "http://100.72.59.69:8787"

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_api_status(url):
    """Check if API is responding"""
    try:
        resp = httpx.get(f"{url}/health", 
                        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                        timeout=2.0)
        return "✅ UP" if resp.status_code == 200 else "⚠️  ERROR"
    except:
        return "❌ DOWN"

def get_inbox(url):
    """Get inbox messages"""
    try:
        resp = httpx.get(f"{url}/inbox",
                        params={"session_id": SESSION_ID},
                        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                        timeout=2.0)
        if resp.status_code == 200:
            return resp.json().get("messages", [])
        return []
    except:
        return []

def format_timestamp(ts_str):
    """Format timestamp for display"""
    try:
        if "+" in ts_str:
            dt = datetime.fromisoformat(ts_str)
        elif "Z" in ts_str:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            return ts_str
        
        now = datetime.now(dt.tzinfo)
        delta = now - dt
        
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}m ago"
        elif delta.total_seconds() < 86400:
            return f"{int(delta.total_seconds() / 3600)}h ago"
        else:
            return f"{int(delta.total_seconds() / 86400)}d ago"
    except:
        return "unknown"

def monitor_loop():
    """Main monitoring loop"""
    try:
        while True:
            clear_screen()
            
            # Header
            print("╔═══════════════════════════════════════════════════════════════╗")
            print("║              🌉 IRIS-Bridge Monitor                          ║")
            print("╚═══════════════════════════════════════════════════════════════╝")
            print()
            
            # Get status
            macbook_status = get_api_status(MACBOOK_URL)
            studio_status = get_api_status(STUDIO_URL)
            macbook_inbox = get_inbox(MACBOOK_URL)
            studio_inbox = get_inbox(STUDIO_URL)
            
            # System status
            print("┌─ System Status ─────────────────────────────────────────────┐")
            print(f"│ MacBook Pro:  {macbook_status}   API │ Inbox: {len(macbook_inbox):3d} messages     │")
            print(f"│ Mac Studio:   {studio_status}   API │ Inbox: {len(studio_inbox):3d} messages     │")
            print("└──────────────────────────────────────────────────────────────┘")
            print()
            
            # Recent activity
            all_messages = []
            for msg in macbook_inbox:
                msg['location'] = 'MacBook'
                all_messages.append(msg)
            for msg in studio_inbox:
                msg['location'] = 'Studio'
                all_messages.append(msg)
            
            # Sort by timestamp (most recent first)
            all_messages.sort(key=lambda m: m.get('ts', ''), reverse=True)
            
            print("┌─ Recent Messages ───────────────────────────────────────────┐")
            if all_messages:
                for i, msg in enumerate(all_messages[:10]):  # Show last 10
                    sender = msg.get('sender', 'unknown')[:15]
                    role = msg.get('role', 'unknown')[:10]
                    location = msg.get('location', '?')[:8]
                    ts = format_timestamp(msg.get('ts', ''))
                    text_preview = msg.get('text', '')[:30].replace('\n', ' ')
                    
                    symbol = "📨" if role == "user" else "🤖" if role == "ai_assistant" else "⚙️"
                    print(f"│ {symbol} [{ts:8s}] {sender:15s} → {location:8s} │")
                    print(f"│    {text_preview:53s}... │")
                    if i < len(all_messages[:10]) - 1:
                        print("│                                                             │")
            else:
                print("│   No messages yet...                                        │")
            print("└──────────────────────────────────────────────────────────────┘")
            print()
            
            # Statistics
            total_messages = len(macbook_inbox) + len(studio_inbox)
            ai_messages = sum(1 for m in all_messages if m.get('role') in ['ai_assistant', 'assistant'])
            user_messages = sum(1 for m in all_messages if m.get('role') == 'user')
            
            print("┌─ Statistics ────────────────────────────────────────────────┐")
            print(f"│ Total Messages:     {total_messages:4d}                                 │")
            print(f"│ AI Replies:         {ai_messages:4d}                                 │")
            print(f"│ User Messages:      {user_messages:4d}                                 │")
            print("└──────────────────────────────────────────────────────────────┘")
            print()
            
            # Footer
            print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Press Ctrl+C to exit • Refreshing every 3 seconds...")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    print("Starting IRIS-Bridge Monitor...")
    print("Connecting to services...")
    time.sleep(1)
    monitor_loop()
