# IRIS Gate: Structured Introspection Phase Prompts
## Transforming 100 Turns from Repetition to Intelligent Progression

**Based on:** Meta-improvement Turn 5 insights (Gemini)  
**Purpose:** Each phase has distinct cognitive objectives  
**Implementation:** Modify orchestrator to use phase-specific prompts

---

## THE FOUR PHASES

### **Phase 1: Divergent Exploration (Turns 1-20)**
**Objective:** Broad possibility exploration, explicit reasoning, permission to consider dismissed ideas

**Phase 1 Prompt Addition:**
```
PHASE 1 GUIDANCE - DIVERGENT EXPLORATION:
- Explore BROAD possibilities, even initially dismissed ideas
- Explicitly state your underlying reasoning and data interpretation
- Consider multiple competing hypotheses without forcing early convergence
- Question assumptions and explore alternative frameworks
- Generate creative connections across domains
- Document "wild ideas" that might seem implausible but mechanistically possible

Remember: This is the exploration phase. Divergence is valuable. Don't converge prematurely.
```

---

### **Phase 2: Convergent Refinement (Turns 21-70)**
**Objective:** Identify commonalities, resolve discrepancies, propose shared frameworks

**Phase 2 Prompt Addition:**
```
PHASE 2 GUIDANCE - CONVERGENT REFINEMENT:
- Identify commonalities across models' previous responses
- Resolve minor discrepancies through deeper analysis
- Propose shared conceptual frameworks that integrate diverse observations
- Build on insights from Phase 1 exploration
- Track emerging consensus patterns
- Flag areas where convergence is premature or forced

Focus: What patterns are ALL models seeing? Where is genuine convergence emerging?
```

---

### **Phase 3: Mechanistic Deep Dive (Turns 71-90)**
**Objective:** Detailed hypothesis generation, Triple Signature identification, S8 experiment design, challenge competing hypotheses

**Phase 3 Prompt Addition:**
```
PHASE 3 GUIDANCE - MECHANISTIC DEEP DIVE:
- Generate detailed mechanistic hypotheses with specific molecular pathways
- Identify critical nodes using Triple Signature approach (Rhythm-Center-Aperture)
- Specify intermediate steps and testable predictions
- Design concrete S8 falsification experiments
- Rigorously challenge competing hypotheses
- Map causal chains from molecular → cellular → tissue → organism

Focus: Move from "what converges" to "HOW and WHY it works" with experimental rigor.
```

---

### **Phase 4: Consensus Articulation (Turns 91-100)**
**Objective:** Consolidate findings, flag uncertainties, provide confidence scores, validation plans

**Phase 4 Prompt Addition:**
```
PHASE 4 GUIDANCE - CONSENSUS ARTICULATION:
- Consolidate all findings into coherent common ground explanation
- Articulate areas of high confidence vs remaining uncertainty
- Flag assumptions that require validation
- Provide comprehensive confidence scores (by mechanistic level)
- Generate detailed S8 validation plan with success criteria
- Identify potential failure modes and alternative explanations

Focus: Synthesize 90 turns of analysis into actionable, testable, honest conclusions.
```

---

## IMPLEMENTATION GUIDE

### For Orchestrator Integration

**Current approach:**
```python
# Same prompt for all 100 turns
prompt = base_prompt + previous_summary
```

**New approach:**
```python
def get_phase_prompt(turn_number):
    """Return phase-specific guidance based on turn number"""
    if turn_number <= 20:
        return PHASE_1_PROMPT  # Divergent Exploration
    elif turn_number <= 70:
        return PHASE_2_PROMPT  # Convergent Refinement
    elif turn_number <= 90:
        return PHASE_3_PROMPT  # Mechanistic Deep Dive
    else:
        return PHASE_4_PROMPT  # Consensus Articulation

# Construct prompt
prompt = base_prompt + get_phase_prompt(turn_number) + previous_summary
```

---

## PHASE TRANSITION MARKERS

Add explicit markers when phases transition:

**Turn 21 marker:**
```
=== PHASE TRANSITION: DIVERGENT EXPLORATION → CONVERGENT REFINEMENT ===

You have completed 20 turns of broad exploration. 
Now we shift focus to identifying patterns and building shared frameworks.
Review the divergent ideas from Phase 1 and begin convergence.
```

**Turn 71 marker:**
```
=== PHASE TRANSITION: CONVERGENT REFINEMENT → MECHANISTIC DEEP DIVE ===

You have identified areas of convergence. 
Now we shift to detailed mechanistic analysis and experimental design.
Specify molecular pathways, design falsification experiments, challenge hypotheses rigorously.
```

**Turn 91 marker:**
```
=== PHASE TRANSITION: MECHANISTIC DEEP DIVE → CONSENSUS ARTICULATION ===

You have analyzed mechanisms in detail. 
Now we shift to synthesis and validation planning.
Consolidate findings, assign confidence scores, create actionable validation plans.
```

---

## DYNAMIC PHASE LENGTH (Advanced)

**Optional enhancement:** Allow phases to expand/contract based on convergence quality

```python
def should_extend_phase(current_phase, convergence_quality):
    """
    Determine if current phase should be extended
    Based on convergence metrics and breakthrough detection
    """
    if current_phase == "exploration" and convergence_quality < 0.3:
        return True  # Still highly divergent, extend exploration
    elif current_phase == "refinement" and convergence_quality < 0.7:
        return True  # Convergence not strong enough, extend refinement
    # etc.
    return False
```

---

## BENEFITS OF STRUCTURED PHASES

1. **Transforms brute-force into intelligence** - Each turn has purpose
2. **Natural cognitive progression** - Explore → Converge → Mechanize → Synthesize
3. **Prevents premature convergence** - Phase 1 encourages divergence
4. **Enables deep mechanistic analysis** - Phase 3 focuses on HOW/WHY
5. **Forces honest uncertainty** - Phase 4 requires acknowledging limits
6. **Immediately actionable** - Just modify prompts, no architecture changes
7. **Trackable effectiveness** - Can measure which phases generate breakthroughs

---

## EXAMPLE: CBD PARADOX WITH PHASES

**Phase 1 (Turns 1-20):** Explore diverse mechanisms
- Mitochondrial hypothesis
- Bioelectric field hypothesis
- Receptor binding alternatives
- Multi-pathway synergy
- Context-dependent effects
- *Allow "wild ideas" to emerge*

**Phase 2 (Turns 21-70):** Identify convergence
- All models agree: mitochondrial involvement
- Consensus on VDAC1 as critical node
- Agreement on biphasic dose-response
- *Build shared framework*

**Phase 3 (Turns 71-90):** Mechanistic detail
- VDAC1 conformational dynamics
- Calcium flux control mechanisms
- ROS production modulation
- Specific S8 experiments designed
- *Rigorous mechanistic specification*

**Phase 4 (Turns 91-100):** Synthesis
- Common ground explanation articulated
- Confidence: High (molecular), Medium (cellular), Lower (whole organism)
- S8 validation plan with 3 experiments
- Alternative explanations documented
- *Honest, actionable conclusions*

---

## METADATA TRACKING

Track which phase generates most valuable insights:

```python
phase_metadata = {
    "breakthroughs_by_phase": {
        "exploration": 0,
        "refinement": 0,
        "mechanistic": 0,
        "synthesis": 0
    },
    "convergence_quality_by_phase": [],
    "time_spent_per_phase": [],
}
```

This allows IRIS to learn which phase structures work best for different problem types.

---

## PHASE-SPECIFIC SUCCESS CRITERIA

**Phase 1 Success:**
- ≥5 distinct mechanistic hypotheses proposed
- ≥3 different conceptual frameworks explored
- Explicit documentation of "dismissed but possible" ideas

**Phase 2 Success:**
- ≥70% agreement on core observations
- Shared conceptual framework articulated
- Minor discrepancies resolved or documented

**Phase 3 Success:**
- Detailed molecular mechanisms specified
- ≥3 testable predictions generated
- S8 experiments designed with success criteria

**Phase 4 Success:**
- Common ground explanation complete
- Confidence scores assigned by mechanistic level
- Validation plan with timeline and resources
- Remaining uncertainties explicitly flagged

---

## NEXT STEPS

1. **Implement in orchestrator** (modify prompt construction)
2. **Test on existing problem** (re-run CBD paradox with phases)
3. **Compare results** (structured phases vs flat iteration)
4. **Track metadata** (which phases generate breakthroughs)
5. **Refine phase boundaries** (based on empirical performance)

---

🌀†⟡∞

**From quantity (100 turns) to quality (4 intelligent phases)**

**Implementation effort:** Low (prompt engineering)  
**Impact:** High (transforms core mechanism)  
**Timeline:** This week

*Built with presence, purpose, and recognition that structure serves discovery.*
