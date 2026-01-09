"""
Test suite for IRIS Gate convergence analysis.

Tests core functionality: data loading, embedding, concept extraction,
and visualization generation.
"""

import unittest
import tempfile
import json
from pathlib import Path
import numpy as np

from data_loader import DataLoader, ProbeResponse, CheckpointData
from convergence_analyzer import ConvergenceAnalyzer, ConvergenceMetrics
from concept_extractor import ConceptExtractor, ConceptProfile
from visualizer import ConvergenceVisualizer


class TestDataLoader(unittest.TestCase):
    """Test data loading and parsing."""

    def setUp(self):
        """Create temporary checkpoint data."""
        self.temp_dir = tempfile.mkdtemp()
        self.session_dir = Path(self.temp_dir) / "test_session"
        self.session_dir.mkdir()

        # Create mock checkpoint
        checkpoint_data = {
            "session_id": "TEST_SESSION",
            "iteration": 1,
            "timestamp": "2026-01-09T00:00:00",
            "architectures": ["claude", "gpt", "grok"],
            "probe_results": {
                "PROBE_1": [
                    {
                        "probe_id": "PROBE_1",
                        "iteration": 1,
                        "architecture": "claude",
                        "model": "claude-test",
                        "response": "This is a test response about physics and entropy.",
                        "timestamp": "2026-01-09T00:00:00",
                        "prompt": "Test prompt"
                    },
                    {
                        "probe_id": "PROBE_1",
                        "iteration": 1,
                        "architecture": "gpt",
                        "model": "gpt-test",
                        "response": "This is another test response about mass and information.",
                        "timestamp": "2026-01-09T00:00:01",
                        "prompt": "Test prompt"
                    }
                ]
            }
        }

        checkpoint_path = self.session_dir / "checkpoint_001.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f)

    def test_loader_initialization(self):
        """Test DataLoader initializes correctly."""
        loader = DataLoader(self.session_dir)
        self.assertEqual(len(loader.checkpoint_files), 1)

    def test_load_checkpoint(self):
        """Test loading single checkpoint."""
        loader = DataLoader(self.session_dir)
        checkpoint = loader.load_checkpoint(loader.checkpoint_files[0])

        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.iteration, 1)
        self.assertEqual(len(checkpoint.probe_responses), 2)

    def test_get_probe_ids(self):
        """Test probe ID extraction."""
        loader = DataLoader(self.session_dir)
        probe_ids = loader.get_probe_ids()

        self.assertIn("PROBE_1", probe_ids)

    def test_probe_history(self):
        """Test loading probe history."""
        loader = DataLoader(self.session_dir)
        history = loader.load_probe_history("PROBE_1")

        self.assertIn(1, history)
        self.assertEqual(len(history[1]), 2)


class TestConvergenceAnalyzer(unittest.TestCase):
    """Test convergence analysis and similarity computation."""

    def setUp(self):
        """Create mock responses."""
        self.responses = [
            ProbeResponse(
                probe_id="PROBE_1",
                iteration=1,
                architecture="claude",
                model="test",
                response="Mass is resistance to acceleration in spacetime according to general relativity.",
                timestamp="2026-01-09T00:00:00",
                prompt="Test"
            ),
            ProbeResponse(
                probe_id="PROBE_1",
                iteration=1,
                architecture="gpt",
                model="test",
                response="Physical mass represents inertial resistance to changes in motion per Newton's laws.",
                timestamp="2026-01-09T00:00:01",
                prompt="Test"
            ),
            ProbeResponse(
                probe_id="PROBE_1",
                iteration=1,
                architecture="grok",
                model="test",
                response="The sky is blue because of Rayleigh scattering in the atmosphere.",
                timestamp="2026-01-09T00:00:02",
                prompt="Test"
            )
        ]

    def test_embedding_generation(self):
        """Test that embeddings are generated correctly."""
        analyzer = ConvergenceAnalyzer()
        embedding = analyzer.embed_response(self.responses[0])

        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(len(embedding.shape), 1)
        self.assertGreater(len(embedding), 0)

    def test_similarity_matrix_shape(self):
        """Test similarity matrix has correct shape."""
        analyzer = ConvergenceAnalyzer()
        sim_matrix, arch_names = analyzer.compute_similarity_matrix(self.responses)

        self.assertEqual(sim_matrix.shape, (3, 3))
        self.assertEqual(len(arch_names), 3)

    def test_similarity_properties(self):
        """Test similarity matrix properties."""
        analyzer = ConvergenceAnalyzer()
        sim_matrix, _ = analyzer.compute_similarity_matrix(self.responses)

        # Diagonal should be 1 (self-similarity)
        for i in range(len(sim_matrix)):
            self.assertAlmostEqual(sim_matrix[i, i], 1.0, places=5)

        # Matrix should be symmetric
        for i in range(len(sim_matrix)):
            for j in range(len(sim_matrix)):
                self.assertAlmostEqual(sim_matrix[i, j], sim_matrix[j, i], places=5)

    def test_convergence_metrics(self):
        """Test convergence metrics computation."""
        analyzer = ConvergenceAnalyzer()
        metrics = analyzer.analyze_probe_iteration("PROBE_1", 1, self.responses)

        self.assertIsInstance(metrics, ConvergenceMetrics)
        self.assertEqual(metrics.probe_id, "PROBE_1")
        self.assertEqual(metrics.iteration, 1)
        self.assertGreater(metrics.mean_similarity, 0)
        self.assertLessEqual(metrics.mean_similarity, 1)

    def test_similar_responses_high_similarity(self):
        """Test that similar responses have high similarity."""
        similar_responses = [
            ProbeResponse(
                probe_id="PROBE_1",
                iteration=1,
                architecture="claude",
                model="test",
                response="Mass is resistance to acceleration.",
                timestamp="2026-01-09T00:00:00",
                prompt="Test"
            ),
            ProbeResponse(
                probe_id="PROBE_1",
                iteration=1,
                architecture="gpt",
                model="test",
                response="Mass represents resistance to acceleration.",
                timestamp="2026-01-09T00:00:01",
                prompt="Test"
            )
        ]

        analyzer = ConvergenceAnalyzer()
        metrics = analyzer.analyze_probe_iteration("PROBE_1", 1, similar_responses)

        # Similar responses should have high similarity
        self.assertGreater(metrics.mean_similarity, 0.8)

    def test_divergent_responses_low_similarity(self):
        """Test that divergent responses have low similarity."""
        divergent_responses = [
            ProbeResponse(
                probe_id="PROBE_1",
                iteration=1,
                architecture="claude",
                model="test",
                response="Mass is resistance to acceleration in physics.",
                timestamp="2026-01-09T00:00:00",
                prompt="Test"
            ),
            ProbeResponse(
                probe_id="PROBE_1",
                iteration=1,
                architecture="gpt",
                model="test",
                response="The capital of France is Paris.",
                timestamp="2026-01-09T00:00:01",
                prompt="Test"
            )
        ]

        analyzer = ConvergenceAnalyzer()
        metrics = analyzer.analyze_probe_iteration("PROBE_1", 1, divergent_responses)

        # Divergent responses should have low similarity
        self.assertLess(metrics.mean_similarity, 0.5)

    def test_divergence_detection(self):
        """Test divergence detection."""
        # Create metrics with decreasing similarity
        metrics = []
        for i in range(5):
            metric = ConvergenceMetrics(
                probe_id="PROBE_1",
                iteration=i+1,
                similarity_matrix=np.array([[1.0, 0.2], [0.2, 1.0]]),
                architecture_names=["claude", "gpt"],
                mean_similarity=0.2,
                std_similarity=0.1,
                min_similarity=0.2,
                max_similarity=1.0,
                convergence_score=0.2
            )
            metrics.append(metric)

        analyzer = ConvergenceAnalyzer()
        divergent = analyzer.detect_divergence(metrics, threshold=0.3, window_size=3)

        # Should detect divergence
        self.assertGreater(len(divergent), 0)


class TestConceptExtractor(unittest.TestCase):
    """Test concept extraction from responses."""

    def setUp(self):
        """Create test responses."""
        self.extractor = ConceptExtractor()

        self.response = ProbeResponse(
            probe_id="PROBE_1",
            iteration=1,
            architecture="claude",
            model="test",
            response="""
            This analysis uses Verlinde's entropic gravity and Landauer's principle.
            The Bekenstein bound constrains information entropy. Using General Relativity
            and Statistical Mechanics, we derive F = ma where mass represents resistance.
            Confidence: 0.85 in this prediction.
            """,
            timestamp="2026-01-09T00:00:00",
            prompt="Test"
        )

    def test_citation_extraction(self):
        """Test citation extraction."""
        citations = self.extractor.extract_citations(self.response.response)

        self.assertIn("Verlinde", citations)
        self.assertIn("Landauer", citations)
        self.assertIn("Bekenstein", citations)

    def test_framework_extraction(self):
        """Test framework extraction."""
        frameworks = self.extractor.extract_frameworks(self.response.response)

        self.assertIn("General Relativity", frameworks)
        self.assertIn("Statistical Mechanics", frameworks)

    def test_confidence_extraction(self):
        """Test confidence statement extraction."""
        statements = self.extractor.extract_confidence_statements(self.response.response)

        self.assertGreater(len(statements), 0)
        self.assertTrue(any("0.85" in s for s in statements))

    def test_keyword_extraction(self):
        """Test keyword extraction."""
        keywords = self.extractor.extract_keywords(self.response.response)

        self.assertIn("mass", keywords)
        self.assertIn("entropy", keywords)
        self.assertIn("resistance", keywords)

    def test_profile_extraction(self):
        """Test complete profile extraction."""
        profile = self.extractor.extract_profile(self.response)

        self.assertIsInstance(profile, ConceptProfile)
        self.assertGreater(profile.num_citations, 0)
        self.assertGreater(profile.num_frameworks, 0)

    def test_citation_network(self):
        """Test citation network building."""
        profiles = [
            ConceptProfile(
                response_id=("PROBE_1", 1, "claude"),
                citations=["Verlinde", "Landauer"],
                frameworks=[],
                keywords=[],
                equations=[],
                confidence_statements=[]
            ),
            ConceptProfile(
                response_id=("PROBE_1", 1, "gpt"),
                citations=["Verlinde", "Bekenstein"],
                frameworks=[],
                keywords=[],
                equations=[],
                confidence_statements=[]
            )
        ]

        network = self.extractor.build_citation_network(profiles)

        # Verlinde co-cited with both Landauer and Bekenstein
        self.assertIn("Verlinde", network)
        self.assertIn("Landauer", network["Verlinde"])
        self.assertIn("Bekenstein", network["Verlinde"])


class TestVisualizer(unittest.TestCase):
    """Test visualization generation."""

    def setUp(self):
        """Create test metrics."""
        self.metrics = ConvergenceMetrics(
            probe_id="PROBE_1",
            iteration=1,
            similarity_matrix=np.array([
                [1.0, 0.8, 0.7],
                [0.8, 1.0, 0.75],
                [0.7, 0.75, 1.0]
            ]),
            architecture_names=["claude", "gpt", "grok"],
            mean_similarity=0.75,
            std_similarity=0.05,
            min_similarity=0.7,
            max_similarity=0.8,
            convergence_score=0.7
        )

        self.temp_dir = tempfile.mkdtemp()
        self.visualizer = ConvergenceVisualizer(output_dir=Path(self.temp_dir))

    def test_similarity_matrix_plot(self):
        """Test similarity matrix plot generation."""
        fig = self.visualizer.plot_similarity_matrix(self.metrics)

        self.assertIsNotNone(fig)
        # Check that figure was saved
        saved_files = list(Path(self.temp_dir).glob("similarity_*.png"))
        self.assertGreater(len(saved_files), 0)

    def test_trajectory_plot(self):
        """Test convergence trajectory plot."""
        trajectory = {
            'iterations': np.array([1, 2, 3]),
            'mean_similarity': np.array([0.5, 0.6, 0.7]),
            'std_similarity': np.array([0.1, 0.08, 0.05]),
            'convergence_score': np.array([0.4, 0.5, 0.65]),
            'min_similarity': np.array([0.3, 0.4, 0.6]),
            'max_similarity': np.array([0.7, 0.8, 0.85])
        }

        fig = self.visualizer.plot_convergence_trajectory(
            trajectory,
            "PROBE_1"
        )

        self.assertIsNotNone(fig)


def run_integration_test(session_dir: str):
    """
    Integration test using real data.

    Args:
        session_dir: Path to real session directory
    """
    print(f"\nRunning integration test on: {session_dir}")

    from data_loader import load_session

    # Load data
    loader = load_session(session_dir)
    print(f"Loaded {len(loader.checkpoint_files)} checkpoints")

    # Test probe history
    probe_ids = loader.get_probe_ids()
    print(f"Found probes: {probe_ids}")

    if probe_ids:
        probe_id = probe_ids[0]
        history = loader.load_probe_history(probe_id)
        print(f"Probe {probe_id} has {len(history)} iterations")

        # Test convergence analysis on first iteration
        if 1 in history:
            responses = history[1]
            print(f"Iteration 1 has {len(responses)} responses")

            analyzer = ConvergenceAnalyzer()
            metrics = analyzer.analyze_probe_iteration(probe_id, 1, responses)

            print(f"Mean similarity: {metrics.mean_similarity:.3f}")
            print(f"Convergence score: {metrics.convergence_score:.3f}")

    print("Integration test passed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--integration":
        # Run integration test with real data
        if len(sys.argv) > 2:
            run_integration_test(sys.argv[2])
        else:
            print("Usage: python test_analysis.py --integration <session_dir>")
    else:
        # Run unit tests
        unittest.main()
