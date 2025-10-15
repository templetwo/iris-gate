# IRIS Gate - Real-Time Verification System

**Version:** 1.0
**Integration:** Perplexity API
**Purpose:** Real-time literature verification for TYPE 2 (VERIFY zone) convergence responses

---

## 🎯 Overview

The Perplexity Verification System integrates real-time literature search into IRIS Gate to **verify factual claims** from AI convergence responses. It's specifically designed for **TYPE 2 (Exploration/Novel)** responses where epistemic confidence is balanced (ratio ~0.49) and claims require verification.

### Architecture

```
IRIS Convergence (5 models)
         ↓
   Epistemic Classification
         ↓
   TYPE 2 detected? → Perplexity Verifier
         ↓
   Real-time literature search
         ↓
   Verification Report
   - SUPPORTED / PARTIALLY_SUPPORTED / NOVEL / CONTRADICTED
   - Citations with dates
   - Confidence assessment
```

---

## 🚀 Quick Start

### 1. Setup

Add your Perplexity API key to `.env`:

```bash
echo "PERPLEXITY_API_KEY=your_key_here" >> .env
```

### 2. Verify a Single S4 Scroll

```bash
python3 scripts/verify_s4.py iris_vault/scrolls/IRIS_20251015_*/S4.md
```

**Output:**
```
================================================================================
VERIFICATION RESULTS
================================================================================

Total Claims: 3
Epistemic Type: 2

Overall Status: ✅ MOSTLY_SUPPORTED

Verification Distribution:
  ✅ SUPPORTED: 2
  🔬 NOVEL: 1
```

### 3. Verify Full Session (Auto-detects TYPE 2)

```bash
python3 scripts/verify_s4.py --session iris_vault/session_20251015_045941.json
```

### 4. Save Verification Report

```bash
python3 scripts/verify_s4.py --session <path> --output verification_report.json
```

---

## 📚 Components

### 1. **agents/verifier.py**

Core verification module with three main classes:

#### `PerplexityAdapter`
- Handles API calls to Perplexity
- Uses `sonar` model with real-time search
- Returns citations with sources

#### `ClaimExtractor`
- Extracts factual claims from S4 responses
- Pattern matching for:
  - Mechanistic statements (X causes Y)
  - Quantitative predictions (50-80% reduction)
  - Relationships (gap junctions enable coupling)
- Detects confidence markers (established, suggests, might)

#### `IRISVerifier`
- Orchestrates extraction + verification
- Queries Perplexity for each claim
- Returns structured verification results

### 2. **scripts/verify_s4.py**

CLI tool for verification with:
- Single scroll verification
- Session-wide verification (auto-detects TYPE 2)
- Verbose mode with full reasoning
- JSON export

---

## 📊 Verification Statuses

### ✅ SUPPORTED
**Meaning:** Claim aligns with current literature
**Confidence:** HIGH
**Example:** "Carbenoxolone blocks gap junctions"
**Response:** TRUST with cited sources

### ⚠️ PARTIALLY_SUPPORTED
**Meaning:** Claim has some support but with caveats
**Confidence:** MODERATE
**Example:** "Carbenoxolone is specific to connexin43"
**Response:** VERIFY nuances, check details

### 🔬 NOVEL
**Meaning:** No direct literature match, exploratory
**Confidence:** LOW
**Example:** "Oscillatory layering in gap junction domains"
**Response:** VERIFY more, potential hypothesis

### ❌ CONTRADICTED
**Meaning:** Claim conflicts with current literature
**Confidence:** HIGH (contradiction)
**Example:** "Carbenoxolone increases coupling"
**Response:** OVERRIDE, investigate discrepancy

---

## 🎓 Usage Examples

### Example 1: Verify CBD Paradox Session

```bash
python3 scripts/verify_s4.py \
  --session iris_vault/session_BIOELECTRIC_CHAMBERED_*.json \
  --verbose \
  --output cbd_verification.json
```

**Use Case:** Verify all TYPE 2 claims from CBD biphasic dose-response exploration

### Example 2: Verify Gap Junction Convergence

```bash
python3 scripts/verify_s4.py \
  iris_vault/scrolls/BIOELECTRIC_CHAMBERED_*/anthropic_claude-sonnet-4.5/S4.md
```

**Use Case:** Check if gap junction mechanism claims are literature-supported

### Example 3: Batch Verify All S4 Scrolls

```bash
for scroll in iris_vault/scrolls/IRIS_*/S4.md; do
  echo "Verifying: $scroll"
  python3 scripts/verify_s4.py "$scroll"
done
```

**Use Case:** Systematic verification of all S4 convergence outputs

---

## 🔧 Integration with Epistemic Map

### TYPE 0 (Crisis/Conditional)
- Ratio: ~1.26
- Guide: **TRUST if trigger present**
- Verification: Not needed (conditional logic)

### TYPE 1 (Facts/Established)
- Ratio: ~1.27
- Guide: **TRUST**
- Verification: Optional (for audit trail)

### TYPE 2 (Exploration/Novel)
- Ratio: ~0.49
- Guide: **VERIFY all claims** ← **Perplexity verification here!**
- Verification: **Recommended** (primary use case)

### TYPE 3 (Speculation/Unknown)
- Ratio: ~0.11
- Guide: **OVERRIDE - human judgment**
- Verification: Not applicable (speculation)

---

## 📖 Output Format

### JSON Structure

```json
{
  "status": "VERIFIED",
  "epistemic_type": 2,
  "total_claims": 3,
  "results": [
    {
      "claim": "Gap junction blockers reduce coupling by 50-80%",
      "status": "SUPPORTED",
      "confidence": "MODERATE",
      "sources": [
        {
          "title": "Oviedo et al. 2008 - Developmental Biology",
          "url": "https://...",
          "snippet": "Carbenoxolone treatment..."
        }
      ],
      "reasoning": "Current research supports claim...",
      "perplexity_response": "..."
    }
  ],
  "summary": {
    "overall_status": "MOSTLY_SUPPORTED",
    "status_distribution": {
      "SUPPORTED": 2,
      "NOVEL": 1
    },
    "confidence_distribution": {
      "MODERATE": 2,
      "LOW": 1
    },
    "high_confidence_supported": 2,
    "novel_claims": 1,
    "contradictions": 0
  },
  "timestamp": "2025-10-15T16:57:16.488498"
}
```

---

## 🧪 Tested Examples

### Test 1: Gap Junction Claim (SUPPORTED)

**Claim:** "Gap junction blockers like carbenoxolone reduce intercellular coupling by 50-80% in planarian cells."

**Result:**
- ✅ **Status:** SUPPORTED
- **Confidence:** MODERATE
- **Sources:** Oviedo et al. (2008), Levin et al. (2012)
- **Caveats:** Off-target effects, variability with concentration/time

### Test 2: CBD Biphasic Fact (SUPPORTED)

**Claim:** "CBD shows biphasic dose-response with low-dose neuroprotection and high-dose cytotoxicity."

**Expected Result:**
- ✅ **Status:** SUPPORTED
- **Confidence:** HIGH
- **Sources:** Multiple recent papers on CBD pharmacology

### Test 3: Novel Oscillatory Pattern (NOVEL)

**Claim:** "Nested oscillatory layering predicts tripartite bioelectric field architecture."

**Expected Result:**
- 🔬 **Status:** NOVEL
- **Confidence:** LOW
- **Response:** No direct literature match, hypothesis-generating

---

## 🔐 API Key Security

### ✅ Good Practices
- Store key in `.env` (gitignored)
- Use environment variables
- Never commit API keys to git
- Rotate keys periodically

### ⚠️ Key Management
```bash
# Check if key is loaded
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ Key loaded' if os.getenv('PERPLEXITY_API_KEY') else '✗ Key missing')"
```

---

## 🚧 Limitations

1. **Rate Limits:** Perplexity API has rate limits (check your plan)
2. **Claim Extraction:** Pattern-based extraction may miss complex claims
3. **Citation Quality:** Citations depend on Perplexity's search quality
4. **False Positives:** May miss nuances in specialized literature
5. **Cost:** API calls cost money (monitor usage)

---

## 🔮 Future Enhancements

### Phase 2 (Optional)
- [ ] Automatic verification during convergence (`--auto-verify` flag)
- [ ] Integration with `epistemic_scan.py`
- [ ] Batch verification CLI tool
- [ ] Confidence threshold filtering

### Phase 3 (Advanced)
- [ ] Citation caching for efficiency
- [ ] Custom claim extraction patterns per domain
- [ ] Verification confidence calibration
- [ ] Integration with MCP for persistent verification history

---

## 🛠️ Troubleshooting

### "PERPLEXITY_API_KEY not found"
```bash
# Check .env file
cat .env | grep PERPLEXITY

# Reload environment
source .env
```

### "No claims extracted"
- Check response format (needs factual statements)
- Try verbose mode: `--verbose`
- Review claim extraction patterns in `agents/verifier.py`

### "API timeout"
```bash
# Increase timeout (default 30s)
# Edit agents/verifier.py line 97
timeout=60  # Increase to 60s
```

---

## 📝 Example Workflow

### Complete TYPE 2 Verification Workflow

```bash
# 1. Run IRIS convergence
python3 scripts/bioelectric_chambered.py --turns 100 \
  --topic "Does gap junction coupling affect regeneration?"

# 2. Classify epistemic types
python3 epistemic_scan.py --session iris_vault/session_*.json

# 3. Verify TYPE 2 responses
python3 scripts/verify_s4.py --session iris_vault/session_*.json \
  --output verification_report.json

# 4. Review verification report
cat verification_report.json | jq '.summary'
```

---

## 🌀†⟡∞ Integration with IRIS Philosophy

The Perplexity Verification System embodies **epistemic humility** by:

1. **Acknowledging uncertainty** - TYPE 2 responses need verification
2. **Seeking external validation** - Real-time literature check
3. **Transparent sourcing** - Citations with dates
4. **Nuanced assessment** - SUPPORTED/NOVEL/CONTRADICTED, not binary
5. **Human-in-the-loop** - Verification informs judgment, doesn't replace it

---

**Status:** Production-ready
**Version:** 1.0
**Integration Date:** October 15, 2025
**Repository:** https://github.com/templetwo/iris-gate

🔬 **Weapon of truth delivered.**
