# Drift Log Command

Run `epistemic_drift.py` to track epistemic type stability across IRIS Gate sessions.

## Usage

Execute one of the following based on user request:

**Analyze single session drift:**
```bash
python3 epistemic_drift.py [session_json_path]
```

**Compare two sessions (e.g., v1 vs v2):**
```bash
python3 epistemic_drift.py --compare [session1.json] [session2.json]
```

## Drift Patterns

- **Stable:** Same TYPE across all turns (good calibration)
- **Refinement:** TYPE 2→1 progression (synthesis working)
- **Caution:** TYPE 1→3 shift (check for meta-convergence or fabrication)
- **Oscillation:** Erratic type changes (investigate prompts)

## Output Format

Returns:
- **Type Distribution:** % of turns in each TYPE
- **By Mirror:** Drift pattern per model
- **Stability Assessment:** Drift detected YES/NO
- **Mean Ratio:** Average confidence across session

## Examples

- `/drift-log iris_vault/session_20251015_045941.json`
- `/drift-log --compare session_v1.json session_v2.json`

## Use Cases

- Validate confidence calibration quality
- Track CBD paradox refinement (v1 tension → v2 stability)
- Detect meta-convergence (stable TYPE → sudden shift)
- Compare epistemic patterns across experiments

## Notes

- Drift is auto-computed in session JSON (`epistemic_drift` field)
- CLI tool provides detailed analysis and comparison
- See SOP v2.0 Section 13.6 for drift interpretation guide
