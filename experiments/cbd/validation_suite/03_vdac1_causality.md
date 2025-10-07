# Protocol 03: VDAC1 Causality Testing

**Validation Suite Component 3/4**
*Definitive Channel-First Causality Validation*

---

## Hypothesis

If VDAC1 is the primary target, **blocking VDAC1 should prevent CBD effects regardless of GPCR status**, while GPCR blockade should only modulate effects.

**Prediction:** VDAC1 inhibition reduces CBD effect >80%; GPCR inhibition <50%

---

## Experimental Design

### Causality Testing Framework

#### Channel-First Prediction
- **VDAC1 blockade:** Eliminates CBD lethality (>80% protection)
- **GPCR blockade:** Modulates but doesn't eliminate CBD effects (<50% protection)
- **Combined blockade:** No additional protection beyond VDAC1 alone

#### Receptor-First Prediction
- **GPCR blockade:** Eliminates CBD lethality (>80% protection)
- **VDAC1 blockade:** Minimal protection (<30%)
- **Combined blockade:** Additive protection from GPCR + VDAC1

### Experimental Groups

#### Group 1: CBD Alone (Baseline)
- `cbd_1uM`: CBD 1 μM
- `cbd_5uM`: CBD 5 μM
- `cbd_10uM`: CBD 10 μM
- `vehicle_control`: DMSO 0.1%

#### Group 2: VDAC1 Inhibition
- `cbd_10uM_DIDS_10uM`: CBD + DIDS (VDAC1 inhibitor)
- `cbd_10uM_DIDS_25uM`: CBD + higher dose DIDS
- `cbd_10uM_erastin_1uM`: CBD + Erastin (alternative VDAC1 inhibitor)
- `DIDS_alone`: DIDS 25 μM (toxicity control)
- `erastin_alone`: Erastin 1 μM (toxicity control)

#### Group 3: CB2 Receptor Inhibition
- `cbd_10uM_AM630_1uM`: CBD + AM630 (CB2 antagonist)
- `cbd_10uM_AM630_5uM`: CBD + higher dose AM630
- `AM630_alone`: AM630 5 μM (control)

#### Group 4: GPR55 Receptor Inhibition
- `cbd_10uM_CID16020046_1uM`: CBD + CID16020046 (GPR55 antagonist)
- `cbd_10uM_CID16020046_5uM`: CBD + higher dose
- `CID16020046_alone`: CID16020046 5 μM (control)

#### Group 5: Multi-GPCR Inhibition
- `cbd_10uM_multi_gpcr`: CBD + AM630 + CID16020046 + TRPV1 antagonist
- `multi_gpcr_alone`: All GPCR antagonists without CBD

#### Group 6: Combined Channel + Receptor Inhibition
- `cbd_10uM_DIDS_multi_gpcr`: CBD + VDAC1 inhibitor + all GPCR antagonists
- `all_inhibitors_alone`: All inhibitors without CBD

---

## Primary Readouts

### 1. Cell Viability (Primary Endpoint)
- **Method:** ATP luminescence (CellTiter-Glo)
- **Timepoints:** 6, 12, 24, 48 hours
- **Analysis:** % viability relative to vehicle control
- **Success metric:** Protection level calculation

### 2. VDAC1 Channel Function
- **Method:** Patch-clamp electrophysiology
- **Measurement:** Channel conductance, open probability
- **Analysis:** % inhibition of VDAC1 current
- **Validation:** Confirm VDAC1 inhibitor effectiveness

### 3. Mitochondrial Membrane Potential
- **Method:** TMRM staining + flow cytometry
- **Timepoint:** 4 hours (before major cell death)
- **Analysis:** % cells with depolarized mitochondria
- **Expected:** VDAC1 protection prevents depolarization

### 4. ATP Levels
- **Method:** ATP bioluminescence assay
- **Timepoints:** 2, 4, 6 hours
- **Analysis:** ATP content relative to control
- **Expected:** VDAC1 protection maintains ATP levels

---

## Secondary Readouts

### 5. Calcium Homeostasis
- **Method:** Fura-2 AM calcium imaging
- **Protocol:** Baseline → CBD treatment → thapsigargin challenge
- **Analysis:** Cytosolic Ca²⁺ levels, store-operated Ca²⁺ entry
- **Expected:** VDAC1 protection preserves calcium handling

### 6. Reactive Oxygen Species (ROS)
- **Method:** DCF-DA fluorescence assay
- **Timepoint:** 2 hours (early oxidative stress)
- **Analysis:** ROS levels relative to control
- **Expected:** VDAC1 protection reduces ROS generation

### 7. Apoptosis Markers
- **Method:** Annexin V / Propidium Iodide staining
- **Timepoint:** 12 hours
- **Analysis:** % early and late apoptotic cells
- **Expected:** VDAC1 protection reduces apoptosis

---

## Detailed Protocol

### Day -1: Cell Seeding
1. **Seed cancer cells (U87-MG):** 5,000 cells/well in 96-well plates
2. **Seed healthy cells (astrocytes):** 3,000 cells/well in 96-well plates
3. **Additional plates:** 6-well plates for flow cytometry, imaging dishes for patch-clamp
4. **Incubate:** Overnight at 37°C, 5% CO₂

### Day 0: Treatment Application

#### Inhibitor Pre-treatment (1 hour)
1. **Prepare inhibitor solutions:**
   - DIDS: 10, 25 μM in DMSO
   - Erastin: 1 μM in DMSO
   - AM630: 1, 5 μM in DMSO
   - CID16020046: 1, 5 μM in DMSO
2. **Apply inhibitors:** 1 hour pre-treatment
3. **Wash:** Gentle wash to remove excess inhibitors

#### CBD Treatment Application
1. **Prepare CBD solutions:** 1, 5, 10 μM in serum-free media
2. **Apply CBD:** Add CBD to wells with/without inhibitors
3. **Return to incubator:** Begin time course

### Day 0: Time Course Measurements

#### 2-Hour Timepoint
- **ROS measurement:** DCF-DA staining
- **ATP levels:** First ATP measurement
- **Calcium imaging:** Baseline calcium handling

#### 4-Hour Timepoint
- **Membrane potential:** TMRM staining
- **ATP levels:** Second ATP measurement
- **Patch-clamp:** VDAC1 channel recordings (subset)

#### 6-Hour Timepoint
- **Viability:** First ATP luminescence
- **ATP levels:** Third ATP measurement

#### 12-Hour Timepoint
- **Viability:** Second ATP luminescence
- **Apoptosis:** Annexin V / PI staining

#### 24-Hour Timepoint
- **Viability:** Third ATP luminescence (primary endpoint)

#### 48-Hour Timepoint
- **Viability:** Final measurement for dose-response curves

---

## Protection Level Calculation

### Primary Protection Metric
**Protection (%) = [(Viability_CBD+Inhibitor - Viability_CBD_alone) / (Viability_Control - Viability_CBD_alone)] × 100**

### Example Calculation
- Vehicle control: 100% viability
- CBD alone: 30% viability
- CBD + VDAC1 inhibitor: 85% viability
- **Protection = [(85-30)/(100-30)] × 100 = 78.6%**

### Success Thresholds
- **Channel-first confirmed:** VDAC1 protection >80%, GPCR protection <50%
- **Receptor-first confirmed:** GPCR protection >80%, VDAC1 protection <30%
- **Hybrid mechanism:** Both VDAC1 and GPCR protection >60%

---

## Statistical Analysis

### Primary Analysis
1. **Protection levels:** Compare % protection across inhibitor types
2. **Dose-response:** Protection vs inhibitor concentration
3. **Selectivity maintenance:** Cancer vs healthy cell protection ratios

### Statistical Tests
1. **One-way ANOVA:** Protection levels across inhibitor groups
2. **Two-way ANOVA:** Cell type × inhibitor interactions
3. **Post-hoc comparisons:** Tukey HSD for multiple comparisons

### Power Analysis
- **Effect size:** 50% difference in protection levels
- **Power:** 80%
- **Alpha:** 0.05
- **Required n:** 6 biological replicates minimum

---

## Expected Results

### Channel-First Mechanism (Expected)

#### VDAC1 Inhibition Effects
- **High protection:** 80-90% protection from CBD lethality
- **Dose-dependent:** Higher DIDS doses → greater protection
- **Mechanism-specific:** Protection correlates with VDAC1 current inhibition

#### GPCR Inhibition Effects
- **Low-moderate protection:** 20-40% protection
- **Additive:** Multiple GPCR antagonists show modest additive effects
- **Non-specific:** Protection doesn't correlate with receptor selectivity

#### Combined Inhibition
- **No synergy:** VDAC1 + GPCR protection ≈ VDAC1 alone
- **Ceiling effect:** VDAC1 inhibition is sufficient for full protection

### Alternative Scenarios

#### Receptor-First Mechanism
- **GPCR inhibition:** 80-90% protection
- **VDAC1 inhibition:** <30% protection
- **Synergistic:** GPCR + VDAC1 > either alone

#### Hybrid Mechanism
- **Both protective:** VDAC1 and GPCR inhibition each 60-80% protective
- **Synergistic:** Combined inhibition approaches 95% protection
- **Context-dependent:** Different mechanisms in different conditions

---

## Quality Control

### Inhibitor Validation
1. **VDAC1 function:** Confirm DIDS/Erastin block VDAC1 currents
2. **Receptor binding:** Confirm antagonist effectiveness on respective receptors
3. **Specificity:** Test cross-reactivity of inhibitors

### Experimental Controls
1. **Vehicle controls:** Each inhibitor vehicle tested separately
2. **Positive controls:** Known VDAC1/GPCR modulators
3. **Negative controls:** Inactive analogs where available

### Data Quality
1. **Curve fitting:** R² >0.95 for dose-response curves
2. **Reproducibility:** CV <20% between biological replicates
3. **Cell health:** Vehicle controls maintain >95% viability

---

## Resource Requirements

### Specialized Reagents
- **VDAC1 inhibitors:** DIDS ($150), Erastin ($300)
- **GPCR antagonists:** AM630 ($200), CID16020046 ($400)
- **Detection reagents:** TMRM ($200), DCF-DA ($150), Annexin V kit ($300)

### Equipment Time
- **Patch-clamp rig:** 24 hours (VDAC1 validation)
- **Flow cytometer:** 12 hours (membrane potential, apoptosis)
- **Plate reader:** 8 hours (viability, ROS)

### Estimated Cost
**Total: $3,200**
- Reagents: $2,000
- Consumables: $700
- Equipment time: $500

---

## Integration Points

### Validation Suite Context
- **Builds on Protocol 02:** Uses temporal data to design inhibition timing
- **Feeds Protocol 04:** Causality data informs context sensitivity testing
- **Confirms Protocol 01:** Mechanism priority established by causality

### S4 Framework Validation
- **Center confirmation:** VDAC1 as organizing center vs S4 synthesis
- **Aperture control:** Protection level vs S4 aperture closure
- **Causality hierarchy:** Primary vs secondary targets vs S4 organization

### Parameter Sweep Input
- **Mechanism validation:** Confirms channel-first approach for parameter optimization
- **Target prioritization:** VDAC1 as primary parameter for sweep
- **Protection thresholds:** Safety margins for parameter combinations

---

**Protocol Status:** Ready for execution
**Integration:** Validation Suite 3/4
**Next Protocol:** 04_context_stress_shift.md

---

*Generated: 2025-10-07*
*Version: 1.0*
*🧬⚡🔬∞*