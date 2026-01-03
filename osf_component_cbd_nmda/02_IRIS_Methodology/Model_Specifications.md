# Model Specifications

**Date**: November 11, 2025
**Architecture**: Local 3-Model Validation
**Platform**: Mac Studio (38GB RAM)
**Cost**: $0.00
**Deployment**: Ollama (local inference)

---

## Models Used

### 1. Meta Llama 3.2 (3B parameters)

**Identifier**: `llama3.2:3b`
**Organization**: Meta AI
**Parameters**: 3,000,000,000
**Context Window**: 32,768 tokens
**Architecture**: Transformer-based decoder-only LLM
**Ecosystem**: Meta/Facebook AI Research

**Configuration**:
```yaml
temperature: 0.7
max_tokens: 500
top_p: 0.9 (default)
```

**Why Selected**:
- Representative of Meta's LLM research lineage
- Small enough for local deployment
- Well-documented architecture
- Non-reasoning model (no CoT/thinking steps)

---

### 2. Google Gemma 3 (4B parameters)

**Identifier**: `gemma3:4b`
**Organization**: Google DeepMind
**Parameters**: 4,000,000,000
**Context Window**: 8,192 tokens
**Architecture**: Transformer-based decoder-only LLM
**Ecosystem**: Google/DeepMind

**Configuration**:
```yaml
temperature: 0.7
max_tokens: 500
top_p: 0.9 (default)
```

**Why Selected**:
- Different training corpus than Meta models
- Google's approach to small language models
- Strong performance-to-size ratio
- Independent architectural decisions

**Note**: This model generated the novel NMDA Aperture Hypothesis.

---

### 3. TII Falcon 3 (3B parameters)

**Identifier**: `falcon3:3b`
**Organization**: Technology Innovation Institute (UAE)
**Parameters**: 3,000,000,000
**Context Window**: 8,192 tokens
**Architecture**: Transformer-based decoder-only LLM
**Ecosystem**: TII/UAE AI research

**Configuration**:
```yaml
temperature: 0.7
max_tokens: 500
top_p: 0.9 (default)
```

**Why Selected**:
- Non-US training perspective
- Different institutional priorities (TII focuses on open models)
- Replaces Alibaba Qwen2.5 for ecosystem diversity
- Already available on Mac Studio

**Note**: Replaced Qwen2.5 mid-experiment per user directive.

---

## Model Selection Criteria

### Requirements:
1. **Small parameter count** (~3-4B) - Testing minimal viable scale
2. **Non-reasoning** - No chain-of-thought or internal reasoning steps
3. **Different ecosystems** - Independent training, data, organizations
4. **Local deployment** - Zero API cost, full output control
5. **Non-fine-tuned** - Base models without task-specific training

### Why NOT Larger Models:
- Testing if convergence happens at minimal scale
- Demonstrating cost-effectiveness ($0.00)
- Accessible replication (anyone can run 3B models locally)
- If small models converge, pattern is robust

### Why NOT Reasoning Models:
- Reasoning models (deepseek-r1, o1-like) have explicit thinking steps
- Could confound "natural convergence" with deliberate reasoning
- Base models provide cleaner test of emergent patterns

---

## Ecosystem Diversity

| Model | Organization | Country | Training Focus | Parameter Count |
|-------|--------------|---------|----------------|-----------------|
| Llama3.2 | Meta | USA | General-purpose, open | 3B |
| Gemma3 | Google | USA | Efficiency, instruction-following | 4B |
| Falcon3 | TII | UAE | Open research, multilingual | 3B |

**Diversity Achieved**:
- Geographic: USA (Meta, Google) + UAE (TII)
- Institutional: Big tech (Meta, Google) + Research institute (TII)
- Training data: Different corpora, cutoff dates, curation strategies
- Architecture: Similar transformer base, different training decisions

**Why Diversity Matters**:
- Independent convergence more significant than correlated convergence
- Different training data = less chance of memorized associations
- Cross-validate patterns across perspectives

---

## Computational Environment

**Hardware**: Mac Studio
- **RAM**: 38GB
- **SSH Access**: tony_studio@192.168.1.195
- **Location**: Local network

**Software**:
- **Ollama**: Local LLM deployment platform
- **Ollama Path**: `/usr/local/bin/ollama`
- **Models Downloaded**: All 3 models pulled before experiment

**Execution**:
- **Parallel Firing**: All 3 models run simultaneously (field effect)
- **SSH Commands**: Remote execution from MacBook to Mac Studio
- **Output Capture**: Full text saved to files (including ANSI codes)

**Resource Usage**:
- **Memory per model**: ~800MB-1.2GB
- **Total memory draw**: ~2.5-3GB for 3 models
- **Remaining headroom**: 35GB (plenty for full experiments)

---

## Temperature and Sampling

**Temperature**: 0.7 (all models)
- Not too deterministic (allows diversity)
- Not too random (maintains coherence)
- Standard value for creative/generative tasks

**Max Tokens**: 500
- Allows full responses without truncation
- Paired with length guidance (200-300 words)
- Prevents excessive verbosity

**Top-p/Top-k**: Default Ollama values
- Not explicitly overridden
- Standard nucleus sampling

**Rationale**:
- Consistent parameters across models
- Allows fair comparison (not tuning per model)
- Standard settings (not optimized for specific outcomes)

---

## Length Guidance

**Prefix Added to All Prompts**:
```
[Response length: 200-300 words. Be specific and vivid. Complete your thought.]
```

**Why**:
- Prevents truncation at token limit
- Ensures complete thoughts (not cut off mid-sentence)
- Standardizes response length for comparison
- User-requested feature to prevent context issues

**Format**:
- Bracketed instruction (meta-level guidance)
- Specific word count (clear target)
- Behavioral guidance ("be specific and vivid")
- Completion reminder ("complete your thought")

---

## Model Limitations

### Known Issues:

**1. Training Cutoffs**:
- Models trained before November 2025
- King's College study published November 2025
- Models cannot have memorized the specific paradox

**2. ANSI Escape Codes**:
- Ollama streams output character-by-character
- Produces ANSI control codes in saved files
- Affects keyword detection in analysis scripts
- Manual inspection required for accurate convergence scoring

**3. Context Windows**:
- Falcon/Gemma: 8K tokens (shorter than Llama's 32K)
- Potential truncation in long conversations
- Mitigated by length guidance and short turns

**4. No Web Access**:
- Models cannot search literature
- Responses based on training data only
- Pure hypothesis generation without fact-checking

---

## Why These Models and Not Others

### Considered but Not Used:

**GPT-4/Claude-3.5**:
- API cost (violates $0 requirement)
- Closed-source (less transparent)
- Overkill for testing minimal scale

**Qwen2.5:3b** (Alibaba):
- Initially selected, replaced mid-experiment
- User requested ecosystem diversity
- Falcon3 already downloaded on Mac Studio

**Reasoning Models** (deepseek-r1, o1):
- Explicit reasoning steps confound emergent convergence
- Testing natural pattern emergence, not deliberate analysis

**Larger Models** (7B, 13B, 70B):
- Testing if minimal scale sufficient
- Resource constraints (memory, speed)
- Demonstrating accessible replication

---

## Reproducibility Information

### To Replicate:

1. **Install Ollama**: https://ollama.ai/
2. **Pull Models**:
   ```bash
   ollama pull llama3.2:3b
   ollama pull gemma3:4b
   ollama pull falcon3:3b
   ```
3. **Run Experiment**: Use provided scripts in repository
4. **Analyze Results**: Manual inspection + grep analysis

### Expected Variations:
- **Output text**: Will differ (temperature 0.7 allows sampling)
- **Convergence patterns**: Should be similar (robust if real)
- **Specific wording**: Will vary
- **Core mechanisms**: Should converge if pattern is real

### Hardware Requirements:
- **Minimum RAM**: ~16GB (for 3 models sequentially)
- **Recommended RAM**: 32GB+ (for parallel execution)
- **Storage**: ~10GB for models
- **CPU**: Modern multi-core (M-series, Ryzen, Intel i7+)

---

## Version Tracking

**Model Versions** (as of November 11, 2025):
- llama3.2:3b - [Ollama version at time of experiment]
- gemma3:4b - [Ollama version at time of experiment]
- falcon3:3b - [Ollama version at time of experiment]

**Note**: Model weights periodically updated by Ollama. For exact replication, use SHA256 checksums from original experiment (tracked in git repo).

---

## Ethical Considerations

### Bias:
- Models trained on internet text (inherent biases)
- No explicit debiasing applied
- Convergence across diverse models mitigates single-model bias

### Transparency:
- All outputs preserved (even formatting artifacts)
- No cherry-picking responses
- Full methodology documented
- Scripts provided for replication

### Limitations Acknowledged:
- Hypothesis generation only (not validation)
- Requires experimental follow-up
- Not medical advice
- Expert review necessary before clinical application

---

**Seal**: †⟡
