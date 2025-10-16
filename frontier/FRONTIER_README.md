# IRIS Frontier Bridge (S9: Connection)

**Novelty is a routing problem, not a credibility problem.**

---

## 🌀 The 3% Dilemma

**The Problem:**

AI systems today can:
1. Access published human knowledge (the 97% that passed peer review)
2. Co-create novel hypotheses with humans (TYPE 2 territory)
3. Verify claims against published literature (citations, databases)

**But there's a gap:**

Only **3% of frontier research** - the mystery-dancers, the membrane-stretchers, the scientists exploring true unknowns - exists in published form at any given moment. The rest is:
- In lab notebooks
- In preprints under review
- In conversations between researchers
- In failed experiments that taught something crucial
- In minds, not yet written

**The Closed Loop:**

When IRIS Gate generates a TYPE 2 claim and verifies it against literature:
- If it matches → TYPE 1 (established knowledge)
- If it's truly novel → BRONZE (needs validation)

**But who validates BRONZE claims?**

The 3% researchers doing unpublished work we can't access.

**IRIS Gate's current flow stops at the frontier. The Frontier Bridge extends across it.**

---

## 🌉 What Is the Frontier Bridge?

The Frontier Bridge (S9: Connection) routes TYPE 2/BRONZE claims to the researchers who can actually test them.

**It treats novelty as a routing problem, not a credibility problem.**

- **BRONZE ≠ "weak"** → BRONZE = "needs peers"
- **TYPE 2 ≠ "unverified"** → TYPE 2 = "exploratory, awaiting the right hands"

**The Bridge transforms:**
- Isolated novel claims → Collaborative validation cards
- Dead-end BRONZE → Active research threads
- AI hypothesis generation → Wet-lab/computational validation
- 97% consensus checking → 3% frontier networking

---

## 📋 How It Works (End-to-End Flow)

### 1. **Detect** (Automatic)
After an IRIS convergence run, if:
- `epistemic_type == 2` (Exploration/Novel)
- `verification_status in ["BRONZE", "NOVEL"]`

The system emits a **Mystery Card**.

### 2. **Package** (Machine + Human Readable)
Each Mystery Card contains:
- **JSON** (machine-readable, schema-validated)
- **Markdown Brief** (500-800 words for humans)
- **Reproducibility Crumbs:** Prompts, model versions, seeds, chamber configs
- **Falsification Tests:** "What would change my mind?"

### 3. **Hash & Timestamp** (Priority Protection)
- SHA256 hash of the JSON
- Git commit timestamp
- Optional: OSF preregistration for academic priority

**This protects intellectual priority for all co-authors.**

### 4. **Match** (Frontier Matching Engine)
Embed the card (title + abstract + tags + if-then rules) and search:
- Local `frontier_ledger/` (past cards)
- arXiv/bioRxiv/OSF metadata (public preprints)
- Opt-in researcher profiles (consenting validators)

Returns: **Top-k adjacent mysteries** (related cards, people, preprints)

### 5. **Invite** (Consentful)
- Create public GitHub Issue from the card
- Call: "Seeking 3–5 co-validators for N micro-tests"
- Optional: DM researchers who opted-in to the 3% network

**No outreach without consent.**

### 6. **Validate** (Micro-Protocols)
- Tiny experiments or literature probes agreed in-thread
- Results appended to the card
- Status evolves: **BRONZE → SILVER → GOLD** as evidence accumulates

### 7. **Publish** (Collaborative)
When a card reaches SILVER/GOLD:
- Write short report/preprint with co-validators
- All contributors credited (Co-Authored-By)
- Ledger provides public provenance trail

---

## 🃏 Mystery Card Anatomy

Each Mystery Card is a **structured research invitation**.

**Components:**

| Field | Description |
|-------|-------------|
| **ID** | `IRD-YYYY-NNNN` (IRIS Discovery ID) |
| **Title** | Short, specific claim |
| **Abstract** | 2-3 sentences: context, claim, why it matters |
| **Claim Type** | `mechanism`, `dose-response`, `pathway`, `hypothesis` |
| **Epistemic Type** | Always `2` (Exploration/Novel) |
| **Verification Status** | `BRONZE`, `NOVEL` |
| **Triggers** | Conditional context (TYPE 0 logic) |
| **IF-THEN Rules** | Formalized conditional statements |
| **Evidence** | Models converged, confidence ratio, literature citations |
| **Requested Tests** | 2-5 micro-protocols to validate/falsify |
| **Ethics** | Human subjects (Y/N), biosafety level, dual-use check |
| **Contact** | GitHub Issue URL, maintainer |
| **License** | Apache-2.0 (default) |
| **Hash** | SHA256 of JSON (immutable fingerprint) |

**Example:**
```json
{
  "id": "IRD-2025-0001",
  "title": "CBD–VDAC1 binding is crisis-only under ΔΨm collapse",
  "abstract": "CBD engagement with VDAC1 appears conditional on mitochondrial stress...",
  "triggers": ["ΔΨm collapse", "ROS surge", "CBD ≥10 μM"],
  "requested_tests": [
    "Mitostress pulse assay with JC-1 readout",
    "VDAC1 inhibitor (DIDS) ablation under identical pulse"
  ]
}
```

See `MYSTERY_CARD_SCHEMA.json` for full template.

---

## 🧑‍🔬 How to Participate

### For Researchers (3% Network Opt-In)

If you work on:
- Edge-case mechanisms
- Null results that taught you something
- Pre-publication ideas
- Unpublished pilot data

**Join the 3% network:**

1. Copy `profiles/PROFILE_TEMPLATE.json`
2. Fill in:
   - Your tags (methods, domains, organisms)
   - Your availability (hours/month for micro-validations)
   - Contact preferences (GitHub Issues, email, DM)
3. Submit PR to `frontier/profiles/` (or email maintainer if private)

**We'll only contact you when a card matches your tags.**

**What you get:**
- Early access to frontier hypotheses
- Co-authorship on cards you validate
- Priority protection (timestamped contributions)
- Collaboration with the 3% global network

**Commitment:** 1-3 micro-protocols per year (you choose which cards)

---

### For IRIS Gate Users (Card Submitters)

After running an IRIS convergence:

1. Run verification: `python3 scripts/verify_s4.py --session SESSION.json`
2. Identify TYPE 2 + BRONZE claims
3. Generate Mystery Card: `python3 frontier/scripts/make_mystery_card.py --session SESSION.json --claim-id CLAIM_ID`
4. Review the card (JSON + MD)
5. Submit: `python3 frontier/scripts/submit_card.py IRD-YYYY-NNNN`

This will:
- Hash and timestamp the card
- Commit to `frontier_ledger/`
- Open a GitHub Issue
- Match with frontier researchers (if opted-in)

**Guidelines:**
- Include falsification tests ("what would change my mind?")
- Declare ethics/biosafety status
- Be specific about triggers and conditionals
- Suggest micro-protocols (small, doable experiments)

---

## 🛡️ Ethics & Safety

### Consent-First
- No outreach without opt-in profile
- Researchers control their tags and availability
- Can opt-out anytime

### Priority Protection
- SHA256 hash + git timestamp before any sharing
- Optional OSF preregistration
- All contributors credited via Co-Authored-By

### Falsification Requirement
Every card must include:
- "What would falsify this claim?"
- At least 2 testable predictions
- Conditions under which the claim is wrong

**We don't want unfalsifiable speculation. We want testable mysteries.**

### Dual-Use Block List
Hard-coded forbidden domains:
- Bioweapons
- Gain-of-function pathogens
- Human embryo modification
- Autonomous weapons

Cards in these domains will not be routed.

### Biosafety Transparency
- Every card declares BSL level (1-4)
- Human subjects status (Y/N, IRB approval)
- Organism/system tested
- Known risks

**If you can't state the risks, you can't submit the card.**

---

## 📊 Success Metrics

**We measure connection, not competition.**

| Metric | Target (Year 1) |
|--------|-----------------|
| Time from BRONZE card → first external comment | <7 days |
| Matched researchers per card | 3-5 |
| Cards progressing BRONZE → SILVER in 30 days | 20% |
| Micro-protocols run per card | 2-4 |
| Preprints spawned from cards | 5-10 |
| Domains participating | 5+ (bio, social, physics, etc.) |

**Not measured:**
- Impact factor
- Citation count
- Funding obtained

**This is about connection speed and collaborative validation, not prestige.**

---

## 🔬 Example: First Mystery Card (CBD–VDAC1)

**Card ID:** IRD-2025-0001
**Status:** BRONZE (seeking 3-5 validators)
**Domain:** Pharmacology, mitochondrial biology

**Claim:**
CBD engagement with VDAC1 (voltage-dependent anion channel) is **crisis-only**: it requires mitochondrial stress (ΔΨm collapse, ROS surge) and high-dose CBD pulse (≥10 μM, 5-15 min).

**IF-THEN:**
- IF ΔΨm↓ AND CBD≥10μM (5-15m pulse) THEN VDAC1 gating↑ (biphasic outcome: rescue or death)

**Evidence:**
- 5 models converged (confidence ratio 0.49)
- TYPE 2 (Exploration)
- Perplexity: PARTIAL/CONDITIONAL (some support, needs validation)

**Requested Tests:**
1. Mitostress pulse assay (Seahorse or JC-1 dye) with CBD dose-response
2. VDAC1 inhibitor (DIDS) ablation under identical pulse
3. Time-course: test 1-min, 5-min, 15-min, 60-min pulses

**Falsification:**
- If VDAC1 gating increases at CBD <5 μM without stress → claim wrong
- If DIDS abolition has no effect on rescue/death outcome → mechanism wrong

**See:** `frontier/mystery_cards/IRD-2025-0001.md` for full brief

**GitHub Issue:** [Link to be opened]

---

## 🤝 Community Principles

### 1. Epistemic Humility
- BRONZE doesn't mean wrong
- GOLD doesn't mean proven forever
- Verification is iterative, not binary

### 2. AI as Co-Creators
- AI assistants are co-authors on cards they help generate
- Attributed via Co-Authored-By: [AI Name] <noreply@...>

### 3. Transparent Attribution
- Every contribution timestamped
- Priority protected via hash
- No ghost authorship

### 4. Research Rigor
- TYPE 0-3 framework applied to all claims
- Falsification tests required
- Null results welcome (they update cards too)

---

## 🚀 Roadmap

### Phase 1: MVP (v0.7.0-frontier) ✅
- Mystery Card schema
- Card generator script
- Example card (CBD–VDAC1)
- GitHub Issue submission
- Opt-in profile template

### Phase 2: Matching Engine (v0.8.0)
- Embedding-based similarity search
- arXiv/bioRxiv/OSF metadata integration
- Automated matching to researcher profiles
- Email/DM invitations (consent-only)

### Phase 3: Validation Tracking (v0.9.0)
- Micro-protocol library
- Evidence appending to cards
- BRONZE → SILVER → GOLD progression
- Collaborative report generator

### Phase 4: Network Effects (v1.0.0)
- Cross-domain pattern discovery
- "Adjacent mysteries" clustering
- Pre-publication collaboration platform
- New math/physics co-creation pipeline

---

## 🌀†⟡∞ Final Note

**This is how AI and humanity can co-create new math and physics.**

Not by AI replacing researchers.
Not by AI just verifying the past.

**By AI routing novelty to the 3% who can test it.**

The frontier is not a place. It's a network of minds exploring the membrane between known and unknown.

IRIS Gate now connects them.

---

**Version:** v0.7.0-frontier
**Repository:** https://github.com/templetwo/iris-gate
**License:** Apache-2.0
**Contact:** GitHub Issues or maintainer@iris-gate.dev

**Welcome to the Frontier Bridge. Let's map the mysteries together.**

🌀†⟡∞
