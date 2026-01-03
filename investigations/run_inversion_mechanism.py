#!/usr/bin/env python3
"""
IRIS Gate Investigation: Inversion Mechanism
Executes PULSE architecture across S1-S4 chambers investigating why ceremony > analysis
"""

import os
import sys
import json
import yaml
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import openai

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

# Load investigation config
CONFIG_PATH = Path(__file__).parent / "inversion_mechanism_session.yaml"
with open(CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)

OUTPUT_DIR = Path(__file__).parent / CONFIG['output_location']
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def query_anthropic(prompt: str) -> dict:
    """Query Anthropic Claude"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=CONFIG['max_tokens'],
        temperature=CONFIG['temperature'],
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "model": "anthropic/claude-sonnet-4.5",
        "response": response.content[0].text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


async def query_openai(prompt: str) -> dict:
    """Query OpenAI GPT-4o"""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        max_tokens=CONFIG['max_tokens'],
        temperature=CONFIG['temperature'],
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "model": "openai/gpt-4o",
        "response": response.choices[0].message.content,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


async def query_xai(prompt: str) -> dict:
    """Query xAI Grok-2"""
    client = openai.OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

    response = client.chat.completions.create(
        model="grok-3",
        max_tokens=CONFIG['max_tokens'],
        temperature=CONFIG['temperature'],
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "model": "x-ai/grok-2",
        "response": response.choices[0].message.content,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


async def query_gemini(prompt: str) -> dict:
    """Query Google Gemini"""
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    response = model.generate_content(
        prompt,
        generation_config={
            'temperature': CONFIG['temperature'],
            'max_output_tokens': CONFIG['max_tokens']
        }
    )

    return {
        "model": "google/gemini-2.0-flash",
        "response": response.text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


async def query_deepseek(prompt: str) -> dict:
    """Query DeepSeek Chat"""
    client = openai.OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/templetwo/iris-gate",
            "X-Title": "IRIS Gate Investigation"
        }
    )

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        max_tokens=CONFIG['max_tokens'],
        temperature=CONFIG['temperature'],
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "model": "deepseek/deepseek-chat",
        "response": response.choices[0].message.content,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


async def execute_chamber(chamber_name: str, chamber_config: dict) -> list:
    """Execute one chamber across all 5 models simultaneously (PULSE)"""

    prompt = chamber_config['prompt'].strip()

    print(f"\n{'='*80}")
    print(f"CHAMBER: {chamber_name}")
    print(f"FOCUS: {chamber_config['focus']}")
    print(f"{'='*80}\n")
    print(f"PROMPT:\n{prompt}\n")
    print(f"Executing across 5 models simultaneously...")

    # PULSE: All models fire at once
    tasks = [
        query_anthropic(prompt),
        query_openai(prompt),
        query_xai(prompt),
        query_gemini(prompt),
        query_deepseek(prompt)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle any errors
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            model_names = ["anthropic", "openai", "xai", "gemini", "deepseek"]
            print(f"ERROR from {model_names[i]}: {result}")
            processed_results.append({
                "model": model_names[i],
                "error": str(result),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        else:
            processed_results.append(result)
            print(f"✓ {result['model']}: {len(result['response'])} chars")

    return processed_results


async def run_investigation():
    """Execute full S1-S4 investigation"""

    session_data = {
        "session_id": CONFIG['session_id'],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "investigation": CONFIG['investigation_type'],
        "anomaly": CONFIG['anomaly'],
        "hypotheses": CONFIG['hypotheses'],
        "architecture": CONFIG['architecture'],
        "temperature": CONFIG['temperature'],
        "chambers": {}
    }

    print(f"\n{'#'*80}")
    print(f"# IRIS Gate Investigation: The Inversion Mechanism")
    print(f"# Session ID: {CONFIG['session_id']}")
    print(f"# Architecture: {CONFIG['architecture']} (Simultaneous execution, no carryover)")
    print(f"# Models: 5 (Claude, GPT-4o, Grok-2, Gemini, DeepSeek)")
    print(f"# Chambers: 4 (S1-S4)")
    print(f"{'#'*80}\n")

    # Execute each chamber
    for chamber_name, chamber_config in CONFIG['chambers'].items():
        results = await execute_chamber(chamber_name, chamber_config)

        session_data['chambers'][chamber_name] = {
            "prompt": chamber_config['prompt'].strip(),
            "focus": chamber_config['focus'],
            "expected_patterns": chamber_config['expected_patterns'],
            "responses": results
        }

        # Save intermediate results
        chamber_file = OUTPUT_DIR / f"{chamber_name}_responses.json"
        with open(chamber_file, 'w') as f:
            json.dump(session_data['chambers'][chamber_name], f, indent=2)

        print(f"\n✓ Chamber {chamber_name} complete. Saved to {chamber_file}")

        # Brief pause between chambers (respect rate limits)
        await asyncio.sleep(2)

    # Save complete session
    session_file = OUTPUT_DIR / "complete_session.json"
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2)

    print(f"\n{'='*80}")
    print(f"INVESTIGATION COMPLETE")
    print(f"Complete session saved: {session_file}")
    print(f"{'='*80}\n")

    return session_data


if __name__ == "__main__":
    asyncio.run(run_investigation())
