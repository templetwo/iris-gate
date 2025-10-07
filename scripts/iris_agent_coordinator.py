#!/usr/bin/env python3
"""
IRIS Agent Coordinator - Claude Code Integration Layer

Provides the bridge between IRIS methodology agents and Claude Code's global agent system.
Handles agent registration, workflow coordination, pressure monitoring, and validation gates.

Architecture:
    - Dynamic agent registration from iris_agents.yaml
    - Filesystem-based job queue with priority routing
    - Pressure monitoring with auto-pause mechanisms
    - Validation gate enforcement at workflow checkpoints
    - Cross-agent communication and state management

Usage:
    # Start coordinator with auto-registration
    python scripts/iris_agent_coordinator.py --start

    # Register specific agent
    python scripts/iris_agent_coordinator.py --register convergence-validator

    # Monitor workflow status
    python scripts/iris_agent_coordinator.py --status --watch

    # Execute complete S1→S8 workflow
    python scripts/iris_agent_coordinator.py --workflow s1-to-s8 --plan plans/session.yaml
"""

import argparse
import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml
import threading
from dataclasses import dataclass, asdict

from job_queue import FSQueue, Job, JobStatus
from lockfile import LockFile


@dataclass
class AgentCapability:
    """Represents a specific agent capability."""
    name: str
    description: str
    requirements: List[str]
    enabled: bool = True


@dataclass
class TriggerCondition:
    """Represents an agent trigger condition."""
    trigger_type: str  # 'pattern', 'command', 'stage', 'prerequisite'
    condition: str
    priority: int
    args: Optional[Dict] = None
    enabled: bool = True


@dataclass
class AgentSpec:
    """Complete agent specification."""
    agent_id: str
    description: str
    capabilities: List[AgentCapability]
    trigger_conditions: List[TriggerCondition]
    tool_requirements: Dict[str, Any]
    configuration: Dict[str, Any]
    integration_points: Dict[str, Any]


@dataclass
class WorkflowState:
    """Tracks workflow execution state."""
    workflow_id: str
    stage: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'paused'
    pressure: float
    agents_active: List[str]
    checkpoints: Dict[str, datetime]
    metadata: Dict[str, Any]


class PressureMonitor:
    """Monitors and manages workflow pressure across agents."""

    def __init__(self, max_pressure: float = 2.5, check_interval: int = 5):
        """
        Initialize pressure monitor.

        Args:
            max_pressure: Maximum allowed pressure before auto-pause
            check_interval: Pressure check frequency (operations)
        """
        self.max_pressure = max_pressure
        self.check_interval = check_interval
        self.current_pressure = 0.0
        self.pressure_history: List[Tuple[datetime, float]] = []
        self.operation_count = 0
        self.auto_pause_enabled = True
        self.logger = logging.getLogger(f"{__name__}.PressureMonitor")

    def record_operation(self, agent_id: str, operation: str, pressure_delta: float = 0.0):
        """Record an operation and update pressure."""
        self.operation_count += 1
        self.current_pressure = max(0.0, self.current_pressure + pressure_delta)

        timestamp = datetime.now()
        self.pressure_history.append((timestamp, self.current_pressure))

        # Trim history to last 100 entries
        if len(self.pressure_history) > 100:
            self.pressure_history = self.pressure_history[-100:]

        self.logger.debug(f"Operation recorded: {agent_id}.{operation}, pressure={self.current_pressure:.2f}")

        # Check if pressure check is needed
        if self.operation_count % self.check_interval == 0:
            self.check_pressure_gate()

    def check_pressure_gate(self) -> bool:
        """
        Check if pressure exceeds threshold.

        Returns:
            True if pressure is within limits, False if exceeded
        """
        if self.current_pressure > self.max_pressure:
            self.logger.warning(f"Pressure threshold exceeded: {self.current_pressure:.2f} > {self.max_pressure}")

            if self.auto_pause_enabled:
                self.logger.info("Auto-pause triggered due to pressure threshold")
                return False

        return True

    def get_pressure_stats(self) -> Dict[str, Any]:
        """Get current pressure statistics."""
        recent_pressures = [p for _, p in self.pressure_history[-10:]]

        return {
            "current_pressure": self.current_pressure,
            "max_pressure": self.max_pressure,
            "operation_count": self.operation_count,
            "pressure_trend": {
                "recent_mean": sum(recent_pressures) / len(recent_pressures) if recent_pressures else 0.0,
                "recent_max": max(recent_pressures) if recent_pressures else 0.0,
                "recent_min": min(recent_pressures) if recent_pressures else 0.0,
            },
            "auto_pause_enabled": self.auto_pause_enabled,
            "threshold_exceeded": self.current_pressure > self.max_pressure
        }

    def reset_pressure(self):
        """Reset pressure to zero (e.g., after successful checkpoint)."""
        self.current_pressure = 0.0
        self.logger.info("Pressure reset to 0.0")


class ValidationGateRunner:
    """Runs validation gates at workflow checkpoints."""

    def __init__(self, gates_config: Dict[str, Dict], logger: logging.Logger):
        """
        Initialize validation gate runner.

        Args:
            gates_config: Gate configurations from iris_agents.yaml
            logger: Logger instance
        """
        self.gates = gates_config
        self.logger = logger

    def run_gate(self, gate_name: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Run a specific validation gate.

        Args:
            gate_name: Name of gate to run
            context: Context data for gate evaluation

        Returns:
            Tuple of (gate_passed, diagnostic_info)
        """
        if gate_name not in self.gates:
            self.logger.warning(f"Gate '{gate_name}' not configured, assuming pass")
            return True, {"status": "no_gate_configured"}

        gate_config = self.gates[gate_name]
        self.logger.info(f"Running validation gate: {gate_name}")

        try:
            # S1-S3 advance gate
            if gate_name.endswith("_advance_gate"):
                return self._run_advance_gate(gate_config, context)

            # S4 success gate
            elif gate_name == "s4_success_gate":
                return self._run_s4_success_gate(gate_config, context)

            # Convergence validation gate
            elif gate_name == "convergence_validation":
                return self._run_convergence_gate(gate_config, context)

            else:
                self.logger.warning(f"Unknown gate type: {gate_name}")
                return False, {"error": f"unknown_gate_type: {gate_name}"}

        except Exception as e:
            self.logger.error(f"Gate execution error: {e}")
            return False, {"error": str(e)}

    def _run_advance_gate(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """Run advance gate for S1-S3 chambers."""
        min_mirrors_pass = config.get("min_mirrors_pass", 2)
        max_pressure = config.get("max_pressure", 2.0)

        mirrors_completed = context.get("mirrors_completed", [])
        current_pressure = context.get("pressure", 0.0)

        gate_pass = (
            len(mirrors_completed) >= min_mirrors_pass and
            current_pressure <= max_pressure
        )

        diagnostic = {
            "gate_pass": gate_pass,
            "mirrors_completed": len(mirrors_completed),
            "min_required": min_mirrors_pass,
            "current_pressure": current_pressure,
            "max_pressure": max_pressure
        }

        return gate_pass, diagnostic

    def _run_s4_success_gate(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """Run success gate for S4 chamber completion."""
        min_convergence = config.get("min_convergence_score", 0.70)
        min_mirrors_agree = config.get("min_mirrors_agree", 3)
        max_contradiction = config.get("max_contradiction_threshold", 0.25)

        convergence_score = context.get("convergence_score", 0.0)
        mirrors_agreeing = context.get("mirrors_agreeing", 0)
        contradiction_level = context.get("contradiction_level", 1.0)

        gate_pass = (
            convergence_score >= min_convergence and
            mirrors_agreeing >= min_mirrors_agree and
            contradiction_level <= max_contradiction
        )

        diagnostic = {
            "gate_pass": gate_pass,
            "convergence_score": convergence_score,
            "min_convergence_required": min_convergence,
            "mirrors_agreeing": mirrors_agreeing,
            "min_mirrors_required": min_mirrors_agree,
            "contradiction_level": contradiction_level,
            "max_contradiction_allowed": max_contradiction
        }

        return gate_pass, diagnostic

    def _run_convergence_gate(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """Run convergence validation gate."""
        min_agreement = config.get("agreement_score_min", 0.70)
        max_std = config.get("std_deviation_max", 0.30)

        agreement_score = context.get("agreement_score", 0.0)
        std_deviation = context.get("std_deviation", 1.0)

        gate_pass = (
            agreement_score >= min_agreement and
            std_deviation <= max_std
        )

        diagnostic = {
            "gate_pass": gate_pass,
            "agreement_score": agreement_score,
            "min_agreement_required": min_agreement,
            "std_deviation": std_deviation,
            "max_std_allowed": max_std
        }

        return gate_pass, diagnostic


class IRISAgentCoordinator:
    """Main coordinator for IRIS methodology agents in Claude Code."""

    def __init__(self, config_path: str = "config/iris_agents.yaml"):
        """
        Initialize IRIS agent coordinator.

        Args:
            config_path: Path to IRIS agents configuration
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.pressure_monitor = PressureMonitor(
            max_pressure=self.config.get("global_integration", {}).get("workflow_integration", {}).get("pressure_monitoring", {}).get("global_pressure_gate", 2.5),
            check_interval=5
        )

        gate_config = self.config.get("iris_agents", {}).get("session-orchestrator", {}).get("configuration", {}).get("gates", {})
        self.validation_gates = ValidationGateRunner(gate_config, self.logger)

        # Job queue
        queue_config = self.config.get("global_integration", {}).get("claude_code_integration", {})
        self.queue = FSQueue(
            queue_dir=queue_config.get("temp_directory", ".iris_agents_temp/") + "queue",
            archive_dir=queue_config.get("temp_directory", ".iris_agents_temp/") + "archive",
            logger=self.logger
        )

        # Registered agents
        self.registered_agents: Dict[str, AgentSpec] = {}
        self.active_workflows: Dict[str, WorkflowState] = {}

        # State tracking
        self.shared_state_path = Path(".iris_agents_temp/shared_state.json")
        self.shared_state_path.parent.mkdir(exist_ok=True)

    def _load_config(self) -> Dict:
        """Load IRIS agents configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration not found: {self.config_path}")

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def register_agents(self, agent_ids: Optional[List[str]] = None):
        """
        Register IRIS agents with the coordinator.

        Args:
            agent_ids: Specific agents to register, or None for all
        """
        iris_agents = self.config.get("iris_agents", {})

        if agent_ids is None:
            agent_ids = list(iris_agents.keys())

        for agent_id in agent_ids:
            if agent_id not in iris_agents:
                self.logger.warning(f"Agent '{agent_id}' not found in configuration")
                continue

            agent_config = iris_agents[agent_id]

            # Parse capabilities
            capabilities = []
            for cap in agent_config.get("capabilities", []):
                capabilities.append(AgentCapability(
                    name=cap.replace("_", " ").title(),
                    description=f"Capability: {cap}",
                    requirements=[]
                ))

            # Parse trigger conditions
            triggers = []
            for trigger in agent_config.get("trigger_conditions", []):
                triggers.append(TriggerCondition(
                    trigger_type=list(trigger.keys())[0],
                    condition=trigger.get("condition", ""),
                    priority=trigger.get("priority", 20),
                    args=trigger
                ))

            # Create agent spec
            agent_spec = AgentSpec(
                agent_id=agent_id,
                description=agent_config.get("description", ""),
                capabilities=capabilities,
                trigger_conditions=triggers,
                tool_requirements=agent_config.get("tool_requirements", {}),
                configuration=agent_config.get("configuration", {}),
                integration_points=agent_config.get("integration_points", {})
            )

            self.registered_agents[agent_id] = agent_spec
            self.logger.info(f"Registered agent: {agent_id}")

    def create_job(self, agent_id: str, command: str, args: Dict = None, priority: int = 20) -> Optional[Job]:
        """
        Create a job for the specified agent.

        Args:
            agent_id: Target agent identifier
            command: Command to execute
            args: Command arguments
            priority: Job priority (lower = higher priority)

        Returns:
            Created job or None if agent not registered
        """
        if agent_id not in self.registered_agents:
            self.logger.error(f"Agent '{agent_id}' not registered")
            return None

        agent_spec = self.registered_agents[agent_id]

        job = Job(
            command=command,
            role=agent_id,
            description=f"{agent_id}: {command}",
            priority=priority,
            timeout=300,  # 5 minutes default
            metadata=args or {}
        )

        return job

    def execute_workflow(self, workflow_type: str, plan_path: Optional[str] = None) -> str:
        """
        Execute a complete IRIS workflow.

        Args:
            workflow_type: Type of workflow ('s1-to-s8', 'convergence-only', etc.)
            plan_path: Path to workflow plan file

        Returns:
            Workflow ID for tracking
        """
        workflow_id = f"IRIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{workflow_type}"

        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            stage="initialization",
            status="pending",
            pressure=0.0,
            agents_active=[],
            checkpoints={},
            metadata={"workflow_type": workflow_type, "plan_path": plan_path}
        )

        self.active_workflows[workflow_id] = workflow_state
        self.logger.info(f"Started workflow: {workflow_id}")

        if workflow_type == "s1-to-s8":
            self._execute_s1_to_s8_workflow(workflow_id, plan_path)
        elif workflow_type == "convergence-only":
            self._execute_convergence_workflow(workflow_id, plan_path)
        else:
            self.logger.error(f"Unknown workflow type: {workflow_type}")
            workflow_state.status = "failed"

        return workflow_id

    def _execute_s1_to_s8_workflow(self, workflow_id: str, plan_path: Optional[str]):
        """Execute complete S1→S8 workflow."""
        workflow_state = self.active_workflows[workflow_id]

        try:
            # Stage 1: Session Orchestration
            workflow_state.stage = "session_orchestration"
            workflow_state.status = "running"
            self._update_workflow_state(workflow_id)

            session_job = self.create_job(
                "session-orchestrator",
                f"/start-iris-session {plan_path or 'default'}",
                priority=5
            )
            if session_job:
                self.queue.enqueue(session_job)
                workflow_state.agents_active.append("session-orchestrator")

            # Record checkpoint
            workflow_state.checkpoints["session_started"] = datetime.now()
            self.pressure_monitor.record_operation("coordinator", "session_start", 0.2)

            # Stage 2: Convergence Validation (triggered after S4)
            # This will be triggered automatically by the session orchestrator

            # Stage 3: S4 Extraction (triggered after convergence validation)
            # This will be triggered automatically

            # Stage 4: Simulation (triggered after S4 extraction)
            # This will be triggered automatically

            # Stage 5: Protocol Translation (triggered after simulation)
            # This will be triggered automatically

            self.logger.info(f"S1→S8 workflow initiated: {workflow_id}")

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            workflow_state.status = "failed"
            workflow_state.metadata["error"] = str(e)

    def _execute_convergence_workflow(self, workflow_id: str, plan_path: Optional[str]):
        """Execute convergence analysis only."""
        workflow_state = self.active_workflows[workflow_id]

        try:
            workflow_state.stage = "convergence_analysis"
            workflow_state.status = "running"

            convergence_job = self.create_job(
                "convergence-validator",
                f"/validate-convergence {plan_path or './vault'}",
                priority=15
            )
            if convergence_job:
                self.queue.enqueue(convergence_job)
                workflow_state.agents_active.append("convergence-validator")

            workflow_state.checkpoints["convergence_started"] = datetime.now()
            self.pressure_monitor.record_operation("coordinator", "convergence_start", 0.1)

            self.logger.info(f"Convergence workflow initiated: {workflow_id}")

        except Exception as e:
            self.logger.error(f"Convergence workflow failed: {e}")
            workflow_state.status = "failed"
            workflow_state.metadata["error"] = str(e)

    def _update_workflow_state(self, workflow_id: str):
        """Update workflow state in shared storage."""
        if workflow_id not in self.active_workflows:
            return

        workflow_state = self.active_workflows[workflow_id]

        # Update shared state file
        shared_state = {}
        if self.shared_state_path.exists():
            with open(self.shared_state_path) as f:
                shared_state = json.load(f)

        shared_state[workflow_id] = asdict(workflow_state)

        with open(self.shared_state_path, 'w') as f:
            json.dump(shared_state, f, indent=2, default=str)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status."""
        if workflow_id not in self.active_workflows:
            return None

        workflow_state = self.active_workflows[workflow_id]
        pressure_stats = self.pressure_monitor.get_pressure_stats()

        return {
            "workflow_id": workflow_id,
            "stage": workflow_state.stage,
            "status": workflow_state.status,
            "agents_active": workflow_state.agents_active,
            "checkpoints": {k: v.isoformat() for k, v in workflow_state.checkpoints.items()},
            "pressure": pressure_stats,
            "metadata": workflow_state.metadata
        }

    def list_active_workflows(self) -> List[str]:
        """List all active workflow IDs."""
        return list(self.active_workflows.keys())

    def emergency_stop(self, workflow_id: Optional[str] = None, preserve_state: bool = True):
        """
        Emergency stop for workflows.

        Args:
            workflow_id: Specific workflow to stop, or None for all
            preserve_state: Whether to preserve state for recovery
        """
        if workflow_id:
            workflow_ids = [workflow_id] if workflow_id in self.active_workflows else []
        else:
            workflow_ids = list(self.active_workflows.keys())

        for wf_id in workflow_ids:
            workflow_state = self.active_workflows[wf_id]
            workflow_state.status = "emergency_stopped"
            workflow_state.metadata["emergency_stop_time"] = datetime.now().isoformat()
            workflow_state.metadata["preserve_state"] = preserve_state

            self.logger.warning(f"Emergency stop executed: {wf_id}")

            if preserve_state:
                self._update_workflow_state(wf_id)
            else:
                del self.active_workflows[wf_id]

    def cleanup_resources(self):
        """Clean up temporary resources and stale state."""
        # Clean up temporary files
        temp_dir = Path(".iris_agents_temp/")
        if temp_dir.exists():
            import shutil
            for item in temp_dir.iterdir():
                if item.is_file() and item.name.endswith('.tmp'):
                    item.unlink()
                elif item.is_dir() and 'stale' in item.name:
                    shutil.rmtree(item)

        # Archive completed workflows
        completed_workflows = [
            wf_id for wf_id, state in self.active_workflows.items()
            if state.status in ["completed", "failed"]
        ]

        for wf_id in completed_workflows:
            self._update_workflow_state(wf_id)  # Final state save
            del self.active_workflows[wf_id]

        self.logger.info(f"Cleaned up {len(completed_workflows)} completed workflows")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IRIS Agent Coordinator - Claude Code Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start coordinator and register all agents
  %(prog)s --start

  # Register specific agent
  %(prog)s --register convergence-validator

  # Execute S1→S8 workflow
  %(prog)s --workflow s1-to-s8 --plan plans/bioelectric_session.yaml

  # Monitor workflow status
  %(prog)s --status --watch

  # Emergency stop all workflows
  %(prog)s --emergency-stop --preserve-state
        """
    )

    parser.add_argument(
        "--config",
        default="config/iris_agents.yaml",
        help="Path to IRIS agents config (default: config/iris_agents.yaml)"
    )

    parser.add_argument(
        "--start",
        action="store_true",
        help="Start coordinator and register all agents"
    )

    parser.add_argument(
        "--register",
        metavar="AGENT_ID",
        help="Register specific agent"
    )

    parser.add_argument(
        "--workflow",
        choices=["s1-to-s8", "convergence-only"],
        help="Execute workflow type"
    )

    parser.add_argument(
        "--plan",
        help="Path to workflow plan file"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Show workflow status"
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch status continuously (with --status)"
    )

    parser.add_argument(
        "--emergency-stop",
        action="store_true",
        help="Emergency stop all workflows"
    )

    parser.add_argument(
        "--preserve-state",
        action="store_true",
        help="Preserve state during emergency stop"
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up temporary resources"
    )

    args = parser.parse_args()

    try:
        coordinator = IRISAgentCoordinator(config_path=args.config)

        if args.start:
            coordinator.register_agents()
            print("IRIS Agent Coordinator started successfully")
            print(f"Registered agents: {list(coordinator.registered_agents.keys())}")

        if args.register:
            coordinator.register_agents([args.register])
            print(f"Registered agent: {args.register}")

        if args.workflow:
            workflow_id = coordinator.execute_workflow(args.workflow, args.plan)
            print(f"Started workflow: {workflow_id}")

        if args.status:
            workflows = coordinator.list_active_workflows()
            if not workflows:
                print("No active workflows")
            else:
                for wf_id in workflows:
                    status = coordinator.get_workflow_status(wf_id)
                    if status:
                        print(f"\nWorkflow: {wf_id}")
                        print(f"  Stage: {status['stage']}")
                        print(f"  Status: {status['status']}")
                        print(f"  Active agents: {', '.join(status['agents_active'])}")
                        print(f"  Pressure: {status['pressure']['current_pressure']:.2f}")

            if args.watch:
                print("\nWatching status (Ctrl+C to stop)...")
                try:
                    while True:
                        time.sleep(5)
                        # Refresh status display
                        print("\n" + "="*50)
                        workflows = coordinator.list_active_workflows()
                        for wf_id in workflows:
                            status = coordinator.get_workflow_status(wf_id)
                            if status:
                                print(f"{wf_id}: {status['stage']} ({status['status']})")
                except KeyboardInterrupt:
                    print("\nStopped watching")

        if args.emergency_stop:
            coordinator.emergency_stop(preserve_state=args.preserve_state)
            print("Emergency stop executed")

        if args.cleanup:
            coordinator.cleanup_resources()
            print("Resource cleanup completed")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())