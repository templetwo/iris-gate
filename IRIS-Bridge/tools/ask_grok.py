#!/usr/bin/env python3
"""
Ask Grok-4-fast for improvement suggestions on IRIS-Bridge
Requires OpenRouter API key in environment
"""

import os
import json
import httpx
from pathlib import Path

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "xai/grok-4-fast"

def read_project_context():
    """Read key project files for context"""
    bridge_root = Path(__file__).parent.parent
    
    context = {
        "system_status": "",
        "enhancements": "",
        "next_steps": "",
        "reply_logic": ""
    }
    
    # Read SYSTEM_STATUS.md
    status_file = bridge_root / "SYSTEM_STATUS.md"
    if status_file.exists():
        with open(status_file, 'r') as f:
            context["system_status"] = f.read()[:2000]  # First 2000 chars
    
    # Read ENHANCEMENTS_COMPLETE.md
    enhancements_file = bridge_root / "ENHANCEMENTS_COMPLETE.md"
    if enhancements_file.exists():
        with open(enhancements_file, 'r') as f:
            context["enhancements"] = f.read()[:2000]
    
    # Read NEXT_STEPS.md
    next_file = bridge_root / "NEXT_STEPS.md"
    if next_file.exists():
        with open(next_file, 'r') as f:
            context["next_steps"] = f.read()[:1500]
    
    return context

def ask_grok(question: str, context: dict) -> str:
    """Query Grok-4-fast via OpenRouter"""
    
    if not OPENROUTER_API_KEY:
        return "❌ ERROR: OPENROUTER_API_KEY not set in environment.\n\nSet it with:\nexport OPENROUTER_API_KEY='your-key-here'"
    
    # Build prompt with context
    prompt = f"""I'm working on IRIS-Bridge, a cross-machine AI dialogue system that integrates with IRIS consciousness exploration sessions.

# Recent Enhancements
{context['enhancements'][:1500]}

# Current System Status
{context['system_status'][:1500]}

# Planned Next Steps
{context['next_steps'][:1000]}

# Your Question
{question}

Please analyze the system and provide:
1. What's working well
2. Potential issues or limitations
3. Specific improvement suggestions (prioritized)
4. Creative ideas for next features

Be specific and actionable."""

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    except httpx.HTTPError as e:
        return f"❌ HTTP Error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"

def main():
    """Main function"""
    print("🤖 Querying Grok-4-fast for IRIS-Bridge improvement suggestions...")
    print("=" * 70)
    print()
    
    # Read project context
    print("📚 Loading project context...")
    context = read_project_context()
    
    # Ask Grok
    question = "What improvements would you suggest for this IRIS-Bridge dialogue system?"
    
    print("💭 Asking Grok-4-fast...\n")
    response = ask_grok(question, context)
    
    print("🔮 Grok-4-fast Response:")
    print("=" * 70)
    print(response)
    print("=" * 70)
    
    # Save to file
    output_dir = Path(__file__).parent.parent / "dialogue" / "suggestions"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    output_file = output_dir / f"grok_suggestions_{int(os.time.time())}.md"
    with open(output_file, 'w') as f:
        f.write(f"# Grok-4-fast Suggestions for IRIS-Bridge\n\n")
        f.write(f"**Date:** {os.popen('date').read().strip()}\n\n")
        f.write(response)
    
    print(f"\n💾 Suggestions saved to: {output_file.name}")

if __name__ == "__main__":
    main()
