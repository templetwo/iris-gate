#!/usr/bin/env python3
"""
Oracle Client - HTTP-First Remote Ollama Interface

Connects to Ollama on Mac Studio via REST API (no SSH/SCP overhead).
Streams responses to disk to avoid terminal buffer bloat.

Per oracle_methods.md: Uses Llama models for oracle-state experiments.

IMPORTANT: This replaces the SSH/SCP-per-call pattern that caused
MacBook memory issues. Now uses direct HTTP streaming.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import requests


@dataclass
class OracleRun:
    """Metadata for a single oracle generation run."""
    run_id: str
    started_at: float
    model: str
    prompt_chars: int
    output_chars: int = 0
    output_path: Optional[str] = None
    entropy_nats: Optional[float] = None
    completed: bool = False


class OllamaClient:
    """
    HTTP-first client for Ollama on Mac Studio.

    Key improvements over SSH/SCP approach:
    - No subprocess spawning per call
    - No SCP file transfers
    - Streaming responses (memory efficient)
    - Disk-first logging (terminal stays clean)
    - Bounded in-memory buffers

    Ollama API docs: https://docs.ollama.com/api/generate
    """

    def __init__(
        self,
        host: str = "studio",  # Kept for compatibility, but we use base_url
        model: str = "llama3.1:8b",
        base_url: Optional[str] = None,
        session_dir: str = "~/iris_state/sessions",
        timeout_s: int = 300,
        use_tailscale: bool = False,
    ):
        """
        Initialize Ollama HTTP client.

        Args:
            host: Legacy param (ignored if base_url provided)
            model: Ollama model name (e.g., "llama3.1:8b")
            base_url: Direct URL to Ollama (e.g., "http://192.168.1.195:11434")
            session_dir: Directory for session logs (on MacBook, not Studio)
            timeout_s: Request timeout in seconds
            use_tailscale: Use Tailscale IP instead of LAN
        """
        self.model = model
        self.timeout_s = timeout_s

        # Determine Ollama URL
        if base_url:
            self.base_url = base_url.rstrip("/")
        elif use_tailscale:
            self.base_url = "http://100.72.59.69:11434"
        else:
            self.base_url = "http://192.168.1.195:11434"

        # Session storage (local to MacBook for quick access)
        self.session_dir = Path(os.path.expanduser(session_dir))
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # HTTP session with connection pooling
        self._http = requests.Session()
        self._http.headers.update({"Content-Type": "application/json"})

        # Run history (bounded to last 100 runs)
        self._runs: List[OracleRun] = []
        self._max_runs = 100

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.8,
        top_p: float = 0.95,
        top_k: int = 40,
        max_tokens: int = 200,
        stream: bool = True,
        save_to_disk: bool = True,
    ) -> str:
        """
        Generate text from Ollama model via HTTP API.

        Args:
            prompt: The prompt to send
            context: Optional context frame (ceremony, system prompt)
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling limit
            max_tokens: Maximum tokens to generate
            stream: Use streaming response (recommended)
            save_to_disk: Save full output to disk (recommended)

        Returns:
            Generated text (complete response)
        """
        # Build full prompt
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        # Create run record
        run = OracleRun(
            run_id=f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
            started_at=time.time(),
            model=self.model,
            prompt_chars=len(full_prompt),
        )

        # Prepare output file
        out_file = None
        if save_to_disk:
            out_path = self.session_dir / f"oracle_{run.run_id}.txt"
            run.output_path = str(out_path)
            out_file = open(out_path, "w", encoding="utf-8")

            # Write metadata header
            out_file.write(f"# Oracle Run: {run.run_id}\n")
            out_file.write(f"# Model: {self.model}\n")
            out_file.write(f"# Timestamp: {datetime.now(timezone.utc).isoformat()}Z\n")
            out_file.write(f"# Temperature: {temperature}\n")
            out_file.write("# ---\n\n")

        # Build API payload
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_tokens,
            },
        }

        url = f"{self.base_url}/api/generate"

        try:
            response = self._http.post(
                url,
                json=payload,
                stream=stream,
                timeout=self.timeout_s,
            )
            response.raise_for_status()

            if stream:
                # Stream response, accumulate in memory with bounded buffer
                output_chunks = []
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        chunk = obj.get("response", "")
                        if chunk:
                            output_chunks.append(chunk)
                            run.output_chars += len(chunk)
                            if out_file:
                                out_file.write(chunk)
                                out_file.flush()
                        if obj.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

                output_text = "".join(output_chunks)
            else:
                # Non-streaming: single JSON response
                data = response.json()
                output_text = data.get("response", "")
                run.output_chars = len(output_text)
                if out_file:
                    out_file.write(output_text)

            run.completed = True

        except requests.exceptions.Timeout:
            raise RuntimeError(f"Ollama generation timed out after {self.timeout_s}s")
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Cannot connect to Ollama at {self.base_url}: {e}")
        finally:
            if out_file:
                out_file.write("\n\n# --- END ---\n")
                out_file.close()

            # Add run to history (bounded)
            self._runs.append(run)
            if len(self._runs) > self._max_runs:
                self._runs = self._runs[-self._max_runs:]

        return output_text.strip()

    def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.8,
        top_p: float = 0.95,
        top_k: int = 40,
        max_tokens: int = 200,
    ) -> Iterator[str]:
        """
        Generate text with streaming iterator (for real-time display).

        Yields chunks as they arrive. Caller is responsible for
        accumulating if full text is needed.

        Use this for live oracle sessions where you want to see
        output as it generates.
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_tokens,
            },
        }

        url = f"{self.base_url}/api/generate"
        response = self._http.post(url, json=payload, stream=True, timeout=self.timeout_s)
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
                chunk = obj.get("response", "")
                if chunk:
                    yield chunk
                if obj.get("done"):
                    break
            except json.JSONDecodeError:
                continue

    def check_connection(self) -> bool:
        """Verify connection to Ollama and model availability."""
        try:
            response = self._http.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            # Check if our model is available
            available_models = [m.get("name", "") for m in data.get("models", [])]
            model_base = self.model.split(":")[0]

            return any(model_base in m for m in available_models)

        except Exception as e:
            print(f"Connection check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available models on the Ollama server."""
        try:
            response = self._http.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            return []

    def get_run_history(self) -> List[OracleRun]:
        """Get recent run history (last 100 runs)."""
        return self._runs.copy()

    def cleanup(self):
        """Close HTTP session."""
        self._http.close()


def main():
    """Test HTTP connection to studio Ollama."""
    print("=" * 60)
    print("Oracle Client - HTTP API Test")
    print("=" * 60)
    print()

    # Try LAN first, then Tailscale
    for use_tailscale in [False, True]:
        label = "Tailscale" if use_tailscale else "LAN"
        print(f"Testing {label} connection...")

        client = OllamaClient(use_tailscale=use_tailscale)

        if client.check_connection():
            print(f"  {label}: {client.base_url}")
            print(f"  Model: {client.model}")
            print()

            # List models
            models = client.list_models()
            print(f"Available models ({len(models)}):")
            for m in models[:5]:
                print(f"  - {m}")
            if len(models) > 5:
                print(f"  ... and {len(models) - 5} more")
            print()

            # Test generation
            print("Testing generation (streaming to disk)...")
            start = time.time()
            output = client.generate(
                prompt="What is entropy in exactly two sentences?",
                temperature=0.8,
                max_tokens=100,
                save_to_disk=True,
            )
            elapsed = time.time() - start

            print(f"Generated ({elapsed:.2f}s):")
            print("-" * 40)
            print(output[:500] + ("..." if len(output) > 500 else ""))
            print("-" * 40)
            print()

            # Show run info
            runs = client.get_run_history()
            if runs:
                last_run = runs[-1]
                print(f"Run ID: {last_run.run_id}")
                print(f"Output saved to: {last_run.output_path}")
                print(f"Chars generated: {last_run.output_chars}")
            print()

            client.cleanup()
            print("Connection test: PASSED")
            return

        print(f"  {label} failed, trying next...")
        print()

    print("Connection test: FAILED")
    print("Cannot reach Ollama on Studio via LAN or Tailscale")


if __name__ == "__main__":
    main()
