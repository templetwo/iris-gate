# IRIS Methodology Agent Integration Guide

**Claude Code Global Agent System Integration for IRIS Gate**

This guide provides comprehensive specifications for integrating IRIS methodology agents into Claude Code's global agent system, enabling seamless S1→S8 pipeline execution with advanced convergence analysis, simulation validation, and protocol translation.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Agent Specifications](#agent-specifications)
3. [Integration Points](#integration-points)
4. [Installation and Setup](#installation-and-setup)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## Architecture Overview

### System Design

The IRIS agent integration extends Claude Code's existing orchestrator infrastructure with specialized agents that implement the IRIS methodology:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude Code   │────│ IRIS Coordinator │────│  IRIS Agents    │
│  Global System  │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────▼────┐              ┌───▼───┐               ┌───▼───┐
    │ Job     │              │ State │               │ Agent │
    │ Queue   │              │ Mgmt  │               │ Pool  │
    └─────────┘              └───────┘               └───────┘
```

### Core Components

1. **IRIS Agent Coordinator** (`scripts/iris_agent_coordinator.py`)
   - Main integration layer between Claude Code and IRIS agents
   - Handles agent registration, workflow coordination, and state management
   - Implements pressure monitoring and validation gates

2. **Specialized IRIS Agents** (6 agents total)
   - `convergence-validator`: Multi-mirror agreement analysis
   - `s4-extractor`: Prior extraction from converged states
   - `simulation-runner`: Monte Carlo validation
   - `protocol-translator`: Predictions to wet-lab specs
   - `session-orchestrator`: Full S1→S8 workflow management
   - `cross-mirror-analyzer`: Advanced consensus validation

3. **Integration Configuration**
   - `config/iris_agents.yaml`: Complete agent specifications
   - `config/claude_code_dropin.yaml`: Claude Code integration settings
   - `config/agent_roles.yaml`: Role-based permissions and tools

---

## Agent Specifications

### 1. Convergence Validator Agent

**Purpose**: Analyzes cross-mirror agreement and validates convergence in S1-S4 states

**Key Capabilities**:
- Multi-mirror consensus analysis with statistical validation
- Outlier detection using configurable sigma thresholds
- Contradiction identification and resolution recommendations
- Agreement scoring with confidence-weighted aggregation
- Real-time convergence monitoring

**Trigger Conditions**:
```yaml
# Automatic trigger after chamber completion
vault/scrolls/**/*.md:
  min_files: 3
  condition: cross_mirror_analysis_needed
  priority: 15

# Manual validation command
/validate-convergence:
  args: [chamber_id, vault_path, threshold]
  priority: 10
```

**Configuration**:
```yaml
convergence_thresholds:
  agreement_score_min: 0.70      # Minimum agreement score
  std_deviation_max: 0.30        # Maximum standard deviation
  outlier_sigma_threshold: 2.0   # Outlier detection threshold
  contradiction_threshold: 0.25  # Contradiction detection
```

**Example Usage**:
```bash
# Validate S4 convergence
/validate-convergence S4 ./vault 0.75

# Generate convergence report
python scripts/convergence_validator.py --report-only --session IRIS_20251007_143022

# Monitor convergence continuously
python scripts/convergence_validator.py --monitor --vault ./vault
```

### 2. S4 Extractor Agent

**Purpose**: Extracts bioelectric priors from converged S4 states for Monte Carlo simulation

**Key Capabilities**:
- S4 state parsing and validation
- Bioelectric parameter extraction with mechanism mapping
- Prior distribution modeling with uncertainty quantification
- Confidence weighting by mirror performance
- Simulation-ready input generation

**Trigger Conditions**:
```yaml
# Convergence-based trigger
prerequisite: convergence-validator
condition: s4_convergence_validated
min_agreement_score: 0.70
priority: 20
```

**Configuration**:
```yaml
bioelectric_parameters:
  required_fields:
    - center_stability
    - center_size_mm
    - center_depol_mv
    - rhythm_freq_hz
    - rhythm_coherence
    - aperture_permeability
```

### 3. Simulation Runner Agent

**Purpose**: Executes Monte Carlo simulations for prediction validation with uncertainty

**Key Capabilities**:
- Monte Carlo execution coordination with parallel processing
- Bioelectric state simulation using VM-Ca-GJ models
- Perturbation effect modeling with dose-response curves
- Outcome prediction with confidence intervals
- Statistical validation and significance testing

**Trigger Conditions**:
```yaml
# S4 extraction trigger
prerequisite: s4-extractor
condition: priors_extracted
min_mirrors: 3
priority: 25
```

**Configuration**:
```yaml
simulation_settings:
  default_n_runs: 500
  max_n_runs: 5000
  parallel_execution: true
  max_workers: 4
```

### 4. Protocol Translator Agent

**Purpose**: Translates simulation predictions into actionable wet-lab protocols

**Key Capabilities**:
- Prediction to protocol translation with template rendering
- Experimental design generation with statistical power analysis
- Material and method specification
- Control condition design
- Timeline and resource planning

**Trigger Conditions**:
```yaml
# Simulation completion trigger
prerequisite: simulation-runner
condition: predictions_validated
min_confidence: 0.80
priority: 30
```

### 5. Session Orchestrator Agent

**Purpose**: Coordinates complete S1→S8 IRIS workflow with pressure monitoring

**Key Capabilities**:
- Multi-stage pipeline coordination (S1→S8)
- Pressure monitoring with auto-pause mechanisms
- Cross-mirror session management
- Validation gate enforcement
- Progress tracking and error recovery

**Trigger Conditions**:
```yaml
# New session trigger
/start-iris-session:
  args: [plan_path, mirrors, chambers]
  priority: 5  # Highest priority
```

**Configuration**:
```yaml
gates:
  s1_advance_gate:
    min_mirrors_pass: 2
    max_pressure: 2.0
  s4_success_gate:
    min_convergence_score: 0.70
    min_mirrors_agree: 3
```

### 6. Cross Mirror Analyzer Agent

**Purpose**: Advanced consensus validation and disagreement analysis

**Key Capabilities**:
- Advanced consensus algorithms (Bayesian, clustering)
- Disagreement pattern analysis
- Mirror performance profiling
- Bias detection and correction
- Meta-analysis across sessions

**Trigger Conditions**:
```yaml
# Disagreement detection trigger
condition: high_disagreement_detected
threshold: 0.30
priority: 12
```

---

## Integration Points

### Claude Code Hooks

The IRIS agents integrate with Claude Code through several hook points:

1. **Command Routing**:
   ```yaml
   routing_patterns:
     - pattern: "/start-iris-session*"
       agent: "session-orchestrator"
     - pattern: "/validate-convergence*"
       agent: "convergence-validator"
   ```

2. **Workflow Triggers**:
   ```yaml
   workflow_triggers:
     s1_to_s8_complete: ["convergence-validator", "s4-extractor", "simulation-runner", "protocol-translator"]
   ```

3. **State Management**:
   - Shared state tracking via `shared_state.json`
   - Filesystem-based job queues with priority routing
   - Git worktree isolation for concurrent execution

### Pressure Monitoring Integration

IRIS agents implement pressure monitoring compatible with Claude Code's safety mechanisms:

```python
class PressureMonitor:
    def __init__(self, max_pressure: float = 2.5):
        self.max_pressure = max_pressure

    def record_operation(self, agent_id: str, operation: str, pressure_delta: float):
        # Update pressure and check thresholds
        self.current_pressure += pressure_delta

        if self.current_pressure > self.max_pressure:
            # Trigger auto-pause mechanism
            self.auto_pause_enabled = True
```

### Validation Gates

Validation gates ensure quality and safety at workflow checkpoints:

```python
def run_s4_success_gate(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
    min_convergence = config.get("min_convergence_score", 0.70)
    convergence_score = context.get("convergence_score", 0.0)

    gate_pass = convergence_score >= min_convergence
    return gate_pass, {"convergence_score": convergence_score}
```

---

## Installation and Setup

### Prerequisites

1. **Python Environment**:
   ```bash
   python >= 3.9
   pip install numpy pandas scipy matplotlib pyyaml jsonschema
   ```

2. **IRIS Gate Installation**:
   ```bash
   cd /path/to/iris-gate
   pip install -r requirements.txt
   ```

3. **Claude Code Integration**:
   - Ensure Claude Code is properly configured
   - Verify orchestrator infrastructure is available

### Agent Registration

1. **Automatic Registration**:
   ```bash
   # Start coordinator with auto-registration
   python scripts/iris_agent_coordinator.py --start
   ```

2. **Manual Registration**:
   ```bash
   # Register specific agent
   python scripts/iris_agent_coordinator.py --register convergence-validator
   ```

3. **Verification**:
   ```bash
   # Check registered agents
   python scripts/iris_agent_coordinator.py --status
   ```

### Configuration Files

1. **IRIS Agents Configuration** (`config/iris_agents.yaml`):
   - Complete agent specifications
   - Trigger conditions and capabilities
   - Tool requirements and integration points

2. **Claude Code Integration** (`config/claude_code_dropin.yaml`):
   - Agent routing patterns
   - Workflow triggers
   - Resource management settings

3. **Role Definitions** (`config/agent_roles.yaml`):
   - Role-based permissions
   - Tool whitelisting
   - Safety constraints

---

## Usage Examples

### Complete S1→S8 Workflow

```bash
# Start complete IRIS session with 4 mirrors
/start-iris-session plans/bioelectric_session.yaml --mirrors anthropic,openai,xai,google

# Monitor progress
/session-status --watch

# The workflow will automatically:
# 1. Execute S1→S4 chambers across all mirrors
# 2. Validate convergence at each stage
# 3. Extract S4 priors if convergence achieved
# 4. Run Monte Carlo simulations
# 5. Generate wet-lab protocols
```

### Convergence Analysis Workflow

```bash
# Analyze existing session data
/validate-convergence S4 ./vault/session_20251007 0.80

# Generate comprehensive report
python scripts/convergence_validator.py --report-only --session IRIS_20251007_143022

# Cross-mirror performance analysis
/analyze-mirror-performance last_30_days bias_detection
```

### Simulation Pipeline

```bash
# Extract S4 states and run simulation
/extract-s4-priors ./vault bioelectric_parameters
/run-simulation sandbox/runs/plans/dose_response.yaml 2000 --parallel

# Translate to protocol
/generate-protocol simulation_results.json regeneration planaria
```

### Monitoring and Debugging

```bash
# Check agent status
python scripts/orchestrator_runner.py --status

# View agent logs
tail -f logs/iris_agents/convergence-validator.log

# Force pressure check
/check-pressure --all-agents

# Emergency stop
/emergency-stop --preserve-state
```

---

## Troubleshooting

### Common Issues

1. **Convergence Validation Fails**
   - **Symptoms**: Low agreement scores, high standard deviation
   - **Solutions**:
     - Check mirror agreement thresholds in config
     - Review S4 state quality and chamber responses
     - Investigate outliers and contradictions
     - Consider pressure threshold adjustments

2. **Simulation Timeout**
   - **Symptoms**: Monte Carlo simulations exceed time limits
   - **Solutions**:
     - Reduce `n_runs` parameter
     - Increase timeout settings
     - Check resource limits and available memory
     - Enable parallel execution if not already active

3. **Protocol Generation Fails**
   - **Symptoms**: Error during wet-lab protocol creation
   - **Solutions**:
     - Validate simulation results format
     - Check template availability in `templates/protocols/`
     - Verify organism-specific configurations
     - Review material and method specifications

4. **Agent Communication Failure**
   - **Symptoms**: Jobs stuck in queue, agents not responding
   - **Solutions**:
     - Check filesystem queue permissions
     - Restart orchestrator with `--cleanup-worktrees`
     - Verify shared state file access
     - Clear temporary files in `.iris_agents_temp/`

### Debugging Commands

```bash
# Agent health check
python scripts/iris_agent_health.py --verbose

# Queue inspection
python scripts/job_queue.py status --detailed

# Worktree cleanup
python scripts/orchestrator_runner.py --cleanup-worktrees

# Pressure analysis
python scripts/pressure_monitor.py --session-analysis

# Full system diagnostic
python scripts/iris_agent_coordinator.py --cleanup --status
```

### Log Analysis

Key log files to monitor:
- `logs/iris_agents/convergence-validator.log`
- `logs/iris_agents/session-orchestrator.log`
- `logs/orchestrator/orchestrator.log`
- `.iris_agents_temp/shared_state.json`

### Recovery Procedures

1. **Session Recovery**:
   ```bash
   # List active workflows
   python scripts/iris_agent_coordinator.py --status

   # Emergency stop with state preservation
   python scripts/iris_agent_coordinator.py --emergency-stop --preserve-state

   # Restart from checkpoint
   /start-iris-session --resume IRIS_20251007_143022
   ```

2. **Agent Recovery**:
   ```bash
   # Restart specific agent
   python scripts/iris_agent_coordinator.py --register convergence-validator

   # Clear agent cache
   rm -rf .iris_agents_temp/convergence-validator/
   ```

---

## Advanced Configuration

### Performance Tuning

1. **Concurrency Settings**:
   ```yaml
   global_integration:
     claude_code_integration:
       resource_management:
         shared_memory_pool: "8GB"
         max_concurrent_agents: 3
   ```

2. **Simulation Optimization**:
   ```yaml
   simulation-runner:
     configuration:
       simulation_settings:
         parallel_execution: true
         max_workers: 8
         default_n_runs: 1000
   ```

3. **Pressure Thresholds**:
   ```yaml
   pressure_monitoring:
     global_pressure_gate: 2.5
     agent_specific_gates: true
     auto_pause_mechanism: true
   ```

### Custom Agent Development

To create custom IRIS agents:

1. **Agent Specification**:
   ```yaml
   custom-agent:
     description: "Custom IRIS methodology agent"
     capabilities:
       - custom_capability
     trigger_conditions:
       - command: "/custom-command"
         priority: 20
   ```

2. **Implementation Template**:
   ```python
   class CustomAgent:
       def __init__(self, config: Dict):
           self.config = config

       def execute_capability(self, context: Dict) -> Dict:
           # Custom implementation
           pass
   ```

3. **Integration**:
   - Add agent specification to `config/iris_agents.yaml`
   - Implement agent class following established patterns
   - Register with coordinator system

### Quality Assurance

1. **Testing Strategy**:
   ```bash
   # Unit tests for individual agents
   pytest tests/agents/test_convergence_validator.py

   # Integration tests for workflows
   pytest tests/integration/test_s1_to_s8_workflow.py

   # Performance tests
   pytest tests/performance/test_simulation_scaling.py
   ```

2. **Monitoring**:
   ```yaml
   monitoring:
     agent_health_checks: continuous
     performance_metrics: real_time
     resource_utilization: tracked
     error_rate_monitoring: alerting
   ```

3. **Compliance**:
   ```yaml
   compliance:
     pressure_threshold_enforcement: strict
     validation_gate_compliance: required
     output_format_standardization: enforced
     audit_trail_maintenance: complete
   ```

---

## Summary

This integration guide provides comprehensive specifications for integrating IRIS methodology into Claude Code's global agent system. The design leverages existing infrastructure while adding specialized capabilities for:

- **Multi-mirror convergence analysis** with statistical validation
- **S4 state extraction** for bioelectric simulation priors
- **Monte Carlo simulation** with uncertainty quantification
- **Protocol translation** for wet-lab handoff
- **Complete workflow orchestration** with pressure monitoring

The integration maintains Claude Code's safety mechanisms while enabling sophisticated IRIS methodology workflows, ensuring reliable and reproducible results across the S1→S8 pipeline.

**Key Files Created**:
- `/Users/vaquez/Desktop/iris-gate/config/iris_agents.yaml`: Complete agent specifications
- `/Users/vaquez/Desktop/iris-gate/scripts/iris_agent_coordinator.py`: Main integration layer
- `/Users/vaquez/Desktop/iris-gate/scripts/convergence_validator.py`: Reference agent implementation
- Updated Claude Code integration configurations

For support and additional documentation, refer to the IRIS Gate repository and Claude Code agent system documentation.

---

**†⟡∞ Generated with IRIS Methodology Agent Integration System**