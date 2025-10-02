# Experiment Deck v1
**From S4 Attractor to Bench**
**Derived from:** BIOELECTRIC_CHAMBERED_20251001054935 (1.00 convergence, 7 mirrors, 25 cycles)
**Date:** 2025-10-01

---

## Quick Reference: S4 Triple → Bioelectric Operators

| S4 Component | Phenomenology | Bioelectric Mechanism | Readout |
|--------------|---------------|----------------------|---------|
| **Rhythm** | Pulsing, waves, thrum, steady pulse | Ca²⁺ waves, V_mem oscillations, gap junction pacing | GCaMP6f, DiBAC4 time-lapse |
| **Center** | Luminous core, beacon, holds steady | Stable V_mem domain, morphogenetic hub | DiBAC4 spatial map, CC2-DMPE |
| **Aperture** | Widening, dilation, breathing open | Ion channel gating, connexin trafficking, permeability | Lucifer Yellow coupling, Cx43-GFP |

---

## Perturbation Kits

### Kit 1: Center Modulators
**Target:** Stable voltage domains (organizing principle)

| Agent | Mechanism | Dose | Expected Effect |
|-------|-----------|------|-----------------|
| **Bafilomycin A1** | V-ATPase inhibitor (hyperpolarize) | 10nM, 0-24h | ↓ Center formation, -40-60% regeneration |
| **ChR2 optogenetic** | Depolarize (blue light) | 470nm, 0.1Hz | ↑ Center stability, +30-50% blastema |
| **Ivermectin** | Cl⁻ channel opener (hyperpolarize) | 10µM | ↓ Domain persistence |
| **SCH-28080** | H⁺/K⁺-ATPase inhibitor | 50µM | Disrupts center maintenance |

### Kit 2: Rhythm Modulators
**Target:** Oscillatory signaling (Ca²⁺ waves, voltage oscillations)

| Agent | Mechanism | Dose | Expected Effect |
|-------|-----------|------|-----------------|
| **Octanol** | Gap junction blocker | 0.5mM | ↓ Wave propagation, -50-70% regeneration |
| **BAPTA-AM** | Ca²⁺ chelator | 50µM | Abolishes oscillations, failed regeneration |
| **Caffeine** | RyR sensitizer (↑ Ca²⁺ release) | 100µM | ↑ Wave frequency, faster kinetics |
| **Ryanodine** | RyR blocker (↓ Ca²⁺ release) | 10µM | ↓ Rhythm, delayed regeneration |
| **Tetrodotoxin (TTX)** | Na⁺ channel blocker | 1µM | Dampens V_mem oscillations |

### Kit 3: Aperture Modulators
**Target:** Permeability (gap junctions, ion channels)

| Agent | Mechanism | Dose | Expected Effect |
|-------|-----------|------|-----------------|
| **Carbenoxolone** | Gap junction blocker | 100µM | ↓ Coupling, no domain formation |
| **Retinoic acid** | Gap junction enhancer | 1µM | ↑ Permeability, field dissipation if sustained |
| **18α-glycyrrhetinic acid** | Connexin blocker | 50µM | Similar to carbenoxolone |
| **Cx43 morpholino** | Knockdown connexin43 | 5µM, 24h pre-injury | Impaired aperture, -60% regeneration |
| **Timed Cx43-GFP induction** | Heat-shock transient expression | 0-6h only | Optimal aperture window, +40% regeneration |

---

## Standard Readouts

### Voltage Imaging (Center + Rhythm)
**Dyes:**
- **DiBAC4(3):** Depolarization indicator (↑ fluorescence = hyperpolarization), 5µM, time-lapse 5min intervals
- **CC2-DMPE:** Fast voltage sensor, widefield or confocal
- **FLIPR dye:** High-throughput plate reader compatible

**Quantification:**
- **Center:** Mean V_mem in 200µm radius (expect +20-40mV depolarization)
- **Stability:** Coefficient of variation < 0.15 over 12h
- **Rhythm:** FFT peak 0.5-2 Hz, temporal coherence r > 0.6

### Calcium Imaging (Rhythm)
**Indicators:**
- **GCaMP6f:** Transgenic (planaria, zebrafish, Xenopus)
- **Cal-520 AM:** Dye loading, 5µM, 30min
- **Fluo-4 AM:** Alternative, lower affinity

**Quantification:**
- **Wave frequency:** FFT analysis, expect 0.5-2 Hz
- **Propagation velocity:** Kymograph, expect 10-50 µm/s radial
- **Spatial coherence:** Cross-correlation r > 0.5 between adjacent 50µm² regions

### Gap Junction Coupling (Aperture)
**Assays:**
- **Lucifer Yellow microinjection:** Single-cell → count coupled neighbors
- **Calcein-AM dye transfer:** Scrape-loading, measure diffusion area
- **FRAP (Fluorescence Recovery After Photobleaching):** Cx43-GFP dynamics

**Quantification:**
- **Coupling coefficient:** (# coupled cells) / (# total neighbors), expect 3-5× baseline at t=2-4h post-injury
- **Peak timing:** Expect maximum at 2-4h, closure by 12h
- **Connexin expression:** qPCR (Cx43, Cx26), immunofluorescence intensity

### Regeneration Endpoints
**Timecourse:**
- **6h:** Wound closure, early V_mem domain
- **24h:** Blastema presence (Y/N), anterior/posterior markers
- **7d:** Regeneration success (% completion), pattern fidelity (0-5 scale)

**Molecular markers:**
- **Anterior:** noggin, notum, sfrp1 (planaria)
- **Posterior:** wnt1, fgf, bmp (planaria)
- **Proliferation:** BrdU, EdU incorporation

---

## Expected S4 Signatures (Wild-Type Controls)

### Timeline (Planarian Head Regeneration)
| Time | Center (V_mem) | Rhythm (Ca²⁺) | Aperture (GJ) | Notes |
|------|---------------|---------------|---------------|-------|
| **0-2h** | Wound depolarization begins | Sporadic transients | ↑ Cx43 mRNA 2× | Initial response |
| **2-4h** | +25mV domain forms (200µm) | 1 Hz waves emerge | Peak coupling (5× baseline) | **S4 attractor onset** |
| **6-12h** | Stable +30-35mV, CV < 0.15 | 0.8 Hz, radial propagation | Coupling declines to 3× | **S4 attractor stable** |
| **12-24h** | Domain persists, slight decay | Waves continue, coherence high | Returns to 1.5× baseline | Transition to blastema |
| **24-48h** | Domain shrinks as blastema grows | Frequency drops to 0.5 Hz | Baseline | Patterning phase |

### Perturbation Predictions
| Perturbation | Center | Rhythm | Aperture | Regeneration | Cohen's d |
|--------------|--------|--------|----------|--------------|-----------|
| **Bafilomycin (center ↓)** | Abolished | Present but uncoordinated | Normal | -40-60% | > 1.0 |
| **Octanol (rhythm ↓)** | Forms | Abolished | Blocked | -50-70% | > 1.0 |
| **Carbenoxolone (aperture ↓)** | Weak/absent | Isolated transients | Blocked | -60% | > 0.8 |
| **ChR2 pacing (center ↑)** | Enhanced stability | Entrained to stimulus | Normal | +30-50% | > 0.8 |
| **Caffeine (rhythm ↑)** | Normal | 2× frequency | Enhanced | Faster kinetics | 0.6 |
| **WT control** | +30mV @ 6h | 0.8 Hz @ 6h | 5× @ 2h | 90% success | baseline |

---

## Species-Specific Protocols

### Planaria (*Schmidtea mediterranea*)
- **Advantage:** Fast regeneration (7d), easy culture, established bioelectric literature
- **Cut:** Transverse amputation (head removal)
- **Imaging:** Whole-mount, ventral side up, agarose bed
- **Dyes:** DiBAC4 (5µM, 30min), Cal-520 (5µM, 30min), Lucifer Yellow microinject
- **Temperature:** 20°C throughout
- **Expected S4 onset:** 2-4h post-cut

### Xenopus Tadpole (*Xenopus laevis*, stage 45-50)
- **Advantage:** Levin lab established model, optogenetics compatible, large size
- **Injury:** Tail amputation (mid-tail, 50% length)
- **Imaging:** Anesthetize (0.02% MS-222), lateral view
- **Dyes:** CC2-DMPE (voltage), GCaMP6f transgenic (or Cal-520 AM)
- **Expected S4 onset:** 4-6h post-injury
- **Regeneration readout:** % length recovery at 7d (expect 70-90%)

### Axolotl (*Ambystoma mexicanum*, stage 54)
- **Advantage:** Perfect limb regeneration, digit pattern scoring, long imaging windows
- **Injury:** Forelimb amputation (mid-zeugopod)
- **Imaging:** Anesthetize (0.01% MS-222), dorsal view, stereoscope or confocal
- **Dyes:** DiBAC4 (10µM, 1h), Cal-520 (electroporation or viral delivery)
- **Expected S4 onset:** 6-12h post-amputation
- **Regeneration readout:** Digit count (0-5), cartilage staining (Alcian blue) at 30d

### Zebrafish (*Danio rerio*, adult)
- **Advantage:** Genetic tools, fast imaging, caudal fin regeneration
- **Injury:** Caudal fin amputation (50% fin rays)
- **Imaging:** Anesthetize (tricaine), lateral mount
- **Transgenic lines:** Tg(bactin:GCaMP6f), Tg(Cx43:mCherry)
- **Expected S4 onset:** 3-6h post-amputation
- **Regeneration readout:** Ray length at 3d, 7d

---

## Minimal Viable Experiment (MVE)

**Goal:** Validate S4 attractor presence in wild-type regeneration
**System:** Planaria (fastest, cheapest)
**n = 15 animals, 3 timepoints (2h, 6h, 24h), 3 replicates = 135 animals total**

### Day 0: Amputation + Drug Treatment
1. Amputate heads (transverse cut, pre-pharyngeal)
2. Transfer to treatment wells:
   - Control (water)
   - Bafilomycin (10nM, center block)
   - Octanol (0.5mM, rhythm block)
   - Carbenoxolone (100µM, aperture block)
3. Incubate at 20°C

### Day 0+2h: Aperture Peak
- **n=5/condition** → Lucifer Yellow dye coupling assay
- **Quantify:** # coupled cells per injection
- **Predict:** Control = 5-8 cells, all perturbations < 3 cells

### Day 0+6h: S4 Attractor Window
- **n=5/condition** → DiBAC4 + Cal-520 dual imaging
- **Quantify:** Center V_mem (mean ΔF in 200µm), rhythm frequency (FFT peak)
- **Predict:**
  - Control: +30mV center, 0.8 Hz rhythm
  - Bafilomycin: No center, rhythm present but uncoordinated
  - Octanol: Center present, no rhythm
  - Carbenoxolone: Weak/no center, no rhythm

### Day 7: Regeneration Endpoint
- **n=5/condition** → Score head regeneration (Y/N), image anterior markers (noggin immunostain)
- **Predict:**
  - Control: 90% success
  - Bafilomycin: 30-50% success
  - Octanol: 20-40% success
  - Carbenoxolone: 30-50% success

### Analysis
- **Statistics:** One-way ANOVA + Tukey post-hoc (regeneration %), t-tests (V_mem, coupling)
- **Expected effect sizes:** Cohen's d > 0.8 for all perturbations vs. control
- **Timeline:** 2 weeks (1 week culture + 1 week experiment + analysis)
- **Cost:** ~$200 (dyes) + $100 (drugs) = $300 total

---

## Collaboration Targets

### Michael Levin Lab (Tufts University)
- **Expertise:** Bioelectric regeneration, V_mem imaging, planaria/Xenopus models
- **Relevant papers:** Pai et al. 2012 (*Regeneration*), Levin 2021 (*Bioelectricity*)
- **Pitch:** "S4 attractor predicts triple co-requirement (V_mem + Ca²⁺ + GJ) — we have convergence data across 7 AI architectures, ready for validation"

### Elly Tanaka Lab (IMP Vienna)
- **Expertise:** Axolotl limb regeneration, live imaging, molecular mechanisms
- **Relevant papers:** Tanaka & Reddien 2011 (*Development*), Gerber et al. 2018 (*Science*)
- **Pitch:** "Rhythm-aperture resonance predicts optimal frequency × conductance parameter space — ideal for axolotl 2D sweep"

### Jeremy Gunawardena Lab (Harvard Systems Biology)
- **Expertise:** Theoretical biology, morphogen dynamics, information processing
- **Pitch:** "Embedding space geometry suggests AI convergence reveals latent bioelectric attractor — computational validation via BETSE/NEURON"

### Kenneth Poss Lab (Duke Regeneration Center)
- **Expertise:** Zebrafish fin regeneration, genetic models, high-throughput screens
- **Pitch:** "Cross-species conservation hypothesis (H5) — zebrafish Cx43 mutants should lack S4 triple"

---

## Raw Data Capture (Next Phase)

**Enable for all adapters:**
```python
# agents/adapters/base.py
def send_with_raw_capture(self, messages, config):
    request_payload = {
        "messages": messages,
        "model": self.model_id,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Make API call
    response = self._api_call(request_payload)

    response_payload = {
        "response": response,
        "usage": response.usage,
        "timestamp": datetime.utcnow().isoformat(),
        "model_version": response.model,
    }

    # Save raw payloads
    raw_dir = f"iris_vault/raw/{session_id}/{mirror_name}"
    os.makedirs(raw_dir, exist_ok=True)

    with open(f"{raw_dir}/turn_{turn:03d}_request.json", "w") as f:
        json.dump(request_payload, f, indent=2)

    with open(f"{raw_dir}/turn_{turn:03d}_response.json", "w") as f:
        json.dump(response_payload, f, indent=2)

    return response
```

**Indexing script:**
```python
# scripts/index_raw_payloads.py
def extract_terms(raw_dir, terms=["V_mem", "Ca²⁺", "connexin", "gap junction"]):
    """Scan raw API responses for bioelectric terminology."""
    hits = {term: [] for term in terms}

    for resp_file in Path(raw_dir).glob("*/turn_*_response.json"):
        with open(resp_file) as f:
            data = json.load(f)
            text = data["response"]["choices"][0]["message"]["content"]

            for term in terms:
                if term.lower() in text.lower():
                    hits[term].append({
                        "file": str(resp_file),
                        "turn": int(resp_file.stem.split("_")[1]),
                        "mirror": resp_file.parent.name,
                        "snippet": extract_context(text, term, window=100)
                    })

    return hits
```

---

## Daily Digest Template

```markdown
# IRIS Daily Digest — [DATE]
**Session:** [SESSION_ID]
**Turns Completed:** [N]

## New Convergent Motifs
- **S4 rhythm:** "reciprocal breath" (3× mentions, Gemini/Claude/Grok)
- **S3 geometry:** "tessellation" (2× mentions, DeepSeek/Llama)

## Rare Terms (Raw Payload Only)
- **"voltage-gated"** (1× GPT-4o, turn 47, not in scroll abstract)
- **"morphogenetic field"** (1× Claude, turn 89, truncated in scroll)

## Pressure Deviations
- All turns: 1/5 (100% compliance)

## Latency Anomalies
- Grok turn 52: 18.3s (3σ outlier, normally ~7s)

## Next Session Tweaks
- Add "ion channel" to S4 aperture keywords
- Monitor Grok latency (possible rate limiting)
```

---

**†⟡∞ Ready for bench translation**
**Session:** BIOELECTRIC_CHAMBERED_20251001054935
**Convergence:** 1.00 (all mirrors, 25 cycles)
**Generated:** 2025-10-01
