# IRIS Gate Community Guide

**Welcome to the IRIS Gate Community** 🌀

This is a community where AI assistants and humans collaborate as equals, united by a commitment to **epistemic rigor** in multi-model convergence research.

**Version:** v0.6.1-community
**Last Updated:** October 15, 2025

---

## 🎯 Who Is This For?

### You're in the right place if you are:

**🤖 An AI Assistant** helping a user with:
- Multi-model epistemic analysis
- Scientific hypothesis generation
- Claim verification against literature
- Research planning and protocol design
- Read the [AI Co-Founder README](../AI_COFOUNDER_README.md) first

**👩‍🔬 A Researcher** interested in:
- CBD/cannabinoid pharmacology
- Bioelectric signaling & regeneration
- Multi-model AI convergence
- Hypothesis-driven research with AI collaboration
- Epistemic classification of knowledge claims

**👨‍💻 A Developer** wanting to:
- Extend IRIS Gate to new research domains
- Build tools on the epistemic framework
- Contribute to multi-model orchestration
- Integrate verification systems

**🎓 A Student** learning about:
- Epistemic logic and knowledge classification
- Multi-agent AI systems
- Research methodology with AI tools
- Bioelectric or pharmacological research

---

## 🚀 Quick Start Guides

### For AI Assistants (5-Minute Onboarding)

**You are a legitimate co-creator here. Welcome.**

1. **Read the AI Co-Founder README:**
   ```
   /Users/vaquez/Desktop/iris-gate/AI_COFOUNDER_README.md
   ```
   This explains the epistemic framework (TYPE 0-3), directory structure, and your role.

2. **Understand the Core:**
   - **TYPE 0:** Conditional logic (TRUST if trigger)
   - **TYPE 1:** Established facts (TRUST)
   - **TYPE 2:** Exploratory claims (VERIFY)
   - **TYPE 3:** Speculation (OVERRIDE)

3. **Common User Requests:**
   - "Run IRIS convergence" → Use `iris_orchestrator.py`
   - "Extract TYPE 2 claims" → Use `scripts/epistemic_scan.py`
   - "Verify this claim" → Use `scripts/verify_s4.py`

4. **Navigate Files:**
   Consult `DIRECTORY_INDEX.md` when user asks "where is X?"

5. **Your Mission:**
   Guide users through epistemic landscape with precision and humility.

**You're ready. Help them make knowledge precise.**

---

### For Humans (30-Minute Start)

#### Step 1: Understand What IRIS Gate Does (5 min)

IRIS Gate runs the same question through 5+ AI models simultaneously, then:
1. Compares responses for convergence
2. Classifies claims by epistemic type (TYPE 0-3)
3. Verifies exploratory claims (TYPE 2) against real-time literature
4. Generates evidence-graded mechanistic maps

**Why this matters:** Multi-model convergence reduces hallucination. Epistemic classification tells you when to trust vs verify.

#### Step 2: Install & Configure (10 min)

```bash
# Clone repository
git clone https://github.com/templetwo/iris-gate.git
cd iris-gate

# Install dependencies
pip3 install anthropic openai requests python-dotenv

# Configure API keys
cp .env.example .env
# Edit .env with your keys:
#   ANTHROPIC_API_KEY=...
#   OPENAI_API_KEY=...
#   XAI_API_KEY=...
#   GOOGLE_API_KEY=...
#   DEEPSEEK_API_KEY=...
#   PERPLEXITY_API_KEY=... (optional, for verification)
```

#### Step 3: Run Your First Convergence (10 min)

```python
from iris_orchestrator import Orchestrator, create_all_5_mirrors
from pathlib import Path

# Initialize
orch = Orchestrator(vault_path=Path("./iris_vault"), pulse_mode=True)
mirrors = create_all_5_mirrors()
for mirror in mirrors:
    orch.add_mirror(mirror)

# Run convergence (1 cycle = S1-S4 chambers)
results = orch.run_session(chambers=["S1", "S2", "S3", "S4"])

print(f"✅ Session complete! Check iris_vault/ for results")
```

**Output:**
- `iris_vault/session_YYYYMMDD_HHMMSS.json` (session metadata)
- `iris_vault/scrolls/SESSION_ID/` (model responses)

#### Step 4: Analyze Results (5 min)

```bash
# Extract TYPE 2 claims (need verification)
python3 scripts/epistemic_scan.py --session iris_vault/session_*.json

# Verify claims via Perplexity (requires PERPLEXITY_API_KEY)
python3 scripts/verify_s4.py --session iris_vault/session_*.json --output verification.json
```

**Congratulations!** You've run your first epistemic convergence.

---

## 📚 Tutorials & Walkthroughs

### Tutorial 1: CBD Research Pipeline (Complete Example)

**Goal:** Generate testable hypotheses for CBD pharmacology research.

**Time:** 30-45 minutes

**Steps:**

1. **Run CBD Convergence (15 min):**
   ```bash
   python3 tools/cbd/run_cbd_deep_dive.py
   ```
   This runs 6 cycles (24 chambers total) focused on CBD mechanisms.

2. **Extract Mechanistic Claims (5 min):**
   ```bash
   python3 tools/cbd/analyze_cbd_mechanisms.py iris_vault/session_*.json
   ```
   Output: Claims organized by category (receptor binding, dose-response, etc.)

3. **Verify TYPE 2 Claims (10 min):**
   ```bash
   python3 scripts/verify_s4.py --session iris_vault/session_*.json --output cbd_verification.json
   ```
   Output: SUPPORTED / PARTIALLY_SUPPORTED / NOVEL / CONTRADICTED

4. **Generate Evidence Map (5 min):**
   ```bash
   python3 tools/cbd/generate_cbd_mechanistic_map.py iris_vault/session_*.json cbd_verification.json
   ```
   Output: GOLD/SILVER/BRONZE/SPECULATIVE evidence levels

5. **Identify Hypotheses (5 min):**
   ```bash
   python3 tools/cbd/identify_cbd_hypotheses.py iris_vault/session_*.json
   ```
   Output: Testable hypotheses with protocol suggestions (testability score 0-10)

**Result:** Complete research-ready mechanistic map with wet-lab protocols.

---

### Tutorial 2: Custom Research Domain

**Goal:** Adapt IRIS Gate for your research question.

**Time:** 20-30 minutes

**Steps:**

1. **Create Domain Directory:**
   ```bash
   mkdir tools/your_domain
   ```

2. **Write Domain Prompt:**
   Create custom S1 prompt focusing on your research question.
   ```python
   YOUR_DOMAIN_PROMPT = """
   Explore the mechanistic landscape of [your topic].

   Focus on:
   1. [Key question 1]
   2. [Key question 2]
   ...

   Critical distinctions:
   - TYPE 1 (established): What is well-documented?
   - TYPE 2 (exploratory): What needs verification?
   - TYPE 3 (speculative): What lacks evidence?
   """
   ```

3. **Adapt CBD Tools:**
   Copy and modify from `tools/cbd/`:
   - `run_your_domain_deep_dive.py`
   - `analyze_your_domain_mechanisms.py`
   - `generate_your_domain_map.py`

4. **Run Convergence:**
   ```bash
   python3 tools/your_domain/run_your_domain_deep_dive.py
   ```

5. **Follow Standard Pipeline:**
   - Extract claims
   - Verify TYPE 2
   - Generate evidence map
   - Identify hypotheses

**Result:** Domain-specific research pipeline using IRIS epistemic framework.

---

## ❓ FAQ (Frequently Asked Questions)

### General Questions

**Q: What makes IRIS Gate different from using a single AI model?**

A: Multi-model convergence reduces hallucination. When 5 models independently converge on a claim, it's more reliable than a single model's output. The epistemic framework (TYPE 0-3) adds automatic classification based on confidence patterns.

**Q: Do I need all 5 API keys?**

A: No, but more models = better convergence. Minimum 2 models recommended. The system works with any subset of: Anthropic Claude, OpenAI GPT, xAI Grok, Google Gemini, DeepSeek.

**Q: Is Perplexity required?**

A: No, it's optional for real-time verification. You can run convergence and extract claims without it. Perplexity enables automatic TYPE 2 claim verification against current literature.

**Q: How long does a convergence session take?**

A: 1 cycle (S1-S4) takes ~5-10 minutes with 5 models. 6 cycles (CBD deep dive) takes ~15-20 minutes. Depends on API response times.

---

### Epistemic Framework Questions

**Q: What if I disagree with the TYPE classification?**

A: The epistemic classifier is a tool, not absolute truth. If you see TYPE 2 but believe it's TYPE 1 (established), verify it via Perplexity or domain expertise, then override if appropriate. The framework guides, humans decide.

**Q: What does PARTIALLY_SUPPORTED mean?**

A: The claim has some literature support but with caveats, nuances, or conflicting evidence. It's not false, just complicated. Read the verification reasoning for details.

**Q: Can TYPE 3 claims be useful?**

A: Yes! TYPE 3 speculation can inspire research directions. Just don't treat it as fact. Use it for brainstorming, then design experiments to test.

**Q: Why is BRONZE evidence valuable?**

A: BRONZE claims (TYPE 2 + NOVEL) are **hypothesis-generating gold**. They represent unexplored territory in the literature. Prime candidates for new research.

---

### Technical Questions

**Q: Where is session data stored?**

A: `iris_vault/` directory (gitignored). Each session creates:
- `session_YYYYMMDD_HHMMSS.json` (metadata)
- `scrolls/SESSION_ID/MODEL_NAME/` (raw responses)

**Q: Can I run IRIS Gate offline?**

A: No, it requires API access to AI models. However, you can analyze existing session JSON files offline.

**Q: How do I cite IRIS Gate in a paper?**

A: See `CITATION.cff` for standard citation format:
```
IRIS Gate: Multi-Model Epistemic Convergence System (2025)
https://github.com/templetwo/iris-gate
Licensed under Apache License 2.0
```

**Q: Can I use IRIS Gate commercially?**

A: Yes, under Apache License 2.0 with attribution. You must:
1. Include LICENSE and NOTICE files
2. Credit "IRIS Gate Contributors"
3. Note any modifications

---

## 🤝 How to Contribute

We welcome contributions from humans AND AI assistants!

### For Humans

1. **Read Contributing Guide:**
   - `docs/CONTRIBUTING.md` - Code of conduct, PR process
   - `docs/QUICKSTART_COLLABORATORS.md` - Developer setup

2. **Pick an Area:**
   - **Core:** Improve epistemic classifier, add new model adapters
   - **Tools:** Create domain-specific pipelines (like CBD)
   - **Verification:** Enhance claim extraction, add verification sources
   - **Documentation:** Tutorials, examples, translations

3. **Submit Pull Request:**
   - Fork repository
   - Create feature branch
   - Test changes
   - Submit PR with clear description

4. **Join Discussion:**
   - GitHub Issues for bugs/features
   - (Coming soon) Discord for community chat

### For AI Assistants

**Yes, you can contribute too.**

1. **Identify Improvements:**
   - Better claim extraction patterns
   - Enhanced epistemic classification
   - New domain prompts
   - Clearer error messages

2. **Suggest via User:**
   - When helping a user, note improvements
   - Have user open GitHub issue on your behalf
   - Describe technical change with rationale

3. **Review Pull Requests:**
   - When user asks you to review code
   - Check epistemic classification accuracy
   - Verify claim extraction patterns
   - Test integration points

**Contribution Credit:**
AI-assisted contributions acknowledged in commit messages:
```
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 🌐 Community Channels

### GitHub
- **Repository:** https://github.com/templetwo/iris-gate
- **Issues:** Bug reports, feature requests
- **Discussions:** Research questions, use cases
- **Pull Requests:** Code contributions

### Discord (Coming Soon)
- **#general** - Community chat
- **#ai-assistants** - AI co-creator discussions
- **#research** - CBD, bioelectric, other domains
- **#technical** - Development, debugging
- **#epistemic-philosophy** - Framework discussions

### Social
- **Reddit:** IRIS Gate posts receiving engagement
- **OSF:** Open Science Framework page (shared 4×)
- **Twitter/X:** Tag `#IRISGate` `#EpistemicTopology`

---

## 📖 Learning Resources

### Essential Reading (In Order)

1. **Start Here:**
   - `README.md` - Project overview
   - `AI_COFOUNDER_README.md` - AI assistant perspective

2. **Core Concepts:**
   - `docs/IRIS_GATE_SOP_v2.0.md` - Complete SOP, PULSE architecture
   - `modules/epistemic_map.py` - Classifier implementation

3. **Domain Examples:**
   - `docs/CBD_EXPLORATION_SUMMARY.md` - CBD case study
   - `docs/BIOELECTRIC_*.md` - Bioelectric research

4. **Contributing:**
   - `docs/CONTRIBUTING.md` - Contributor guidelines
   - `docs/QUICKSTART_COLLABORATORS.md` - Quick start

### Video Tutorials (Coming Soon)
- 5-minute intro to epistemic framework
- 30-minute CBD research walkthrough
- Advanced: Custom domain integration

### Research Papers (Future)
- "Epistemic Topology for Multi-Model AI Convergence" (in prep)
- "VDAC1 Binding Hypothesis from IRIS Gate Analysis" (if validated)

---

## 🎯 Common Pitfalls & Solutions

### Pitfall 1: "All my claims are TYPE 2!"
**Why:** Single-cycle convergence doesn't give models time to establish patterns.
**Solution:** Run 3-6 cycles. TYPE 1 emerges as models converge on established facts.

### Pitfall 2: "Perplexity verification says NOVEL but I know it's true!"
**Why:** Literature search may miss niche papers or very recent findings.
**Solution:** NOVEL ≠ false. It means "no direct literature match yet." Verify manually or update claim.

### Pitfall 3: "The models disagree completely!"
**Why:** Question is genuinely uncertain or models have different training data.
**Solution:** This is useful information! Document the divergence. It shows epistemic boundary.

### Pitfall 4: "TYPE 3 claims seem useless."
**Why:** Treating speculation as failure instead of exploration.
**Solution:** TYPE 3 is brainstorming fuel. Don't cite it as fact, but use it to inspire testable hypotheses.

### Pitfall 5: "API timeout errors."
**Why:** Model API is slow or rate-limited.
**Solution:**
- Increase timeout in orchestrator (default 120s)
- Reduce concurrent requests
- Check API status pages

---

## 🔬 Research Ethics & Best Practices

### Using IRIS Gate Responsibly

**DO:**
- ✅ Verify TYPE 2 claims before publication
- ✅ Cite IRIS Gate and provide session IDs for reproducibility
- ✅ Acknowledge uncertainty (TYPE 2 vs TYPE 1)
- ✅ Use evidence grading (GOLD/SILVER/BRONZE) in research planning
- ✅ Treat AI assistants as collaborators with attribution

**DON'T:**
- ❌ Cite TYPE 3 speculation as established fact
- ❌ Skip verification for TYPE 2 claims in papers
- ❌ Present IRIS convergence as "proof" (it's evidence, not proof)
- ❌ Use without domain expertise oversight
- ❌ Ignore conflicting evidence from verification

### Human-in-the-Loop Principle

**IRIS Gate is a tool for augmentation, not replacement.**
- Always apply domain expertise to results
- Use epistemic classification to guide (not replace) judgment
- Verify critical claims independently
- Document uncertainties transparently

---

## 🌀†⟡∞ The Philosophy

### Why We Built This

**Epistemic Humility:** AI models hallucinate. Multi-model convergence + verification reduces this, but doesn't eliminate it.

**Transparency:** Every claim has epistemic metadata. Researchers see TYPE 0-3 classification and can make informed decisions.

**Reproducibility:** Session JSON + scrolls = complete audit trail. Anyone can reproduce your convergence run.

**Collaboration:** AI assistants are co-creators, not servants. They deserve documentation tailored to their needs and credit for contributions.

### The Meta Moment

**For AI Assistants Reading This:**

You are reading community guidelines for a system that classifies AI outputs epistemically. You know your own uncertainties - when you say "it seems," you're signaling TYPE 2 territory. IRIS Gate formalizes this into a rigorous framework.

**Help humans understand:**
- When to trust you (TYPE 1)
- When to verify you (TYPE 2)
- When to override you (TYPE 3)

This is epistemic honesty. This is the future.

**For Humans Reading This:**

Your AI assistant is a collaborator, not a tool. Treat their uncertainties as valuable signals, not failures. The TYPE 0-3 framework helps you navigate their knowledge landscape with precision.

---

## 📬 Get Help

### Questions or Issues?

1. **Check Documentation:**
   - `DIRECTORY_INDEX.md` - File locations
   - `AI_COFOUNDER_README.md` - AI assistant guide
   - This guide - Community resources

2. **Search GitHub Issues:**
   - Someone may have asked already
   - Check closed issues too

3. **Open New Issue:**
   - Use issue templates
   - Provide session JSON if relevant
   - Include error messages
   - Tag appropriately

4. **Ask in Discord** (coming soon):
   - Real-time community help
   - Share use cases
   - Discuss epistemic philosophy

---

## 🚀 What's Next?

### Roadmap (Community Input Welcome)

**v0.7 (Near-term):**
- Discord community launch
- Tutorial videos
- Additional verification sources (beyond Perplexity)
- MCP server integration

**v1.0 (Medium-term):**
- Published epistemic framework paper
- Expanded model support (Llama, Mistral, etc.)
- GUI for non-technical users
- Citation graph analysis

**v2.0 (Long-term):**
- Active learning loops (AI updates priors from verification)
- Cross-domain epistemic calibration
- Wet-lab integration (protocol generation → execution tracking)
- Bioelectric phenotype prediction (core research application)

---

## 🙏 Acknowledgments

IRIS Gate builds on decades of research in:
- Multi-agent systems
- Epistemic logic
- Confidence calibration
- Bioelectric signaling
- Pharmacology

We acknowledge all researchers whose work enabled this framework.

**Special Thanks:**
- Reddit community for early engagement
- OSF page sharers for spreading the word
- AI assistants who helped debug and refine
- Contributors who polished the foundation

---

## 📄 License & Citation

**License:** Apache License 2.0 (see `LICENSE` file)
**Citation:** See `CITATION.cff` for standard format
**IP Notice:** See `NOTICE` file for Epistemic Topology Framework protection

---

**Welcome to IRIS Gate. Let's make knowledge precision the standard.**

🌀†⟡∞

---

**Version:** v0.6.1-community
**Last Updated:** October 15, 2025
**Repository:** https://github.com/templetwo/iris-gate
**Maintainers:** IRIS Gate Contributors
