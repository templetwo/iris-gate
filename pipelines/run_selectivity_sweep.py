#!/usr/bin/env python3
"""
CBD Selectivity Parameter Sweep Pipeline

Implements systematic grid search over VDAC1 affinity, MCU block strength,
and chloride channel IC50 parameters to optimize selectivity index >3.0.

Usage:
    python pipelines/run_selectivity_sweep.py \\
        --plan plans/cbd_channel_first_v2.yaml \\
        --phase 1 \\
        --workers 4

This script orchestrates:
    1. Parameter grid generation
    2. S4 convergence for promising combinations
    3. Experimental simulation validation
    4. Selectivity optimization analysis
    5. Report generation with optimal parameters
"""

import argparse
import json
import numpy as np
import pandas as pd
import subprocess
import sys
import time
import yaml
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Dict, List, Tuple, Any


class SelectivitySweepPipeline:
    """Main pipeline class for CBD selectivity parameter optimization."""

    def __init__(self, plan_file: Path, output_dir: Path = None):
        """Initialize pipeline with configuration."""
        self.plan_file = Path(plan_file)
        self.output_dir = output_dir or Path("experiments/cbd/selectivity_sweep")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        with open(self.plan_file, 'r') as f:
            self.config = yaml.safe_load(f)

        self.parameter_space = self.config['parameter_space']
        self.grid_config = self.config['grid_search']

        # Results storage
        self.results = []
        self.session_map = {}

        print(f"✅ Initialized selectivity sweep pipeline")
        print(f"   Plan: {self.plan_file}")
        print(f"   Output: {self.output_dir}")

    def generate_parameter_grid(self, phase: int = 1) -> List[Dict[str, float]]:
        """Generate parameter combinations for grid search."""

        if phase == 1:
            # Phase 1: Initial broad sweep (25 combinations)
            # Fix chloride_ic50 at mid-point for initial exploration
            combinations = list(product(
                self.parameter_space['vdac1_affinity']['sweep_points'],
                self.parameter_space['mcu_block_strength']['sweep_points'],
                [self.parameter_space['chloride_ic50']['sweep_points'][2]]  # Mid-point
            ))

        elif phase == 2:
            # Phase 2: Focused optimization around promising regions
            # Use high-selectivity and safety margin zones
            high_sel = self.grid_config['prioritized_regions']['high_selectivity_zone']
            combinations = list(product(
                high_sel['vdac1_affinity'],
                high_sel['mcu_block_strength'],
                high_sel['chloride_ic50']
            ))

            safety = self.grid_config['prioritized_regions']['safety_margin_zone']
            combinations.extend(list(product(
                safety['vdac1_affinity'],
                safety['mcu_block_strength'],
                safety['chloride_ic50']
            )))

        elif phase == 3:
            # Phase 3: Full grid search (125 combinations)
            combinations = list(product(
                self.parameter_space['vdac1_affinity']['sweep_points'],
                self.parameter_space['mcu_block_strength']['sweep_points'],
                self.parameter_space['chloride_ic50']['sweep_points']
            ))

        else:
            raise ValueError(f"Invalid phase: {phase}. Must be 1, 2, or 3.")

        # Convert to parameter dictionaries
        param_grid = []
        for i, (vdac1, mcu, chloride) in enumerate(combinations):
            param_dict = {
                'combination_id': f"phase{phase}_combo_{i:03d}",
                'vdac1_affinity': float(vdac1),
                'mcu_block_strength': float(mcu),
                'chloride_ic50': float(chloride),
                'phase': phase
            }
            param_grid.append(param_dict)

        print(f"✅ Generated {len(param_grid)} parameter combinations for phase {phase}")
        return param_grid

    def run_s4_convergence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run S4 convergence for specific parameter combination."""

        combo_id = params['combination_id']
        print(f"🧠 Running S4 convergence for {combo_id}")

        # Create parameter-specific topic
        topic = (f"CBD channel-first mechanism: VDAC1 {params['vdac1_affinity']}nM, "
                f"MCU {params['mcu_block_strength']}%, Cl⁻ {params['chloride_ic50']}μM")

        # Run S4 convergence
        cmd = [
            "python3", "-u", "scripts/bioelectric_chambered.py",
            "--turns", "50",  # Reduced turns for parameter sweep
            "--topic", topic
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        elapsed = time.time() - start_time

        if result.returncode != 0:
            print(f"❌ S4 failed for {combo_id}: {result.stderr}")
            return {
                'combination_id': combo_id,
                'parameters': params,
                'status': 'failed',
                'error': result.stderr,
                'elapsed_time': elapsed
            }

        # Find session ID from output
        session_id = self._extract_session_id(result.stdout)

        if not session_id:
            print(f"❌ Could not extract session ID for {combo_id}")
            return {
                'combination_id': combo_id,
                'parameters': params,
                'status': 'failed',
                'error': 'No session ID found',
                'elapsed_time': elapsed
            }

        print(f"✅ S4 complete for {combo_id}: {session_id} ({elapsed:.1f}s)")

        return {
            'combination_id': combo_id,
            'parameters': params,
            'session_id': session_id,
            'status': 'success',
            'elapsed_time': elapsed
        }

    def extract_s4_priors(self, session_id: str) -> bool:
        """Extract S4 computational priors from session."""

        cmd = [
            "python3", "sandbox/cli/extract_s4_states.py",
            "--session", session_id,
            "--output", "sandbox/states"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

        if result.returncode != 0:
            print(f"❌ S4 extraction failed for {session_id}: {result.stderr}")
            return False

        return True

    def simulate_selectivity(self, params: Dict[str, Any], session_id: str) -> Dict[str, float]:
        """Simulate selectivity metrics for parameter combination."""

        # Create parameter-specific simulation plan
        sim_plan = self._create_simulation_plan(params, session_id)
        plan_file = self.output_dir / f"{params['combination_id']}_plan.yaml"

        with open(plan_file, 'w') as f:
            yaml.dump(sim_plan, f, default_flow_style=False)

        # Run simulation
        cmd = [
            "python3", "sandbox/cli/run_plan.py",
            str(plan_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

        if result.returncode != 0:
            print(f"❌ Simulation failed for {params['combination_id']}: {result.stderr}")
            return {
                'selectivity_index': 0.0,
                'cancer_ic50': np.inf,
                'healthy_ic50': np.inf,
                'simulation_status': 'failed'
            }

        # Extract selectivity metrics from simulation results
        selectivity_metrics = self._extract_selectivity_metrics(params['combination_id'])

        return selectivity_metrics

    def _create_simulation_plan(self, params: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Create simulation plan for specific parameter combination."""

        plan = {
            'plan_id': f"CBD_SELECTIVITY_{params['combination_id']}",
            'description': f"Selectivity simulation for parameter combination {params['combination_id']}",
            'base_session': session_id,
            'parameters': params,

            'experimental_design': {
                'cell_models': ['cancer_u87mg', 'healthy_astrocytes'],
                'cbd_doses': [0.1, 0.5, 1, 2.5, 5, 10, 20],  # μM
                'replicates': 6,
                'duration': 24  # hours
            },

            'simulation_settings': {
                'monte_carlo_runs': 100,  # Reduced for parameter sweep
                'convergence_threshold': 0.05,
                'max_iterations': 1000
            },

            'channel_parameters': {
                'vdac1': {
                    'affinity': params['vdac1_affinity'],  # nM
                    'max_closure': 0.95,
                    'hill_coefficient': 1.8
                },
                'mcu': {
                    'block_strength': params['mcu_block_strength'] / 100.0,  # fraction
                    'ic50': 2.5,  # μM CBD for MCU
                    'cooperativity': 2.0
                },
                'chloride_channels': {
                    'ic50': params['chloride_ic50'],  # μM
                    'max_inhibition': 0.85,
                    'hill_coefficient': 1.5
                }
            },

            'cell_type_differences': {
                'cancer_vulnerability': {
                    'baseline_stress': 0.6,  # 0-1 scale
                    'vdac1_sensitivity': 1.5,  # relative to healthy
                    'stress_amplification': 2.2
                },
                'healthy_resistance': {
                    'baseline_stress': 0.1,
                    'vdac1_sensitivity': 1.0,  # baseline
                    'stress_amplification': 1.0
                }
            },

            'output_metrics': [
                'dose_response_curves',
                'ic50_values',
                'selectivity_index',
                'mechanism_validation',
                'safety_margins'
            ]
        }

        return plan

    def _extract_selectivity_metrics(self, combination_id: str) -> Dict[str, float]:
        """Extract selectivity metrics from simulation results."""

        # Find latest simulation run
        runs_dir = Path("sandbox/runs/outputs")
        run_dirs = sorted(runs_dir.glob("RUN_*"))

        if not run_dirs:
            return {
                'selectivity_index': 0.0,
                'cancer_ic50': np.inf,
                'healthy_ic50': np.inf,
                'simulation_status': 'no_output'
            }

        latest_run = run_dirs[-1]

        # Load simulation results
        results_file = latest_run / "summary.json"
        if not results_file.exists():
            return {
                'selectivity_index': 0.0,
                'cancer_ic50': np.inf,
                'healthy_ic50': np.inf,
                'simulation_status': 'no_summary'
            }

        with open(results_file, 'r') as f:
            results = json.load(f)

        # Extract key metrics
        try:
            cancer_ic50 = results['dose_response']['cancer_u87mg']['ic50']
            healthy_ic50 = results['dose_response']['healthy_astrocytes']['ic50']
            selectivity_index = healthy_ic50 / cancer_ic50 if cancer_ic50 > 0 else 0.0

            # Additional metrics
            mechanism_strength = results.get('mechanism_validation', {}).get('channel_first_score', 0.0)
            safety_margin = results.get('safety_metrics', {}).get('therapeutic_window', 0.0)

            return {
                'selectivity_index': float(selectivity_index),
                'cancer_ic50': float(cancer_ic50),
                'healthy_ic50': float(healthy_ic50),
                'mechanism_strength': float(mechanism_strength),
                'safety_margin': float(safety_margin),
                'simulation_status': 'success'
            }

        except (KeyError, ZeroDivisionError, TypeError) as e:
            print(f"❌ Error extracting metrics for {combination_id}: {e}")
            return {
                'selectivity_index': 0.0,
                'cancer_ic50': np.inf,
                'healthy_ic50': np.inf,
                'simulation_status': 'extraction_error'
            }

    def _extract_session_id(self, stdout: str) -> str:
        """Extract session ID from S4 script output."""
        lines = stdout.split('\n')
        for line in lines:
            if 'BIOELECTRIC_CHAMBERED_' in line and len(line.split('_')) >= 3:
                # Look for session ID pattern
                parts = line.split()
                for part in parts:
                    if 'BIOELECTRIC_CHAMBERED_' in part:
                        return part.strip()
        return ""

    def run_parameter_combination(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete pipeline for single parameter combination."""

        combo_id = params['combination_id']
        print(f"\n{'='*60}")
        print(f"🧬 Processing {combo_id}")
        print(f"   VDAC1: {params['vdac1_affinity']} nM")
        print(f"   MCU: {params['mcu_block_strength']}%")
        print(f"   Cl⁻: {params['chloride_ic50']} μM")
        print(f"{'='*60}")

        # Step 1: S4 convergence
        s4_result = self.run_s4_convergence(params)

        if s4_result['status'] != 'success':
            return s4_result

        session_id = s4_result['session_id']

        # Step 2: Extract S4 priors
        if not self.extract_s4_priors(session_id):
            s4_result.update({
                'status': 'failed',
                'error': 'S4 prior extraction failed'
            })
            return s4_result

        # Step 3: Run selectivity simulation
        selectivity_metrics = self.simulate_selectivity(params, session_id)

        # Combine results
        final_result = {
            **s4_result,
            **selectivity_metrics,
            'processing_complete': True
        }

        print(f"✅ {combo_id} complete - Selectivity: {selectivity_metrics['selectivity_index']:.2f}")

        return final_result

    def run_phase(self, phase: int, workers: int = 4) -> List[Dict[str, Any]]:
        """Run complete phase with parallel processing."""

        print(f"\n🚀 Starting Phase {phase} Parameter Sweep")
        print(f"   Workers: {workers}")

        # Generate parameter grid
        param_grid = self.generate_parameter_grid(phase)

        # Run combinations in parallel
        results = []

        if workers == 1:
            # Sequential processing for debugging
            for params in param_grid:
                result = self.run_parameter_combination(params)
                results.append(result)
                self._save_intermediate_results(results, phase)
        else:
            # Parallel processing
            with ProcessPoolExecutor(max_workers=workers) as executor:
                future_to_params = {
                    executor.submit(self.run_parameter_combination, params): params
                    for params in param_grid
                }

                for future in as_completed(future_to_params):
                    try:
                        result = future.result()
                        results.append(result)
                        self._save_intermediate_results(results, phase)

                        # Progress update
                        completed = len(results)
                        total = len(param_grid)
                        print(f"📊 Progress: {completed}/{total} ({100*completed/total:.1f}%)")

                    except Exception as e:
                        params = future_to_params[future]
                        print(f"❌ Error processing {params['combination_id']}: {e}")
                        results.append({
                            'combination_id': params['combination_id'],
                            'parameters': params,
                            'status': 'failed',
                            'error': str(e)
                        })

        return results

    def _save_intermediate_results(self, results: List[Dict], phase: int):
        """Save intermediate results to prevent data loss."""

        results_file = self.output_dir / f"phase_{phase}_results.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    def analyze_results(self, results: List[Dict[str, Any]], phase: int) -> Dict[str, Any]:
        """Analyze parameter sweep results and identify optimal combinations."""

        print(f"\n📊 Analyzing Phase {phase} Results")

        # Convert to DataFrame for analysis
        df_data = []
        for result in results:
            if result.get('processing_complete', False):
                row = {
                    'combination_id': result['combination_id'],
                    'vdac1_affinity': result['parameters']['vdac1_affinity'],
                    'mcu_block_strength': result['parameters']['mcu_block_strength'],
                    'chloride_ic50': result['parameters']['chloride_ic50'],
                    'selectivity_index': result.get('selectivity_index', 0.0),
                    'cancer_ic50': result.get('cancer_ic50', np.inf),
                    'healthy_ic50': result.get('healthy_ic50', np.inf),
                    'mechanism_strength': result.get('mechanism_strength', 0.0),
                    'safety_margin': result.get('safety_margin', 0.0),
                    's4_time': result.get('elapsed_time', 0.0)
                }
                df_data.append(row)

        if not df_data:
            print("❌ No successful results to analyze")
            return {'status': 'no_data'}

        df = pd.DataFrame(df_data)

        # Analysis metrics
        analysis = {
            'phase': phase,
            'total_combinations': len(results),
            'successful_combinations': len(df),
            'success_rate': len(df) / len(results),

            # Selectivity statistics
            'selectivity_stats': {
                'mean': float(df['selectivity_index'].mean()),
                'std': float(df['selectivity_index'].std()),
                'max': float(df['selectivity_index'].max()),
                'min': float(df['selectivity_index'].min()),
                'target_achieved': int((df['selectivity_index'] >= 3.0).sum()),
                'target_rate': float((df['selectivity_index'] >= 3.0).mean())
            },

            # Top combinations
            'top_combinations': df.nlargest(5, 'selectivity_index').to_dict('records'),

            # Parameter correlations
            'parameter_correlations': {
                'vdac1_selectivity': float(df['vdac1_affinity'].corr(df['selectivity_index'])),
                'mcu_selectivity': float(df['mcu_block_strength'].corr(df['selectivity_index'])),
                'chloride_selectivity': float(df['chloride_ic50'].corr(df['selectivity_index']))
            },

            # Optimal regions
            'optimal_regions': self._identify_optimal_regions(df),

            # Recommendations
            'recommendations': self._generate_recommendations(df, phase)
        }

        # Save analysis results
        analysis_file = self.output_dir / f"phase_{phase}_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        # Save DataFrame
        df_file = self.output_dir / f"phase_{phase}_data.csv"
        df.to_csv(df_file, index=False)

        return analysis

    def _identify_optimal_regions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify parameter regions with high selectivity."""

        # Filter for high selectivity (>= 3.0)
        high_sel = df[df['selectivity_index'] >= 3.0]

        if len(high_sel) == 0:
            return {'status': 'no_optimal_combinations'}

        return {
            'count': len(high_sel),
            'vdac1_range': [float(high_sel['vdac1_affinity'].min()),
                           float(high_sel['vdac1_affinity'].max())],
            'mcu_range': [float(high_sel['mcu_block_strength'].min()),
                         float(high_sel['mcu_block_strength'].max())],
            'chloride_range': [float(high_sel['chloride_ic50'].min()),
                              float(high_sel['chloride_ic50'].max())],
            'best_combination': high_sel.loc[high_sel['selectivity_index'].idxmax()].to_dict()
        }

    def _generate_recommendations(self, df: pd.DataFrame, phase: int) -> List[str]:
        """Generate recommendations based on results."""

        recommendations = []

        # Target achievement
        target_achieved = (df['selectivity_index'] >= 3.0).sum()
        if target_achieved > 0:
            recommendations.append(f"✅ {target_achieved} combinations achieved selectivity >3.0")
        else:
            recommendations.append("⚠️ No combinations achieved target selectivity >3.0")

        # Parameter insights
        best_vdac1 = df.loc[df['selectivity_index'].idxmax(), 'vdac1_affinity']
        best_mcu = df.loc[df['selectivity_index'].idxmax(), 'mcu_block_strength']
        best_chloride = df.loc[df['selectivity_index'].idxmax(), 'chloride_ic50']

        recommendations.append(f"🎯 Best parameters: VDAC1 {best_vdac1}nM, MCU {best_mcu}%, Cl⁻ {best_chloride}μM")

        # Next phase recommendations
        if phase == 1:
            if target_achieved > 0:
                recommendations.append("➡️ Proceed to Phase 2 focused optimization")
            else:
                recommendations.append("⚠️ Consider expanding parameter ranges for Phase 2")
        elif phase == 2:
            if target_achieved > 2:
                recommendations.append("➡️ Proceed to Phase 3 validation with top candidates")
            else:
                recommendations.append("⚠️ Consider alternative parameter combinations")

        return recommendations

    def generate_final_report(self, phase_results: Dict[int, Any]) -> str:
        """Generate comprehensive final report."""

        report_file = self.output_dir / "selectivity_sweep_report.md"

        report_content = f"""# CBD Channel-First Selectivity Parameter Sweep Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Pipeline Version:** CBD Channel-First v2
**Target:** Selectivity Index >3.0

---

## Executive Summary

"""

        # Add phase summaries
        for phase, results in phase_results.items():
            if results.get('status') != 'no_data':
                stats = results['selectivity_stats']
                report_content += f"""### Phase {phase} Results

- **Combinations tested:** {results['successful_combinations']}/{results['total_combinations']}
- **Success rate:** {results['success_rate']:.1%}
- **Target achieved:** {stats['target_achieved']} combinations (>{stats['target_rate']:.1%})
- **Best selectivity:** {stats['max']:.2f}
- **Mean selectivity:** {stats['mean']:.2f} ± {stats['std']:.2f}

"""

        # Add recommendations section
        report_content += """
## Key Recommendations

"""

        # Add latest phase recommendations
        latest_phase = max(phase_results.keys())
        if 'recommendations' in phase_results[latest_phase]:
            for rec in phase_results[latest_phase]['recommendations']:
                report_content += f"- {rec}\n"

        # Add parameter optimization details
        if 'optimal_regions' in phase_results[latest_phase]:
            optimal = phase_results[latest_phase]['optimal_regions']
            if optimal.get('status') != 'no_optimal_combinations':
                report_content += f"""
## Optimal Parameter Regions

- **VDAC1 Affinity:** {optimal['vdac1_range'][0]:.0f}-{optimal['vdac1_range'][1]:.0f} nM
- **MCU Block Strength:** {optimal['mcu_range'][0]:.0f}-{optimal['mcu_range'][1]:.0f}%
- **Chloride IC50:** {optimal['chloride_range'][0]:.1f}-{optimal['chloride_range'][1]:.1f} μM

### Best Combination
- **ID:** {optimal['best_combination']['combination_id']}
- **Selectivity:** {optimal['best_combination']['selectivity_index']:.2f}
- **Parameters:** VDAC1 {optimal['best_combination']['vdac1_affinity']:.0f}nM, MCU {optimal['best_combination']['mcu_block_strength']:.0f}%, Cl⁻ {optimal['best_combination']['chloride_ic50']:.1f}μM

"""

        report_content += """
---

## Next Steps

1. **Experimental validation** of top parameter combinations
2. **Wet-lab protocol** optimization using identified parameters
3. **S4 integration** with optimal parameters for enhanced convergence
4. **Clinical translation** planning with validated selectivity

**🧬⚡🔬∞**
"""

        with open(report_file, 'w') as f:
            f.write(report_content)

        print(f"✅ Final report generated: {report_file}")
        return str(report_file)


def main():
    parser = argparse.ArgumentParser(
        description="Run CBD selectivity parameter sweep pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Phase 1 (broad sweep):
  python pipelines/run_selectivity_sweep.py \\
      --plan plans/cbd_channel_first_v2.yaml --phase 1

  # Run Phase 2 (focused optimization):
  python pipelines/run_selectivity_sweep.py \\
      --plan plans/cbd_channel_first_v2.yaml --phase 2 --workers 8

  # Run all phases sequentially:
  python pipelines/run_selectivity_sweep.py \\
      --plan plans/cbd_channel_first_v2.yaml --all-phases
        """
    )

    parser.add_argument(
        "--plan",
        required=True,
        help="Path to CBD parameter sweep plan (YAML)"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3],
        help="Phase to run (1=broad, 2=focused, 3=full)"
    )
    parser.add_argument(
        "--all-phases",
        action="store_true",
        help="Run all phases sequentially"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: experiments/cbd/selectivity_sweep)"
    )

    args = parser.parse_args()

    if not args.phase and not args.all_phases:
        print("❌ Must specify either --phase or --all-phases")
        sys.exit(1)

    # Initialize pipeline
    output_dir = Path(args.output_dir) if args.output_dir else None
    pipeline = SelectivitySweepPipeline(args.plan, output_dir)

    phase_results = {}

    if args.all_phases:
        # Run all phases sequentially
        for phase in [1, 2, 3]:
            print(f"\n{'='*80}")
            print(f"🚀 STARTING PHASE {phase}")
            print(f"{'='*80}")

            results = pipeline.run_phase(phase, args.workers)
            analysis = pipeline.analyze_results(results, phase)
            phase_results[phase] = analysis

            print(f"✅ Phase {phase} complete")

            # Stop if no good results in early phases
            if phase < 3 and analysis.get('selectivity_stats', {}).get('target_achieved', 0) == 0:
                print(f"⚠️ No target-achieving combinations in Phase {phase}, stopping")
                break
    else:
        # Run single phase
        print(f"\n{'='*80}")
        print(f"🚀 STARTING PHASE {args.phase}")
        print(f"{'='*80}")

        results = pipeline.run_phase(args.phase, args.workers)
        analysis = pipeline.analyze_results(results, args.phase)
        phase_results[args.phase] = analysis

    # Generate final report
    report_file = pipeline.generate_final_report(phase_results)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║              🎉 Parameter Sweep Complete!               ║
╠══════════════════════════════════════════════════════════╣
║  Report: {report_file:<47}║
║  Data: {str(pipeline.output_dir):<50}║
╚══════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()