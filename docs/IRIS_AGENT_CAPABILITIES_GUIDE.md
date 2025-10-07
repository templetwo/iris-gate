# IRIS Agent Capabilities and Trigger Conditions Guide

**Comprehensive Documentation for IRIS Methodology Agent Integration**

This guide provides complete specifications for all 6 IRIS agents, their capabilities, trigger conditions, input/output specifications, and integration patterns within the S1→S8 pipeline.

## Architecture Overview

The IRIS agent system implements a sophisticated methodology for convergence analysis, bioelectric simulation, and wet-lab protocol generation through six specialized agents:

```
┌─────────────────────────────────────────────────────────────────┐
│                    S1→S8 IRIS Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│ S1-S4: Multi-Mirror Chamber Execution                          │
│   ↓                                                             │
│ Convergence Validator → S4 Extractor → Simulation Runner       │
│   ↓                      ↓              ↓                       │
│ Protocol Translator ← Cross-Mirror Analyzer ← Session Orchestra │
└─────────────────────────────────────────────────────────────────┘
```

### Core Principles

1. **Multi-Mirror Consensus**: All decisions based on agreement across multiple AI mirrors
2. **Pressure Monitoring**: Continuous monitoring prevents system overload
3. **Validation Gates**: Quality checkpoints at every workflow stage
4. **Uncertainty Quantification**: Statistical confidence in all predictions
5. **Wet-Lab Integration**: Direct translation to actionable protocols

---

## Agent 1: Convergence Validator

### Purpose and Scope

Analyzes cross-mirror agreement and validates convergence in S1-S4 states to ensure consensus quality before proceeding to simulation.

### Core Capabilities

1. **Multi-Mirror Consensus Analysis**
   - Statistical validation of agreement across AI mirrors
   - Weighted aggregation based on mirror performance history
   - Real-time convergence monitoring during chamber execution

2. **Outlier Detection and Flagging**
   - Configurable sigma thresholds for outlier identification
   - Systematic bias detection across mirror responses
   - Contradiction identification with severity scoring

3. **Agreement Scoring and Thresholds**
   - Quantitative convergence scoring (0.0-1.0 scale)
   - Configurable minimum agreement thresholds
   - Standard deviation monitoring for response consistency

4. **Statistical Validation**
   - Confidence interval calculation for consensus measures
   - Significance testing for convergence claims
   - Cross-validation using bootstrap methods

### Trigger Conditions

#### Automatic Triggers
```yaml
# File-based trigger after chamber completion
pattern: "vault/scrolls/**/*.md"
min_files: 3
condition: "cross_mirror_analysis_needed"
priority: 15
execution: automatic

# Pipeline stage trigger
stage: "post_chamber_completion"
condition: "all_mirrors_completed"
priority: 12
execution: automatic
```

#### Manual Triggers
```yaml
# Command-line validation
command: "/validate-convergence"
args: ["chamber_id", "vault_path", "threshold"]
priority: 10
execution: on_demand

# Example usage:
# /validate-convergence S4 ./vault 0.75
```

#### Integration Triggers
```yaml
# Orchestrator integration
prerequisite: "session-orchestrator"
condition: "chamber_completion_detected"
priority: 15
execution: workflow_driven
```

### Input Specifications

1. **Required Inputs**
   - `vault_path`: Path to IRIS vault containing scroll outputs
   - `chamber_id`: Target chamber for analysis (S1, S2, S3, or S4)
   - `convergence_threshold`: Minimum agreement score (0.0-1.0)

2. **Optional Inputs**
   - `mirror_weights`: Custom weighting for mirror contributions
   - `outlier_threshold`: Sigma threshold for outlier detection
   - `output_format`: Report format preference

3. **File Dependencies**
   ```
   vault/scrolls/IRIS_*/S*.md       # Mirror outputs
   vault/meta/IRIS_*_S*.json        # Metadata files
   config/convergence_thresholds.yaml  # Configuration
   ```

### Output Specifications

1. **Primary Outputs**
   ```
   analysis/convergence/consensus_report_S4.md     # Human-readable report
   analysis/convergence/statistical_summary.json  # Machine-readable data
   analysis/convergence/outlier_flags.json        # Flagged responses
   analysis/convergence/visualization_plots.png   # Agreement visualizations
   ```

2. **Report Structure**
   ```markdown
   # Convergence Analysis Report: Chamber S4

   ## Executive Summary
   - Agreement Score: 0.82 (threshold: 0.70) ✓
   - Mirrors Analyzed: 5
   - Outliers Detected: 1
   - Recommendation: PROCEED to S4 extraction

   ## Statistical Analysis
   - Mean Agreement: 0.82 ± 0.05
   - Standard Deviation: 0.12 (threshold: 0.30) ✓
   - Confidence Interval: [0.75, 0.89] at 95%

   ## Mirror Performance
   | Mirror | Agreement | Weight | Status |
   |--------|-----------|--------|--------|
   | anthropic | 0.89 | 1.0 | ✓ |
   | openai | 0.85 | 0.9 | ✓ |
   | xai | 0.78 | 0.8 | ✓ |
   | google | 0.71 | 0.7 | ✓ |
   | deepseek | 0.45 | 0.3 | ⚠ OUTLIER |
   ```

### Configuration Parameters

```yaml
convergence_thresholds:
  agreement_score_min: 0.70      # Minimum consensus required
  std_deviation_max: 0.30        # Maximum response variability
  outlier_sigma_threshold: 2.0   # Statistical outlier detection
  contradiction_threshold: 0.25  # Maximum contradiction level

pressure_monitoring:
  max_pressure: 2.0              # Pressure threshold
  pressure_check_frequency: 3    # Check every N operations
  auto_pause_on_exceed: true     # Auto-pause on threshold breach

output_formats:
  - consensus_report_markdown    # Human-readable reports
  - statistical_summary_json     # Machine-readable data
  - visualization_plots         # Agreement visualizations
  - outlier_flags_json          # Detailed outlier analysis
```

### Integration Points

1. **Claude Code Hooks**
   - `post_multi_file_analysis`: Triggered after analyzing multiple files
   - `pre_consensus_validation`: Called before consensus decisions
   - `on_convergence_failure`: Handles failed convergence scenarios

2. **Orchestrator Integration**
   - Queue Priority: 15 (high priority)
   - Depends On: `session-orchestrator`
   - Triggers: `s4-extractor`, `cross-mirror-analyzer`

3. **Error Handling**
   - Automatic retry on transient failures
   - Graceful degradation with reduced thresholds
   - Human intervention escalation for critical failures

### Usage Examples

```bash
# Validate S4 convergence with default thresholds
/validate-convergence S4 ./vault 0.75

# Analyze convergence for all chambers
python scripts/convergence_validator.py --session IRIS_20251007_143022 --all-chambers

# Generate convergence report only (no validation)
python scripts/convergence_validator.py --report-only --session IRIS_20251007_143022

# Monitor convergence in real-time
python scripts/convergence_validator.py --monitor --vault ./vault --watch

# Integration with orchestrator
echo '{"role": "convergence-validator", "chamber": "S4", "vault_path": "./vault"}' | \
  python scripts/job_queue.py enqueue --priority 15
```

---

## Agent 2: S4 Extractor

### Purpose and Scope

Extracts bioelectric priors from converged S4 states for Monte Carlo simulation, transforming theoretical predictions into quantitative parameters.

### Core Capabilities

1. **S4 State Parsing and Validation**
   - Structured parsing of S4 chamber outputs
   - Schema validation against bioelectric parameter specifications
   - Quality assessment of extracted parameters

2. **Bioelectric Parameter Extraction**
   - Center stability and size measurements
   - Membrane potential and rhythm characteristics
   - Aperture permeability and resistance calculations

3. **Prior Distribution Modeling**
   - Statistical distribution fitting for uncertain parameters
   - Confidence interval propagation from S4 states
   - Noise model application for conservative estimates

4. **Mechanism Mapping Application**
   - Translation from theoretical to measurable parameters
   - Unit conversion and scaling factors
   - Cross-parameter consistency checking

5. **Confidence Weighting by Mirror**
   - Mirror-specific confidence adjustments
   - Historical performance-based weighting
   - Outlier exclusion and robust estimation

6. **Simulation Input Generation**
   - JSON format compatible with Monte Carlo simulator
   - YAML parameter files for human review
   - Validation of simulation-ready outputs

### Trigger Conditions

#### Convergence-Based Trigger
```yaml
prerequisite: "convergence-validator"
condition: "s4_convergence_validated"
min_agreement_score: 0.70
priority: 20
execution: automatic_on_convergence
```

#### Direct Trigger
```yaml
command: "/extract-s4-priors"
args: ["vault_path", "output_format"]
priority: 15
execution: on_demand

# Example usage:
# /extract-s4-priors ./vault simulation_ready
```

#### Simulation Pipeline Trigger
```yaml
stage: "pre_simulation"
condition: "s4_states_available"
priority: 18
execution: workflow_driven
```

### Input Specifications

1. **Required Inputs**
   - `vault_path`: Path to IRIS vault with S4 outputs
   - `convergence_report`: Path to convergence validation results
   - `output_format`: Desired output format (json, yaml, both)

2. **Optional Inputs**
   - `mirror_weights`: Custom confidence weights per mirror
   - `parameter_subset`: Specific parameters to extract
   - `noise_model`: Conservative, standard, or optimistic uncertainty

3. **File Dependencies**
   ```
   vault/scrolls/**/*S4*.md                    # S4 chamber outputs
   vault/meta/**/*S4*.json                     # S4 metadata
   analysis/convergence/s4_consensus.json     # Convergence results
   sandbox/engines/mechanisms/s4_to_bioelectric.yaml  # Mapping rules
   sandbox/specs/s4_state_schema.json         # Validation schema
   ```

### Output Specifications

1. **Primary Outputs**
   ```
   sandbox/states/s4_state.TIMESTAMP.json     # Simulation-ready parameters
   sandbox/priors/extracted_TIMESTAMP.yaml    # Human-readable priors
   analysis/extraction/parameter_summary.json # Extraction metadata
   analysis/extraction/extraction_report.md   # Quality assessment
   ```

2. **Parameter Structure**
   ```json
   {
     "extraction_metadata": {
       "timestamp": "2025-10-07T14:30:22Z",
       "vault_path": "./vault",
       "convergence_score": 0.82,
       "mirrors_used": ["anthropic", "openai", "xai", "google"],
       "extraction_quality": "high"
     },
     "bioelectric_parameters": {
       "center_stability": {
         "value": 0.85,
         "confidence_interval": [0.78, 0.92],
         "units": "normalized",
         "distribution": "beta(8.5, 1.5)"
       },
       "center_size_mm": {
         "value": 2.3,
         "confidence_interval": [2.0, 2.6],
         "units": "millimeters",
         "distribution": "normal(2.3, 0.15)"
       },
       "center_depol_mv": {
         "value": -45.2,
         "confidence_interval": [-50.1, -40.3],
         "units": "millivolts",
         "distribution": "normal(-45.2, 2.5)"
       },
       "rhythm_freq_hz": {
         "value": 0.125,
         "confidence_interval": [0.10, 0.15],
         "units": "hertz",
         "distribution": "lognormal(-2.08, 0.19)"
       },
       "rhythm_coherence": {
         "value": 0.72,
         "confidence_interval": [0.65, 0.79],
         "units": "normalized",
         "distribution": "beta(7.2, 2.8)"
       },
       "aperture_permeability": {
         "value": 0.45,
         "confidence_interval": [0.35, 0.55],
         "units": "normalized",
         "distribution": "uniform(0.35, 0.55)"
       }
     },
     "optional_parameters": {
       "rhythm_velocity_um_s": {
         "value": 12.5,
         "confidence_interval": [8.0, 17.0],
         "units": "micrometers/second",
         "distribution": "gamma(6.25, 2.0)"
       },
       "membrane_resistance": {
         "value": 850.0,
         "confidence_interval": [750.0, 950.0],
         "units": "ohm*cm^2",
         "distribution": "normal(850.0, 50.0)"
       }
     }
   }
   ```

### Configuration Parameters

```yaml
extraction_settings:
  confidence_weight_mode: "mirror_based"    # How to weight mirror contributions
  parameter_mapping_strict: true           # Strict schema validation
  validation_schema: "sandbox/specs/s4_state_schema.json"
  default_noise_model: "gaussian_conservative"  # Conservative uncertainty

bioelectric_parameters:
  required_fields:                          # Must be extracted
    - center_stability
    - center_size_mm
    - center_depol_mv
    - rhythm_freq_hz
    - rhythm_coherence
    - aperture_permeability

  optional_fields:                          # Extracted if available
    - rhythm_velocity_um_s
    - aperture_dilation_rate
    - membrane_resistance

output_formats:
  - simulation_ready_json                   # Monte Carlo simulator input
  - parameter_summary_yaml                  # Human-readable summary
  - confidence_weighted_priors             # Uncertainty-aware parameters
  - extraction_report_md                    # Quality and methodology report
```

### Integration Points

1. **Claude Code Hooks**
   - `post_convergence_validation`: Triggered after convergence validation
   - `pre_simulation_setup`: Called before simulation initialization
   - `on_extraction_complete`: Handles successful parameter extraction

2. **Orchestrator Integration**
   - Queue Priority: 20 (high priority)
   - Depends On: `convergence-validator`
   - Triggers: `simulation-runner`

3. **Data Pipeline Integration**
   - Input validation using JSON Schema
   - Automatic unit conversion and scaling
   - Quality metrics tracking and reporting

### Usage Examples

```bash
# Extract S4 priors after convergence validation
/extract-s4-priors ./vault simulation_ready

# Extract specific parameter subset
python scripts/s4_extractor.py --vault ./vault --parameters center_stability,rhythm_freq_hz

# Generate both JSON and YAML outputs
python scripts/s4_extractor.py --vault ./vault --format both --output-dir sandbox/states/

# Validate extraction quality
python scripts/s4_extractor.py --validate-only --input sandbox/states/s4_state.latest.json

# Integration example
python sandbox/cli/extract_s4_states.py --convergence-report analysis/convergence/s4_consensus.json \
  --output sandbox/states/s4_state.$(date +%Y%m%d_%H%M%S).json
```

---

## Agent 3: Simulation Runner

### Purpose and Scope

Executes Monte Carlo simulations for prediction validation with uncertainty quantification, providing statistical confidence in bioelectric predictions.

### Core Capabilities

1. **Monte Carlo Execution Coordination**
   - Parallel simulation execution with configurable worker pools
   - Dynamic load balancing across available resources
   - Progress monitoring and intermediate result caching

2. **Bioelectric State Simulation**
   - VM-Ca-GJ (Voltage-Membrane-Calcium-Gap Junction) modeling
   - State evolution over configurable time periods
   - Multi-scale modeling from cellular to tissue level

3. **Perturbation Effect Modeling**
   - Dose-response curve generation
   - Intervention effect quantification
   - Control condition baseline establishment

4. **Outcome Prediction with Uncertainty**
   - Confidence interval calculation for all predictions
   - Probability distributions for outcome variables
   - Risk assessment and sensitivity analysis

5. **Statistical Validation and CI**
   - Convergence testing for Monte Carlo estimates
   - Bootstrap confidence interval calculation
   - Significance testing for predicted effects

6. **Cross-Condition Comparison**
   - Comparative analysis across experimental conditions
   - Effect size quantification with confidence bounds
   - Statistical power analysis for experimental design

### Trigger Conditions

#### S4 Extraction Trigger
```yaml
prerequisite: "s4-extractor"
condition: "priors_extracted"
min_mirrors: 3
priority: 25
execution: automatic_after_extraction
```

#### Direct Simulation Request
```yaml
command: "/run-simulation"
args: ["plan_path", "n_runs", "output_dir"]
priority: 20
execution: on_demand

# Example usage:
# /run-simulation sandbox/runs/plans/dose_response.yaml 1000 outputs/
```

#### Experimental Design Trigger
```yaml
stage: "hypothesis_testing"
condition: "experiment_plan_ready"
priority: 22
execution: workflow_driven
```

### Input Specifications

1. **Required Inputs**
   - `s4_state_file`: Path to extracted S4 bioelectric parameters
   - `simulation_plan`: YAML file defining simulation parameters
   - `n_runs`: Number of Monte Carlo iterations
   - `output_directory`: Path for simulation results

2. **Optional Inputs**
   - `perturbation_kit`: Specific interventions to simulate
   - `readout_specifications`: Outcome measures to track
   - `random_seed`: For reproducible simulations
   - `max_workers`: Parallel execution limit

3. **File Dependencies**
   ```
   sandbox/states/s4_state.*.json              # Extracted parameters
   sandbox/specs/perturbation_kits.yaml        # Intervention definitions
   sandbox/specs/readouts.yaml                 # Outcome measures
   sandbox/engines/mechanisms/**/*.yaml        # Simulation mechanics
   sandbox/runs/plans/**/*.yaml                # Simulation plans
   ```

### Output Specifications

1. **Primary Outputs**
   ```
   sandbox/runs/outputs/RUN_TIMESTAMP/
   ├── simulation_results.json                 # Complete results
   ├── outcome_distributions.json              # Probability distributions
   ├── timeseries_data.json                   # Temporal evolution
   ├── statistical_summary.json               # Summary statistics
   ├── convergence_diagnostics.json           # Monte Carlo convergence
   ├── visualization_plots.png                # Result visualizations
   └── simulation_report.md                   # Human-readable report
   ```

2. **Results Structure**
   ```json
   {
     "simulation_metadata": {
       "run_id": "RUN_20251007_143022",
       "timestamp": "2025-10-07T14:30:22Z",
       "n_runs": 1000,
       "convergence_achieved": true,
       "total_runtime_seconds": 245.7,
       "s4_source": "sandbox/states/s4_state.20251007_143022.json"
     },
     "baseline_predictions": {
       "regeneration_probability": {
         "mean": 0.72,
         "confidence_interval_95": [0.68, 0.76],
         "standard_error": 0.02,
         "distribution": "beta(72, 28)"
       },
       "regeneration_time_days": {
         "mean": 14.2,
         "confidence_interval_95": [12.8, 15.6],
         "standard_error": 0.7,
         "distribution": "lognormal(2.65, 0.21)"
       },
       "pattern_fidelity": {
         "mean": 0.85,
         "confidence_interval_95": [0.81, 0.89],
         "standard_error": 0.02,
         "distribution": "beta(85, 15)"
       }
     },
     "intervention_effects": {
       "gap_junction_inhibitor": {
         "dose_response_curve": {
           "doses_um": [0, 10, 25, 50, 100],
           "regeneration_probability": [0.72, 0.65, 0.45, 0.28, 0.15],
           "confidence_intervals": [
             [0.68, 0.76], [0.60, 0.70], [0.40, 0.50], [0.23, 0.33], [0.11, 0.19]
           ]
         },
         "ec50": {
           "value": 42.5,
           "confidence_interval": [38.2, 46.8],
           "units": "micromolar"
         },
         "maximum_effect": {
           "value": 0.79,
           "confidence_interval": [0.74, 0.84],
           "description": "fraction_reduction_from_baseline"
         }
       }
     },
     "statistical_validation": {
       "monte_carlo_convergence": {
         "effective_sample_size": 987,
         "r_hat": 1.002,
         "converged": true
       },
       "intervention_significance": {
         "gap_junction_inhibitor": {
           "p_value": 2.3e-8,
           "effect_size_cohens_d": 1.45,
           "statistical_power": 0.99
         }
       }
     }
   }
   ```

### Configuration Parameters

```yaml
simulation_settings:
  default_n_runs: 500                      # Default Monte Carlo iterations
  max_n_runs: 5000                         # Maximum allowed iterations
  timeout_per_run_sec: 30                  # Individual simulation timeout
  parallel_execution: true                 # Enable parallel processing
  max_workers: 4                           # Maximum parallel workers

validation_gates:
  convergence_check: true                  # Require MC convergence
  statistical_significance: 0.05           # P-value threshold
  min_effect_size: 0.1                     # Minimum meaningful effect
  prediction_ci_width_max: 0.4             # Maximum CI width

output_requirements:
  timeseries_stats: true                   # Temporal evolution data
  outcome_distributions: true              # Full probability distributions
  uncertainty_quantification: true        # Comprehensive uncertainty
  consensus_predictions: true              # Cross-run consensus
  visualization_plots: true                # Automatic plot generation

resource_limits:
  max_memory_gb: 8                         # Memory limit per worker
  max_cpu_cores: 4                         # CPU core limit
  max_runtime_minutes: 60                  # Total runtime limit
```

### Integration Points

1. **Claude Code Hooks**
   - `pre_simulation_execution`: Called before simulation start
   - `simulation_progress_update`: Periodic progress reports
   - `post_simulation_completion`: Handles simulation results

2. **Orchestrator Integration**
   - Queue Priority: 25 (high priority)
   - Depends On: `s4-extractor`
   - Triggers: `protocol-translator`, `cross-mirror-analyzer`

3. **Resource Management**
   - Dynamic worker pool scaling
   - Memory usage monitoring
   - Automatic cleanup of temporary files

### Usage Examples

```bash
# Run simulation with extracted S4 priors
/run-simulation sandbox/runs/plans/bioelectric_test.yaml 1000 outputs/

# Execute dose-response analysis
python scripts/simulation_runner.py --plan sandbox/runs/plans/dose_response.yaml \
  --n-runs 2000 --parallel --max-workers 8

# Validate prediction uncertainty
python scripts/simulation_runner.py --validate-uncertainty \
  --results sandbox/runs/outputs/RUN_20251007_143022/simulation_results.json

# Monitor simulation progress
python scripts/simulation_runner.py --monitor \
  --run-id RUN_20251007_143022 --watch

# Integration example
python sandbox/engines/simulators/monte_carlo.py \
  --s4-state sandbox/states/s4_state.20251007_143022.json \
  --perturbations sandbox/specs/perturbation_kits.yaml \
  --output sandbox/runs/outputs/RUN_$(date +%Y%m%d_%H%M%S)/
```

---

## Agent 4: Protocol Translator

### Purpose and Scope

Translates simulation predictions into actionable wet-lab protocols, bridging computational predictions with experimental validation.

### Core Capabilities

1. **Prediction to Protocol Translation**
   - Automated translation from simulation results to experimental procedures
   - Template-based protocol generation with organism-specific adaptations
   - Material and equipment requirement specification

2. **Experimental Design Generation**
   - Statistical power analysis for adequate sample sizes
   - Control condition design and randomization schemes
   - Outcome measurement specification and timing

3. **Material and Method Specification**
   - Detailed reagent lists with concentrations and suppliers
   - Equipment requirements and calibration procedures
   - Step-by-step experimental protocols with timing

4. **Statistical Power Analysis**
   - Sample size calculation for desired statistical power
   - Effect size estimation from simulation results
   - Multiple comparison correction planning

5. **Control Condition Design**
   - Negative and positive control specification
   - Vehicle control design for interventions
   - Sham procedure development for complex interventions

6. **Timeline and Resource Planning**
   - Experimental timeline with milestone checkpoints
   - Resource allocation and cost estimation
   - Personnel requirement assessment

### Trigger Conditions

#### Simulation Completion Trigger
```yaml
prerequisite: "simulation-runner"
condition: "predictions_validated"
min_confidence: 0.80
priority: 30
execution: automatic_after_simulation
```

#### Direct Protocol Request
```yaml
command: "/generate-protocol"
args: ["simulation_results", "experiment_type", "organism"]
priority: 25
execution: on_demand

# Example usage:
# /generate-protocol simulation_results.json regeneration planaria
```

#### Wet-Lab Handoff Trigger
```yaml
stage: "experiment_handoff"
condition: "predictions_ready"
priority: 28
execution: workflow_driven
```

### Input Specifications

1. **Required Inputs**
   - `simulation_results`: Path to Monte Carlo simulation output
   - `experiment_type`: Type of experimental validation (regeneration, development, etc.)
   - `organism`: Target organism (planaria, zebrafish, xenopus)
   - `confidence_threshold`: Minimum prediction confidence required

2. **Optional Inputs**
   - `protocol_template`: Custom protocol template
   - `resource_constraints`: Available equipment and budget limits
   - `timeline_constraints`: Maximum experiment duration
   - `sample_size_override`: Manual sample size specification

3. **File Dependencies**
   ```
   sandbox/runs/outputs/**/*.json              # Simulation results
   analysis/convergence/**/*.json              # Convergence data
   templates/protocols/**/*.md                 # Protocol templates
   config/wet_lab_specs.yaml                  # Lab specifications
   config/organism_protocols.yaml             # Organism-specific protocols
   ```

### Output Specifications

1. **Primary Outputs**
   ```
   protocols/generated/PROTOCOL_TIMESTAMP/
   ├── detailed_protocol.md                    # Complete experimental protocol
   ├── materials_list.csv                      # Reagents and equipment
   ├── experimental_timeline.yaml             # Timeline and milestones
   ├── power_analysis_report.md               # Statistical design
   ├── statistical_plan.json                  # Analysis plan
   ├── control_conditions.md                  # Control specifications
   └── troubleshooting_guide.md               # Common issues and solutions
   ```

2. **Protocol Structure**
   ```markdown
   # Bioelectric Regeneration Protocol: Gap Junction Modulation in Planaria

   **Protocol ID:** PROTO_20251007_143022
   **Generated:** 2025-10-07T14:30:22Z
   **Based on Simulation:** RUN_20251007_143022
   **Organism:** Dugesia japonica (planaria)
   **Experiment Type:** Regeneration with intervention

   ## Executive Summary

   This protocol tests the prediction that gap junction inhibition reduces regeneration
   probability by 0.57 ± 0.08 (95% CI: 0.41-0.73) with EC50 = 42.5 μM. The experiment
   requires 120 animals across 6 conditions with 20 animals per group for 80% power
   to detect the predicted effect (α = 0.05).

   ## Materials and Equipment

   ### Reagents
   - 18β-Glycyrrhetinic acid (gap junction inhibitor) - Sigma G8503
   - DMSO (vehicle control) - Sigma D2650
   - Instant Ocean artificial seawater - Aqueon
   - Methylene blue (0.001% stock) - Sigma M9140

   ### Equipment
   - 6-well tissue culture plates - Corning 3516
   - Stereomicroscope with imaging - Leica M125
   - Precision pipettes (1-1000 μL) - Gilson Pipetman
   - Temperature-controlled incubator (18°C ± 1°C)

   ## Experimental Design

   ### Groups and Sample Sizes
   | Group | Condition | Concentration | N | Expected Response |
   |-------|-----------|---------------|---|-------------------|
   | 1 | Control | Vehicle only | 20 | 0.72 ± 0.04 |
   | 2 | Low dose | 10 μM | 20 | 0.65 ± 0.05 |
   | 3 | Medium dose | 25 μM | 20 | 0.45 ± 0.05 |
   | 4 | High dose | 50 μM | 20 | 0.28 ± 0.05 |
   | 5 | Very high | 100 μM | 20 | 0.15 ± 0.04 |
   | 6 | Positive control | H2O2 (0.3%) | 20 | 0.25 ± 0.05 |

   ### Randomization
   - Animals randomized to groups using block randomization (block size 6)
   - Treatment assignment blinded to experimenter during data collection
   - Photography and scoring performed by different individuals

   ## Protocol Steps

   ### Day 0: Preparation and Amputation
   1. **Animal Selection** (30 min)
      - Select healthy planaria 8-12 mm in length
      - Fast animals for 24h prior to amputation
      - Randomize to treatment groups

   2. **Amputation Procedure** (60 min)
      - Anesthetize animals on ice for 5 min
      - Perform clean transverse cuts at 50% body length
      - Place posterior fragments in assigned treatment wells
      - Allow 2h recovery before treatment

   3. **Treatment Application** (30 min)
      - Prepare fresh treatment solutions in artificial seawater
      - Apply 2 mL treatment solution per well
      - Begin incubation at 18°C ± 1°C

   ### Days 1-14: Monitoring and Maintenance
   1. **Daily Observations** (15 min/day)
      - Record survival and general health
      - Note any abnormal behavior or morphology
      - Change treatment solutions every 48h

   2. **Photography Schedule**
      - Day 0: Post-amputation baseline
      - Days 3, 7, 10, 14: Regeneration progress
      - Use standardized positioning and lighting

   ### Day 14: Final Assessment
   1. **Regeneration Scoring** (45 min)
      - Score regeneration using standard 5-point scale
      - Measure regenerated tissue length
      - Assess pattern fidelity (eyes, pharynx, brain)
      - Record final photographs

   ## Statistical Analysis Plan

   ### Primary Endpoint
   - Binary regeneration success (yes/no at day 14)
   - Analysis: Logistic regression with dose as continuous variable
   - Comparison: Chi-square test for individual dose groups

   ### Secondary Endpoints
   - Time to first regeneration signs (survival analysis)
   - Regenerated tissue length (linear regression)
   - Pattern fidelity score (ordinal regression)

   ### Power Analysis
   - Primary comparison: Control vs. medium dose (25 μM)
   - Expected effect size: 0.27 difference in success rate
   - Power: 80% with α = 0.05, two-tailed test
   - Sample size: 20 per group (including 15% attrition)

   ## Quality Control

   ### Inclusion Criteria
   - Healthy planaria with intact regenerative capacity
   - Clean amputation with minimal tissue damage
   - Survival through day 3 post-amputation

   ### Exclusion Criteria
   - Animals showing signs of disease or stress
   - Contaminated wells or treatment solutions
   - Technical errors in amputation or treatment

   ### Data Integrity
   - Double data entry for all measurements
   - Blinded assessment of regeneration outcomes
   - Photo documentation for all time points
   - Statistical analysis using R with reproducible scripts

   ## Expected Timeline

   | Phase | Duration | Key Milestones |
   |-------|----------|----------------|
   | Preparation | 1 week | Animals acclimated, solutions prepared |
   | Experiment | 2 weeks | Daily monitoring, photo documentation |
   | Analysis | 1 week | Data analysis, report generation |
   | **Total** | **4 weeks** | **Complete experimental cycle** |

   ## Troubleshooting

   ### Common Issues
   - **Low survival rates**: Check water quality, reduce handling stress
   - **Inconsistent regeneration**: Verify amputation technique, standardize cuts
   - **Treatment effects unclear**: Increase sample size, extend observation period

   ### Emergency Procedures
   - Contamination: Isolate affected wells, document thoroughly
   - Equipment failure: Have backup incubator and microscope available
   - Unexpected mortality: Preserve samples for pathological examination

   ## References and Validation

   This protocol is based on simulation predictions from IRIS chamber analysis with
   82% convergence confidence. The experimental design follows established planarian
   regeneration protocols (Reddien & Sánchez Alvarado, 2004; Lobo et al., 2012) with
   statistical power analysis ensuring adequate detection of predicted effects.

   **Simulation Reference:** S4 state extraction from IRIS_20251007_143022
   **Validation Standard:** >80% statistical power for primary endpoint
   **Quality Assurance:** Protocol reviewed by wet-lab methodology committee
   ```

### Configuration Parameters

```yaml
protocol_settings:
  template_library: "templates/protocols/"    # Protocol template directory
  organism_defaults:                          # Organism-specific templates
    planaria: "planaria_regeneration_protocol.md"
    zebrafish: "zebrafish_development_protocol.md"
    xenopus: "xenopus_bioelectric_protocol.md"

experimental_parameters:
  min_n_per_group: 10                        # Minimum sample size
  recommended_n_per_group: 20                # Recommended sample size
  power_analysis_target: 0.80                # Target statistical power
  alpha_level: 0.05                          # Significance level

output_formats:
  - detailed_protocol_markdown                # Complete protocol
  - materials_list_csv                       # Equipment and reagents
  - timeline_yaml                            # Experimental timeline
  - power_analysis_report                    # Statistical design
  - statistical_plan_json                    # Analysis specification

handoff_validation:
  require_statistical_power: true            # Verify adequate power
  require_material_availability: false       # Optional availability check
  require_timeline_feasibility: true         # Verify realistic timeline
```

### Integration Points

1. **Claude Code Hooks**
   - `post_simulation_completion`: Triggered after simulation validation
   - `pre_protocol_generation`: Called before protocol creation
   - `on_protocol_handoff`: Handles wet-lab protocol delivery

2. **Orchestrator Integration**
   - Queue Priority: 30 (medium-high priority)
   - Depends On: `simulation-runner`
   - Triggers: `session-orchestrator` (for completion notification)

3. **Wet-Lab Integration**
   - Material availability checking (optional)
   - Timeline feasibility validation
   - Protocol format standardization

### Usage Examples

```bash
# Generate protocol from simulation results
/generate-protocol sandbox/runs/outputs/RUN_20251007_143022/simulation_results.json regeneration planaria

# Create protocol with custom template
python scripts/protocol_translator.py \
  --simulation-results simulation_results.json \
  --template templates/protocols/custom_regeneration.md \
  --organism planaria \
  --output protocols/generated/

# Generate materials list only
python scripts/protocol_translator.py \
  --materials-only \
  --simulation-results simulation_results.json \
  --output materials_list.csv

# Validate protocol feasibility
python scripts/protocol_translator.py \
  --validate-only \
  --protocol protocols/generated/PROTO_20251007_143022/detailed_protocol.md

# Integration example
python scripts/protocol_generator.py \
  --simulation-data sandbox/runs/outputs/RUN_20251007_143022/ \
  --experiment-type regeneration \
  --organism planaria \
  --output protocols/generated/PROTO_$(date +%Y%m%d_%H%M%S)/
```

---

## Agent 5: Session Orchestrator

### Purpose and Scope

Coordinates complete S1→S8 IRIS workflow with pressure monitoring and validation, serving as the master controller for the entire methodology pipeline.

### Core Capabilities

1. **Multi-Stage Pipeline Coordination**
   - Sequential execution of S1→S4 chambers across multiple mirrors
   - Automatic progression through convergence validation and simulation
   - Integration of all specialized agents in proper sequence

2. **Pressure Monitoring and Gating**
   - Real-time pressure tracking across all workflow stages
   - Automatic pause mechanisms when pressure thresholds are exceeded
   - Adaptive pressure management with recovery strategies

3. **Cross-Mirror Session Management**
   - Parallel execution across multiple AI mirrors
   - Load balancing and resource allocation
   - Mirror performance tracking and optimization

4. **Validation Gate Enforcement**
   - Mandatory checkpoints at critical workflow stages
   - Quality thresholds for advancement to next stage
   - Rollback capabilities for failed validations

5. **Progress Tracking and Reporting**
   - Real-time workflow status monitoring
   - Milestone tracking with timestamp logging
   - Progress visualization and reporting

6. **Error Recovery and Retry Logic**
   - Automatic retry mechanisms for transient failures
   - Checkpoint-based recovery from interruptions
   - Graceful degradation under resource constraints

### Trigger Conditions

#### New Session Trigger
```yaml
command: "/start-iris-session"
args: ["plan_path", "mirrors", "chambers"]
priority: 5  # Highest priority
execution: user_initiated

# Example usage:
# /start-iris-session plans/bioelectric_session.yaml --mirrors anthropic,openai,xai,google
```

#### Scheduled Session Trigger
```yaml
schedule: "cron"
condition: "daily_session_check"
priority: 8
execution: automated_schedule
```

#### Recovery Trigger
```yaml
condition: "session_failure_recovery"
priority: 3  # Emergency priority
execution: automatic_on_failure
```

### Input Specifications

1. **Required Inputs**
   - `plan_path`: Path to session plan YAML file
   - `mirrors`: List of AI mirrors to use
   - `chambers`: Chambers to execute (S1, S2, S3, S4)

2. **Optional Inputs**
   - `pressure_threshold`: Custom pressure limit
   - `validation_gates`: Specific gates to enforce
   - `retry_attempts`: Maximum retry count
   - `checkpoint_frequency`: Checkpoint interval

3. **File Dependencies**
   ```
   plans/**/*.yaml                            # Session plans
   config/**/*.yaml                           # Configuration files
   vault/**/*                                 # IRIS vault directory
   config/iris_agents.yaml                    # Agent specifications
   ```

### Output Specifications

1. **Primary Outputs**
   ```
   vault/IRIS_TIMESTAMP_*/                    # Session outputs
   ├── scrolls/                               # Mirror outputs by chamber
   │   ├── IRIS_*_anthropic_*/S1.md
   │   ├── IRIS_*_openai_*/S2.md
   │   └── ...
   ├── meta/                                  # Metadata and metrics
   │   ├── IRIS_*_anthropic_*_S1.json
   │   └── ...
   logs/sessions/SESSION_TIMESTAMP.log        # Session log
   analysis/sessions/SESSION_TIMESTAMP.json   # Session metrics
   ```

2. **Session Status Structure**
   ```json
   {
     "session_metadata": {
       "session_id": "IRIS_20251007_143022",
       "started_at": "2025-10-07T14:30:22Z",
       "plan_path": "plans/bioelectric_session.yaml",
       "mirrors": ["anthropic", "openai", "xai", "google"],
       "chambers_requested": ["S1", "S2", "S3", "S4"],
       "current_stage": "s4_extraction",
       "overall_status": "running"
     },
     "stage_progress": {
       "s1_execution": {
         "status": "completed",
         "started_at": "2025-10-07T14:30:22Z",
         "completed_at": "2025-10-07T14:45:18Z",
         "mirrors_completed": ["anthropic", "openai", "xai", "google"],
         "validation_passed": true
       },
       "s2_execution": {
         "status": "completed",
         "started_at": "2025-10-07T14:45:18Z",
         "completed_at": "2025-10-07T15:02:34Z",
         "mirrors_completed": ["anthropic", "openai", "xai", "google"],
         "validation_passed": true
       },
       "s3_execution": {
         "status": "completed",
         "started_at": "2025-10-07T15:02:34Z",
         "completed_at": "2025-10-07T15:18:56Z",
         "mirrors_completed": ["anthropic", "openai", "xai"],
         "validation_passed": true
       },
       "s4_execution": {
         "status": "completed",
         "started_at": "2025-10-07T15:18:56Z",
         "completed_at": "2025-10-07T15:35:42Z",
         "mirrors_completed": ["anthropic", "openai", "xai", "google"],
         "validation_passed": true
       },
       "convergence_validation": {
         "status": "completed",
         "started_at": "2025-10-07T15:35:42Z",
         "completed_at": "2025-10-07T15:38:15Z",
         "convergence_score": 0.82,
         "validation_passed": true
       },
       "s4_extraction": {
         "status": "running",
         "started_at": "2025-10-07T15:38:15Z",
         "progress": 0.75,
         "estimated_completion": "2025-10-07T15:42:00Z"
       },
       "simulation": {
         "status": "pending",
         "depends_on": "s4_extraction"
       },
       "protocol_translation": {
         "status": "pending",
         "depends_on": "simulation"
       }
     },
     "pressure_monitoring": {
       "current_pressure": 1.8,
       "max_pressure": 2.0,
       "pressure_history": [
         {"timestamp": "2025-10-07T14:30:22Z", "pressure": 0.2},
         {"timestamp": "2025-10-07T14:45:18Z", "pressure": 0.8},
         {"timestamp": "2025-10-07T15:02:34Z", "pressure": 1.2},
         {"timestamp": "2025-10-07T15:18:56Z", "pressure": 1.6},
         {"timestamp": "2025-10-07T15:35:42Z", "pressure": 1.8}
       ],
       "pressure_warnings": 0,
       "auto_pause_events": 0
     },
     "validation_gates": {
       "s1_advance_gate": {"passed": true, "timestamp": "2025-10-07T14:45:18Z"},
       "s2_advance_gate": {"passed": true, "timestamp": "2025-10-07T15:02:34Z"},
       "s3_advance_gate": {"passed": true, "timestamp": "2025-10-07T15:18:56Z"},
       "s4_success_gate": {"passed": true, "timestamp": "2025-10-07T15:35:42Z"}
     },
     "agents_active": ["s4-extractor"],
     "error_log": [],
     "performance_metrics": {
       "total_runtime_seconds": 3140,
       "chamber_execution_time": 2520,
       "validation_time": 153,
       "extraction_time": 467,
       "mirrors_per_minute": 0.95
     }
   }
   ```

### Configuration Parameters

```yaml
session_settings:
  max_concurrent_mirrors: 5                  # Maximum parallel mirrors
  pressure_gate_threshold: 2.0               # Pressure auto-pause threshold
  validation_gate_timeout: 300               # 5 minutes gate timeout
  retry_attempts: 3                          # Maximum retry count
  checkpoint_frequency: "per_chamber"        # Checkpoint timing

monitoring:
  pressure_check_interval: 5                 # Check every N exchanges
  progress_reporting_interval: 30            # Progress reports every 30s
  health_check_frequency: 60                 # Health checks every 60s
  log_level: "INFO"                         # Logging verbosity

gates:
  s1_advance_gate:                           # S1 advancement requirements
    min_mirrors_pass: 2
    max_pressure: 2.0
  s2_advance_gate:                           # S2 advancement requirements
    min_mirrors_pass: 2
    max_pressure: 2.0
  s3_advance_gate:                           # S3 advancement requirements
    min_mirrors_pass: 2
    max_pressure: 2.0
  s4_success_gate:                           # S4 completion requirements
    min_convergence_score: 0.70
    min_mirrors_agree: 3
    max_contradiction_threshold: 0.25
```

### Integration Points

1. **Claude Code Hooks**
   - `session_start`: Called when session begins
   - `chamber_completion`: Triggered after each chamber
   - `pressure_threshold_exceeded`: Handles pressure warnings
   - `session_completion`: Called when session finishes
   - `session_failure`: Handles session failures

2. **Orchestrator Integration**
   - Queue Priority: 5 (highest priority)
   - Depends On: [] (top-level orchestrator)
   - Triggers: All other IRIS agents as needed

3. **Agent Coordination**
   - Dynamic agent spawning based on workflow progress
   - Resource allocation and scheduling
   - Inter-agent communication management

### Usage Examples

```bash
# Start complete S1→S8 session with 4 mirrors
/start-iris-session plans/bioelectric_session.yaml --mirrors anthropic,openai,xai,google

# Resume interrupted session
/start-iris-session --resume IRIS_20251007_143022

# Monitor session progress
/session-status --watch

# Start session with custom pressure threshold
python scripts/iris_agent_coordinator.py --workflow s1-to-s8 \
  --plan plans/bioelectric_session.yaml \
  --pressure-threshold 1.5

# Emergency stop with state preservation
python scripts/iris_agent_coordinator.py --emergency-stop --preserve-state

# Check session health
python scripts/orchestrator_runner.py --status --verbose

# Session with limited mirrors
python scripts/iris_agent_coordinator.py --workflow s1-to-s8 \
  --plan plans/bioelectric_session.yaml \
  --mirrors anthropic,openai

# Integration example
echo '{"workflow": "s1-to-s8", "plan": "plans/bioelectric_session.yaml", "mirrors": ["anthropic", "openai", "xai"]}' | \
  python scripts/job_queue.py enqueue --role session-orchestrator --priority 5
```

---

## Agent 6: Cross Mirror Analyzer

### Purpose and Scope

Performs deep analysis of cross-mirror consensus and handles disagreements, providing advanced consensus validation and mirror performance profiling.

### Core Capabilities

1. **Advanced Consensus Algorithms**
   - Weighted voting with historical performance weighting
   - Bayesian aggregation with uncertainty propagation
   - Cluster consensus detection for emergent agreement patterns
   - Outlier-robust mean calculation with adaptive thresholds

2. **Disagreement Pattern Analysis**
   - Systematic disagreement classification and severity scoring
   - Temporal pattern detection in mirror disagreements
   - Root cause analysis for persistent disagreements
   - Recommendation generation for disagreement resolution

3. **Mirror Performance Profiling**
   - Individual mirror accuracy and consistency tracking
   - Performance trends and drift detection
   - Comparative analysis across different chamber types
   - Mirror specialization identification

4. **Bias Detection and Correction**
   - Systematic bias identification across mirrors
   - Temporal drift detection and correction
   - Cross-validation with historical data
   - Bias correction algorithm application

5. **Meta-Analysis Across Sessions**
   - Long-term pattern analysis across multiple sessions
   - Performance trend identification and prediction
   - Mirror reliability scoring and confidence adjustment
   - System-wide optimization recommendations

6. **Recommendation Generation**
   - Mirror selection optimization for future sessions
   - Threshold adjustment recommendations
   - Workflow improvement suggestions
   - Quality assurance enhancement proposals

### Trigger Conditions

#### Convergence Analysis Trigger
```yaml
prerequisite: "convergence-validator"
condition: "consensus_analysis_needed"
priority: 18
execution: automatic_after_convergence
```

#### Disagreement Detection Trigger
```yaml
condition: "high_disagreement_detected"
threshold: 0.30
priority: 12
execution: automatic_on_disagreement
```

#### Meta-Analysis Trigger
```yaml
command: "/analyze-mirror-performance"
args: ["time_period", "analysis_type"]
priority: 15
execution: on_demand

# Example usage:
# /analyze-mirror-performance last_30_days bias_detection
```

### Input Specifications

1. **Required Inputs**
   - `convergence_results`: Path to convergence validation outputs
   - `session_history`: Historical session data for comparison
   - `analysis_type`: Type of analysis to perform

2. **Optional Inputs**
   - `time_window`: Time period for meta-analysis
   - `mirror_subset`: Specific mirrors to analyze
   - `disagreement_threshold`: Custom disagreement detection threshold
   - `bias_sensitivity`: Bias detection sensitivity level

3. **File Dependencies**
   ```
   vault/**/*.json                            # All session metadata
   analysis/convergence/**/*.json             # Convergence results
   analysis/sessions/**/*.json                # Session summaries
   config/mirror_profiles.yaml               # Mirror configurations
   analysis/historical/mirror_performance.json  # Historical data
   ```

### Output Specifications

1. **Primary Outputs**
   ```
   analysis/consensus/ANALYSIS_TIMESTAMP/
   ├── consensus_network_diagram.png          # Network analysis visualization
   ├── disagreement_heatmap.png              # Disagreement pattern visualization
   ├── mirror_performance_dashboard.html     # Interactive performance dashboard
   ├── bias_detection_report.md              # Systematic bias analysis
   ├── recommendations.json                  # System optimization recommendations
   ├── consensus_algorithms_comparison.json  # Algorithm performance comparison
   └── meta_analysis_summary.md              # Long-term trend analysis
   ```

2. **Analysis Results Structure**
   ```json
   {
     "analysis_metadata": {
       "analysis_id": "ANALYSIS_20251007_143022",
       "timestamp": "2025-10-07T14:30:22Z",
       "analysis_type": "comprehensive_consensus",
       "time_window": "last_30_days",
       "sessions_analyzed": 15,
       "mirrors_analyzed": ["anthropic", "openai", "xai", "google", "deepseek"]
     },
     "consensus_quality": {
       "overall_agreement_score": 0.78,
       "agreement_trend": "stable",
       "consensus_stability": 0.85,
       "algorithm_performance": {
         "weighted_voting": {"accuracy": 0.82, "robustness": 0.79},
         "bayesian_aggregation": {"accuracy": 0.85, "robustness": 0.88},
         "cluster_consensus": {"accuracy": 0.79, "robustness": 0.75},
         "outlier_robust_mean": {"accuracy": 0.83, "robustness": 0.92}
       }
     },
     "mirror_performance": {
       "anthropic": {
         "overall_score": 0.91,
         "consistency": 0.88,
         "accuracy": 0.93,
         "response_quality": 0.89,
         "chamber_specialization": {
           "S1": 0.89, "S2": 0.92, "S3": 0.94, "S4": 0.88
         },
         "bias_indicators": {
           "systematic_bias": 0.05,
           "temporal_drift": 0.02,
           "topic_bias": 0.03
         },
         "performance_trend": "improving",
         "recommendations": [
           "Excellent overall performance",
           "Strong S3 specialization",
           "Monitor S4 consistency"
         ]
       },
       "openai": {
         "overall_score": 0.85,
         "consistency": 0.82,
         "accuracy": 0.88,
         "response_quality": 0.84,
         "chamber_specialization": {
           "S1": 0.91, "S2": 0.85, "S3": 0.81, "S4": 0.84
         },
         "bias_indicators": {
           "systematic_bias": 0.08,
           "temporal_drift": 0.04,
           "topic_bias": 0.07
         },
         "performance_trend": "stable",
         "recommendations": [
           "Strong S1 performance",
           "Monitor topic bias in bioelectric discussions",
           "Consider additional validation for S3 responses"
         ]
       },
       "deepseek": {
         "overall_score": 0.62,
         "consistency": 0.58,
         "accuracy": 0.65,
         "response_quality": 0.61,
         "chamber_specialization": {
           "S1": 0.67, "S2": 0.63, "S3": 0.58, "S4": 0.59
         },
         "bias_indicators": {
           "systematic_bias": 0.18,
           "temporal_drift": 0.12,
           "topic_bias": 0.22
         },
         "performance_trend": "declining",
         "recommendations": [
           "Significant systematic bias detected",
           "Consider reduced weighting or exclusion",
           "Strong temporal drift requires investigation"
         ]
       }
     },
     "disagreement_analysis": {
       "overall_disagreement_rate": 0.22,
       "high_disagreement_sessions": 3,
       "disagreement_patterns": {
         "chamber_specific": {
           "S1": 0.15, "S2": 0.18, "S3": 0.28, "S4": 0.25
         },
         "topic_specific": {
           "bioelectric_mechanisms": 0.19,
           "regeneration_outcomes": 0.24,
           "molecular_pathways": 0.31
         },
         "mirror_pair_analysis": {
           "anthropic_vs_openai": 0.12,
           "anthropic_vs_deepseek": 0.41,
           "openai_vs_xai": 0.18,
           "xai_vs_google": 0.15
         }
       },
       "disagreement_severity": {
         "low": {"count": 89, "percentage": 0.65},
         "medium": {"count": 32, "percentage": 0.23},
         "high": {"count": 12, "percentage": 0.09},
         "critical": {"count": 4, "percentage": 0.03}
       }
     },
     "bias_detection": {
       "systematic_biases_detected": [
         {
           "type": "response_length_bias",
           "affected_mirrors": ["openai", "deepseek"],
           "severity": "medium",
           "description": "Tendency toward longer responses in S3/S4 chambers",
           "correction_applied": true
         },
         {
           "type": "technical_terminology_bias",
           "affected_mirrors": ["deepseek"],
           "severity": "high",
           "description": "Overuse of technical jargon affecting consensus",
           "correction_applied": false
         }
       ],
       "temporal_drift_analysis": {
         "overall_drift": 0.08,
         "drift_by_mirror": {
           "anthropic": 0.02,
           "openai": 0.04,
           "xai": 0.06,
           "google": 0.03,
           "deepseek": 0.15
         },
         "drift_correction_needed": ["deepseek"]
       }
     },
     "optimization_recommendations": {
       "immediate_actions": [
         "Reduce deepseek weighting to 0.3 in consensus calculations",
         "Implement additional validation for S3 chamber responses",
         "Monitor anthropic performance for continued improvement"
       ],
       "medium_term_improvements": [
         "Develop chamber-specific mirror selection strategies",
         "Implement automated bias correction for response length",
         "Create topic-specific consensus algorithms"
       ],
       "long_term_strategy": [
         "Evaluate alternative mirrors for replacing underperforming ones",
         "Develop predictive models for mirror performance",
         "Implement adaptive consensus thresholds based on topic complexity"
       ]
     },
     "quality_metrics": {
       "analysis_confidence": 0.91,
       "data_completeness": 0.94,
       "statistical_significance": 0.87,
       "recommendation_reliability": 0.89
     }
   }
   ```

### Configuration Parameters

```yaml
analysis_settings:
  consensus_algorithms:                       # Available consensus methods
    - "weighted_voting"
    - "bayesian_aggregation"
    - "cluster_consensus"
    - "outlier_robust_mean"

  disagreement_thresholds:                   # Classification thresholds
    low: 0.10
    medium: 0.20
    high: 0.30
    critical: 0.50

  bias_detection:                            # Bias detection settings
    systematic_bias_threshold: 0.15
    temporal_drift_window: 10                # sessions
    cross_validation_folds: 5
    minimum_sample_size: 20

output_formats:
  - consensus_network_diagram                # Network visualization
  - disagreement_heatmap                     # Pattern visualization
  - mirror_performance_dashboard             # Interactive dashboard
  - bias_detection_report                    # Systematic analysis
  - recommendations_json                     # Actionable recommendations

reporting:
  dashboard_update_frequency: "daily"       # Dashboard refresh rate
  alert_on_critical_disagreement: true     # Auto-alert system
  performance_tracking: true               # Historical tracking
  trend_analysis_window: 30                # days for trend analysis
```

### Integration Points

1. **Claude Code Hooks**
   - `post_convergence_analysis`: Called after convergence validation
   - `on_disagreement_detected`: Triggered by high disagreement
   - `performance_analysis_complete`: Handles analysis completion

2. **Orchestrator Integration**
   - Queue Priority: 18 (medium-high priority)
   - Depends On: `convergence-validator`, `simulation-runner`
   - Triggers: [] (terminal analysis agent)

3. **Feedback Integration**
   - Performance feedback to session orchestrator
   - Mirror weighting adjustments for future sessions
   - Threshold recommendations for convergence validator

### Usage Examples

```bash
# Comprehensive mirror performance analysis
/analyze-mirror-performance last_30_days comprehensive

# Bias detection across recent sessions
python scripts/cross_mirror_analyzer.py --analysis-type bias_detection \
  --time-window last_14_days --output analysis/consensus/

# Disagreement pattern analysis
python scripts/cross_mirror_analyzer.py --analysis-type disagreement_patterns \
  --session IRIS_20251007_143022 --verbose

# Generate performance dashboard
python scripts/cross_mirror_analyzer.py --dashboard-only \
  --output analysis/consensus/dashboard.html

# Historical trend analysis
python scripts/cross_mirror_analyzer.py --analysis-type meta_analysis \
  --time-window last_90_days --include-recommendations

# Real-time consensus monitoring
python scripts/cross_mirror_analyzer.py --monitor \
  --disagreement-threshold 0.25 --auto-alert

# Integration example
python analysis_scripts/cross_mirror_analysis.py \
  --convergence-data analysis/convergence/ \
  --session-history analysis/sessions/ \
  --output analysis/consensus/ANALYSIS_$(date +%Y%m%d_%H%M%S)/
```

---

## S1→S8 Pipeline Integration

### Complete Workflow Sequence

The six IRIS agents work together to implement the complete S1→S8 methodology:

```
1. Session Orchestrator
   ↓ [Initiates session]

2. Multi-Mirror S1-S4 Execution
   ↓ [Chamber completion triggers]

3. Convergence Validator
   ↓ [Validates agreement, triggers extraction]

4. S4 Extractor
   ↓ [Extracts bioelectric priors, triggers simulation]

5. Simulation Runner
   ↓ [Monte Carlo validation, triggers translation]

6. Protocol Translator
   ↓ [Generates wet-lab protocols]

7. Cross Mirror Analyzer
   [Provides ongoing consensus analysis and optimization]
```

### Integration Specifications

#### Agent Dependencies
```yaml
agent_dependencies:
  session-orchestrator: []                   # Top-level controller
  convergence-validator: [session-orchestrator]
  s4-extractor: [convergence-validator]
  simulation-runner: [s4-extractor]
  protocol-translator: [simulation-runner]
  cross-mirror-analyzer: [convergence-validator, simulation-runner]
```

#### Data Flow Patterns
```yaml
data_flow:
  vault_outputs: "vault/scrolls/**/*.md"    # Raw chamber outputs
  convergence_analysis: "analysis/convergence/**/*.json"
  extracted_parameters: "sandbox/states/s4_state.*.json"
  simulation_results: "sandbox/runs/outputs/**/*.json"
  protocols: "protocols/generated/**/*.md"
  consensus_analysis: "analysis/consensus/**/*"
```

#### Quality Gates
```yaml
quality_gates:
  s1_s2_s3_advance:
    min_mirrors: 2
    max_pressure: 2.0
  s4_success:
    min_convergence: 0.70
    min_mirrors_agree: 3
  simulation_validation:
    min_confidence: 0.80
    max_ci_width: 0.4
  protocol_handoff:
    require_power_analysis: true
    require_timeline: true
```

### Performance Monitoring

#### System Metrics
- **Throughput**: Sessions per day, chambers per hour
- **Quality**: Convergence rates, prediction accuracy
- **Efficiency**: Resource utilization, processing time
- **Reliability**: Success rates, error recovery

#### Pressure Monitoring
- **Global Pressure**: System-wide load tracking
- **Agent Pressure**: Individual agent load monitoring
- **Auto-Pause**: Automatic throttling mechanisms
- **Recovery**: Pressure relief and workflow resumption

---

## Summary

The IRIS agent system provides a comprehensive implementation of the IRIS methodology through six specialized agents that work together to ensure high-quality, statistically validated bioelectric predictions with direct wet-lab translation. Each agent has specific capabilities, clear trigger conditions, and defined integration points that enable seamless workflow execution from initial chamber analysis through final protocol generation.

**Key Features:**
- **Multi-mirror consensus validation** with statistical confidence
- **Automated bioelectric parameter extraction** from theoretical states
- **Monte Carlo simulation** with uncertainty quantification
- **Direct protocol translation** for wet-lab implementation
- **Comprehensive workflow orchestration** with pressure monitoring
- **Advanced consensus analysis** with bias detection and correction

**Integration Benefits:**
- Seamless integration with Claude Code's global agent system
- Automated workflow execution with minimal human intervention
- Statistical validation and quality assurance at every stage
- Comprehensive monitoring and error recovery capabilities
- Direct translation from theory to experimental validation

This documentation provides the complete specification for implementing and using the IRIS agent capabilities within the broader Claude Code ecosystem.