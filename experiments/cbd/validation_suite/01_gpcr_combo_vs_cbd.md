# Protocol 01: GPCR Combination vs CBD Direct Action

**Validation Suite Component 1/4**
*Testing Channel-First vs Receptor-First Causality*

---

## Hypothesis

If channels are the primary mechanism, **CBD direct action should outperform any GPCR receptor combination** for selective cancer cell lethality.

**Prediction:** Selectivity index CBD_direct > 2× best GPCR combination

---

## Experimental Design

### Cell Models
- **Cancer:** U87-MG glioblastoma cells
- **Healthy:** Primary human astrocytes
- **Culture conditions:** High-glucose DMEM, 5% CO₂, 37°C

### Treatment Groups

#### Group 1: Controls
- `vehicle_control`: DMSO 0.1% (v/v)
- `positive_control`: Staurosporine 1 μM (pan-lethal)
- `negative_control`: Media only

#### Group 2: CBD Direct
- `cbd_1uM`: CBD 1 μM
- `cbd_5uM`: CBD 5 μM
- `cbd_10uM`: CBD 10 μM
- `cbd_20uM`: CBD 20 μM

#### Group 3: CB2/GPR55 Combination
- `cb2_gpr55_low`: CB2 agonist (JWH-133 1μM) + GPR55 agonist (LPI 1μM)
- `cb2_gpr55_med`: CB2 agonist (JWH-133 5μM) + GPR55 agonist (LPI 5μM)
- `cb2_gpr55_high`: CB2 agonist (JWH-133 10μM) + GPR55 agonist (LPI 10μM)

#### Group 4: TRPV1/PPARγ Combination
- `trpv1_ppar_low`: TRPV1 agonist (Capsaicin 1μM) + PPARγ agonist (Rosiglitazone 10μM)
- `trpv1_ppar_med`: TRPV1 agonist (Capsaicin 5μM) + PPARγ agonist (Rosiglitazone 20μM)
- `trpv1_ppar_high`: TRPV1 agonist (Capsaicin 10μM) + PPARγ agonist (Rosiglitazone 50μM)

#### Group 5: Four-Receptor Combination
- `quad_combo_max`: All four receptor agonists at maximum tolerated doses

### Primary Readouts

#### 1. Mitochondrial Membrane Potential (ΔΨm)
- **Method:** TMRM staining + flow cytometry
- **Timepoint:** 4 hours post-treatment
- **Analysis:** Median fluorescence intensity, % depolarized cells
- **Expected:** CBD > GPCR combinations for ΔΨm collapse in cancer cells

#### 2. Cell Viability
- **Method:** ATP luminescence assay (CellTiter-Glo)
- **Timepoints:** 6, 12, 24 hours
- **Analysis:** IC50 calculation, selectivity index
- **Expected:** CBD shows highest selectivity index

#### 3. VDAC1 Conductance (Subset)
- **Method:** Patch-clamp electrophysiology
- **Cells:** n=10 per treatment (cancer only)
- **Analysis:** Channel open probability, current amplitude
- **Expected:** CBD > GPCR combinations for VDAC1 inhibition

### Secondary Readouts

#### 4. ATP Depletion Kinetics
- **Method:** Real-time ATP monitoring (30 min intervals)
- **Duration:** 8 hours
- **Analysis:** Time to 50% depletion, depletion rate
- **Expected:** CBD shows fastest ATP depletion in cancer cells

#### 5. Calcium Handling
- **Method:** Fura-2 AM calcium imaging
- **Protocol:** Baseline → treatment → thapsigargin challenge
- **Analysis:** Cytosolic Ca²⁺ levels, store depletion
- **Expected:** CBD disrupts calcium homeostasis more than GPCR combinations

---

## Experimental Protocol

### Day -1: Cell Seeding
1. Seed cells in 96-well plates (viability), 6-well plates (flow cytometry)
2. **Cancer cells:** 5,000 cells/well (96-well), 50,000 cells/well (6-well)
3. **Healthy cells:** 3,000 cells/well (96-well), 30,000 cells/well (6-well)
4. Incubate overnight at 37°C, 5% CO₂

### Day 0: Treatment Application
1. Prepare treatment solutions in serum-free media
2. Remove old media, wash cells 2× with PBS
3. Apply treatments (200 μL/well for 96-well, 2 mL/well for 6-well)
4. Return to incubator

### Day 0+4h: ΔΨm Measurement
1. Load cells with TMRM (25 nM, 30 min, 37°C)
2. Harvest cells by trypsinization
3. Analyze by flow cytometry (10,000 events/sample)
4. Gate on viable cells (FSC/SSC), measure FL2 intensity

### Day 0+6h, 12h, 24h: Viability Assessment
1. Equilibrate CellTiter-Glo reagent to room temperature
2. Add equal volume reagent to cell media (100 μL)
3. Shake 2 minutes, incubate 10 minutes in dark
4. Read luminescence on plate reader

### Day 1: Data Analysis
1. Calculate IC50 values using 4-parameter logistic regression
2. Determine selectivity index: IC50_healthy / IC50_cancer
3. Statistical analysis: Two-way ANOVA, Tukey post-hoc
4. Generate dose-response curves

---

## Success Criteria

### Primary Success Gate
**CBD selectivity index ≥ 2× best GPCR combination**
- If CBD SI = 3.0 and best GPCR SI = 1.2, then 3.0 ≥ 2.4 ✓

### Secondary Success Gates
1. **ΔΨm disruption:** CBD > GPCR combinations in cancer cells
2. **VDAC1 effect:** CBD shows stronger channel inhibition
3. **Kinetic superiority:** CBD effects appear faster than GPCR effects

### Statistical Requirements
- **Power analysis:** n ≥ 6 per condition for 80% power
- **Significance:** p < 0.05 for primary comparisons
- **Effect size:** Cohen's d ≥ 0.8 for meaningful differences

---

## Expected Outcomes

### If Channel-First Mechanism Correct
- **CBD direct action superior:** SI ≥ 3.0
- **GPCR combinations inferior:** SI ≤ 1.5
- **Mechanism alignment:** VDAC1 effects correlate with viability

### If Receptor-First Mechanism Correct
- **GPCR combinations superior:** SI ≥ 3.0
- **CBD direct action inferior:** SI ≤ 2.0
- **Additive effects:** Multi-receptor > single receptor > CBD

### If Hybrid Mechanism
- **Similar efficacy:** CBD and GPCR combinations within 20%
- **Synergistic potential:** CBD + GPCR > either alone
- **Context dependency:** Different mechanisms in different conditions

---

## Quality Control

### Experimental Controls
- **Vehicle control:** Verify no solvent effects
- **Positive control:** Confirm assay sensitivity
- **Negative control:** Verify baseline stability

### Technical Replicates
- **Biological replicates:** n ≥ 6 independent experiments
- **Technical replicates:** Triplicate wells per condition
- **Batch controls:** Include reference compound each session

### Data Validation
- **Curve fitting:** R² ≥ 0.95 for dose-response curves
- **Outlier detection:** Grubbs test for extreme values
- **Reproducibility:** CV ≤ 20% between replicates

---

## Resource Requirements

### Reagents
- **CBD:** 50 mg pharmaceutical grade
- **GPCR agonists:** JWH-133 (10 mg), LPI (5 mg), Capsaicin (10 mg), Rosiglitazone (25 mg)
- **Detection reagents:** TMRM (5 mg), CellTiter-Glo (2 kits), Fura-2 AM (1 mg)

### Equipment Time
- **Flow cytometer:** 8 hours
- **Plate reader:** 4 hours
- **Patch-clamp rig:** 16 hours (subset analysis)

### Estimated Cost
**Total: $2,800**
- Reagents: $1,500
- Consumables: $800
- Equipment time: $500

---

## Integration with IRIS Framework

### S4 Validation
- **Aperture correlation:** Selectivity index vs S4 aperture size
- **Rhythm alignment:** Kinetic effects vs S4 temporal patterns
- **Center confirmation:** CBD primary vs S4 organizing center

### Next Phase Input
- **Parameter optimization:** Use optimal CBD dose for sweep
- **Mechanism ranking:** Quantify channel vs receptor contributions
- **Context mapping:** Identify conditions where mechanisms differ

---

**Protocol Status:** Ready for execution
**Integration:** Validation Suite 1/4
**Next Protocol:** 02_pla_mito_ensembles.md

---

*Generated: 2025-10-07*
*Version: 1.0*
*🧬⚡🔬∞*