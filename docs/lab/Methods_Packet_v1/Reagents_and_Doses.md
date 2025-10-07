# CBD Channel-First Methods: Reagents and Doses

**Wet-Lab Implementation Package v1.0**
*Optimized for Channel-First Mechanism Validation*

---

## Primary Test Compounds

### CBD (Cannabidiol) - Primary Agent
- **Source:** Pharmaceutical grade (≥99% purity)
- **Stock preparation:** 10 mM in DMSO
- **Storage:** -20°C, protected from light, aliquot to avoid freeze-thaw
- **Working concentrations:** 0.1, 0.5, 1, 2.5, 5, 10, 20 μM
- **Final DMSO concentration:** ≤0.2% (validated non-toxic)

**Dose Rationale:**
- Range covers IC50 values from preliminary studies (2-15 μM)
- Log spacing for accurate curve fitting
- Upper limit ensures saturation without solvent toxicity

### Vehicle Controls
- **DMSO:** 0.1-0.2% final concentration
- **Media control:** Standard culture media only
- **Sham treatment:** All handling steps without active compound

---

## Channel-Specific Inhibitors

### VDAC1 Channel Inhibitors

#### DIDS (Primary VDAC1 Inhibitor)
- **Source:** Sigma-Aldrich (D3514)
- **Stock preparation:** 10 mM in DMSO
- **Working concentrations:** 10, 25, 50 μM
- **Application:** 1-hour pre-treatment before CBD
- **Mechanism:** Anion channel blocker, VDAC1-selective at these concentrations

#### Erastin (Alternative VDAC1 Inhibitor)
- **Source:** Selleck Chemicals (S7242)
- **Stock preparation:** 10 mM in DMSO
- **Working concentrations:** 0.5, 1, 2 μM
- **Application:** 1-hour pre-treatment before CBD
- **Mechanism:** VDAC1-dependent ferroptosis inducer, used at sub-lethal doses

### MCU (Mitochondrial Calcium Uniporter) Inhibitors

#### Ruthenium Red
- **Source:** Sigma-Aldrich (R2751)
- **Stock preparation:** 1 mM in water (prepare fresh)
- **Working concentrations:** 1, 5, 10 μM
- **Application:** 30-minute pre-treatment
- **Mechanism:** MCU channel blocker

#### Mitoxantrone (Alternative MCU Inhibitor)
- **Source:** Sigma-Aldrich (M6545)
- **Stock preparation:** 1 mM in DMSO
- **Working concentrations:** 0.1, 0.5, 1 μM
- **Application:** 1-hour pre-treatment
- **Mechanism:** Selective MCU inhibitor

### Chloride Channel Inhibitors

#### NPPB (5-Nitro-2-(3-phenylpropylamino)benzoic acid)
- **Source:** Sigma-Aldrich (N4779)
- **Stock preparation:** 50 mM in DMSO
- **Working concentrations:** 10, 50, 100 μM
- **Application:** 30-minute pre-treatment
- **Mechanism:** Volume-regulated chloride channel inhibitor

#### DCPIB (Alternative Chloride Channel Inhibitor)
- **Source:** Tocris (2589)
- **Stock preparation:** 10 mM in DMSO
- **Working concentrations:** 1, 5, 10 μM
- **Application:** 30-minute pre-treatment
- **Mechanism:** Volume-sensitive outwardly rectifying chloride channel inhibitor

---

## GPCR Modulators (Control Comparisons)

### CB2 Receptor Modulators

#### AM630 (CB2 Antagonist)
- **Source:** Tocris (1120)
- **Stock preparation:** 10 mM in DMSO
- **Working concentrations:** 1, 5 μM
- **Application:** 1-hour pre-treatment

#### JWH-133 (CB2 Agonist - for combination studies)
- **Source:** Tocris (1343)
- **Stock preparation:** 10 mM in DMSO
- **Working concentrations:** 1, 5, 10 μM
- **Application:** Simultaneous with CB2 antagonist studies

### GPR55 Receptor Modulators

#### CID16020046 (GPR55 Antagonist)
- **Source:** Tocris (4396)
- **Stock preparation:** 10 mM in DMSO
- **Working concentrations:** 1, 5 μM
- **Application:** 1-hour pre-treatment

#### LPI (Lysophosphatidylinositol, GPR55 Agonist)
- **Source:** Cayman Chemical (62215)
- **Stock preparation:** 1 mM in ethanol:PBS (1:1)
- **Working concentrations:** 1, 5, 10 μM
- **Application:** For combination studies

### TRPV1 Modulators

#### Capsazepine (TRPV1 Antagonist)
- **Source:** Tocris (0454)
- **Stock preparation:** 10 mM in DMSO
- **Working concentrations:** 1, 10 μM
- **Application:** 1-hour pre-treatment

---

## Detection and Analysis Reagents

### Cell Viability Assays

#### CellTiter-Glo Luminescent Assay
- **Source:** Promega (G7570)
- **Application:** Primary viability endpoint
- **Protocol:** 1:1 volume addition, 10-minute incubation
- **Readout:** Luminescence (relative ATP levels)

#### LDH Cytotoxicity Assay
- **Source:** Thermo Fisher (88953)
- **Application:** Membrane integrity assessment
- **Protocol:** 30-minute reaction at room temperature
- **Readout:** Absorbance 490 nm

### Mitochondrial Function Assays

#### TMRM (Tetramethylrhodamine Methyl Ester)
- **Source:** Thermo Fisher (T668)
- **Stock preparation:** 1 mM in DMSO
- **Working concentration:** 25 nM
- **Application:** Mitochondrial membrane potential
- **Protocol:** 30-minute loading at 37°C
- **Readout:** Flow cytometry or fluorescence microscopy

#### MitoSOX Red
- **Source:** Thermo Fisher (M36008)
- **Stock preparation:** 5 mM in DMSO
- **Working concentration:** 2.5 μM
- **Application:** Mitochondrial superoxide detection
- **Protocol:** 10-minute loading at 37°C
- **Readout:** Flow cytometry (585/650 nm)

#### DCF-DA (General ROS Detection)
- **Source:** Sigma-Aldrich (D6883)
- **Stock preparation:** 10 mM in DMSO
- **Working concentration:** 10 μM
- **Application:** Cytoplasmic ROS levels
- **Protocol:** 30-minute loading at 37°C
- **Readout:** Flow cytometry (488/535 nm)

### Calcium Imaging

#### Fura-2 AM
- **Source:** Thermo Fisher (F1221)
- **Stock preparation:** 1 mM in DMSO + 20% Pluronic F-127
- **Working concentration:** 2 μM
- **Application:** Cytosolic calcium measurement
- **Protocol:** 45-minute loading at 37°C, 15-minute de-esterification
- **Readout:** Ratiometric imaging (340/380 nm excitation, 510 nm emission)

### Apoptosis Detection

#### Annexin V-FITC / Propidium Iodide Kit
- **Source:** BD Biosciences (556547)
- **Application:** Early and late apoptosis detection
- **Protocol:** 15-minute staining at room temperature
- **Readout:** Flow cytometry (FITC: 488/530 nm, PI: 488/610 nm)

---

## Proximity Ligation Assay (PLA) Reagents

### Primary Antibodies

#### CBD Detection
- **Anti-CBD antibody:** Custom polyclonal (rabbit)
- **Source:** Generated against CBD-BSA conjugate
- **Dilution:** 1:500
- **Validation:** Western blot confirmed specificity

#### Channel Targets
- **Anti-VDAC1:** Abcam ab14734 (mouse monoclonal)
- **Dilution:** 1:1000
- **Anti-MCU:** Sigma-Aldrich HPA016480 (rabbit polyclonal)
- **Dilution:** 1:500

#### GPCR Targets
- **Anti-CB2:** Santa Cruz sc-25494 (goat polyclonal)
- **Dilution:** 1:500
- **Anti-GPR55:** Custom antibody (sheep polyclonal)
- **Dilution:** 1:300

### PLA Detection Kit
- **Source:** Sigma-Aldrich (DUO92101)
- **Components:** PLA probes, ligation solution, amplification reagents
- **Protocol:** Standard Duolink protocol with modifications for mitochondrial targets

---

## Stress Induction Reagents

### Oxidative Stress
- **Hydrogen peroxide (H₂O₂):** 30% solution, dilute to 25-100 μM
- **Application:** 1-hour treatment to induce mild-moderate oxidative stress

### Mitochondrial Stress
- **Rotenone:** Complex I inhibitor, 50-200 nM, 2-hour treatment
- **FCCP:** Uncoupling agent, 0.5-2 μM, 30-minute treatment followed by recovery

### Antioxidant Rescue
- **N-acetylcysteine (NAC):** 5 mM, 2-hour pre-treatment
- **Application:** Mitochondrial stress rescue experiments

---

## Cell Culture Requirements

### Cell Lines

#### Cancer Model: U87-MG Glioblastoma
- **Source:** ATCC HTB-14
- **Media:** High-glucose DMEM + 10% FBS + 1% Pen/Strep
- **Passage:** Use passages 5-20 for consistency
- **Seeding density:** 5,000 cells/well (96-well), 50,000 cells/well (6-well)

#### Healthy Control: Primary Human Astrocytes
- **Source:** ScienCell Research (1800)
- **Media:** Astrocyte Medium (ScienCell 1801) + supplements
- **Passage:** Use passages 3-8 maximum
- **Seeding density:** 3,000 cells/well (96-well), 30,000 cells/well (6-well)

#### Alternative Healthy Control: SVG-p12 Astrocytes
- **Source:** ATCC CRL-8621
- **Media:** High-glucose DMEM + 10% FBS + 1% Pen/Strep
- **Usage:** Immortalized alternative when primary cells unavailable

### Culture Conditions
- **Temperature:** 37°C
- **CO₂:** 5%
- **Humidity:** >90%
- **Media changes:** Every 2-3 days, 24h before experiments

---

## Quality Control Standards

### Reagent Validation

#### Stock Solution Verification
- **Concentration confirmation:** UV-Vis spectroscopy for compounds with known extinction coefficients
- **Purity check:** HPLC analysis for critical compounds
- **Stability testing:** Store aliquots at multiple temperatures, test over time

#### Cell Line Authentication
- **STR profiling:** Confirm cell line identity quarterly
- **Mycoplasma testing:** PCR-based detection monthly
- **Growth curve validation:** Ensure consistent doubling times

### Experimental Controls

#### Positive Controls
- **Staurosporine (1 μM):** Pan-apoptotic positive control
- **Thapsigargin (1 μM):** ER stress positive control
- **FCCP (5 μM):** Mitochondrial uncoupling positive control

#### Negative Controls
- **Vehicle only:** Match highest solvent concentration
- **Media only:** Untreated cells
- **Heat-killed cells:** Non-viable control for cytotoxicity assays

### Acceptance Criteria

#### Assay Performance
- **Z' factor:** ≥0.5 for high-throughput assays
- **CV:** ≤20% for biological replicates, ≤10% for technical replicates
- **Dynamic range:** ≥10-fold between positive and negative controls

#### Data Quality
- **Curve fitting:** R² ≥0.95 for dose-response curves
- **Hill slopes:** 0.5-3.0 for meaningful dose-response relationships
- **Reproducibility:** IC50 values within 2-fold between experiments

---

## Safety and Handling

### Chemical Safety

#### High-Risk Compounds
- **DMSO:** Use in ventilated area, avoid skin contact
- **Ruthenium Red:** Wear gloves, avoid inhalation
- **Rotenone:** Handle in fume hood, suspected carcinogen

#### Waste Disposal
- **Organic solvents:** Collect in appropriate waste containers
- **Cell culture waste:** Autoclave before disposal
- **Contaminated tips/plates:** Bleach treatment before autoclaving

### Biological Safety
- **BSL-2 practices:** Standard for all cell culture work
- **Personal protective equipment:** Lab coat, gloves, safety glasses
- **Spill procedures:** Immediate containment and decontamination

---

## Cost Estimates

### Per-Experiment Costs (96-well format, n=6)

#### Basic Screening (CBD dose-response)
- **Reagents:** $180
- **Consumables:** $45
- **Total per experiment:** $225

#### Full Validation (CBD + inhibitors + PLA)
- **Reagents:** $450
- **Consumables:** $120
- **Total per experiment:** $570

#### Complete Parameter Sweep (125 combinations)
- **Reagents:** $8,500
- **Consumables:** $2,800
- **Equipment time:** $3,200
- **Total project cost:** $14,500

---

**Document Version:** 1.0
**Last Updated:** 2025-10-07
**Next Review:** Upon completion of validation studies

**🧬⚡🔬∞**