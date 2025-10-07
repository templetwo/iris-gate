# Protocol 02: PLA Mitochondrial Ensemble Mapping

**Validation Suite Component 2/4**
*Temporal Analysis of CBD-Target Interactions*

---

## Hypothesis

If channel-first mechanism is correct, **CBD-VDAC1 interactions should precede CBD-GPCR interactions** temporally, and mitochondrial localization should be primary.

**Prediction:** CBD-VDAC1 PLA signal peaks 15+ minutes before CBD-GPCR PLA signals

---

## Experimental Design

### Proximity Ligation Assay (PLA) Strategy

#### Target Interaction Pairs
1. **CBD-VDAC1** (Primary channel target)
2. **CBD-CB2** (Primary GPCR target)
3. **CBD-GPR55** (Secondary GPCR target)
4. **CBD-TRPV1** (Tertiary GPCR target)
5. **Control pairs** (non-specific interactions)

#### Temporal Analysis Points
- **5 minutes:** Initial binding events
- **15 minutes:** Early interaction establishment
- **30 minutes:** Peak interaction period
- **60 minutes:** Sustained interaction phase
- **120 minutes:** Late-phase interactions

### Cell Models

#### Cancer Cells: U87-MG Glioblastoma
- **Rationale:** High VDAC1 expression, metabolic stress
- **Expected pattern:** Strong CBD-VDAC1 signal, rapid onset

#### Healthy Cells: Primary Human Astrocytes
- **Rationale:** Normal mitochondrial function, CBD resistance
- **Expected pattern:** Weaker CBD-VDAC1 signal, delayed onset

### Subcellular Localization Analysis

#### Mitochondrial Compartments
- **Outer membrane:** VDAC1 primary location
- **Inner membrane:** CB2, potential mitochondrial GPCRs
- **Matrix:** Control region for specificity

#### Cytoplasmic Compartments
- **Plasma membrane:** CB2, GPR55, TRPV1 primary locations
- **Endoplasmic reticulum:** Secondary target sites
- **Cytosol:** Non-specific binding control

---

## Experimental Protocol

### Day -2: Cell Preparation
1. **Seed cells on coverslips**
   - 18mm round coverslips in 12-well plates
   - **Cancer cells:** 20,000 cells/well
   - **Healthy cells:** 15,000 cells/well
2. **Coat coverslips:** Poly-L-lysine (0.1 mg/mL, 30 min)
3. **Incubate:** 48h at 37°C, 5% CO₂ for full adherence

### Day 0: CBD Treatment and Fixation

#### Treatment Application
1. **CBD preparation:** 10 μM in serum-free media
2. **Control preparation:** Vehicle (DMSO 0.1%)
3. **Remove media,** wash 2× with warm PBS
4. **Apply treatments** (1 mL/well)

#### Time-Course Fixation
- **5 min:** Fix first timepoint set
- **15 min:** Fix second timepoint set
- **30 min:** Fix third timepoint set
- **60 min:** Fix fourth timepoint set
- **120 min:** Fix final timepoint set

#### Fixation Protocol
1. **Remove treatment media**
2. **Wash:** 2× with PBS
3. **Fix:** 4% paraformaldehyde, 15 min, room temperature
4. **Wash:** 3× with PBS
5. **Store:** 4°C in PBS until PLA processing

### Day 1: PLA Processing

#### Primary Antibody Incubation
1. **Permeabilization:** 0.1% Triton X-100, 10 min
2. **Blocking:** 5% normal goat serum, 1h, room temperature
3. **Primary antibodies:**
   - Anti-CBD: 1:500 (rabbit, custom antibody)
   - Anti-VDAC1: 1:1000 (mouse, Abcam)
   - Anti-CB2: 1:500 (goat, Santa Cruz)
   - Anti-GPR55: 1:300 (sheep, custom)
   - Anti-TRPV1: 1:500 (guinea pig, Millipore)
4. **Incubation:** 4°C overnight

### Day 2: PLA Completion and Imaging

#### PLA Procedure (Duolink Kit)
1. **Wash:** 3× with PBS-T (0.1% Tween-20)
2. **Secondary PLA probes:** 1h, 37°C
   - Anti-rabbit PLUS
   - Anti-mouse MINUS (for CBD-VDAC1)
   - Anti-goat MINUS (for CBD-CB2)
   - etc.
3. **Ligation:** 30 min, 37°C
4. **Amplification:** 100 min, 37°C
5. **Final wash:** 2× SSC, then 0.2× SSC

#### Mitochondrial Staining
1. **MitoTracker Green:** 200 nM, 30 min, 37°C
2. **DAPI nuclear stain:** 1 μg/mL, 5 min
3. **Mount:** Fluoromount-G anti-fade medium

#### Confocal Imaging
1. **Objectives:** 63× oil immersion, NA 1.4
2. **Channels:**
   - DAPI (nuclei): 405 nm excitation
   - FITC (mitochondria): 488 nm excitation
   - Texas Red (PLA signals): 594 nm excitation
3. **Z-stacks:** 0.2 μm steps, full cell thickness
4. **Fields:** Minimum 20 fields per condition

---

## Image Analysis Pipeline

### PLA Signal Quantification

#### Signal Detection
1. **3D image reconstruction** from z-stacks
2. **PLA dot identification:** Size filtering (0.2-2.0 μm diameter)
3. **Intensity thresholding:** 3× background standard deviation
4. **Colocalization analysis:** PLA dots vs mitochondrial mask

#### Spatial Analysis
1. **Mitochondrial mask generation** from MitoTracker signal
2. **Colocalization coefficient:** PLA dots within mitochondrial regions
3. **Distance mapping:** PLA dots to nearest mitochondria
4. **Subcellular distribution:** Quantitative localization

#### Temporal Analysis
1. **Signal intensity curves:** PLA signal vs time for each target
2. **Peak timing identification:** Maximum signal timepoint
3. **Onset kinetics:** Time to 50% maximum signal
4. **Duration analysis:** Signal persistence over 120 min

### Statistical Analysis

#### Primary Endpoints
1. **Peak timing comparison:** CBD-VDAC1 vs CBD-GPCR timing
2. **Mitochondrial colocalization:** % PLA signals in mitochondria
3. **Signal intensity:** Maximum PLA dots per cell

#### Statistical Tests
1. **Temporal differences:** One-way ANOVA with post-hoc
2. **Colocalization:** Mann-Whitney U test
3. **Intensity comparisons:** Two-way ANOVA (treatment × time)

---

## Expected Results

### Channel-First Mechanism Pattern

#### Temporal Sequence
1. **5-15 min:** CBD-VDAC1 PLA signals appear
2. **15-30 min:** CBD-VDAC1 signals peak
3. **30-60 min:** CBD-GPCR signals begin appearing
4. **60-120 min:** CBD-GPCR signals reach peak

#### Spatial Distribution
- **CBD-VDAC1:** >80% mitochondrial colocalization
- **CBD-CB2:** Mixed mitochondrial/plasma membrane
- **CBD-GPR55/TRPV1:** <30% mitochondrial colocalization

#### Cell Type Differences
- **Cancer cells:** Strong, rapid CBD-VDAC1 signals
- **Healthy cells:** Weaker, delayed CBD-VDAC1 signals

### Receptor-First Mechanism Pattern

#### Alternative Temporal Sequence
1. **5-15 min:** CBD-GPCR PLA signals appear first
2. **15-30 min:** CBD-GPCR signals peak
3. **30-60 min:** CBD-VDAC1 signals begin
4. **60-120 min:** CBD-VDAC1 signals reach peak

#### Alternative Spatial Distribution
- **CBD-GPCR:** Strong plasma membrane signals
- **CBD-VDAC1:** Secondary, weaker mitochondrial signals
- **Sequential signaling:** GPCR → mitochondrial recruitment

---

## Success Criteria

### Primary Success Gate
**CBD-VDAC1 interaction precedes CBD-GPCR interactions by ≥15 minutes**
- Quantified as peak timing difference between interaction pairs
- Minimum effect size: 15 minute difference

### Secondary Success Gates
1. **Mitochondrial priority:** CBD-VDAC1 >80% mitochondrial colocalization
2. **Signal strength:** CBD-VDAC1 signal intensity > CBD-GPCR signals
3. **Cell type specificity:** Cancer > healthy cells for CBD-VDAC1 timing

### Quality Control Gates
1. **Signal specificity:** Control PLA signals <10% of specific signals
2. **Reproducibility:** CV <25% between biological replicates
3. **Image quality:** >90% cells successfully analyzed

---

## Advanced Analysis Options

### Single-Cell Resolution
- **Individual cell tracking:** Temporal dynamics per cell
- **Population heterogeneity:** Distribution of interaction timing
- **Correlation analysis:** Mitochondrial content vs PLA signal strength

### Super-Resolution Validation
- **STORM/PALM imaging:** Nanoscale localization of interactions
- **Dual-color super-resolution:** Simultaneous VDAC1 and CBD detection
- **Mitochondrial ultrastructure:** Correlation with interaction sites

### Live-Cell PLA (Future)
- **Real-time interaction monitoring:** Dynamic PLA with live imaging
- **Photoactivatable CBD:** Controlled interaction timing
- **FRET-based validation:** Complementary interaction detection

---

## Resource Requirements

### Reagents
- **Primary antibodies:** Custom CBD antibody ($800), commercial antibodies ($600)
- **PLA kit:** Duolink kit with multiple probe combinations ($1,200)
- **Imaging reagents:** MitoTracker, DAPI, mounting medium ($300)

### Equipment Time
- **Confocal microscope:** 40 hours (5 timepoints × 2 cell types × 4 targets)
- **Image analysis workstation:** 20 hours processing time

### Personnel
- **Specialized training:** PLA technique, confocal imaging
- **Analysis expertise:** Image quantification, statistical analysis

### Estimated Cost
**Total: $3,500**
- Reagents: $2,900
- Equipment time: $600

---

## Integration with Validation Suite

### Connection to Protocol 01
- **Mechanism confirmation:** Temporal data supports GPCR vs channel priority
- **Selectivity correlation:** PLA timing differences vs selectivity index

### Input to Protocol 03
- **Causality framework:** Temporal sequence for causality testing
- **Target prioritization:** Strongest interactions for inhibition studies

### S4 Framework Integration
- **Temporal mapping:** PLA kinetics vs S4 rhythm patterns
- **Spatial organization:** Mitochondrial ensembles vs S4 organizing center
- **Interaction hierarchy:** Primary vs secondary targets vs S4 aperture control

---

**Protocol Status:** Ready for execution
**Integration:** Validation Suite 2/4
**Next Protocol:** 03_vdac1_causality.md

---

*Generated: 2025-10-07*
*Version: 1.0*
*🧬⚡🔬∞*