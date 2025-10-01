# agents/adapters/__init__.py
from .ollama import OllamaAdapter

ADAPTERS = {
    "ollama": OllamaAdapter,
}

__all__ = ["OllamaAdapter", "ADAPTERS"]
