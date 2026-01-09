"""
Data loader for IRIS Gate convergence checkpoint data.

Loads and parses checkpoint JSON files from convergence sessions,
providing structured access to probe results across iterations.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProbeResponse:
    """Single model response to a probe question."""
    probe_id: str
    iteration: int
    architecture: str
    model: str
    response: str
    timestamp: str
    prompt: str

    @property
    def response_length(self) -> int:
        """Character count of response."""
        return len(self.response)

    @property
    def word_count(self) -> int:
        """Word count of response."""
        return len(self.response.split())


@dataclass
class CheckpointData:
    """Data from a single checkpoint file."""
    session_id: str
    iteration: int
    timestamp: str
    architectures: List[str]
    probe_responses: List[ProbeResponse] = field(default_factory=list)

    @property
    def num_responses(self) -> int:
        """Total number of responses in this checkpoint."""
        return len(self.probe_responses)

    def get_responses_by_probe(self, probe_id: str) -> List[ProbeResponse]:
        """Get all responses for a specific probe."""
        return [r for r in self.probe_responses if r.probe_id == probe_id]

    def get_responses_by_architecture(self, arch: str) -> List[ProbeResponse]:
        """Get all responses from a specific architecture."""
        return [r for r in self.probe_responses if r.architecture == arch]


class DataLoader:
    """
    Load and parse IRIS Gate checkpoint data.

    Expected structure:
    - session_dir/checkpoint_001.json
    - session_dir/checkpoint_002.json
    - ...

    Each checkpoint contains probe_results dict with probe_id keys.
    """

    def __init__(self, session_dir: Path):
        """
        Initialize loader.

        Args:
            session_dir: Path to session directory containing checkpoints

        Raises:
            ValueError: If session_dir doesn't exist or has no checkpoints
        """
        self.session_dir = Path(session_dir)
        if not self.session_dir.exists():
            raise ValueError(f"Session directory not found: {session_dir}")

        self.checkpoint_files = sorted(self.session_dir.glob("checkpoint_*.json"))
        if not self.checkpoint_files:
            raise ValueError(f"No checkpoint files found in {session_dir}")

        logger.info(f"Found {len(self.checkpoint_files)} checkpoint files")

    def load_checkpoint(self, checkpoint_path: Path) -> Optional[CheckpointData]:
        """
        Load a single checkpoint file.

        Args:
            checkpoint_path: Path to checkpoint JSON

        Returns:
            CheckpointData object or None if loading fails
        """
        try:
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)

            # Parse probe results (dict with probe_id keys)
            probe_responses = []
            probe_results = data.get('probe_results', {})

            for probe_id, responses in probe_results.items():
                for response_data in responses:
                    # Handle missing fields gracefully
                    try:
                        probe_responses.append(ProbeResponse(
                            probe_id=response_data.get('probe_id', probe_id),
                            iteration=response_data.get('iteration', data.get('iteration', 0)),
                            architecture=response_data.get('architecture', 'unknown'),
                            model=response_data.get('model', 'unknown'),
                            response=response_data.get('response', response_data.get('content', '')),
                            timestamp=response_data.get('timestamp', data.get('timestamp', '')),
                            prompt=response_data.get('prompt', '')
                        ))
                    except Exception as e:
                        logger.warning(f"Skipping malformed response in {checkpoint_path}: {e}")

            return CheckpointData(
                session_id=data['session_id'],
                iteration=data['iteration'],
                timestamp=data['timestamp'],
                architectures=data['architectures'],
                probe_responses=probe_responses
            )

        except Exception as e:
            logger.error(f"Failed to load {checkpoint_path}: {e}")
            return None

    def load_all_checkpoints(self) -> List[CheckpointData]:
        """
        Load all checkpoint files in the session.

        Returns:
            List of CheckpointData objects, sorted by iteration
        """
        checkpoints = []
        for cp_path in self.checkpoint_files:
            cp_data = self.load_checkpoint(cp_path)
            if cp_data:
                checkpoints.append(cp_data)

        checkpoints.sort(key=lambda x: x.iteration)
        logger.info(f"Loaded {len(checkpoints)} checkpoints")
        return checkpoints

    def get_probe_ids(self) -> List[str]:
        """Get all unique probe IDs across checkpoints."""
        # Load first checkpoint to get probe IDs
        first_cp = self.load_checkpoint(self.checkpoint_files[0])
        if first_cp:
            return sorted(set(r.probe_id for r in first_cp.probe_responses))
        return []

    def get_architectures(self) -> List[str]:
        """Get list of architectures."""
        first_cp = self.load_checkpoint(self.checkpoint_files[0])
        if first_cp:
            return first_cp.architectures
        return []

    def load_probe_history(self, probe_id: str) -> Dict[int, List[ProbeResponse]]:
        """
        Load all responses for a specific probe across iterations.

        Args:
            probe_id: Probe identifier (e.g., 'PROBE_1')

        Returns:
            Dict mapping iteration -> list of responses from all architectures
        """
        history = {}
        for cp_data in self.load_all_checkpoints():
            responses = cp_data.get_responses_by_probe(probe_id)
            if responses:
                history[cp_data.iteration] = responses

        return history


def load_session(session_dir: str) -> DataLoader:
    """
    Convenience function to create a DataLoader.

    Args:
        session_dir: Path to session directory

    Returns:
        DataLoader instance
    """
    return DataLoader(Path(session_dir))


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        loader = load_session(sys.argv[1])
        print(f"Probe IDs: {loader.get_probe_ids()}")
        print(f"Architectures: {loader.get_architectures()}")
        print(f"Checkpoints: {len(loader.checkpoint_files)}")
