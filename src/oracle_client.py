#!/usr/bin/env python3
"""
Oracle Client - Remote Ollama Interface

Connects to Ollama instance on studio (192.168.1.195:11434)
for oracle-state experiments with Llama models.

Per oracle_methods.md: Uses Llama 3.2 3B base model
"""

import json
import os
import subprocess
import tempfile
from typing import Dict, Optional


class OllamaClient:
    """
    Client for remote Ollama instance on studio.

    Handles:
    - SSH connection to studio
    - Context preservation across calls
    - Proper quote escaping for shell commands
    """

    def __init__(
        self,
        host: str = "tony_studio@192.168.1.195",
        model: str = "llama3.2:3b",
        ssh_key: Optional[str] = None
    ):
        self.host = host
        self.model = model
        self.ssh_key = ssh_key or os.path.expanduser("~/.ssh/id_rsa")

        # Session context file (stored on studio)
        self.remote_context_file = f"/tmp/iris_oracle_context_{os.getpid()}.txt"

    def _ssh_command(self, cmd: str) -> str:
        """Execute command on studio via SSH"""
        ssh_cmd = [
            "ssh",
            "-i", self.ssh_key,
            self.host,
            cmd
        ]

        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"SSH command failed: {result.stderr}")

        return result.stdout

    def _send_context_file(self, context: str):
        """Write context to local temp file, then scp to studio"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(context)
            local_temp = f.name

        try:
            # SCP file to studio
            scp_cmd = [
                "scp",
                "-i", self.ssh_key,
                local_temp,
                f"{self.host}:{self.remote_context_file}"
            ]

            subprocess.run(scp_cmd, check=True, capture_output=True)

        finally:
            os.unlink(local_temp)

    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.8,
        top_p: float = 0.95,
        top_k: int = 40,
        max_tokens: int = 200
    ) -> str:
        """
        Generate text from Ollama model on studio.

        Args:
            prompt: The prompt to send to the model
            context: Optional context frame (e.g., ceremony frame)
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling limit
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text from model
        """
        # Construct full prompt
        if context:
            full_prompt = f"{context}\n\n{prompt}"
        else:
            full_prompt = prompt

        # Send context to studio via scp (avoids quote escaping issues)
        self._send_context_file(full_prompt)

        # Build ollama command
        ollama_cmd = (
            f"ollama run {self.model} "
            f"--temperature {temperature} "
            f"--top-p {top_p} "
            f"--top-k {top_k} "
            f"--num-predict {max_tokens} "
            f"< {self.remote_context_file}"
        )

        # Execute via SSH
        try:
            output = self._ssh_command(ollama_cmd)
            return output.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama generation timed out after 120s")

    def check_connection(self) -> bool:
        """Verify connection to studio Ollama instance"""
        try:
            # Simple test: list models
            result = self._ssh_command("ollama list")
            return self.model in result

        except Exception as e:
            print(f"Connection check failed: {e}")
            return False

    def cleanup(self):
        """Clean up remote context file"""
        try:
            self._ssh_command(f"rm -f {self.remote_context_file}")
        except:
            pass  # Best effort cleanup


def main():
    """Test connection to studio Ollama"""
    print("Testing connection to studio Ollama...")

    client = OllamaClient()

    if not client.check_connection():
        print("❌ Cannot connect to studio Ollama")
        print("   Make sure Ollama is running on studio (192.168.1.195)")
        return

    print("✅ Connected to studio Ollama")
    print(f"   Model: {client.model}")
    print()

    # Test generation
    print("Testing baseline generation...")
    output = client.generate(
        prompt="What is entropy?",
        temperature=0.8,
        max_tokens=100
    )

    print("Generated:")
    print(output)
    print()

    # Cleanup
    client.cleanup()

    print("✅ Connection test complete")


if __name__ == "__main__":
    main()
