#!/usr/bin/env python3
"""
Discover available flagship model identifiers from each API provider.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load API keys from Desktop
env_path = Path("/Users/vaquez/Desktop/api_keys.env")
load_dotenv(env_path, override=True)

def discover_openai_models():
    """Query OpenAI API for available GPT models."""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        models = client.models.list()
        gpt_models = sorted([m.id for m in models.data if m.id.startswith("gpt")])

        print("\n" + "="*80)
        print("OPENAI GPT MODELS")
        print("="*80)
        for model in gpt_models:
            print(f"  • {model}")

        # Find flagship candidates
        flagship_candidates = [m for m in gpt_models if "gpt-5" in m or "gpt-4o" in m]
        if flagship_candidates:
            print(f"\nFlagship candidates: {flagship_candidates[-1]}")

        return gpt_models
    except Exception as e:
        print(f"\n✗ OpenAI error: {e}")
        return []

def discover_xai_models():
    """Query xAI API for available Grok models."""
    try:
        import requests

        api_key = os.getenv("XAI_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get("https://api.x.ai/v1/models", headers=headers)

        print("\n" + "="*80)
        print("xAI GROK MODELS")
        print("="*80)

        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                models = sorted([m["id"] for m in data["data"]])
                for model in models:
                    print(f"  • {model}")

                # Find flagship
                grok_models = [m for m in models if "grok" in m.lower()]
                if grok_models:
                    print(f"\nFlagship candidates: {grok_models[-1]}")

                return models
            else:
                print(f"Unexpected response format: {data}")
        else:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")

        return []
    except Exception as e:
        print(f"\n✗ xAI error: {e}")
        return []

def discover_gemini_models():
    """Query Google Gemini API for available models."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        models = genai.list_models()

        print("\n" + "="*80)
        print("GOOGLE GEMINI MODELS")
        print("="*80)

        gemini_models = []
        for m in models:
            model_id = m.name.replace("models/", "")
            if "gemini" in model_id.lower():
                gemini_models.append(model_id)
                print(f"  • {model_id}")

        # Find flagship
        flagship = [m for m in gemini_models if "gemini-3" in m or "gemini-2.5" in m]
        if flagship:
            print(f"\nFlagship candidates: {flagship[0] if flagship else gemini_models[0]}")

        return gemini_models
    except Exception as e:
        print(f"\n✗ Gemini error: {e}")
        return []

def main():
    print("\n🔍 DISCOVERING FLAGSHIP MODEL IDENTIFIERS\n")

    openai_models = discover_openai_models()
    xai_models = discover_xai_models()
    gemini_models = discover_gemini_models()

    print("\n" + "="*80)
    print("RECOMMENDED FLAGSHIP CONFIGURATION")
    print("="*80)

    # Suggest best models
    gpt_flagship = next((m for m in reversed(openai_models) if "gpt-5" in m),
                        next((m for m in reversed(openai_models) if "gpt-4o" in m), "gpt-4o"))

    grok_flagship = next((m for m in reversed(xai_models) if "grok" in m.lower()), "grok-beta")

    gemini_flagship = next((m for m in gemini_models if "gemini-3-pro" in m),
                          next((m for m in gemini_models if "gemini-3-flash" in m),
                               next((m for m in gemini_models if "gemini-2.5" in m), "gemini-2.0-flash-exp")))

    print(f"""
GPT Flagship:    {gpt_flagship}
Grok Flagship:   {grok_flagship}
Gemini Flagship: {gemini_flagship}
Claude Flagship: claude-sonnet-4-5-20250929
DeepSeek:        deepseek-chat
    """)

if __name__ == "__main__":
    main()
