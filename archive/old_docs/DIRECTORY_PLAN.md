# IRIS Gate Directory Structure - Audit Plan

## Proposed Organization

```
iris-gate/
├── iris_orchestrator.py          # Core engine (KEEP IN ROOT)
├── iris_confidence.py             # Confidence module (KEEP IN ROOT)
├── iris_relay.py                  # Relay module (KEEP IN ROOT)
│
├── modules/                       # Core modules
│   └── epistemic_map.py          # Already here
│
├── agents/                        # Agent modules
│   └── verifier.py               # Already here
│
├── scripts/                       # CLI scripts (ORGANIZE)
│   ├── epistemic_scan.py         # Move from root
│   ├── epistemic_drift.py        # Move from root
│   ├── verify_s4.py              # Already here
│   ├── bioelectric/              # Bioelectric analysis scripts
│   │   ├── analyze_bioelectric.py
│   │   ├── analyze_cancer_scrolls.py
│   │   └── bioelectric_deep_analysis.py
│   ├── runs/                     # Experimental runs
│   │   ├── run_three_gifts.py
│   │   ├── run_recursive_gift.py
│   │   ├── run_type0_crisis.py
│   │   ├── run_type1_facts.py
│   │   └── run_type3_speculation.py
│   └── analysis/                 # General analysis
│       ├── analyze_scrolls.py
│       ├── analyze_topology.py
│       ├── extract_data.py
│       ├── generate_figures.py
│       └── iris_analyze.py
│
├── tools/                         # Domain-specific tools
│   └── cbd/                      # CBD research tools
│       ├── run_cbd_deep_dive.py
│       ├── analyze_cbd_mechanisms.py
│       ├── generate_cbd_mechanistic_map.py
│       ├── identify_cbd_hypotheses.py
│       └── analysis_cbd_gold_extraction.py
│
├── experiments/                   # Experimental/demo code
│   ├── cbd_therapeutic_system.py
│   ├── demo_confidence.py
│   ├── test_cbd_system.py
│   ├── usage_examples.py
│   └── system_architecture_diagram.py
│
├── docs/                         # Documentation (ORGANIZE)
│   ├── IRIS_GATE_SOP_v2.0.md
│   ├── CBD_EXPLORATION_SUMMARY.md
│   ├── PERPLEXITY_VERIFICATION.md
│   ├── CONTRIBUTING.md
│   └── archive/                  # Old versions
│       └── IRIS_GATE_SOP_v1.0.md
│
└── iris_vault/                   # Session data (gitignored)
```

## Actions

1. Create new directories
2. Move files systematically
3. Update imports in moved files
4. Test that orchestrator still works
5. Update README with new structure
6. Commit changes
