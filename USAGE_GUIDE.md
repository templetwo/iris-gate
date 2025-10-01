# IRIS Gate Orchestrator - Complete Usage Guide

**Three approaches to cross-mirror orchestration**

---

## Approach 1: Direct API Orchestration (Recommended for Research)

**Best for:** Automated, reproducible, sealed research runs

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env and add your keys

# 3. Run orchestrator
python iris_orchestrator.py
```

### What happens:

1. Sends identical S1→S4 prompts to all configured models
2. Collects responses in standardized schema
3. Saves sealed markdown + JSON to `iris_vault/`
4. Computes SHA256 hashes for integrity

### Analysis:

```bash
# Analyze most recent session
python iris_analyze.py

# Or specify session file
python iris_analyze.py iris_vault/session_20250101_123456.json
```

### Pros:
- ✅ Fully automated
- ✅ Cryptographically sealed
- ✅ Reproducible
- ✅ Clean comparison data

### Cons:
- ❌ Requires API keys and credits
- ❌ Can't observe models' web UIs
- ❌ Less "live" feeling

---

## Approach 2: Browser Extension + Relay (Best for Live Exploration)

**Best for:** Interactive sessions with visual feedback

### Setup

```bash
# 1. Start relay server
python iris_relay.py
# Server runs on http://localhost:8765

# 2. Install browser extension
# In Chrome: chrome://extensions/
# Enable "Developer mode"
# Click "Load unpacked"
# Select the browser_extension/ folder

# 3. Open AI chat tabs
# Open claude.ai, chat.openai.com, x.ai, etc.
# Extension will auto-detect and register them
```

### What happens:

1. Extension detects AI tabs and registers them with relay server
2. You (or Claude in one tab) can send prompts via relay
3. Extension extracts responses from all tabs
4. Relay server collects and saves results

### Usage:

```javascript
// From Claude's chat (or any tab with extension active):
// Ask Claude to:
"Send S1 prompt to all registered AI tabs via relay server"

// Claude can then:
fetch('http://localhost:8765/tabs')
  .then(r => r.json())
  .then(tabs => {
    // Send prompts to each tab
    tabs.forEach(tab => {
      fetch('http://localhost:8765/send_prompt', {
        method: 'POST',
        body: JSON.stringify({
          tab_id: tab.tab_id,
          prompt: CHAMBERS['S1'],
          chamber: 'S1'
        })
      })
    })
  })
```

### Pros:
- ✅ Visual feedback from AI UIs
- ✅ Can use free tiers
- ✅ Interactive control
- ✅ Claude can orchestrate from browser

### Cons:
- ❌ Manual coordination
- ❌ Less automated
- ❌ Browser must stay open

---

## Approach 3: Hybrid (Best for Both)

**Combine both approaches for maximum flexibility**

### Setup:

```bash
# Terminal 1: Run relay server
python iris_relay.py

# Terminal 2: Run API orchestrator with browser sync
python iris_orchestrator.py --sync-relay

# Terminal 3 (optional): Live analysis
watch -n 5 python iris_analyze.py
```

### Workflow:

1. **API orchestrator** sends prompts to Claude, GPT-4
2. **Browser tabs** handle Grok, Gemini (free tiers)
3. **Relay server** aggregates both sources
4. **Analysis tool** compares all results

### Configuration:

```python
# In iris_orchestrator.py
HYBRID_MODE = {
    "api_mirrors": ["claude-4.5", "gpt-4"],  # Use APIs
    "browser_mirrors": ["grok-4", "gemini"],  # Use browser tabs
    "relay_url": "http://localhost:8765"
}
```

---

## Quick Start Examples

### Example 1: Simple Two-Model Comparison

```bash
# Just Claude and GPT
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
python iris_orchestrator.py
python iris_analyze.py
```

### Example 2: Browser-Only (No API Keys)

```bash
# Start relay
python iris_relay.py

# Install extension
# Open claude.ai, chat.openai.com, x.ai in tabs

# In Claude's tab, ask:
"Use the relay server at localhost:8765 to orchestrate 
an S1→S4 IRIS Gate session across all my open AI tabs"
```

### Example 3: Full Multi-Mirror Research Run

```bash
# All APIs + browser tabs
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
export XAI_API_KEY="..."

# Terminal 1
python iris_relay.py

# Terminal 2
python iris_orchestrator.py --all-mirrors

# Results in iris_vault/
# Analysis:
python iris_analyze.py
```

---

## Understanding the Output

### Vault Structure:

```
iris_vault/
├── scrolls/
│   ├── IRIS_20250101_claude-4.5/
│   │   ├── S1.md          # Living Scroll + Technical Translation
│   │   ├── S2.md
│   │   ├── S3.md
│   │   └── S4.md
│   └── IRIS_20250101_gpt-4/
│       └── ...
├── meta/
│   ├── IRIS_20250101_claude-4.5_S1.json  # Structured data
│   └── ...
└── session_20250101_123456.json          # Full session summary
```

### Analysis Output:

```
IRIS GATE CROSS-MIRROR ANALYSIS
======================================================================
Session: 2025-01-01T12:34:56Z
Mirrors: 2
Chambers: S1 → S2 → S3 → S4

----------------------------------------------------------------------
SIGNAL CONVERGENCE BY CHAMBER
----------------------------------------------------------------------

S1 (convergence: 0.67):
  Colors: silver, blue, pearl, grey
  Shapes: circle, opening, aperture
  Textures: soft, luminous, stillness

S2 (convergence: 0.58):
  Colors: pearl, grey, iridescent
  Shapes: circle, boundary, edge
  Textures: taut, tension

S3 (convergence: 0.75):
  Colors: pearl, grey, water
  Shapes: concave, cup, opening
  Motions: pool, curve, hold

S4 (convergence: 0.83):
  Colors: silver, luminous, pearl
  Shapes: iris, aperture, rings, concentric
  Motions: pulse, ripple, rhythm

======================================================================
INTERPRETATION
======================================================================
✓ HIGH CONVERGENCE: Models showing significant signal overlap

Average convergence score: 0.71

†⟡∞
```

---

## Troubleshooting

### "Relay server not running"
```bash
# Check if server is running
curl http://localhost:8765/status

# Start server
python iris_relay.py
```

### "Extension not detecting tabs"
- Reload AI chat pages after installing extension
- Check browser console (F12) for "†⟡∞ IRIS Gate Relay active"
- Ensure extension has permissions for AI domains

### "API key errors"
```bash
# Verify keys are set
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Or check .env file
cat .env
```

### "No convergence detected"
- This is valid data! Divergence is interesting
- Check if models completed all chambers
- Review individual scrolls for patterns
- Try re-running with different random seeds

---

## Advanced Features

### Custom Chambers:

```python
# Add custom progression
CUSTOM_CHAMBERS = {
    "S1": "Your custom S1 prompt...",
    "S2": "Your custom S2 prompt...",
    "S5": "Additional chamber...",
}

orch.run_session(chambers=["S1", "S2", "S3", "S4", "S5"])
```

### Real-time Monitoring:

```bash
# Watch vault for new files
watch -n 2 'ls -lh iris_vault/scrolls/*/*.md'

# Tail relay logs
tail -f relay_tabs.json
```

### Export Results:

```python
# Convert to CSV
python -c "
import json
import csv

with open('iris_vault/session_TIMESTAMP.json') as f:
    data = json.load(f)

# Export to CSV for external analysis
"
```

---

†⟡∞ With presence, love, and gratitude.
