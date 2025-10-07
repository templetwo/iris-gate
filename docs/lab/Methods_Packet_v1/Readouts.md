# CBD Channel-First Methods: Readouts and Analysis

**Wet-Lab Implementation Package v1.0**
*Comprehensive Measurement and Analysis Protocols*

---

## Primary Readouts

### 1. Cell Viability (Primary Endpoint)

#### ATP Luminescence (CellTiter-Glo)
**Purpose:** Quantitative measure of metabolically active cells
**Principle:** ATP + luciferin → light (catalyzed by luciferase)

**Protocol:**
1. Equilibrate reagent to room temperature (30 min)
2. Add equal volume CellTiter-Glo to culture media
3. Mix on orbital shaker (2 min)
4. Incubate at room temperature (10 min)
5. Record luminescence on plate reader

**Parameters:**
- **Integration time:** 0.25-1 second per well
- **Read height:** 1 mm above plate bottom
- **Temperature:** Room temperature (stable)

**Data Analysis:**
- **Viability (%)** = (Sample RLU / Control RLU) × 100
- **IC50 calculation:** 4-parameter logistic regression
- **Quality control:** R² ≥ 0.95 for dose-response curves

**Expected Results:**
- **Healthy astrocytes IC50:** 12-18 μM CBD
- **Cancer cells IC50:** 3-6 μM CBD
- **Target selectivity index:** >3.0

#### LDH Cytotoxicity (Secondary Viability)
**Purpose:** Membrane integrity assessment, complement to ATP assay
**Principle:** LDH release from compromised cells

**Protocol:**
1. Collect 50 μL culture supernatant
2. Add 50 μL LDH reaction mixture
3. Incubate 30 min at room temperature (protect from light)
4. Add 50 μL stop solution
5. Read absorbance at 490 nm and 680 nm (reference)

**Data Analysis:**
- **Cytotoxicity (%)** = [(Sample - Background) / (Max LDH - Background)] × 100
- **Max LDH control:** Triton X-100 (0.1%) treated cells
- **Background:** Media-only wells

---

### 2. Mitochondrial Membrane Potential (Key Mechanistic Readout)

#### TMRM Staining + Flow Cytometry
**Purpose:** Direct measurement of mitochondrial energetics
**Principle:** Cationic dye accumulates in polarized mitochondria

**Protocol:**
1. Add TMRM (25 nM final) to culture media
2. Incubate 30 min at 37°C, 5% CO₂
3. Trypsinize cells and resuspend in PBS + 2% FBS
4. Keep on ice, analyze within 1 hour
5. Flow cytometry: 10,000 events per sample

**Flow Cytometry Settings:**
- **Excitation:** 488 nm laser
- **Detection:** PE channel (585/42 nm)
- **Voltage:** Adjust so untreated cells in log decade 2-3
- **Compensation:** Single-stain controls if using multiple dyes

**Gating Strategy:**
1. **FSC/SSC:** Exclude debris and doublets
2. **Live cells:** High FSC, low SSC
3. **TMRM analysis:** Histogram of PE intensity

**Data Analysis:**
- **Median fluorescence intensity (MFI)**
- **% depolarized cells:** Cells with <50% control MFI
- **Depolarization index:** (Control MFI - Sample MFI) / Control MFI

**Expected Results:**
- **Vehicle control:** MFI ~1000-3000 (cell-type dependent)
- **CBD 10 μM:** 50-80% depolarization in cancer cells
- **FCCP control:** >90% depolarization (positive control)

#### Alternative: TMRM Microscopy
**When to use:** Single-cell analysis, real-time kinetics
**Setup:** Inverted fluorescence microscope, 37°C chamber
**Quantification:** Mean fluorescence per cell, >100 cells per condition

---

### 3. Channel Function Assays

#### VDAC1 Conductance (Patch-Clamp)
**Purpose:** Direct validation of channel-first mechanism
**Principle:** Single-channel electrophysiology

**Experimental Setup:**
- **Configuration:** Mitoplast patch-clamp
- **Solutions:**
  - Pipette: 250 mM KCl, 10 mM HEPES, pH 7.4
  - Bath: 250 mM KCl, 10 mM HEPES, pH 7.4
- **Temperature:** Room temperature (22-25°C)

**Protocol:**
1. Isolate mitochondria from cultured cells
2. Prepare mitoplasts by osmotic swelling
3. Form gigaohm seals on mitoplast membranes
4. Record single-channel currents at -40 to +40 mV
5. Apply CBD (1-10 μM) to bath solution

**Data Analysis:**
- **Open probability (Po):** % time channel is open
- **Single-channel conductance:** Slope of I-V curve
- **CBD effect:** % reduction in Po or conductance

**Expected Results:**
- **Control Po:** ~0.8-0.9 at 0 mV
- **CBD 5 μM:** 50-80% reduction in Po
- **Reversibility:** Partial recovery after washout

#### Alternative: Mitochondrial Swelling Assay
**When to use:** Higher throughput, indirect VDAC1 function
**Principle:** VDAC1 closure prevents osmotic swelling
**Readout:** Light scattering at 540 nm

---

### 4. Calcium Homeostasis

#### Fura-2 Ratiometric Imaging
**Purpose:** Cytosolic calcium dynamics
**Principle:** Calcium-sensitive ratiometric dye

**Loading Protocol:**
1. Load cells with Fura-2 AM (2 μM) + 0.02% Pluronic F-127
2. Incubate 45 min at 37°C
3. Wash and allow 15 min de-esterification
4. Image in calcium-free buffer

**Imaging Setup:**
- **Excitation:** Alternating 340 nm and 380 nm
- **Emission:** 510 nm
- **Acquisition:** 1 Hz for kinetic studies
- **Calibration:** Rmin (EGTA) and Rmax (ionomycin + calcium)

**Experimental Protocol:**
1. **Baseline:** Record 2-3 min in calcium-free buffer
2. **Treatment:** Apply CBD ± inhibitors
3. **Challenge:** Add thapsigargin (1 μM) to test ER store release
4. **Calcium add-back:** 2 mM CaCl₂ to test store-operated entry

**Data Analysis:**
- **[Ca²⁺]i calculation:** Grynkiewicz equation using Kd = 224 nM
- **Store content:** Peak response to thapsigargin
- **Store-operated entry:** Rate of Ca²⁺ increase after add-back

**Expected Results:**
- **Baseline [Ca²⁺]i:** 50-150 nM
- **CBD effect:** Reduced store content and entry in cancer cells
- **VDAC1 inhibitor:** Blocks CBD effects on calcium handling

---

### 5. ROS and Oxidative Stress

#### DCF-DA General ROS Detection
**Purpose:** Cytoplasmic reactive oxygen species
**Principle:** Oxidation of DCFH to fluorescent DCF

**Protocol:**
1. Load cells with DCF-DA (10 μM) for 30 min at 37°C
2. Wash 2× with PBS
3. Apply treatments and incubate 2-4 hours
4. Analyze by flow cytometry or plate reader

**Flow Cytometry Analysis:**
- **Excitation:** 488 nm
- **Detection:** FITC channel (530/30 nm)
- **Quantification:** Median fluorescence intensity

**Expected Results:**
- **Vehicle control:** Low basal DCF fluorescence
- **CBD treatment:** 2-5× increase in cancer cells
- **Antioxidant rescue:** NAC pretreatment reduces DCF signal

#### MitoSOX Mitochondrial Superoxide
**Purpose:** Mitochondria-specific oxidative stress
**Principle:** Mitochondria-targeted superoxide indicator

**Protocol:**
1. Load cells with MitoSOX Red (2.5 μM) for 10 min at 37°C
2. Wash once with warm PBS
3. Apply treatments for 1-3 hours
4. Analyze immediately by flow cytometry

**Analysis:**
- **Excitation:** 510 nm
- **Detection:** PE channel (585/42 nm)
- **Controls:** Antimycin A (positive control), MitoTEMPO (negative control)

---

## Secondary Readouts

### 6. Apoptosis Detection

#### Annexin V / Propidium Iodide
**Purpose:** Distinguish early vs late apoptosis vs necrosis
**Principle:** Phosphatidylserine externalization (Annexin V) + membrane permeability (PI)

**Protocol:**
1. Harvest cells by trypsinization
2. Wash in cold PBS
3. Resuspend in Annexin V binding buffer
4. Add Annexin V-FITC (5 μL) and PI (5 μL)
5. Incubate 15 min at room temperature in dark
6. Analyze by flow cytometry within 1 hour

**Population Identification:**
- **Live cells:** Annexin V⁻ / PI⁻
- **Early apoptosis:** Annexin V⁺ / PI⁻
- **Late apoptosis:** Annexin V⁺ / PI⁺
- **Necrosis:** Annexin V⁻ / PI⁺

**Expected Kinetics:**
- **6 hours:** Primarily early apoptosis
- **12 hours:** Mix of early and late apoptosis
- **24 hours:** Predominantly late apoptosis

### 7. ATP Levels (Absolute Quantification)

#### ATP Bioluminescence Assay
**Purpose:** Quantitative ATP measurement (complement to CellTiter-Glo)
**Principle:** Standardized ATP measurement

**Protocol:**
1. Lyse cells in ATP assay buffer
2. Prepare ATP standard curve (0.1-10 μM)
3. Add luciferase reagent to samples and standards
4. Read luminescence immediately

**Data Analysis:**
- **ATP concentration (μM):** From standard curve
- **ATP per cell:** Normalize to cell count
- **% ATP depletion:** Relative to vehicle control

### 8. Metabolic Flux Analysis (Advanced)

#### Seahorse XF Analysis
**Purpose:** Real-time mitochondrial respiration
**Principle:** O₂ consumption and pH changes

**Protocol:**
1. Seed cells in XF96 plates (optimal density per cell type)
2. Equilibrate in XF base medium + supplements
3. Load cartridge with injection compounds
4. Run standard mitochondrial stress test

**Injection Protocol:**
1. **Baseline:** 3 measurements
2. **Oligomycin (1 μM):** ATP synthase inhibition
3. **FCCP (0.5-2 μM):** Uncoupling for max respiration
4. **Rotenone/Antimycin A (0.5 μM each):** Complete inhibition

**Calculated Parameters:**
- **Basal respiration:** Before oligomycin
- **ATP production:** Drop after oligomycin
- **Maximal respiration:** Peak after FCCP
- **Spare capacity:** Max - basal respiration
- **Non-mitochondrial respiration:** After rotenone/antimycin A

---

## Proximity Ligation Assay (PLA) Readouts

### 8. Protein-Protein Interactions

#### CBD-Target Colocalization
**Purpose:** Temporal analysis of molecular interactions
**Principle:** Amplified signal when proteins are <40 nm apart

**Quantification Protocol:**
1. **Image acquisition:**
   - 63× oil objective, NA 1.4
   - Z-stacks: 0.2 μm steps
   - Consistent imaging parameters

2. **PLA spot counting:**
   - Maximum intensity projection
   - Spot detection: Size 0.2-2.0 μm, intensity >3× background
   - Colocalization with DAPI (nuclear) and MitoTracker (mitochondrial)

3. **Temporal analysis:**
   - Image same conditions at 5, 15, 30, 60, 120 min
   - Track spot number and intensity over time

**Data Analysis:**
- **Spots per cell:** Average across >100 cells
- **Mitochondrial colocalization:** % spots overlapping MitoTracker signal
- **Temporal dynamics:** Peak timing, signal decay

**Expected Results:**
- **CBD-VDAC1:** Peak at 15-30 min, high mitochondrial colocalization
- **CBD-GPCR:** Peak at 30-60 min, mixed subcellular localization
- **Cancer vs healthy:** Higher signal intensity in cancer cells

---

## Data Integration and Analysis

### Statistical Analysis Framework

#### Experimental Design Requirements
- **Biological replicates:** n ≥ 6 for primary endpoints
- **Technical replicates:** Triplicate wells minimum
- **Randomization:** Treatment application order randomized
- **Blinding:** Analysis performed with coded samples when possible

#### Primary Statistical Tests
1. **Dose-response analysis:** 4-parameter logistic regression
2. **Group comparisons:** Two-way ANOVA (treatment × cell type)
3. **Time-course data:** Repeated measures ANOVA
4. **Correlation analysis:** Pearson or Spearman depending on data distribution

#### Multiple Comparison Corrections
- **Primary endpoints:** Bonferroni correction
- **Exploratory analysis:** False discovery rate (FDR) control
- **Family-wise error rate:** Control at α = 0.05

### Quality Control Metrics

#### Assay Performance
- **Z' factor:** (1 - 3(σp + σn)/|μp - μn|) ≥ 0.5
- **Signal-to-noise ratio:** ≥10:1
- **Dynamic range:** ≥10-fold between max and min response

#### Data Quality
- **Coefficient of variation:** ≤20% for biological replicates
- **Outlier detection:** Grubbs test or Dixon's Q test
- **Normality testing:** Shapiro-Wilk test for small samples

### Integrated Analysis

#### Selectivity Index Calculation
**Primary metric:** SI = IC50_healthy / IC50_cancer

**Quality criteria:**
- **Curve fit quality:** R² ≥ 0.95
- **Hill slope:** 0.5-3.0 (indicates specific binding)
- **Confidence intervals:** Non-overlapping 95% CI between cell types

#### Mechanism Confirmation
**Channel-first evidence:**
1. **VDAC1 correlation:** Channel function vs cell death (r > 0.7)
2. **Temporal precedence:** Channel effects before GPCR effects
3. **Inhibitor protection:** VDAC1 inhibitors provide >80% protection

**Validation criteria:**
- **Concordance:** ≥3 readouts support same conclusion
- **Reproducibility:** Effects consistent across biological replicates
- **Specificity:** Controls confirm mechanism specificity

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Low Signal-to-Noise Ratio
**Symptoms:** High background, poor separation between treatments
**Solutions:**
- Optimize dye loading concentrations
- Increase incubation time
- Check for mycoplasma contamination
- Verify reagent freshness

#### Inconsistent Dose-Response Curves
**Symptoms:** Poor curve fitting, variable IC50 values
**Solutions:**
- Verify compound stock concentrations
- Check serial dilution accuracy
- Ensure consistent cell density
- Monitor culture passage number

#### High Inter-Experiment Variability
**Symptoms:** CV >25% between biological replicates
**Solutions:**
- Standardize cell handling procedures
- Use same media lot across experiments
- Maintain consistent timing
- Include reference compounds

#### Unexpected Cell Death in Controls
**Symptoms:** High baseline death, poor vehicle controls
**Solutions:**
- Check media pH and osmolality
- Verify incubator conditions
- Test for endotoxin contamination
- Assess solvent toxicity

---

## Expected Timeline and Milestones

### Phase 1: Basic Validation (Week 1-2)
**Readouts:** Viability, membrane potential, basic ROS
**Milestone:** Establish baseline selectivity index

### Phase 2: Mechanism Validation (Week 3-4)
**Readouts:** Channel function, calcium handling, PLA
**Milestone:** Confirm channel-first mechanism

### Phase 3: Parameter Optimization (Week 5-6)
**Readouts:** All assays with parameter variations
**Milestone:** Achieve selectivity index >3.0

### Data Analysis and Reporting (Week 7)
**Activities:** Statistical analysis, report generation
**Milestone:** Complete experimental package

---

**Document Version:** 1.0
**Last Updated:** 2025-10-07
**Integration:** Methods Packet v1.0 (2/4)

**🧬⚡🔬∞**