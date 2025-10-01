#!/usr/bin/env python3
"""
IRIS New Experiment Scaffold Generator

Creates a complete experiment directory from templates with all placeholders filled.

Usage:
    python pipelines/new_experiment.py --topic "Your question here" \\
        --id EXP_SLUG --organism planaria --factor aperture

Example:
    python pipelines/new_experiment.py \\
        --topic "Does serotonin modulate regeneration speed?" \\
        --id SEROTONIN_REGEN --organism planaria --factor rhythm
"""

import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


def create_experiment_scaffold(topic, exp_id, organism, factor, output_dir="experiments"):
    """Create populated experiment directory from templates."""

    # Create experiment directory
    exp_path = Path(output_dir) / exp_id
    exp_path.mkdir(parents=True, exist_ok=True)

    # Map factor to defaults
    factor_defaults = {
        "aperture": {
            "factor_name": "Aperture",
            "factor_mechanism": "Gap junction coupling",
            "factor_kit": "aperture",
            "agent": "carbenoxolone",
            "dose_low": "50µM",
            "dose_mid": "100µM",
            "dose_high": "200µM",
            "effect_low": 0.5,
            "effect_mid": 1.0,
            "effect_high": 1.5,
            "biomarker_1": "Gap junction coupling (Lucifer Yellow)",
            "biomarker_2": "V_mem domain size (DiBAC4)",
            "timepoint_1": 2,
            "timepoint_2": 6,
        },
        "rhythm": {
            "factor_name": "Rhythm",
            "factor_mechanism": "Bioelectric oscillations",
            "factor_kit": "rhythm",
            "agent": "octanol",
            "dose_low": "0.25mM",
            "dose_mid": "0.5mM",
            "dose_high": "0.75mM",
            "effect_low": 0.5,
            "effect_mid": 1.0,
            "effect_high": 1.5,
            "biomarker_1": "Ca²⁺ wave frequency (Cal-520)",
            "biomarker_2": "Ca²⁺ coherence (FFT)",
            "timepoint_1": 2,
            "timepoint_2": 6,
        },
        "center": {
            "factor_name": "Center",
            "factor_mechanism": "V_mem domain stability",
            "factor_kit": "center",
            "agent": "bafilomycin",
            "dose_low": "5nM",
            "dose_mid": "10nM",
            "dose_high": "20nM",
            "effect_low": 0.5,
            "effect_mid": 1.0,
            "effect_high": 1.5,
            "biomarker_1": "V_mem domain size (DiBAC4)",
            "biomarker_2": "Domain stability (tracking)",
            "timepoint_1": 2,
            "timepoint_2": 6,
        }
    }

    # Get factor-specific defaults
    defaults = factor_defaults.get(factor, factor_defaults["aperture"])

    # Common placeholders
    placeholders = {
        "EXP_ID": exp_id,
        "TOPIC": topic,
        "DATE": datetime.now().strftime("%Y-%m-%d"),
        "PROBLEM_STATEMENT": topic,
        "ORGANISM": organism,
        "PRIMARY_OUTCOME": "Regeneration success at 7d",
        "PLAN_ID": f"{exp_id}_MINIMAL",
        "SESSION_ID": "AUTO_FILLED_FROM_S4",
        "RUN_ID": "AUTO_FILLED_AFTER_SIMULATION",
        "THRESHOLD_PP": "10",
        "SUCCESS_THRESHOLD": "0.80",
        "SYNERGY_THRESHOLD": "0.10",
        "COMP_DAYS": "3",
        "WETLAB_DAYS": "10",
        "COST_USD": "850",
    }

    # Merge with factor defaults
    placeholders.update(defaults)

    # Load and populate each template
    template_dir = Path("templates")

    # 1. Experiment overview
    populate_template(
        template_dir / "EXPERIMENT_TEMPLATE.md",
        exp_path / "README.md",
        placeholders
    )

    # 2. Minimal plan
    populate_template(
        template_dir / "sandbox_plan_minimal.yaml",
        exp_path / f"{exp_id}_minimal_plan.yaml",
        placeholders
    )

    # 3. Synergy plan (optional)
    populate_template(
        template_dir / "sandbox_plan_synergy.yaml",
        exp_path / f"{exp_id}_synergy_plan.yaml",
        placeholders
    )

    # 4. Pre-registration
    prereg_placeholders = placeholders.copy()
    prereg_placeholders.update({
        "TITLE": f"Testing {factor} perturbation in {organism} regeneration",
        "PI_NAME": "YOUR_NAME",
        "EMAIL": "your.email@institution.edu",
        "FUNDING_SOURCE": "N/A",
        "N_ARMS": "4",
        "TOTAL_N": "120",
        "N_PER_ARM": "30",
        "REGISTRATION_PLATFORM": "OSF",
    })

    populate_template(
        template_dir / "prereg_template.md",
        exp_path / "prereg_draft.md",
        prereg_placeholders
    )

    # 5. Create subdirectories
    (exp_path / "outputs").mkdir(exist_ok=True)
    (exp_path / "reports").mkdir(exist_ok=True)
    (exp_path / "data").mkdir(exist_ok=True)

    # 6. Create metadata file
    metadata = {
        "exp_id": exp_id,
        "topic": topic,
        "organism": organism,
        "factor": factor,
        "created": datetime.now().isoformat(),
        "status": "draft",
        "placeholders": placeholders
    }

    with open(exp_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Experiment scaffold created: {exp_path}")
    print(f"📁 Files created:")
    print(f"   - README.md (experiment overview)")
    print(f"   - {exp_id}_minimal_plan.yaml (single-factor plan)")
    print(f"   - {exp_id}_synergy_plan.yaml (2×2 synergy plan)")
    print(f"   - prereg_draft.md (pre-registration template)")
    print(f"   - metadata.json (experiment metadata)")
    print(f"\n📋 Next steps:")
    print(f"   1. Review and customize README.md")
    print(f"   2. Run S4 convergence: python scripts/bioelectric_chambered.py --turns 100")
    print(f"   3. Extract S4 priors: python sandbox/cli/extract_s4_states.py")
    print(f"   4. Run simulation: python sandbox/cli/run_plan.py {exp_path / f'{exp_id}_minimal_plan.yaml'}")

    return exp_path


def populate_template(template_path, output_path, placeholders):
    """Load template, replace placeholders, write to output."""
    with open(template_path, "r") as f:
        content = f.read()

    # Replace all placeholders
    for key, value in placeholders.items():
        content = content.replace(f"{{{key}}}", str(value))

    with open(output_path, "w") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Create new IRIS experiment from templates"
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Research question in 1-2 sentences"
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Experiment ID (slug format, e.g., APERTURE_REGEN)"
    )
    parser.add_argument(
        "--organism",
        default="planaria",
        help="Organism system (default: planaria)"
    )
    parser.add_argument(
        "--factor",
        choices=["aperture", "rhythm", "center"],
        default="aperture",
        help="Primary factor to test (default: aperture)"
    )
    parser.add_argument(
        "--output",
        default="experiments",
        help="Output directory (default: experiments/)"
    )

    args = parser.parse_args()

    create_experiment_scaffold(
        topic=args.topic,
        exp_id=args.id,
        organism=args.organism,
        factor=args.factor,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
