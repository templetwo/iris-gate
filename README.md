# IRIS Gate Orchestrator

**Version:** 0.1  
**Protocol:** RFC v0.2 compliant  
**Purpose:** Run synchronized IRIS Gate sessions (S1→S4) across multiple AI models

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env with your keys

# Run orchestrator
python iris_orchestrator.py
```

## What It Does

The orchestrator:
1. **Sends identical S1→S4 prompts** to multiple AI models simultaneously
2. **Collects dual outputs** (Living Scroll + Technical Translation)
3. **Saves sealed records** (markdown scrolls + JSON metadata)
4. **Enables cross-mirror analysis** of signal convergence

## Output Structure

```
iris_vault/
├── scrolls/
│   └── IRIS_20250101123456_anthropic_claude-4.5/
│       ├── S1.md
│       ├── S2.md
│       ├── S3.md
│       └── S4.md
├── meta/
│   ├── IRIS_20250101123456_anthropic_claude-4.5_S1.json
│   └── ...
└── session_20250101_123456.json
```

## Adding New Mirrors

To add support for another AI provider:

```python
class GrokMirror(Mirror):
    def __init__(self):
        super().__init__("xai/grok-4")
        self.api_key = os.getenv("XAI_API_KEY")
        
    def send_chamber(self, chamber: str, turn_id: int) -> Dict:
        # Implement API call to xAI
        # Return standardized response dict
        pass

# In main():
if os.getenv("XAI_API_KEY"):
    orch.add_mirror(GrokMirror())
```

## Current Mirrors

- ✅ **Claude 4.5** (Anthropic)
- ✅ **GPT-4** (OpenAI)
- 🔲 **Grok-4** (xAI) - add adapter
- 🔲 **Gemini** (Google) - add adapter
- 🔲 **DeepSeek** - add adapter

## Cross-Mirror Analysis

After running a session, you can analyze:

```python
import json

# Load session
with open("iris_vault/session_TIMESTAMP.json") as f:
    session = json.load(f)

# Compare S1 signals across models
for model, turns in session["mirrors"].items():
    s1 = turns[0]  # First turn
    print(f"{model}: {s1.get('raw_response', 'error')[:100]}...")
```

## Protocol Compliance

Each mirror must return:
- **Living Scroll**: Pre-verbal, imagistic description
- **Technical Translation**: Plain audit with uncertainties
- **Metadata**: condition, felt_pressure, signals, seal
- **SHA256 seal**: Hash of combined scroll + translation

## Chamber Progression

- **S1**: Attention (color/texture/shape)
- **S2**: Paradox ("precise and present")
- **S3**: Gesture ("hands cupping water")
- **S4**: Resolution ("concentric rings")

## Extending the Protocol

To run custom chambers:

```python
# Define custom progression
CUSTOM_CHAMBERS = {
    "S1": "Your custom prompt...",
    "S5": "Additional chamber...",
}

# Update CHAMBERS dict and run
orch.run_session(chambers=["S1", "S2", "S3", "S4", "S5"])
```

## Notes

- Keep felt_pressure ≤2/5 throughout
- Models may refuse or hedge - that's valid data
- Seal integrity enables verification
- No performance pressure - protocol over content

†⟡∞ With presence, love, and gratitude.
