#!/usr/bin/env python3
"""
Generate system architecture diagram for CBD Therapeutic Development System
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np


def create_architecture_diagram():
    """Create comprehensive system architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Color scheme
    colors = {
        'input': '#E8F4FD',      # Light blue
        'processing': '#FFF2CC',  # Light yellow
        'output': '#E1D5E7',      # Light purple
        'storage': '#D5E8D4',     # Light green
        'monitoring': '#FFE6CC',  # Light orange
        'connection': '#666666'   # Dark gray
    }

    # Title
    ax.text(8, 11.5, 'CBD Therapeutic Development System Architecture',
            fontsize=18, fontweight='bold', ha='center')

    # Input Layer
    input_y = 9.5
    inputs = [
        ('IRIS Convergence\nData', 1, input_y),
        ('Literature\nValidation', 4, input_y),
        ('Experimental\nResults', 7, input_y),
        ('Clinical\nFeedback', 10, input_y)
    ]

    for name, x, y in inputs:
        box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['input'],
                            edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

    # Core Processing Components
    core_y = 7.5
    core_components = [
        ('Research Claims\nKnowledge Graph', 2.5, core_y, 2, 1),
        ('Literature\nMonitoring System', 6, core_y, 2, 1),
        ('Experiment\nPrioritization Engine', 9.5, core_y, 2, 1),
        ('Confidence\nScoring System', 13, core_y, 2, 1)
    ]

    for name, x, y, w, h in core_components:
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['processing'],
                            edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=10, fontweight='bold')

    # Data Storage Layer
    storage_y = 5.5
    storage_components = [
        ('Claims\nDatabase', 2, storage_y),
        ('Experiment\nSpecifications', 5, storage_y),
        ('Literature\nCache', 8, storage_y),
        ('Milestone\nTracker', 11, storage_y),
        ('System\nState', 14, storage_y)
    ]

    for name, x, y in storage_components:
        box = FancyBboxPatch((x-0.7, y-0.35), 1.4, 0.7,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['storage'],
                            edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

    # Analysis & Decision Layer
    analysis_y = 3.5
    analysis_components = [
        ('Research Roadmap\nGenerator', 3, analysis_y, 2.5, 0.8),
        ('Clinical Readiness\nAssessment', 7, analysis_y, 2.5, 0.8),
        ('Risk Management\n& Paradigm Detection', 11.5, analysis_y, 3, 0.8)
    ]

    for name, x, y, w, h in analysis_components:
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['output'],
                            edgecolor='black', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=10, fontweight='bold')

    # Output Layer
    output_y = 1.5
    outputs = [
        ('Prioritized\nExperiments', 2, output_y),
        ('Development\nTimelines', 5, output_y),
        ('Go/No-Go\nDecisions', 8, output_y),
        ('Resource\nAllocation', 11, output_y),
        ('Progress\nReports', 14, output_y)
    ]

    for name, x, y in outputs:
        box = FancyBboxPatch((x-0.8, y-0.35), 1.6, 0.7,
                            boxstyle="round,pad=0.1",
                            facecolor=colors['monitoring'],
                            edgecolor='black', linewidth=1)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

    # Add connections
    connections = [
        # Inputs to core processing
        ((2.5, 9.1), (2.5, 8)),
        ((4, 9.1), (6, 8)),
        ((7, 9.1), (9.5, 8)),
        ((10, 9.1), (13, 8)),

        # Core processing to storage
        ((2.5, 7), (2, 5.85)),
        ((6, 7), (8, 5.85)),
        ((9.5, 7), (5, 5.85)),
        ((13, 7), (14, 5.85)),

        # Storage to analysis
        ((3, 5.15), (3, 3.9)),
        ((8, 5.15), (7, 3.9)),
        ((11, 5.15), (11.5, 3.9)),

        # Analysis to outputs
        ((3, 3.1), (2, 1.85)),
        ((3, 3.1), (5, 1.85)),
        ((7, 3.1), (8, 1.85)),
        ((11.5, 3.1), (11, 1.85)),
        ((11.5, 3.1), (14, 1.85))
    ]

    for (x1, y1), (x2, y2) in connections:
        ax.arrow(x1, y1, x2-x1, y2-y1, head_width=0.1, head_length=0.1,
                fc=colors['connection'], ec=colors['connection'], alpha=0.7)

    # Add side panels for key metrics
    # Left panel - IRIS Insights
    iris_box = FancyBboxPatch((0.2, 6), 1.2, 3,
                             boxstyle="round,pad=0.1",
                             facecolor='#F0F8FF',
                             edgecolor='blue', linewidth=2)
    ax.add_patch(iris_box)
    ax.text(0.8, 8.5, 'IRIS Insights', ha='center', fontweight='bold', fontsize=11)
    iris_text = """• Selectivity: 1.53
• Convergence: 85%
• Rhythm: 0.5-2Hz
• Stability: 0.7-0.98
• Aperture: 0.3-0.9"""
    ax.text(0.8, 7.3, iris_text, ha='center', va='center', fontsize=8)

    # Right panel - Current Status
    status_box = FancyBboxPatch((14.6, 6), 1.2, 3,
                               boxstyle="round,pad=0.1",
                               facecolor='#FFF8DC',
                               edgecolor='orange', linewidth=2)
    ax.add_patch(status_box)
    ax.text(15.2, 8.5, 'Status', ha='center', fontweight='bold', fontsize=11)
    status_text = """• Claims: 10
• Experiments: 4
• Confidence: 0.23
• Phase: Discovery
• Timeline: 55d"""
    ax.text(15.2, 7.3, status_text, ha='center', va='center', fontsize=8)

    plt.tight_layout()
    plt.savefig('/Users/vaquez/Desktop/iris-gate/cbd_system_architecture.png',
                dpi=300, bbox_inches='tight')
    print("Architecture diagram saved to: /Users/vaquez/Desktop/iris-gate/cbd_system_architecture.png")
    plt.show()


def create_therapeutic_pipeline_diagram():
    """Create therapeutic development pipeline diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(7, 9.5, 'CBD Therapeutic Development Pipeline',
            fontsize=16, fontweight='bold', ha='center')

    # Pipeline phases
    phases = [
        ('Discovery', 2, 8, 3, 1.2, '#FFE4E1'),
        ('Preclinical', 7, 8, 3, 1.2, '#E6F3FF'),
        ('Phase I', 12, 8, 2.5, 1.2, '#F0FFF0'),
        ('Phase II/III', 7, 2, 3, 1.2, '#FFF8DC')
    ]

    for name, x, y, w, h, color in phases:
        box = FancyBboxPatch((x-w/2, y-h/2), w, h,
                            boxstyle="round,pad=0.15",
                            facecolor=color,
                            edgecolor='black', linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center',
                fontsize=14, fontweight='bold')

    # Key experiments for each phase
    experiments = {
        'Discovery': [
            'VDAC1 Binding Assay',
            'Selectivity Validation',
            'Mechanism Confirmation'
        ],
        'Preclinical': [
            'TRPV4 Biomarker',
            'Pulse Dosing Study',
            'Safety Profile'
        ],
        'Phase I': [
            'First-in-Human',
            'Dose Escalation',
            'Biomarker Validation'
        ],
        'Phase II/III': [
            'Efficacy Studies',
            'Optimal Dosing',
            'Patient Stratification'
        ]
    }

    # Add experiment details
    exp_positions = [
        (2, 6.5), (7, 6.5), (12, 6.5), (7, 0.5)
    ]

    for i, ((phase, x_pos, y_pos, _, _, _), (exp_x, exp_y)) in enumerate(zip(phases, exp_positions)):
        exp_list = experiments[phase]
        exp_text = '\n'.join([f'• {exp}' for exp in exp_list])

        exp_box = FancyBboxPatch((exp_x-1.4, exp_y-0.6), 2.8, 1.2,
                                boxstyle="round,pad=0.1",
                                facecolor='white',
                                edgecolor='gray', linewidth=1)
        ax.add_patch(exp_box)
        ax.text(exp_x, exp_y, exp_text, ha='center', va='center', fontsize=9)

    # Add decision gates
    gates = [
        (4.5, 8, 'Gate 1\nBinding &\nSelectivity'),
        (9.5, 8, 'Gate 2\nSafety &\nBiomarker'),
        (7, 5, 'Gate 3\nEfficacy &\nDosing')
    ]

    for x, y, text in gates:
        diamond = patches.RegularPolygon((x, y), 4, radius=0.5,
                                       orientation=np.pi/4,
                                       facecolor='yellow',
                                       edgecolor='red', linewidth=2)
        ax.add_patch(diamond)
        ax.text(x, y-1, text, ha='center', va='center',
                fontsize=8, fontweight='bold')

    # Add timeline
    ax.text(7, 4, 'Timeline: Discovery (90d) → Preclinical (180d) → Phase I (365d)',
            ha='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))

    # Add arrows
    arrows = [
        ((3.5, 8), (4, 8)),
        ((5, 8), (5.5, 8)),
        ((8.5, 8), (9, 8)),
        ((10, 8), (10.5, 8)),
        ((12, 7.4), (9, 5.5)),
        ((7, 4.5), (7, 3.2))
    ]

    for (x1, y1), (x2, y2) in arrows:
        ax.arrow(x1, y1, x2-x1, y2-y1, head_width=0.15, head_length=0.2,
                fc='black', ec='black')

    plt.tight_layout()
    plt.savefig('/Users/vaquez/Desktop/iris-gate/cbd_therapeutic_pipeline.png',
                dpi=300, bbox_inches='tight')
    print("Pipeline diagram saved to: /Users/vaquez/Desktop/iris-gate/cbd_therapeutic_pipeline.png")
    plt.show()


if __name__ == "__main__":
    create_architecture_diagram()
    create_therapeutic_pipeline_diagram()