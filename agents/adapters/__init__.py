# agents/adapters/__init__.py
# Note: Ollama adapter disabled for cloud-only mode
# from .ollama import OllamaAdapter

ADAPTERS = {
    # "ollama": OllamaAdapter,  # Disabled for cloud-only mode
}

__all__ = ["ADAPTERS"]
