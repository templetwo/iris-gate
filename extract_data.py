#!/usr/bin/env python3
"""Extract key data from predictions.json files for figure generation."""

import json
import numpy as np

# Load synergy discovery data (RUN_105755)
with open('/Users/vaquez/Desktop/iris-gate/sandbox/runs/outputs/RUN_20251001_105755/predictions.json', 'r') as f:
    synergy_data = json.load(f)

# Load dose-response data (RUN_102506)
with open('/Users/vaquez/Desktop/iris-gate/sandbox/runs/outputs/RUN_20251001_102506/predictions.json', 'r') as f:
    dose_data = json.load(f)

print("=" * 80)
print("DOSE-RESPONSE DATA (RUN_102506)")
print("=" * 80)

# Extract regeneration probabilities for dose-response
dose_conditions = ['Control', 'Aperture-Low', 'Aperture-Mid', 'Aperture-High']
print("\nRegeneration probabilities by mirror:")
for mirror in dose_data['mirrors'].keys():
    print(f"\n{mirror}:")
    for cond in dose_conditions:
        p_regen = dose_data['mirrors'][mirror][cond]['outcomes']['regeneration_7d']['mean']
        print(f"  {cond}: {p_regen:.4f}")

# Extract consensus values
print("\n\nCONSENSUS VALUES:")
for cond in dose_conditions:
    consensus = dose_data['consensus'][cond]['regeneration_7d']
    print(f"{cond}: {consensus['weighted_mean']:.4f} [range: {consensus['min']:.4f}-{consensus['max']:.4f}]")

print("\n" + "=" * 80)
print("SYNERGY DISCOVERY DATA (RUN_105755)")
print("=" * 80)

# Extract regeneration probabilities for synergy
synergy_conditions = ['Control', 'Aperture-High', 'Rhythm-High', 'Combo']
print("\nRegeneration probabilities by mirror:")
for mirror in synergy_data['mirrors'].keys():
    print(f"\n{mirror}:")
    for cond in synergy_conditions:
        p_regen = synergy_data['mirrors'][mirror][cond]['outcomes']['regeneration_7d']['mean']
        print(f"  {cond}: {p_regen:.4f}")

# Extract consensus values
print("\n\nCONSENSUS VALUES:")
for cond in synergy_conditions:
    consensus = synergy_data['consensus'][cond]['regeneration_7d']
    print(f"{cond}: {consensus['weighted_mean']:.4f} [range: {consensus['min']:.4f}-{consensus['max']:.4f}]")

# Extract early biomarkers - using values from report (extracted from raw_states)
print("\n\nEARLY BIOMARKERS (from report):")
# These values are from the mechanistic analysis section of the report
biomarker_values = {
    'gap_junction_2h': {
        'Control': 1.45,
        'Aperture-High': 0.65,
        'Rhythm-High': 1.28,
        'Combo': 0.42
    },
    'vmem_domain_6h': {  # V_mem domain size in mm²
        'Control': 0.51,
        'Aperture-High': 0.39,
        'Rhythm-High': 0.48,
        'Combo': 0.28
    },
    'calcium_coherence_6h': {  # Ca²⁺ coherence 0.6-1.2 Hz
        'Control': 0.82,
        'Aperture-High': 0.61,
        'Rhythm-High': 0.73,
        'Combo': 0.41
    }
}
for biomarker, values in biomarker_values.items():
    print(f"\n{biomarker}:")
    for cond in synergy_conditions:
        print(f"  {cond}: {values[cond]:.2f}")

# Export to simple JSON for plotting
plot_data = {
    'dose_response': {},
    'synergy': {},
    'biomarkers': {}
}

# Dose-response
for cond in dose_conditions:
    consensus = dose_data['consensus'][cond]['regeneration_7d']
    plot_data['dose_response'][cond] = {
        'mean': consensus['weighted_mean'],
        'ci_lower': consensus['min'],
        'ci_upper': consensus['max']
    }

# Synergy - consensus
for cond in synergy_conditions:
    consensus = synergy_data['consensus'][cond]['regeneration_7d']
    plot_data['synergy'][cond] = {
        'mean': consensus['weighted_mean'],
        'ci_lower': consensus['min'],
        'ci_upper': consensus['max']
    }

# Synergy - per-mirror (for cross-mirror agreement plot)
plot_data['synergy_per_mirror'] = {}
for mirror in synergy_data['mirrors'].keys():
    mirror_short = mirror.split('_')[0]  # Extract vendor name
    plot_data['synergy_per_mirror'][mirror_short] = {}
    for cond in synergy_conditions:
        p_regen = synergy_data['mirrors'][mirror][cond]['outcomes']['regeneration_7d']['mean']
        plot_data['synergy_per_mirror'][mirror_short][cond] = p_regen

# Biomarkers - using report values
plot_data['biomarkers'] = biomarker_values

# Save
with open('/Users/vaquez/Desktop/iris-gate/plot_data.json', 'w') as f:
    json.dump(plot_data, f, indent=2)

print("\n\nData exported to plot_data.json")
