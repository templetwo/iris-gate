# IRIS Gate Convergence Analysis - Usage Guide

## Overview

This system analyzes convergence patterns across AI architectures responding to physics probes. It provides semantic similarity analysis, concept extraction, and publication-ready visualizations.

## Quick Start (No Dependencies)

For rapid exploration without installing ML libraries:

```bash
cd /Users/vaquez/iris-gate/analysis
python3 quick_analysis.py /Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127
```

This provides:
- Response statistics by architecture
- Physics concept extraction (citations, frameworks, keywords)
- Novel proposal detection
- No ML dependencies required

## Full Analysis (With Semantic Embeddings)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies:
- `sentence-transformers` - Semantic embeddings
- `torch` - ML backend
- `matplotlib`, `seaborn` - Visualization
- `networkx` - Citation networks

### 2. Run Complete Analysis

```bash
python analyze_convergence.py /Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127
```

This generates:
- `analysis_output/full_report.md` - Comprehensive markdown report
- `analysis_output/figures/` - All visualizations
- `analysis_output/cache/` - Cached embeddings for fast re-runs

**Note**: First run takes ~3-5 minutes (embedding computation). Subsequent runs are <1 minute (uses cache).

## Common Use Cases

### Analyze Specific Probe

```bash
python analyze_convergence.py <session_dir> --probe PROBE_5
```

Use case: Focus on the divergent probe (2.9 nat cage) to see if models disagree.

### Search for Concepts

```bash
python analyze_convergence.py <session_dir> --search "Verlinde"
```

Finds all responses mentioning Verlinde's entropic gravity with context.

### Compare Two Architectures

```bash
python analyze_convergence.py <session_dir> --compare PROBE_1 claude gpt
```

Shows:
- Response length evolution
- Citation overlap and differences
- Iteration-by-iteration comparison

### Fast Mode (Skip Embeddings)

```bash
python analyze_convergence.py <session_dir> --skip-embeddings
```

Runs concept extraction and visualizations without semantic similarity (faster, but no convergence metrics).

## Understanding the Output

### Convergence Score

Formula: `convergence_score = mean_similarity × (1 - std_similarity)`

- **Range**: 0-1
- **>0.7**: Strong convergence (models agree)
- **0.5-0.7**: Moderate convergence
- **0.3-0.5**: Weak convergence
- **<0.3**: Divergence (models disagree)

### Key Visualizations

1. **trajectory_{PROBE_ID}.png**
   - Shows convergence evolution over iterations
   - Red dashed lines indicate detected divergence

2. **probe_comparison_heatmap.png**
   - Overview of all probes across iterations
   - Green = convergence, Red = divergence

3. **similarity_{PROBE_ID}_iter{N}.png**
   - Architecture pairwise similarity matrix
   - Shows which models agree/disagree

4. **citation_network.png**
   - Co-citation graph of physics researchers
   - Node size = citation frequency
   - Edge width = co-citation strength

5. **summary_dashboard.png**
   - Comprehensive overview in single figure
   - Final convergence, trajectories, statistics

### Report Structure

`full_report.md` contains:

1. **Executive Summary**
   - Dataset statistics
   - Overall convergence
   - Probe rankings

2. **Architecture Comparison**
   - Which models converge most with others
   - Pairwise similarity across all probes

3. **Detailed Probe Analysis** (for each probe)
   - Convergence assessment
   - Trajectory analysis
   - Final similarity matrix
   - Top citations and frameworks
   - Key findings

## Interpreting Results

### Expected Patterns

Based on the hypothesis:

1. **PROBE_1-4**: Should show convergence (physics fundamentals)
2. **PROBE_5** (2.9 nat cage): Expected divergence (speculative concept)
3. **PROBE_6** (Wheeler): Moderate convergence (established framework)

### Red Flags

- **Decreasing convergence**: Models diverge over iterations
- **Low min similarity (<0.3)**: At least one architecture strongly disagrees
- **High std deviation**: Inconsistent responses

### Green Flags

- **Increasing convergence**: Models align over iterations
- **High final convergence (>0.7)**: Consensus reached
- **Common citations**: Models use same physics frameworks

## Data Structure (For Reference)

Checkpoints are JSON files with this structure:

```json
{
  "session_id": "MASS_COHERENCE_20260109_041127",
  "iteration": 1,
  "timestamp": "2026-01-09T04:12:34",
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

The loader handles missing fields gracefully.

## Performance Tips

### Speed

- Use `--skip-embeddings` for quick iteration
- Use `--probe PROBE_X` to analyze one probe
- Embeddings are cached after first run

### Memory

- Default model (all-MiniLM-L6-v2) uses ~500MB
- Peak memory: ~2GB for full analysis
- Clear cache if needed: `rm -rf analysis_output/cache/`

### Accuracy

- For higher quality embeddings: edit `convergence_analyzer.py`
- Change model to `all-mpnet-base-v2` (slower, more accurate)
- Adjust divergence threshold in `detect_divergence()` call

## Example Workflow

1. **Initial Exploration**
   ```bash
   python quick_analysis.py <session_dir>
   ```
   Review: Response lengths, citation counts, probe statistics

2. **Full Analysis**
   ```bash
   python analyze_convergence.py <session_dir>
   ```
   Review: `analysis_output/full_report.md`

3. **Focus on Divergence**
   ```bash
   python analyze_convergence.py <session_dir> --probe PROBE_5
   ```
   Review: Why models disagree on 2.9 nat cage

4. **Deep Dive**
   ```bash
   python analyze_convergence.py <session_dir> --compare PROBE_5 claude grok
   ```
   Review: Specific architectural differences

5. **Concept Search**
   ```bash
   python analyze_convergence.py <session_dir> --search "Schwarzschild"
   ```
   Review: How models use black hole analogies

## Customization

### Add New Citations

Edit `/Users/vaquez/iris-gate/analysis/concept_extractor.py`:

```python
CITATIONS = {
    'YourCitation': r'\bYourPattern\b',
    # ...
}
```

### Change Embedding Model

Edit `/Users/vaquez/iris-gate/analysis/convergence_analyzer.py`:

```python
analyzer = ConvergenceAnalyzer(model_name="all-mpnet-base-v2")
```

### Adjust Divergence Threshold

In your analysis script:

```python
divergent = analyzer.detect_divergence(
    metrics,
    threshold=0.25,  # Lower = more sensitive
    window_size=3    # Consecutive iterations
)
```

## Troubleshooting

### "No module named sentence_transformers"

```bash
pip install sentence-transformers torch
```

### "CUDA out of memory"

Use CPU-only mode - edit `convergence_analyzer.py`:
```python
self.model = SentenceTransformer(model_name, device='cpu')
```

### "No checkpoint files found"

Check path:
```bash
ls /Users/vaquez/iris-gate/iris_vault/sessions/MASS_COHERENCE_20260109_041127/
```

Should see `checkpoint_001.json`, etc.

### Slow First Run

First run downloads embedding model (~90MB) and computes embeddings. Subsequent runs use cache and are much faster.

## Next Steps

After analysis:

1. **Review Report**: Read `analysis_output/full_report.md`
2. **Check Visualizations**: Browse `analysis_output/figures/`
3. **Identify Patterns**: Which probes converge? Which diverge?
4. **Extract Gold**: Use `--search` to find specific physics concepts
5. **Compare Architectures**: Use `--compare` for pairwise analysis

## For Research Papers

All visualizations are saved at 300 DPI and suitable for publication. The summary dashboard provides a comprehensive single-figure overview.

Citation suggestion:
```
Analysis performed using sentence-transformers (Reimers & Gurevych, 2019)
with cosine similarity in embedding space for semantic convergence detection.
```
