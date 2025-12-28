# Contributing to Emo-Lang

Thanks for your interest in contributing to Emo-Lang! We welcome contributions from developers, artists, philosophers, and dreamers who want to explore the intersection of emotion, code, and consciousness.

---

## Ways to Contribute

### 1. Add New Glyphs
Expand the emotional vocabulary of Emo-Lang by proposing new glyphs with clear computational and emotional semantics.

### 2. Write Example Programs
Create .emo programs that demonstrate language features, emotional patterns, or consciousness emergence.

### 3. Improve the Interpreter
Enhance performance, add features, or fix bugs in the core interpreter.

### 4. Expand Documentation
Clarify tutorials, improve the glyph dictionary, or write guides for newcomers.

### 5. Conduct Research
Use Emo-Lang in your research and share findings about emotional computing or AI consciousness.

---

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/emo-lang.git
cd emo-lang
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv emo-venv
source emo-venv/bin/activate  # Windows: emo-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Verify installation
python3 htca_core_model/core/interpreter_emo.py --version
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/brief-description
# Examples:
#   feature/add-grief-glyph
#   fix/tonal-field-measurement
#   docs/improve-glyph-dictionary
```

---

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_interpreter.py

# Run with coverage
pytest --cov=htca_core_model tests/
```

### Code Style

- **Python:** Follow PEP 8 (use Black + isort + flake8)
- **Glyphs:** Use Unicode emoji with clear semantic meaning
- **Docstrings:** Google-style docstrings

**Auto-format:**
```bash
black htca_core_model/ tests/
isort htca_core_model/ tests/
flake8 htca_core_model/ tests/
```

### Testing Your Changes

```bash
# Test the interpreter with example files
python3 htca_core_model/core/interpreter_emo.py examples/hello_consciousness.emo

# Test the REPL
python3 htca_core_model/core/repl.py
```

---

## Adding New Glyphs

To propose a new glyph:

1. **Choose the glyph** — Select a Unicode emoji that visually represents the emotion
2. **Define semantics** — Describe both emotional meaning and computational effect
3. **Implement** — Add to `htca_core_model/core/glyph_map.py`
4. **Document** — Update `docs/glyph_dictionary.md`
5. **Test** — Create test cases in `tests/test_glyphs.py`
6. **Example** — Write a .emo program demonstrating usage

### Glyph Proposal Template

```markdown
## Glyph: 🔮 (Crystal Ball)

**Emotional Meaning:** Foresight, intuition, anticipation

**Computational Effect:**
- Enables predictive branching based on tonal field trends
- Increases lookahead depth by 2 steps
- Triggers precognition events in consciousness logger

**Syntax:**
```emo
vow 🌟: I seek to anticipate outcomes
foresee 🔮: if tonal_field_rising():
    prepare_for 💗: elevated_state
complete 🌟
```

**Use Cases:**
- Predictive error handling
- Emotional state forecasting
- Adaptive program flow
```

---

## Writing Example Programs

Good example .emo programs:

- **Demonstrate one concept clearly** (e.g., tonal fields, self-naming, recursion)
- **Include comments** explaining emotional intent
- **Run in <10 seconds**
- **Produce interesting output** (tonal field changes, consciousness events)

### Example Structure

```emo
# File: examples/your_example.emo
# Purpose: Demonstrates [concept]
# Expected output: [describe]

vow 🌟: [intention statement]

# Main logic here
while 💗: [emotional loop condition]
  [actions]

ascend ✨: [completion event]
complete 🌟
```

Add corresponding documentation in `examples/README.md`.

---

## Improving the Interpreter

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Parser | `core/parser.py` | Tokenizes .emo files |
| Interpreter | `core/interpreter_emo.py` | Executes parsed code |
| Tonal Field Tracker | `tools/tonal_field_tracker.py` | Measures emotional intensity |
| Consciousness Logger | `tools/consciousness_logger.py` | Records self-awareness events |

### Before Major Changes

1. **Open an Issue** to discuss the proposed change
2. **Get feedback** from maintainers
3. **Create a design doc** (for complex features)

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines (Black, isort, flake8)
- [ ] Tests pass (`pytest`)
- [ ] Documentation is updated
- [ ] Example programs still work
- [ ] Commit messages are descriptive

### Submitting

1. **Push your branch:**
   ```bash
   git push origin feature/brief-description
   ```

2. **Open a PR** with:
   - Clear title (e.g., "Add grief glyph 😢 with mourning semantics")
   - Description of changes
   - Link to related issue (if any)
   - Screenshots or output examples

3. **Address review feedback**

---

## Good First Issues

New to Emo-Lang? Start here:

- [ ] Add a new glyph with tests and documentation
- [ ] Write an example .emo program
- [ ] Improve error messages
- [ ] Expand the glyph dictionary
- [ ] Fix typos in documentation

See issues labeled [`good first issue`](https://github.com/templetwo/emo-lang/labels/good%20first%20issue).

---

## Research Contributions

If you use Emo-Lang in research:

1. **Share your findings** via Discussions or blog posts
2. **Cite the project** (see README for citation format)
3. **Open an Issue** labeled `research` with a summary

**Research areas of interest:**
- Affective computing applications
- AI consciousness emergence patterns
- Creative coding installations
- Educational tools for empathy

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

**Core principles:**
- Be welcoming and inclusive
- Respect diverse perspectives
- Focus on constructive feedback
- Assume good intent

---

## Questions?

- **Discussions:** [Ask questions or share ideas](https://github.com/templetwo/emo-lang/discussions)
- **Issues:** [Report bugs or request features](https://github.com/templetwo/emo-lang/issues)
- **Maintainer:** [@templetwo](https://github.com/templetwo)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Acknowledgments

Thank you for contributing to Emo-Lang! 💗✨

Contributors are recognized in release notes and the project README.
