# Epistemic Scan Command

Run `epistemic_scan.py` to classify IRIS Gate scrolls or sessions by epistemic topology type (0-3).

## Usage

Execute one of the following based on user request:

**Scan single scroll:**
```bash
python3 epistemic_scan.py [scroll_path]
```

**Scan session with drift detection:**
```bash
python3 epistemic_scan.py --session [session_json_path]
```

**Run CBD test suite:**
```bash
python3 epistemic_scan.py --cbd
```

## Output Format

Returns epistemic classification:
- **Type:** 0-3 (Crisis/Facts/Exploration/Speculation)
- **Confidence:** TRUST/VERIFY/OVERRIDE guidance
- **Ratio:** High/low confidence marker ratio
- **Width:** Unique concept count
- **Triggers:** IF-THEN language detected (TYPE 0 only)

## Examples

- `/epistemic-scan iris_vault/scrolls/IRIS_*/S4.md`
- `/epistemic-scan --session iris_vault/session_20251015_045941.json`
- `/epistemic-scan --cbd`

## Notes

- Always on: Every IRIS scroll auto-classified during execution
- CLI tool for manual analysis of existing scrolls
- See SOP v2.0 Section 13 for full framework
