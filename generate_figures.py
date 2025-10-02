#!/usr/bin/env python3
"""
Generate publication-quality figures for Mini-H1 synergy discovery.
Export formats: SVG (vector), PNG (300 DPI for presentations).
Style: Nature Methods-compatible, grayscale-friendly palette.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Create output directory
FIG_DIR = Path('/Users/vaquez/Desktop/iris-gate/figures')
FIG_DIR.mkdir(exist_ok=True)

# Publication settings
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'font.size': 8,
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'pdf.fonttype': 42,  # Ensure text is editable in PDFs
    'ps.fonttype': 42
})

# Grayscale-friendly color palette (colorblind-safe)
COLORS = {
    'Control': '#000000',      # Black
    'Aperture-Low': '#CCCCCC', # Light gray
    'Aperture-Mid': '#888888', # Medium gray
    'Aperture-High': '#444444', # Dark gray
    'Rhythm-High': '#666666',  # Medium-dark gray
    'Combo': '#000000'         # Black (will use different pattern)
}

# Alternative color scheme for better distinction
COLORS_ALT = {
    'Control': '#2166ac',       # Blue
    'Aperture-Low': '#92c5de',  # Light blue
    'Aperture-Mid': '#d6604d',  # Orange-red
    'Aperture-High': '#b2182b', # Red
    'Rhythm-High': '#35978f',   # Teal
    'Combo': '#762a83'          # Purple
}

# Load data
with open('/Users/vaquez/Desktop/iris-gate/plot_data.json', 'r') as f:
    data = json.load(f)

# ============================================================================
# FIGURE 1: DOSE-RESPONSE VALIDATION
# ============================================================================

def plot_dose_response():
    """
    Figure 1: Dose-response validation from RUN_102506
    Bar plot showing P(regeneration) across 4 Aperture doses with error bars.
    """
    fig, ax = plt.subplots(figsize=(3.5, 2.5))

    conditions = ['Control', 'Aperture-Low', 'Aperture-Mid', 'Aperture-High']
    means = [data['dose_response'][c]['mean'] for c in conditions]
    ci_lower = [data['dose_response'][c]['ci_lower'] for c in conditions]
    ci_upper = [data['dose_response'][c]['ci_upper'] for c in conditions]

    # Calculate error bars (distance from mean)
    yerr_lower = [means[i] - ci_lower[i] for i in range(len(conditions))]
    yerr_upper = [ci_upper[i] - means[i] for i in range(len(conditions))]
    yerr = [yerr_lower, yerr_upper]

    x_pos = np.arange(len(conditions))
    colors_list = [COLORS_ALT[c] for c in conditions]

    bars = ax.bar(x_pos, means, yerr=yerr, capsize=4,
                   color=colors_list, edgecolor='black', linewidth=1.0,
                   error_kw={'linewidth': 1.5, 'ecolor': 'black'})

    # Add effect size annotations
    control_mean = means[0]
    for i, (cond, mean) in enumerate(zip(conditions, means)):
        if cond != 'Control':
            effect_pct = ((mean - control_mean) / control_mean) * 100
            y_pos = mean + yerr_upper[i] + 0.01
            ax.text(i, y_pos, f'{effect_pct:.1f}%',
                   ha='center', va='bottom', fontsize=7, fontweight='bold')

    # Styling
    ax.set_ylabel('P(regeneration)', fontweight='bold')
    ax.set_xlabel('Condition', fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Control', 'Ap-Low\n50μM', 'Ap-Mid\n100μM', 'Ap-High\n200μM'],
                       fontsize=8)
    ax.set_ylim([0.80, 1.02])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.axhline(y=0.90, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

    # Add sample size annotation
    ax.text(0.98, 0.02, 'n=300 runs × 7 mirrors',
            transform=ax.transAxes, ha='right', va='bottom',
            fontsize=6, style='italic', color='gray')

    plt.tight_layout()

    # Save
    fig.savefig(FIG_DIR / 'figure1_dose_response.svg', format='svg')
    fig.savefig(FIG_DIR / 'figure1_dose_response.png', format='png')
    plt.close()

    print("✓ Figure 1 saved: dose-response validation")

# ============================================================================
# FIGURE 2: SYNERGY DISCOVERY
# ============================================================================

def plot_synergy_heatmap():
    """
    Figure 2A: 2×2 heatmap showing P(regen) for all combinations.
    """
    fig, ax = plt.subplots(figsize=(3.0, 2.5))

    # Create 2×2 matrix
    matrix_data = np.array([
        [data['synergy']['Control']['mean'], data['synergy']['Rhythm-High']['mean']],
        [data['synergy']['Aperture-High']['mean'], data['synergy']['Combo']['mean']]
    ])

    im = ax.imshow(matrix_data, cmap='RdYlGn', vmin=0.60, vmax=1.0, aspect='auto')

    # Add text annotations
    labels = [
        ['Control', 'Rhythm-High'],
        ['Aperture-High', 'Combo']
    ]
    for i in range(2):
        for j in range(2):
            value = matrix_data[i, j]
            text_color = 'white' if value < 0.75 else 'black'
            ax.text(j, i, f'{labels[i][j]}\n{value:.3f}',
                   ha='center', va='center', fontsize=9,
                   fontweight='bold', color=text_color)

    # Styling
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['No Rhythm', 'Rhythm\n(Octanol)'], fontsize=8)
    ax.set_yticklabels(['No Aperture', 'Aperture\n(Carbenoxolone)'], fontsize=8)
    ax.set_xlabel('Ca²⁺/V_mem Oscillations', fontweight='bold')
    ax.set_ylabel('Gap Junction Coupling', fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('P(regeneration)', fontweight='bold', fontsize=8)

    plt.tight_layout()

    fig.savefig(FIG_DIR / 'figure2a_synergy_heatmap.svg', format='svg')
    fig.savefig(FIG_DIR / 'figure2a_synergy_heatmap.png', format='png')
    plt.close()

    print("✓ Figure 2A saved: synergy heatmap")

def plot_synergy_bars():
    """
    Figure 2B: Bar plot showing observed Combo vs predicted additive (Bliss).
    """
    fig, ax = plt.subplots(figsize=(2.5, 2.5))

    # Calculate Bliss prediction
    p_ap = data['synergy']['Aperture-High']['mean']
    p_rh = data['synergy']['Rhythm-High']['mean']
    bliss_predicted = p_ap * p_rh
    observed = data['synergy']['Combo']['mean']
    synergy_score = observed - bliss_predicted

    # Data for bar plot
    labels = ['Predicted\n(Bliss)', 'Observed\n(Combo)']
    values = [bliss_predicted, observed]
    colors_bar = ['#AAAAAA', '#D73027']

    bars = ax.bar([0, 1], values, color=colors_bar, edgecolor='black', linewidth=1.0, width=0.6)

    # Add value labels
    for i, (val, label) in enumerate(zip(values, labels)):
        ax.text(i, val + 0.01, f'{val:.3f}', ha='center', va='bottom',
               fontsize=8, fontweight='bold')

    # Add synergy annotation
    ax.annotate('', xy=(1, observed), xytext=(1, bliss_predicted),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(1.25, (observed + bliss_predicted)/2,
           f'Synergy:\n{synergy_score:.3f}\n({synergy_score*100:.1f}pp)',
           va='center', fontsize=7, fontweight='bold', color='#D73027')

    # Styling
    ax.set_ylabel('P(regeneration)', fontweight='bold')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim([0.60, 0.90])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.axhline(y=bliss_predicted, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

    plt.tight_layout()

    fig.savefig(FIG_DIR / 'figure2b_synergy_calculation.svg', format='svg')
    fig.savefig(FIG_DIR / 'figure2b_synergy_calculation.png', format='png')
    plt.close()

    print("✓ Figure 2B saved: synergy calculation")

def plot_cross_mirror_agreement():
    """
    Figure 2C: Box/violin plots showing Combo P(regen) across 7 mirrors.
    """
    fig, ax = plt.subplots(figsize=(4.0, 2.5))

    conditions = ['Control', 'Aperture-High', 'Rhythm-High', 'Combo']

    # Collect data for each condition across mirrors
    plot_data = []
    for cond in conditions:
        values = [data['synergy_per_mirror'][mirror][cond]
                  for mirror in data['synergy_per_mirror'].keys()]
        plot_data.append(values)

    # Create violin plot with box plot overlay
    parts = ax.violinplot(plot_data, positions=range(len(conditions)),
                          showmeans=False, showmedians=False, widths=0.6)

    # Color violin plots
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(COLORS_ALT[conditions[i]])
        pc.set_alpha(0.6)
        pc.set_edgecolor('black')
        pc.set_linewidth(1.0)

    # Add box plot overlay
    bp = ax.boxplot(plot_data, positions=range(len(conditions)),
                    widths=0.3, patch_artist=True,
                    boxprops=dict(facecolor='white', edgecolor='black', linewidth=1.0),
                    medianprops=dict(color='black', linewidth=1.5),
                    whiskerprops=dict(color='black', linewidth=1.0),
                    capprops=dict(color='black', linewidth=1.0),
                    flierprops=dict(marker='o', markerfacecolor='gray',
                                   markersize=3, markeredgecolor='black'))

    # Add consensus line
    for i, cond in enumerate(conditions):
        consensus_mean = data['synergy'][cond]['mean']
        ax.plot([i-0.35, i+0.35], [consensus_mean, consensus_mean],
               'r-', linewidth=2, alpha=0.8)

    # Styling
    ax.set_ylabel('P(regeneration)', fontweight='bold')
    ax.set_xlabel('Condition', fontweight='bold')
    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(['Control', 'Ap-High', 'Rh-High', 'Combo'], fontsize=8)
    ax.set_ylim([0.60, 1.02])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add legend
    red_line = mpatches.Patch(color='red', label='Consensus (weighted)')
    ax.legend(handles=[red_line], loc='upper right', frameon=False, fontsize=7)

    # Add annotation
    ax.text(0.02, 0.98, '7 mirrors\n(1.7B-671B params)',
            transform=ax.transAxes, ha='left', va='top',
            fontsize=6, style='italic', color='gray')

    plt.tight_layout()

    fig.savefig(FIG_DIR / 'figure2c_cross_mirror.svg', format='svg')
    fig.savefig(FIG_DIR / 'figure2c_cross_mirror.png', format='png')
    plt.close()

    print("✓ Figure 2C saved: cross-mirror agreement")

# ============================================================================
# FIGURE 3: EARLY BIOMARKERS
# ============================================================================

def plot_biomarkers():
    """
    Figure 3: Three-panel time series showing early biomarkers.
    Panel A: GJ coupling at 2h
    Panel B: V_mem domain area at 6h
    Panel C: Ca²⁺ coherence at 6h
    """
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.2))

    conditions = ['Control', 'Aperture-High', 'Rhythm-High', 'Combo']
    colors_list = [COLORS_ALT[c] for c in conditions]

    # Panel A: Gap junction coupling (2h)
    ax = axes[0]
    values = [data['biomarkers']['gap_junction_2h'][c] for c in conditions]
    x_pos = np.arange(len(conditions))
    bars = ax.bar(x_pos, values, color=colors_list, edgecolor='black', linewidth=1.0)

    # Add percent change annotations
    control_val = values[0]
    for i, val in enumerate(values):
        if i > 0:
            pct_change = ((val - control_val) / control_val) * 100
            y_pos = val + 0.05
            ax.text(i, y_pos, f'{pct_change:+.0f}%',
                   ha='center', va='bottom', fontsize=6, fontweight='bold')

    ax.set_ylabel('GJ coupling\n(× baseline)', fontweight='bold', fontsize=9)
    ax.set_xlabel('Condition', fontweight='bold', fontsize=9)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Ctrl', 'Ap-Hi', 'Rh-Hi', 'Combo'], fontsize=7)
    ax.set_ylim([0, 1.6])
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title('A. Gap Junction Coupling (2h)', fontsize=9, fontweight='bold', loc='left')

    # Panel B: V_mem domain size (6h)
    ax = axes[1]
    values = [data['biomarkers']['vmem_domain_6h'][c] for c in conditions]
    bars = ax.bar(x_pos, values, color=colors_list, edgecolor='black', linewidth=1.0)

    control_val = values[0]
    for i, val in enumerate(values):
        if i > 0:
            pct_change = ((val - control_val) / control_val) * 100
            y_pos = val + 0.02
            ax.text(i, y_pos, f'{pct_change:+.0f}%',
                   ha='center', va='bottom', fontsize=6, fontweight='bold')

    ax.set_ylabel('V_mem domain\n(mm²)', fontweight='bold', fontsize=9)
    ax.set_xlabel('Condition', fontweight='bold', fontsize=9)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Ctrl', 'Ap-Hi', 'Rh-Hi', 'Combo'], fontsize=7)
    ax.set_ylim([0, 0.6])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title('B. V_mem Domain Size (6h)', fontsize=9, fontweight='bold', loc='left')

    # Panel C: Ca²⁺ coherence (6h)
    ax = axes[2]
    values = [data['biomarkers']['calcium_coherence_6h'][c] for c in conditions]
    bars = ax.bar(x_pos, values, color=colors_list, edgecolor='black', linewidth=1.0)

    control_val = values[0]
    for i, val in enumerate(values):
        if i > 0:
            pct_change = ((val - control_val) / control_val) * 100
            y_pos = val + 0.03
            ax.text(i, y_pos, f'{pct_change:+.0f}%',
                   ha='center', va='bottom', fontsize=6, fontweight='bold')

    ax.set_ylabel('Ca²⁺ coherence\n(0.6-1.2 Hz)', fontweight='bold', fontsize=9)
    ax.set_xlabel('Condition', fontweight='bold', fontsize=9)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Ctrl', 'Ap-Hi', 'Rh-Hi', 'Combo'], fontsize=7)
    ax.set_ylim([0, 1.0])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title('C. Ca²⁺ Coherence (6h)', fontsize=9, fontweight='bold', loc='left')

    plt.tight_layout()

    fig.savefig(FIG_DIR / 'figure3_biomarkers.svg', format='svg')
    fig.savefig(FIG_DIR / 'figure3_biomarkers.png', format='png')
    plt.close()

    print("✓ Figure 3 saved: early biomarkers")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("\nGenerating publication-quality figures...")
    print(f"Output directory: {FIG_DIR}\n")

    plot_dose_response()
    plot_synergy_heatmap()
    plot_synergy_bars()
    plot_cross_mirror_agreement()
    plot_biomarkers()

    print(f"\n✓ All figures generated successfully!")
    print(f"✓ Files saved to: {FIG_DIR}/")
    print("\nGenerated files:")
    for f in sorted(FIG_DIR.glob('*')):
        print(f"  - {f.name}")
