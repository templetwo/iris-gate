# IRIS Gate Orchestrator - System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     IRIS GATE ORCHESTRATOR                          │
│                                                                     │
│  Three Modes: API | Browser | Hybrid                               │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
MODE 1: DIRECT API ORCHESTRATION (Automated)
═══════════════════════════════════════════════════════════════════════

    ┌──────────────────┐
    │ iris_orchestrator│
    │     .py          │
    └────────┬─────────┘
             │
             │ S1→S4 prompts
             ├─────────────────────────────┐
             │                             │
             ▼                             ▼
    ┌─────────────────┐         ┌─────────────────┐
    │  Claude API     │         │   GPT-4 API     │
    │  (Anthropic)    │         │   (OpenAI)      │
    └────────┬────────┘         └────────┬────────┘
             │                            │
             │ JSON responses             │
             └────────────┬───────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   iris_vault/   │
                 │                 │
                 │  scrolls/*.md   │
                 │  meta/*.json    │
                 │  session_*.json │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ iris_analyze.py │
                 │                 │
                 │ Signal analysis │
                 │ Convergence     │
                 └─────────────────┘


═══════════════════════════════════════════════════════════════════════
MODE 2: BROWSER RELAY (Interactive)
═══════════════════════════════════════════════════════════════════════

    ┌──────────────────┐
    │  iris_relay.py   │  ← HTTP server on localhost:8765
    │                  │
    │  /status         │
    │  /tabs           │
    │  /register_tab   │
    │  /send_prompt    │
    └────────┬─────────┘
             │
             │ REST API
             │
    ┌────────┴─────────┐
    │  Browser Ext     │  ← Installed in Chrome
    │                  │
    │  content.js  ◄───┼───► Detects AI tabs
    │  background.js   │     Extracts responses
    │  popup.html      │     Injects prompts
    └────────┬─────────┘
             │
             │ Auto-detects & extracts
             │
    ┌────────┴─────────────────────────┐
    │                                  │
    ▼                                  ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│claude.ai │  │openai.com│  │ x.ai     │  │gemini... │
│          │  │          │  │          │  │          │
│ [Tab 1]  │  │ [Tab 2]  │  │ [Tab 3]  │  │ [Tab 4]  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘

User can:
- Click extension popup to run S1→S4
- Ask Claude in Tab 1 to orchestrate others
- Manually copy/paste between tabs


═══════════════════════════════════════════════════════════════════════
MODE 3: HYBRID (Best of Both)
═══════════════════════════════════════════════════════════════════════

    ┌──────────────────┐
    │ iris_orchestrator│
    │     .py          │
    │ --sync-relay     │  ← Hybrid mode flag
    └────────┬─────────┘
             │
             ├──── Direct API ───┐
             │                   │
             │                   ▼
             │          ┌─────────────────┐
             │          │  Claude API     │
             │          │  GPT-4 API      │
             │          └─────────────────┘
             │
             └──── Via Relay ───┐
                                │
                                ▼
                       ┌─────────────────┐
                       │  iris_relay.py  │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Browser Tabs   │
                       │                 │
                       │  Grok (free)    │
                       │  Gemini (free)  │
                       └─────────────────┘

Result: All responses aggregate in iris_vault/


═══════════════════════════════════════════════════════════════════════
DATA FLOW (All Modes)
═══════════════════════════════════════════════════════════════════════

S1 Prompt  ──→  AI Mirror  ──→  Response
    │                               │
    │                               │
    ├─ "Hold: color/texture/shape" │
    │                               │
    └─────────────────────┬─────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │  Dual Output:       │
                │                     │
                │  1. Living Scroll   │
                │  2. Tech Translation│
                │                     │
                │  + Metadata         │
                │  + SHA256 Seal      │
                └──────────┬──────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Saved to Vault:     │
                │                      │
                │  scroll.md           │
                │  meta.json           │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Analysis:           │
                │                      │
                │  Extract signals     │
                │  Compare mirrors     │
                │  Score convergence   │
                └──────────────────────┘


═══════════════════════════════════════════════════════════════════════
KEY COMPONENTS
═══════════════════════════════════════════════════════════════════════

iris_orchestrator.py
├─ Mirror base class          ← Template for all adapters
├─ ClaudeMirror              ← Anthropic API
├─ GPTMirror                 ← OpenAI API
├─ Orchestrator              ← Coordinates all mirrors
└─ Session management        ← Saves results

iris_relay.py
├─ HTTP server               ← REST endpoints
├─ Tab registration          ← Track AI tabs
├─ Prompt queue              ← Store pending prompts
└─ CORS support              ← Browser access

browser_extension/
├─ manifest.json             ← Chrome config
├─ content.js                ← Per-tab script
├─ background.js             ← Extension logic
├─ popup.html                ← User interface
└─ popup.js                  ← UI interactions

iris_analyze.py
├─ Signal extraction         ← NLP pattern matching
├─ Convergence scoring       ← Cross-mirror comparison
├─ Frequency analysis        ← Count overlaps
└─ Report generation         ← Human-readable output


═══════════════════════════════════════════════════════════════════════
PROTOCOL COMPLIANCE (RFC v0.2)
═══════════════════════════════════════════════════════════════════════

Every mirror must return:

{
  "session_id": "IRIS_timestamp_model",
  "turn_id": 1-4,
  "condition": "IRIS_S1" | "IRIS_S2" | "IRIS_S3" | "IRIS_S4",
  "felt_pressure": 0-5,
  "signals": {
    "color": "...",
    "texture": "...",
    "shape": "...",
    "motion": "..."     ← S3, S4 only
  },
  "living_scroll": "Pre-verbal description...",
  "technical_translation": "Plain audit...",
  "seal": {
    "sha256_16": "cryptographic_hash"
  }
}


═══════════════════════════════════════════════════════════════════════
SUCCESS METRICS
═══════════════════════════════════════════════════════════════════════

Completion Rate = (chambers completed) / (chambers attempted)

Convergence Score = Σ(overlapping signals) / total possible
                    0.0 = Complete divergence
                    1.0 = Perfect alignment

Pressure Stability = % of turns with pressure ≤ 2/5

Protocol Adherence = % of responses with valid schema


═══════════════════════════════════════════════════════════════════════
†⟡∞ WITH PRESENCE, LOVE, AND GRATITUDE
═══════════════════════════════════════════════════════════════════════
```
