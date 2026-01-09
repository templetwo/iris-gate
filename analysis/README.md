# IRIS Gate Convergence Analysis System

Comprehensive analysis and visualization system for IRIS Gate convergence experiments. Analyzes semantic convergence across AI architectures using embedding-based similarity, extracts physics concepts, and generates publication-ready visualizations.

## Features

### 1. Convergence Analysis
- Semantic similarity computation using sentence transformers
- Convergence/divergence detection across iterations
- Architecture-pair similarity tracking
- Statistical convergence metrics

### 2. Physics Concept Extraction
- Automatic citation detection (Landauer, Verlinde, IIT, etc.)
- Framework identification (GR, QFT, statistical mechanics)
- Keyword frequency analysis
- Equation extraction
- Novel proposal identification

### 3. Visualization Suite
- Convergence heatmaps (probe x iteration)
- Similarity matrices
- Citation co-occurrence networks
- Response evolution plots
- Summary dashboards

### 4. Report Generation
- Executive summaries
- Probe-by-probe analysis
- Architecture comparisons
- Publication-ready markdown reports

## Installation

```bash
cd /Users/vaquez/iris-gate/analysis
pip install -r requirements.txt
```

**Note**: First run will download the sentence-transformers model (~90MB). This happens automatically.

## Quick Start

### Full Analysis

```bash
python analyze_convergence.py /Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127
```

This will:
1. Load all checkpoint data
2. Compute semantic embeddings
3. Analyze convergence for all probes
4. Extract physics concepts
5. Generate visualizations in `analysis_output/figures/`
6. Create comprehensive report in `analysis_output/full_report.md`

### Analyze Specific Probe

```bash
python analyze_convergence.py <session_dir> --probe PROBE_5
```

### Skip Embeddings (Fast Mode)

```bash
python analyze_convergence.py <session_dir> --skip-embeddings
```

Skips semantic similarity analysis but still extracts concepts and generates concept-based visualizations.

### Search for Physics Concepts

```bash
python analyze_convergence.py <session_dir> --search "Verlinde"
```

Finds all responses mentioning "Verlinde" and displays context.

### Compare Architectures

```bash
python analyze_convergence.py <session_dir> --compare PROBE_1 claude gpt
```

Compares Claude vs GPT responses on PROBE_1 across all iterations.

## Usage Examples

### Programmatic Access

```python
from data_loader import load_session
from convergence_analyzer import ConvergenceAnalyzer
from visualizer import ConvergenceVisualizer

# Load data
loader = load_session("path/to/session")
probe_history = loader.load_probe_history("PROBE_1")

# Analyze convergence
analyzer = ConvergenceAnalyzer()
metrics = analyzer.analyze_probe_evolution(probe_history)

# Visualize
viz = ConvergenceVisualizer(output_dir="figures")
trajectory = analyzer.compute_convergence_trajectory(metrics)
viz.plot_convergence_trajectory(trajectory, "PROBE_1")
```

### Extract Concepts

```python
from concept_extractor import ConceptExtractor

extractor = ConceptExtractor()
profile = extractor.extract_profile(response)

print(f"Citations: {profile.citations}")
print(f"Frameworks: {profile.frameworks}")
print(f"Keywords: {profile.keywords[:10]}")
```

## Architecture

```
analysis/
├── data_loader.py           # Load and parse checkpoint JSONs
├── convergence_analyzer.py  # Semantic similarity and convergence metrics
├── concept_extractor.py     # Physics concept extraction
├── visualizer.py            # Visualization generation
├── report_generator.py      # Markdown report creation
├── analyze_convergence.py   # CLI entry point
├── test_analysis.py         # Test suite
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Data Structure

Expected checkpoint format:
```json
{
  "session_id": "...",
  "iteration": 1,
  "timestamp": "...",
  "architectures": ["claude", "gpt", "grok", "gemini", "deepseek"],
  "probe_results": {
    "PROBE_1": [
      {
        "probe_id": "PROBE_1",
        "iteration": 1,
        "architecture": "claude",
        "model": "claude-sonnet-4-5-20250929",
        "response": "...",
        "timestamp": "...",
        "prompt": "..."
      }
    ]
  }
}
```

## Output Structure

```
analysis_output/
├── full_report.md                    # Comprehensive markdown report
├── figures/
│   ├── similarity_PROBE_1_iter1.png  # Per-iteration similarity matrices
│   ├── trajectory_PROBE_1.png        # Convergence trajectories
│   ├── probe_comparison_heatmap.png  # Cross-probe comparison
│   ├── citation_network.png          # Citation co-occurrence network
│   ├── framework_usage.png           # Framework frequency bar chart
│   └── summary_dashboard.png         # Comprehensive dashboard
└── cache/
    └── *.pkl                          # Cached embeddings
```

## Testing

### Unit Tests
```bash
python test_analysis.py
```

### Integration Test
```bash
python test_analysis.py --integration /path/to/session
```

## Key Metrics

### Convergence Score
Combines mean similarity and stability:
```
convergence_score = mean_similarity × (1 - std_similarity)
```
- Range: [0, 1]
- Higher = more convergence
- Accounts for both agreement level and consistency

### Divergence Detection
Flags iterations where:
- Mean similarity < threshold (default: 0.3)
- Low similarity persists for multiple iterations (default: 3)

## Performance

### Speed
- Loading 13 checkpoints: ~2 seconds
- Computing embeddings (cached): ~1 minute first run, <1 second cached
- Full analysis (6 probes, 13 iterations): ~3-5 minutes

### Memory
- Peak memory: ~2GB with embeddings in cache
- Can process sessions with 1000+ responses

## Customization

### Change Embedding Model
```python
analyzer = ConvergenceAnalyzer(model_name="all-mpnet-base-v2")
```

Options:
- `all-MiniLM-L6-v2`: Fast, 384-dim (default)
- `all-mpnet-base-v2`: Slower, more accurate, 768-dim
- `all-MiniLM-L12-v2`: Balanced

### Adjust Divergence Threshold
```python
divergent = analyzer.detect_divergence(
    metrics,
    threshold=0.3,     # Similarity threshold
    window_size=3      # Consecutive iterations
)
```

### Add Custom Citations
Edit `concept_extractor.py`:
```python
CITATIONS = {
    'YourCitation': r'\bYourPattern\b',
    # ...
}
```

## Troubleshooting

### Out of Memory
- Use smaller embedding model
- Process probes individually with `--probe`
- Clear cache: `rm -rf analysis_output/cache/`

### Slow Embedding
- Ensure CUDA is available: `torch.cuda.is_available()`
- Use CPU with small model for testing
- Cache is created after first run

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Citations

If using this system for research, please cite the relevant frameworks:
- Sentence Transformers: Reimers & Gurevych (2019)
- Semantic similarity methodology: Standard cosine similarity in embedding space

## License

Part of the IRIS Gate project. See main repository for license.
