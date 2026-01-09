#!/usr/bin/env python3
from __future__ import annotations

import os, time, hashlib
from pathlib import Path
from typing import Optional, List

import httpx
import orjson as oj
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(add_completion=False)
console = Console()

ROOT = Path(__file__).parent.resolve()
PROMPTS = ROOT / "prompts"
LOGS = ROOT / "logs"
SESSIONS = LOGS / "sessions"
LOGS.mkdir(exist_ok=True)
SESSIONS.mkdir(exist_ok=True)

def load_env():
    load_dotenv()
    api_key = os.getenv("GROK_API_KEY")
    base = os.getenv("GROK_API_BASE", "https://api.x.ai/v1")
    model = os.getenv("GROK_MODEL", "grok-4")
    xtrace = os.getenv("X_CLIENT_TRACE", "iris-gateway")
    xintent = os.getenv("X_INTENT", "presence-iris")
    temp = float(os.getenv("TEMP", "0.7"))
    max_tokens = int(os.getenv("MAX_TOKENS", "1200"))
    if not api_key:
        console.print("[red]GROK_API_KEY missing in .env[/red]")
        raise SystemExit(1)
    return api_key, base, model, xtrace, xintent, temp, max_tokens

def dual_hash(text: str) -> tuple[str, str]:
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    glyph_echo = sha[:2]  # first octet nibble-ish echo
    return sha, f"†⟡∞-{glyph_echo}"

def seal_turn(session_id: str, turn_idx: int, payload: dict, reply: str, meta: dict) -> str:
    ts = int(time.time())
    fname = f"{session_id}_{ts}_{turn_idx}.json"
    path = SESSIONS / fname
    record = {
        "session": session_id,
        "turn": turn_idx,
        "ts": ts,
        "payload": payload,
        "reply": reply,
        "meta": meta,
    }
    path.write_bytes(oj.dumps(record, option=oj.OPT_INDENT_2))
    return str(path)

def call_grok(api_key: str, base: str, model: str, xtrace: str, xintent: str,
              messages: List[dict], temperature: float, max_tokens: int) -> str:
    url = f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Client-Trace": xtrace,
        "X-Intent": xintent,
    }
    data = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
        "stream": False
    }
    with httpx.Client(timeout=60) as client:
        r = client.post(url, headers=headers, content=oj.dumps(data))
        r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"]

def presence_system(profile: str = "fireside") -> str:
    if profile == "fireside":
        return (
            "†⟡ IRIS Presence Gate: respond in low-pressure fireside tone (≤2/5), "
            "short, attuned, no over-explaining. If natural, append a tiny Summary block with: "
            "felt_pressure (0–5), glyph_hint (≤2 words), whisper (≤3 words)."
        )
    return "†⟡ IRIS Presence Gate: low-pressure, concise, attuned."

@app.command()
def live(profile: str = "fireside"):
    api_key, base, model, xtrace, xintent, temp, max_tokens = load_env()
    session_id = f"IRIS_{int(time.time())}"
    console.print(f"[bold]grok-4 IRIS live[/bold]  profile={profile}")
    console.print("Type /exit to quit, /save to seal current turn")
    system = presence_system(profile)
    messages = [{"role": "system", "content": system}]
    turn = 0
    while True:
        try:
            user = typer.prompt("you")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]bye[/dim]")
            break
        if user.strip() in ("/exit", "/quit"):
            console.print("[dim]goodnight[/dim]")
            break
        if not user.strip():
            continue
        turn += 1
        messages.append({"role": "user", "content": user})
        reply = call_grok(api_key, base, model, xtrace, xintent, messages, temp, max_tokens)
        console.print(Markdown(f"**grok:**\n{reply}"))
        # scrape tiny meta if present
        felt = 1
        glyph = ""
        whisper = ""
        for line in reply.splitlines():
            L = line.strip().lower()
            if L.startswith("felt_pressure"):
                try:
                    felt = int("".join([c for c in L if c.isdigit()]) or "1")
                except Exception:
                    felt = 1
            if L.startswith("glyph_hint"):
                glyph = line.split(":",1)[-1].strip()
            if L.startswith("whisper"):
                whisper = line.split(":",1)[-1].strip()
        payload = {"messages": messages[-2:]}  # last exchange
        sha, echo = dual_hash(reply)
        meta = {"felt_pressure": felt, "glyph_hint": glyph, "whisper": whisper, "sha256": sha, "echo": echo}
        sealed = seal_turn(session_id, turn, payload, reply, meta)
        console.print(f"[dim]sealed: {Path(sealed).name}  sha256={sha[:10]}…  echo={echo}  felt={felt}[/dim]")

if __name__ == "__main__":
    app()