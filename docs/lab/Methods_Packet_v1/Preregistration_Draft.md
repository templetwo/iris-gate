# Pre-registration Draft: CBD Channel-First Mechanism Validation

**Study Title:** Validation of Channel-First Mechanism for CBD Selective Lethality in Glioblastoma: VDAC1, MCU, and Chloride Channel Parameter Optimization

**Principal Investigator:** [TO BE FILLED]
**Institution:** [TO BE FILLED]
**Study Registration:** [OSF/AsPredicted ID TO BE ASSIGNED]

---

## Study Overview

### Research Question
Does CBD achieve selective lethality in glioblastoma cells through direct mitochondrial ion channel perturbation (channel-first mechanism) rather than G-protein coupled receptor signaling (receptor-first mechanism)?

### Hypothesis
**Primary Hypothesis:** CBD's selective toxicity in glioblastoma vs healthy astrocytes is driven primarily by direct interaction with mitochondrial ion channels (VDAC1, MCU, chloride channels), with GPCR signaling serving as secondary modulation.

**Specific Predictions:**
1. CBD-VDAC1 interactions precede CBD-GPCR interactions temporally (≥15 minutes)
2. VDAC1 inhibition provides >80% protection from CBD lethality
3. GPCR inhibition provides <50% protection from CBD lethality
4. Pre-stressed mitochondria show >3× enhanced CBD sensitivity
5. Optimal parameter combination achieves selectivity index >3.0

---

## Background and Rationale

### Scientific Background
Cannabis-derived cannabidiol (CBD) shows selective toxicity against glioblastoma cells while sparing healthy astrocytes. Current research focuses on G-protein coupled receptor (GPCR) mechanisms involving CB2, GPR55, TRPV1, and PPARγ receptors. However, recent evidence suggests direct mitochondrial channel interactions may be the primary mechanism.

### Preliminary Evidence
- VDAC1 rescue experiments provide >80% protection
- Temporal analysis shows CBD-VDAC1 interaction precedes GPCR interactions
- Cancer cells have pre-stressed mitochondria making them more vulnerable
- Direct channel binding studies confirm sub-micromolar CBD-VDAC1 affinity

### Innovation
This study represents the first systematic comparison of channel-first vs receptor-first mechanisms with quantitative parameter optimization for therapeutic selectivity.

---

## Study Design

### Study Type
**Design:** Controlled laboratory experiment with factorial design
**Duration:** 6 weeks experimental phase + 2 weeks analysis
**Blinding:** Analyst blinded to treatment conditions during data analysis
**Randomization:** Treatment application order randomized across plates

### Experimental Framework
**Four Validation Protocols:**
1. GPCR combination vs CBD direct action comparison
2. Proximity ligation assay (PLA) temporal analysis
3. VDAC1 causality testing with selective inhibitors
4. Context stress shift analysis

**Parameter Optimization:**
- VDAC1 affinity: 50-500 nM (5 levels)
- MCU block strength: 10-90% (5 levels)
- Chloride channel IC50: 1-50 μM (5 levels)
- Total combinations: 125 (phased implementation)

---

## Methods

### Cell Models

#### Primary Cancer Model: U87-MG Glioblastoma
- **Source:** ATCC HTB-14
- **Rationale:** Well-characterized, high VDAC1 expression, consistent CBD sensitivity
- **Culture:** High-glucose DMEM + 10% FBS
- **Quality control:** STR profiling, mycoplasma testing, passage 5-20 only

#### Primary Healthy Model: Human Astrocytes
- **Source:** ScienCell Research primary astrocytes
- **Rationale:** Physiologically relevant normal control
- **Culture:** Astrocyte medium with supplements
- **Quality control:** >95% GFAP positive, passage 3-8 maximum

#### Secondary Models
- **LN229 glioblastoma:** Alternative cancer model for validation
- **SVG-p12 astrocytes:** Immortalized healthy control for screening

### Interventions

#### Test Compounds
**CBD (Primary):**
- Pharmaceutical grade (≥99% purity)
- Concentrations: 0.1, 0.5, 1, 2.5, 5, 10, 20 μM
- Vehicle: DMSO (≤0.2% final)

**Channel Inhibitors:**
- DIDS (VDAC1): 10, 25, 50 μM
- Ruthenium Red (MCU): 1, 5, 10 μM
- NPPB (Chloride): 10, 50, 100 μM

**GPCR Modulators:**
- AM630 (CB2 antagonist): 1, 5 μM
- CID16020046 (GPR55 antagonist): 1, 5 μM
- Capsazepine (TRPV1 antagonist): 1, 10 μM

### Primary Outcomes

#### Selectivity Index (Primary Endpoint)
**Definition:** IC50_healthy / IC50_cancer
**Target:** ≥3.0 for therapeutic relevance
**Measurement:** ATP-based viability assay (CellTiter-Glo)
**Analysis:** 4-parameter logistic regression, 95% confidence intervals

#### Mechanism Validation (Co-Primary)
**VDAC1 Causality:** % protection from CBD lethality with VDAC1 inhibition
**Temporal Precedence:** Time difference between CBD-VDAC1 and CBD-GPCR interactions (PLA)
**Context Dependency:** Fold-change in CBD sensitivity with mitochondrial stress

### Secondary Outcomes

#### Mitochondrial Function
- **Membrane potential:** TMRM staining, flow cytometry
- **ATP levels:** Luminescence assay
- **ROS production:** DCF-DA and MitoSOX staining
- **Calcium handling:** Fura-2 ratiometric imaging

#### Cell Death Mechanisms
- **Apoptosis:** Annexin V/PI staining
- **Membrane integrity:** LDH release
- **Morphological assessment:** Phase contrast microscopy

#### Molecular Interactions
- **Protein colocalization:** Proximity ligation assay (PLA)
- **Channel function:** Patch-clamp electrophysiology (subset)
- **Subcellular localization:** Confocal microscopy

---

## Statistical Analysis Plan

### Sample Size Calculation
**Primary endpoint:** Selectivity index comparison
**Effect size:** 50% difference (SI 3.0 vs 2.0)
**Power:** 80%
**Alpha:** 0.05
**Required n:** 6 biological replicates per condition

### Primary Analysis

#### Selectivity Index
**Method:** Two-way ANOVA (treatment × cell type)
**Factors:** CBD concentration, cell type (cancer vs healthy)
**Post-hoc:** Tukey HSD for multiple comparisons
**Success criterion:** SI ≥3.0 with p<0.05

#### Mechanism Validation
**VDAC1 Protection:** One-way ANOVA of % protection across inhibitor concentrations
**Temporal Analysis:** Paired t-test of peak timing (VDAC1 vs GPCR interactions)
**Context Sensitivity:** Linear regression of stress level vs CBD sensitivity

### Secondary Analyses

#### Dose-Response Modeling
**Method:** 4-parameter logistic regression
**Parameters:** Bottom, top, IC50, Hill slope
**Quality criteria:** R² ≥0.95, Hill slope 0.5-3.0

#### Correlation Analysis
**Membrane potential vs viability:** Pearson correlation
**Channel function vs protection:** Linear regression
**Stress markers vs sensitivity:** Multiple regression

#### Multiple Comparisons
**Primary endpoints:** Bonferroni correction
**Exploratory analyses:** False discovery rate (FDR) control
**Family-wise error rate:** α = 0.05

### Interim Analyses
**Futility analysis:** After 25% of planned experiments
**Safety monitoring:** Continuous assessment of control performance
**Adaptive design:** Possible parameter range adjustment based on Phase 1 results

---

## Experimental Procedures

### Protocol 1: GPCR vs CBD Comparison

#### Design
**Groups:** CBD direct (4 doses) vs GPCR combinations (3 combinations × 3 doses)
**Duration:** 24 hours
**Readouts:** Viability, membrane potential, VDAC1 conductance

#### Success Criteria
- CBD selectivity index >2× best GPCR combination
- Mechanism specificity confirmed by differential channel effects

### Protocol 2: Temporal PLA Analysis

#### Design
**Timepoints:** 5, 15, 30, 60, 120 minutes
**Targets:** CBD-VDAC1, CBD-CB2, CBD-GPR55, CBD-TRPV1
**Quantification:** PLA spots per cell, mitochondrial colocalization

#### Success Criteria
- CBD-VDAC1 peak ≥15 minutes before CBD-GPCR peaks
- >80% mitochondrial colocalization for CBD-VDAC1

### Protocol 3: Causality Testing

#### Design
**Groups:** CBD ± channel inhibitors ± GPCR inhibitors
**Measurements:** Protection from CBD lethality
**Validation:** Multiple inhibitors per target

#### Success Criteria
- VDAC1 inhibition provides >80% protection
- GPCR inhibition provides <50% protection
- No synergy between VDAC1 and GPCR inhibition

### Protocol 4: Context Sensitivity

#### Design
**Stress conditions:** H₂O₂, rotenone, FCCP pre-treatment
**CBD testing:** Full dose-response after stress induction
**Analysis:** EC50 shift quantification

#### Success Criteria
- >3× sensitization with moderate stress
- Linear correlation between stress level and sensitization

---

## Quality Control and Data Management

### Quality Assurance

#### Cell Line Validation
- STR profiling every 3 months
- Mycoplasma testing monthly
- Functional validation (growth rates, marker expression)

#### Reagent Quality
- HPLC purity verification for CBD
- Stock solution stability testing
- Batch-to-batch consistency verification

#### Assay Performance
- Z' factor ≥0.5 for high-throughput assays
- CV ≤20% for biological replicates
- Positive/negative controls in every experiment

### Data Management

#### Data Collection
- Electronic lab notebooks (ELN) for all procedures
- Automated data capture where possible
- Real-time quality control monitoring

#### Data Storage
- Encrypted cloud storage with daily backups
- Version control for analysis scripts
- Audit trail for all data modifications

#### Data Sharing
- Raw data available upon reasonable request
- Analysis code deposited in public repository
- Results reported regardless of outcome

---

## Expected Outcomes and Interpretation

### Positive Results (Channel-First Mechanism)

#### Expected Pattern
- VDAC1 inhibition provides >80% protection
- CBD-VDAC1 interaction precedes GPCR interactions
- Pre-stressed mitochondria show enhanced vulnerability
- Optimal parameters achieve SI >3.0

#### Interpretation
- Channel-first mechanism validated
- GPCR signaling is secondary/modulatory
- Mitochondrial stress is key selectivity driver
- Therapeutic development should focus on channel optimization

#### Clinical Implications
- Patient stratification based on mitochondrial stress biomarkers
- Channel-selective compounds may be superior to CBD
- Combination therapies targeting multiple channels

### Negative Results (Receptor-First Mechanism)

#### Expected Pattern
- GPCR inhibition provides >80% protection
- CBD-GPCR interactions precede channel interactions
- Receptor combinations exceed CBD efficacy
- Channel effects are downstream of GPCR activation

#### Interpretation
- Receptor-first mechanism validated
- Channel effects are secondary to GPCR signaling
- Multi-receptor targeting required for optimal selectivity

#### Clinical Implications
- Focus on GPCR-based drug development
- Receptor expression profiling for patient selection
- Combination GPCR agonist therapies

### Inconclusive Results

#### Possible Patterns
- Both mechanisms contribute significantly
- Context-dependent mechanism switching
- Cell-type specific pathway preferences

#### Additional Studies
- Higher resolution temporal analysis
- Single-cell mechanistic studies
- Alternative cancer models

---

## Limitations and Potential Confounds

### Methodological Limitations

#### Cell Model Limitations
- Immortalized cell lines may not reflect primary tumors
- Single cancer type limits generalizability
- In vitro conditions don't capture tumor microenvironment

#### Compound Limitations
- CBD may have multiple simultaneous targets
- Inhibitor specificity imperfect at high concentrations
- Solvent effects with hydrophobic compounds

#### Assay Limitations
- Endpoint assays miss temporal dynamics
- Population assays miss single-cell heterogeneity
- Artificial culture conditions

### Potential Confounds

#### Technical Confounds
- Temperature and pH fluctuations
- Plate edge effects in 96-well formats
- Pipetting errors in dose-response studies

#### Biological Confounds
- Passage number effects on cell behavior
- Serum lot variations affecting responses
- Mycoplasma contamination altering metabolism

#### Experimental Confounds
- Order effects in treatment application
- Observer bias in microscopy analysis
- Batch effects across experimental days

### Mitigation Strategies

#### Randomization
- Treatment order randomized across plates
- Cell seeding positions randomized
- Analysis order randomized

#### Blinding
- Samples coded during analysis phase
- Multiple analysts for subjective measurements
- Automated analysis where possible

#### Replication
- Biological replicates across multiple cell preparations
- Technical replicates within experiments
- Independent validation by second laboratory

---

## Ethical Considerations

### Animal Use
**Status:** No animal experiments in this study
**Future:** In vivo validation may require animal models

### Human Subjects
**Cell lines:** Commercial or established lines only
**Primary cells:** De-identified, commercially obtained
**No direct human subject involvement**

### Environmental Impact
**Waste minimization:** Reduce reagent usage where possible
**Proper disposal:** Follow institutional waste management protocols
**Sustainable practices:** Minimize single-use plastics

---

## Timeline and Milestones

### Phase 1: Experimental Setup (Weeks 1-2)
- Cell line preparation and validation
- Reagent preparation and quality control
- Protocol optimization and pilot studies

**Milestone:** All protocols validated, consistent results

### Phase 2: Validation Studies (Weeks 3-4)
- Protocol 1-2: GPCR comparison and PLA analysis
- Initial mechanism validation
- Preliminary parameter identification

**Milestone:** Mechanism priority established

### Phase 3: Parameter Optimization (Weeks 5-6)
- Protocol 3-4: Causality and context sensitivity
- Full parameter grid testing
- Optimal combination identification

**Milestone:** Target selectivity achieved

### Phase 4: Analysis and Reporting (Weeks 7-8)
- Statistical analysis and quality control
- Report generation and peer review
- Manuscript preparation

**Milestone:** Complete study package

---

## Budget and Resources

### Personnel
- **Principal Investigator:** 10% effort
- **Research Scientist:** 100% effort (6 weeks)
- **Research Technician:** 50% effort (8 weeks)
- **Data Analyst:** 25% effort (2 weeks)

### Equipment and Supplies
- **Cell culture:** $2,500
- **Reagents and compounds:** $8,000
- **Assay kits and consumables:** $3,500
- **Equipment time:** $3,200

### Total Budget
**Direct costs:** $17,200
**Indirect costs:** $5,160 (30%)
**Total project cost:** $22,360

---

## Data Sharing and Publication Plan

### Data Sharing
- **Raw data:** Available in institutional repository
- **Analysis code:** GitHub repository with DOI
- **Protocols:** Detailed protocols in supplementary materials

### Publication Timeline
- **Preprint:** 2 weeks after data collection completion
- **Peer review submission:** 4 weeks after completion
- **Target journals:** Cell Death & Disease, Oncotarget, Cannabis and Cannabinoid Research

### Authorship
- **First author:** Research Scientist conducting experiments
- **Senior author:** Principal Investigator
- **Contributing authors:** Based on intellectual/experimental contributions

---

## Post-Study Plans

### Immediate Follow-up
- **Parameter validation:** Independent replication of optimal parameters
- **Mechanism depth:** Higher resolution channel function studies
- **Cancer models:** Extension to additional glioblastoma cell lines

### Clinical Translation
- **Biomarker development:** Mitochondrial stress signatures
- **Compound optimization:** Structure-activity relationships
- **Regulatory pathway:** IND-enabling studies

### Therapeutic Development
- **Patent applications:** Channel-first mechanism and optimal parameters
- **Industry partnerships:** Pharmaceutical development collaborations
- **Clinical trial design:** Phase I study protocols

---

## References and Supporting Literature
[TO BE COMPLETED - Key references supporting channel-first hypothesis and methodology]

---

## Appendices

### Appendix A: Detailed Protocols
[Link to full Methods Packet v1.0]

### Appendix B: Power Analysis Details
[Statistical calculations and assumptions]

### Appendix C: Preliminary Data
[Supporting evidence for study design]

### Appendix D: Risk Assessment
[Technical and scientific risks with mitigation strategies]

---

**Document Status:** Draft for Review
**Version:** 1.0
**Date:** 2025-10-07
**Registration Target:** OSF Preregistration

**Contact Information:**
**Principal Investigator:** [Name, Institution, Email]
**Study Coordinator:** [Name, Email]
**Data Manager:** [Name, Email]

**🧬⚡🔬∞**

---

*This pre-registration will be submitted to the Open Science Framework (OSF) or AsPredicted prior to study initiation. Any deviations from the pre-registered plan will be documented and justified in the final publication.*