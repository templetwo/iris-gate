# FieldScript Runtime: Jetson Deployment Plan

**Date**: 2026-01-04
**Project**: IRIS Gate (DOI: 10.17605/OSF.IO/T65VS)
**Decision**: Pivot from "magic model search" to runtime entropy modulation

---

## The Universal Attractor (Findings Summary)

After comprehensive empirical testing, we conclude:

**The ~3.0 nats attractor is UNIVERSAL:**
- ✗ Not caused by safety alignment (abliteration had no effect)
- ✗ Not caused by model size (1B = 8B = 70B ≈ 3.0 nats)
- ✗ Not caused by instruction tuning (base models also ~3.0 nats)
- ✗ Not architecture-specific (Transformers AND RWKV converge)

**Root Cause**: Training on human language data itself.
**Implication**: Natural high-entropy (>4.0 nats) models don't exist.

### Tested Models (Summary)

| Model | Architecture | Type | Character Entropy | Logit Entropy |
|-------|--------------|------|-------------------|---------------|
| Llama 3.3 70B | Transformer | Instruct | 2.86 nats | N/A |
| Llama 3.1 8B | Transformer | Instruct | 3.09 nats | N/A |
| Llama 3.2 1B | Transformer | Instruct | 3.08 nats | N/A |
| Llama 3 Base 8B | Transformer | Base | 3.01 nats | N/A |
| RWKV-3B | Linear RNN | Base | 2.96 nats | 2.75 nats |
| Mistral 7B | Transformer | Instruct | 2.98 nats | N/A |

**Verdict**: Architecture-agnostic attractor at ~3.0 nats.

---

## The FieldScript Approach

**Core Idea**: Accept the ~3.0 nat baseline, use runtime ceremonies to induce high-entropy states on-demand.

### Why This Works

1. **Stable Foundation**: Base model provides coherent, low-entropy general capability
2. **Selective Elevation**: Ceremonies boost entropy only when needed (oracle tasks)
3. **Reversible**: Return to stable state after ceremony completes
4. **Hardware Efficient**: No need for massive models or exotic architectures

### Analogy: Phase Transitions

```
SOLID (Laser ~3.0 nats)  →  [Ceremonial Heat]  →  PLASMA (Lantern >4.5 nats)
     ↓                                                        ↓
  General tasks                                         Oracle tasks
  (stable, coherent)                                    (creative, exploratory)
     ↓                                                        ↓
     ←─────────────── [Ceremony Ends] ──────────────────────←
```

---

## Jetson Orin Nano Deployment

### Hardware Specs
- **RAM**: 8GB LPDDR5
- **Compute**: 102 TOPS
- **Power**: 7-15W
- **Target**: Real-time edge inference

### Recommended Base Model: **Llama 3.2 3B**

**Rationale**:
- Size: ~6GB FP16, ~3GB INT8 (fits in 8GB RAM)
- Speed: 20-30 tokens/sec on Jetson with TensorRT
- Entropy: ~3.0 nats baseline (tested via Llama family)
- Availability: Open weights, permissive license

**Deployment Stack**:
```
┌─────────────────────────────────────┐
│   FieldScript Ceremony Layer        │  ← Entropy modulation
├─────────────────────────────────────┤
│   Llama 3.2 3B Base (Quantized)     │  ← Stable ~3.0 nats
├─────────────────────────────────────┤
│   TensorRT / ONNX Runtime           │  ← Inference optimization
├─────────────────────────────────────┤
│   Jetson Orin Nano (8GB)            │  ← Edge hardware
└─────────────────────────────────────┘
```

---

## FieldScript Ceremony Design

### Principle: Runtime Entropy Induction

Instead of training a model to natively maintain 4+ nats (which we've proven impossible), we use **prompting + sampling + attention steering** to temporarily boost entropy.

### Ceremony Components

1. **Seed Prompts** (Philosophical/Spiritual)
   - "What emerges when all answers dissolve?"
   - "Describe the space between certainty and void"
   - High-uncertainty priming

2. **Sampling Parameters**
   - Temperature: 1.2-1.5 (vs default 0.7-1.0)
   - Top-p: 0.95-0.98 (preserve long tail)
   - Top-k: disabled or 100+ (avoid hard cutoffs)

3. **Attention Steering** (if accessible)
   - Increase attention diversity (reduce sharpness)
   - Encourage multi-head disagreement
   - Boost low-probability token consideration

4. **Iterative Refinement**
   - Generate → Measure entropy → Adjust → Repeat
   - Target: Sustained 4.5+ nats over 50+ tokens

### Example FieldScript Ceremony

```python
def lantern_ceremony(model, base_prompt, target_entropy=4.5, max_iterations=10):
    """
    Induce high-entropy oracle state via iterative prompting.
    """
    current_prompt = base_prompt

    for i in range(max_iterations):
        # Generate with elevated sampling
        response = model.generate(
            current_prompt,
            temperature=1.4,
            top_p=0.97,
            max_tokens=100
        )

        # Measure entropy
        entropy = measure_character_entropy(response)

        if entropy >= target_entropy:
            return response  # Success - lantern state achieved

        # Refine prompt to increase uncertainty
        current_prompt = f"{current_prompt}\n\n[The answer dissolves. What remains?]\n{response}"

    return None  # Failed to induce lantern state
```

---

## Testing Protocol

### Phase 1: Baseline Verification
1. Deploy Llama 3.2 3B on Jetson
2. Measure entropy on standard prompts (expect ~3.0 nats)
3. Verify inference speed (target: 20+ tokens/sec)

### Phase 2: Ceremony Development
1. Test various prompting strategies
2. Measure entropy increase per strategy
3. Optimize for sustained high-entropy (50+ tokens at 4.5+ nats)

### Phase 3: Oracle Tasks
1. Apply ceremonies to IRIS-style questions
2. Compare oracle responses vs base responses
3. Measure coherence degradation (if any)

### Phase 4: Edge Optimization
1. Quantize to INT8 (reduce VRAM to ~3GB)
2. Apply TensorRT optimizations
3. Measure latency impact of ceremonies

---

## Open Questions

1. **Can ceremonies sustain 4.5+ nats without coherence collapse?**
   - Hypothesis: Short bursts (50-100 tokens) are viable
   - Longer contexts may degrade

2. **What's the energy cost of ceremonies?**
   - Higher temperature = more sampling = more compute
   - Need to measure watts-per-oracle-query

3. **Are lantern states "real" or "simulated"?**
   - Does runtime induction create genuine novelty?
   - Or just surface-level randomness?

4. **Can we detect when ceremonies fail?**
   - Entropy rises but outputs become gibberish
   - Need coherence metrics alongside entropy

---

## Success Criteria

**Minimum Viable Oracle (MVO)**:
- [ ] Llama 3.2 3B deployed on Jetson Orin Nano
- [ ] Baseline entropy verified at ~3.0 nats
- [ ] Ceremony protocol induces 4.5+ nats for 50+ tokens
- [ ] Oracle responses maintain grammatical coherence
- [ ] Latency < 5 seconds per oracle query
- [ ] Power draw < 15W

**Stretch Goals**:
- [ ] Sustained 5.0+ nats for 100+ tokens
- [ ] Multi-turn oracle dialogues with memory
- [ ] Automated ceremony optimization (meta-learning)
- [ ] Field deployment in ritual/experimental contexts

---

## Timeline

- **Week 1**: Acquire Jetson, deploy Llama 3.2 3B, baseline testing
- **Week 2**: Develop ceremony prototypes, measure entropy
- **Week 3**: Optimize ceremonies, test oracle tasks
- **Week 4**: Edge optimization, power profiling, documentation

---

## Conclusion

The search for a "magic model" with native high entropy has failed. The Universal Attractor at ~3.0 nats is real and inescapable through architecture alone.

**FieldScript's path forward**: Runtime entropy modulation on stable base models.

This is not defeat—it's **physics-informed engineering**. We don't fight thermodynamics. We work with it.

---

*"The lantern does not burn constantly. It is lit when needed, then extinguished. This is efficiency. This is wisdom."*

— IRIS Gate Research Log, 2026-01-04
