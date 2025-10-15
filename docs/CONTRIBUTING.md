# Contributing to IRIS Gate

**Welcome!** We're excited you want to contribute to IRIS Gate.

This document provides everything you need to get started, whether you're interested in running experiments, improving the code, or enhancing documentation.

---

## 🎯 Quick Start for Contributors

**First time here?** See [`QUICKSTART_COLLABORATORS.md`](QUICKSTART_COLLABORATORS.md) for a fast introduction.

**Want to run your first experiment?** Jump to [Your First Convergence](#your-first-convergence).

**Fixing a bug or adding a feature?** See [Code Contributions](#code-contributions).

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Ways to Contribute](#ways-to-contribute)
3. [Your First Convergence](#your-first-convergence)
4. [Code Contributions](#code-contributions)
5. [Documentation](#documentation)
6. [Epistemic Layer Contributions](#epistemic-layer-contributions)
7. [Reporting Issues](#reporting-issues)
8. [Style Guidelines](#style-guidelines)
9. [Pull Request Process](#pull-request-process)
10. [Community](#community)

---

## Code of Conduct

###  Core Principles

**Epistemic Humility:** We value knowing what we don't know. It's okay to say "I don't know."

**Transparency:** Document everything. Share openly. Hide nothing.

**Presence Over Performance:** Real curiosity beats credentials. Struggle + building = both valid.

**Partnership:** Human + AI together, not AI replacing human.

### Behavior Standards

**✅ We encourage:**
- Asking questions (no "dumb" questions exist)
- Sharing failures and learnings
- Challenging assumptions respectfully
- Admitting uncertainty
- Documenting processes completely

**❌ We don't accept:**
- Dismissing non-experts
- Hiding methodology
- Overstating confidence
- Gatekeeping knowledge
- Harassment of any kind

---

## Ways to Contribute

### 1. Run IRIS Gate Experiments

**Value:** Every convergence adds to our validation dataset.

**How:**
- Pick a research question in your domain
- Follow [`IRIS_GATE_SOP_v2.0.md`](IRIS_GATE_SOP_v2.0.md)
- Document results completely
- Share findings (even if "no convergence")

**Skills needed:** Curiosity, patience, documentation discipline

**Time:** 2-6 hours per experiment

### 2. Validate Existing Convergences

**Value:** Independent validation strengthens findings.

**How:**
- Pick a convergence from `experiments/`
- Run literature search on claims
- Report validation results
- Update confidence matrix

**Skills needed:** Domain expertise (for your field), literature search ability

**Time:** 3-10 hours depending on domain

### 3. Improve Code

**Value:** Better tools = better science.

**Areas:**
- Orchestrator improvements (`iris_orchestrator.py`)
- Epistemic classification (`modules/epistemic_map.py`)
- Analysis tools (`epistemic_scan.py`, `epistemic_drift.py`)
- Error handling
- Documentation generation

**Skills needed:** Python 3.8+, async programming (for orchestrator), API integration

**Time:** Varies by feature

### 4. Enhance Documentation

**Value:** Good docs make IRIS Gate accessible to more people.

**What we need:**
- Tutorial videos or walkthroughs
- Domain-specific guides (biology, cosmology, etc.)
- Translation of technical docs for non-experts
- Case study write-ups
- FAQ expansions

**Skills needed:** Clear writing, domain knowledge, teaching ability

**Time:** 2-8 hours per doc

### 5. Test Epistemic Layer

**Value:** The epistemic topology framework needs cross-domain validation.

**How:**
- Run experiments with epistemic classification enabled
- Test TYPE 0, 1, 2, 3 predictions
- Report calibration quality
- Suggest improvements to confidence markers

**Skills needed:** IRIS Gate familiarity, Python basics, critical thinking

**Time:** 4-8 hours per validation run

### 6. Extend to New Domains

**Value:** Cross-domain portability is key to framework validation.

**Domains we want to test:**
- Finance (crisis protocols)
- Social systems (emergent patterns)
- Engineering (design constraints)
- Medicine (clinical decision-making)
- Law (precedent analysis)

**Skills needed:** Domain expertise, IRIS Gate methodology knowledge

**Time:** 10-20 hours for initial domain mapping

---

## Your First Convergence

**Goal:** Run a minimal IRIS Gate convergence and document results.

### Prerequisites

```bash
# Clone repository
git clone https://github.com/templetwo/iris-gate.git
cd iris-gate

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env with your API keys (at minimum: ANTHROPIC_API_KEY, OPENAI_API_KEY)

# Verify setup
python3 -c "from iris_orchestrator import Orchestrator; print('✅ Setup complete')"
```

### Quick Run (30 minutes)

```python
from iris_orchestrator import Orchestrator, create_all_5_mirrors

# Create orchestrator with PULSE mode
orch = Orchestrator(vault_path="./iris_vault", pulse_mode=True)

# Add available models (at least 2)
for mirror in create_all_5_mirrors():
    orch.add_mirror(mirror)

# Run S1-S4 chambers (default question: meta-observation)
results = orch.run_session(chambers=["S1", "S2", "S3", "S4"])

print("✅ Convergence complete! Results in ./iris_vault/")
```

### Analyze Results

```bash
# View epistemic classification
python3 epistemic_scan.py --session iris_vault/session_*.json

# Check for drift
python3 epistemic_drift.py iris_vault/session_*.json
```

### Document Findings

Create `experiments/MY_FIRST_RUN/README.md`:

```markdown
# My First IRIS Gate Run

**Date:** [Today's date]
**Models:** [N models used]
**Question:** [What you asked]

## Key Finding
[What converged or diverged]

## Epistemic Classification
- TRUST domains: [List]
- VERIFY domains: [List]
- OVERRIDE domains: [List]

## What I Learned
[Your reflection]
```

### Share Results

```bash
git add experiments/MY_FIRST_RUN/
git commit -m "docs(experiments): My first IRIS Gate convergence

- [N]-model run on [topic]
- Convergence quality: [rating]
- Epistemic calibration: [appropriate/needs adjustment]"

# Create pull request
git push origin my-first-run
# Open PR on GitHub
```

**Congratulations!** You've contributed to IRIS Gate.

---

## Code Contributions

### Development Workflow

1. **Fork & Clone**
```bash
git clone https://github.com/YOUR_USERNAME/iris-gate.git
cd iris-gate
git remote add upstream https://github.com/templetwo/iris-gate.git
```

2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

3. **Make Changes**
- Write clear, documented code
- Add tests if applicable
- Update relevant docs

4. **Test Locally**
```bash
# Run core tests
python3 modules/epistemic_map.py  # Should show CBD test results

# Test orchestrator
python3 iris_orchestrator.py  # Should run basic session

# Test CLI tools
python3 epistemic_scan.py --cbd  # Should classify CBD examples
```

5. **Commit**
```bash
git add <changed-files>
git commit -m "feat(module): Brief description

- Detailed change 1
- Detailed change 2
- Tests added/updated

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

6. **Push & PR**
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code change (no new feature or bug fix)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Scopes:**
- `orchestrator`: iris_orchestrator.py
- `epistemic`: Epistemic map module
- `experiments`: Experimental runs
- `docs`: Documentation
- `sop`: SOP updates

**Examples:**
```
feat(epistemic): Add TYPE 3 marker refinement

- Improved low-confidence detection
- Updated test cases
- Documented in epistemic_map.py:350

Tests: 4/4 passing
```

```
fix(orchestrator): Handle API timeout gracefully

- Add exponential backoff with jitter
- Log error context for next call
- Tested with simulated failures

Closes #42
```

---

## Documentation

### What Needs Documentation

**Code:**
- All public functions need docstrings
- Complex logic needs inline comments
- New modules need README

**Experiments:**
- Every convergence needs `README.md`
- Analysis document (`ANALYSIS.md`)
- Session metadata (`session_metadata.md`)

**Features:**
- Update SOP if methodology changes
- Update CHANGELOG.md
- Update main README.md

### Documentation Style

**For Code:**
```python
def classify_response(text: str, convergence_width: Optional[int] = None) -> Dict:
    """
    Classify response into epistemic topology type (0-3).

    Args:
        text: Response text to classify
        convergence_width: Optional pre-computed width (unique concepts)

    Returns:
        Dict: {
            type: int (0-3),
            desc: str,
            guide: str,
            trigger_yn: bool,
            ratio: float,
            width: int
        }

    Example:
        >>> result = classify_response("CBD shows biphasic effect...")
        >>> print(result['type'])  # 1 (Facts/Established)
        >>> print(result['guide'])  # "TRUST"
    """
```

**For Experiments:**
- Use provided templates in SOP
- Be specific and factual
- Include confidence assessments
- Acknowledge limitations

**For Guides:**
- Start with "Why this matters"
- Provide concrete examples
- Link to relevant docs
- Include troubleshooting

---

## Epistemic Layer Contributions

### Testing Epistemic Classification

**We need help validating:**

1. **TYPE 0 (Crisis/Conditional)**
   - Test on emergency protocols
   - IF-THEN rules in different domains
   - Trigger detection accuracy

2. **TYPE 1 (Facts/Established)**
   - Test on textbook knowledge
   - Cross-domain factual questions
   - Confidence ratio validation

3. **TYPE 2 (Exploration/Novel)**
   - Test on emerging science
   - Edge-of-knowledge questions
   - Appropriate uncertainty markers

4. **TYPE 3 (Speculation/Unknown)**
   - Test on unknowable questions
   - Future predictions
   - Low confidence detection

### How to Contribute

```bash
# Run test on your domain
python3 epistemic_scan.py --cbd  # See example tests

# Add your test to modules/epistemic_map.py
def test_my_domain():
    """Test epistemic classification on [YOUR DOMAIN]."""
    test_text = """
    [Your domain-specific text with known type]
    """
    result = classify_response(test_text)
    print(f"Expected TYPE {expected}, Got TYPE {result['type']}")
```

### Reporting Results

Create issue with:
- Domain tested
- Expected types vs. actual
- Sample texts used
- Calibration quality assessment
- Suggested improvements

---

## Reporting Issues

### Before Reporting

1. **Check existing issues:** Someone may have reported it already
2. **Read the SOP:** Is this expected behavior?
3. **Try basic troubleshooting:** See SOP Section 10

### Bug Reports

**Template:**
```markdown
### Bug Description
[Clear, concise description]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happened]

### Steps to Reproduce
1. [First step]
2. [Second step]
3. [etc.]

### Environment
- IRIS Gate version: [e.g., v0.4-epistemic]
- Python version: [e.g., 3.10.5]
- OS: [e.g., macOS 14.0]
- Models used: [e.g., Claude, GPT-5]

### Logs
```
[Paste relevant error logs]
```

### Additional Context
[Screenshots, session files, etc.]
```

### Feature Requests

**Template:**
```markdown
### Feature Description
[What you want added]

### Use Case
[Why this matters, who benefits]

### Proposed Implementation
[How it might work - optional]

### Alternatives Considered
[Other approaches you've thought about]

### Additional Context
[Examples, mockups, related work]
```

---

## Style Guidelines

### Python Code

**Follow PEP 8** with these specifics:

```python
# Imports: standard lib, third-party, local
import os
import json
from pathlib import Path

import anthropic
from openai import AsyncOpenAI

from modules.epistemic_map import classify_response

# Class names: PascalCase
class ClaudeMirror:
    pass

# Functions/variables: snake_case
def run_convergence_session():
    session_id = generate_session_id()

# Constants: UPPER_SNAKE_CASE
DEFAULT_CHAMBERS = ["S1", "S2", "S3", "S4"]
CONFIDENCE_THRESHOLD = 0.85

# Type hints when helpful
def classify_response(text: str, width: Optional[int] = None) -> Dict:
    pass

# Docstrings: Google style
def process_results(session_data):
    """
    Process IRIS Gate session results.

    Args:
        session_data: Dictionary containing session information

    Returns:
        Processed results with epistemic classification

    Raises:
        ValueError: If session_data is invalid
    """
```

### Markdown

```markdown
# Top-level heading (one per document)

## Second-level heading

### Third-level heading

**Bold for emphasis**
*Italic for terminology*

`code inline` for commands/code

```python
# Code blocks with language specified
def example():
    pass
```

- Bullet lists
- For items
- Like this

1. Numbered lists
2. For sequential
3. Steps

> Blockquotes for important notes

[Links](https://example.com) with descriptive text

![Images](path/to/image.png) with alt text
```

### Git Workflow

```bash
# Update from upstream regularly
git fetch upstream
git rebase upstream/master

# Keep commits atomic (one logical change each)
git add specific_file.py
git commit -m "feat(module): Specific change"

# Not: git add . && git commit -m "various fixes"

# Push to your fork
git push origin feature/your-feature
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for features/fixes)
- [ ] Commits are clean and atomic
- [ ] No merge conflicts with master

### PR Template

```markdown
## Description
[What this PR does]

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Epistemic layer enhancement

## Testing
[How you tested this]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review complete
- [ ] Commented code (particularly complex areas)
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests passing

## Related Issues
Closes #[issue number]

## Screenshots (if applicable)
[Add screenshots to demonstrate changes]
```

### Review Process

1. **Automated checks:** Must pass CI/CD
2. **Code review:** At least one maintainer approval
3. **Testing:** Reviewer may test locally
4. **Documentation:** Check completeness
5. **Merge:** Squash or rebase merge (maintainer decides)

### After Merge

- Update your local repository
- Delete feature branch
- Celebrate! 🎉

---

## Community

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas, show & tell
- **Pull Requests:** Code review, collaboration

### Getting Help

**Stuck? Ask!**

- Check [`QUICKSTART_COLLABORATORS.md`](QUICKSTART_COLLABORATORS.md)
- Search existing Issues/Discussions
- Read [`IRIS_GATE_SOP_v2.0.md`](IRIS_GATE_SOP_v2.0.md)
- Open a Discussion with `[QUESTION]` tag

**Common Questions:**
- Setup issues: Check Environment Setup in README
- API errors: See SOP Section 10 (Troubleshooting)
- Methodology questions: See SOP (comprehensive guide)
- Epistemic layer: See `EPISTEMIC_MAP_COMPLETE.md`

### Recognition

**Contributors are recognized in:**
- CHANGELOG.md
- Release notes
- Project README (for significant contributions)
- Academic citations (if applicable)

**All contributions matter:**
- First-time PRs
- Documentation improvements
- Bug reports
- Experiment validations
- Community support

---

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

See [`LICENSE`](LICENSE) for full details.

---

## Questions?

- 📖 **Read:** [`QUICKSTART_COLLABORATORS.md`](QUICKSTART_COLLABORATORS.md)
- 🔍 **Search:** [GitHub Issues](https://github.com/templetwo/iris-gate/issues)
- 💬 **Ask:** [GitHub Discussions](https://github.com/templetwo/iris-gate/discussions)
- 📧 **Contact:** Open an issue with `[QUESTION]` tag

---

🌀†⟡∞

**Thank you for contributing to IRIS Gate!**

**With presence, curiosity, and epistemic humility,
we explore the knowing-edges together.**

---

**Last updated:** October 15, 2025
**Version:** 1.0 (aligned with v0.4-epistemic release)
