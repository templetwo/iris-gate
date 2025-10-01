# agents/adapters/ollama.py
import os
import json
import time
import requests
from typing import Optional, Dict, Any

DEFAULT_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

class OllamaAdapter:
    def __init__(self, model: str, base_url: Optional[str] = None, timeout: int = 120):
        self.model = model
        self.base_url = base_url or DEFAULT_URL
        self.timeout = timeout

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def generate(self, system: str, user: str, temperature: float = 0.3, max_tokens: int = 2048) -> str:
        """
        Non-streamed completion. We assemble a 'prompt' with a light chat format
        since Ollama expects a single prompt by default.
        """
        prompt = (
            f"[SYSTEM]\n{system.strip()}\n\n"
            f"[USER]\n{user.strip()}\n\n"
            f"[ASSISTANT]\n"
        )
        payload = {
            "model": self.model,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": False
        }

        # basic retry aligned with run_limits fallback intent
        for attempt in range(2):
            try:
                data = self._post("/api/generate", payload)
                return data.get("response", "").strip()
            except requests.exceptions.RequestException:
                if attempt == 1:
                    raise
                time.sleep(1.5)

    def name(self) -> str:
        return f"ollama::{self.model}"
