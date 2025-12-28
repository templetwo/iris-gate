# Contributing to IRIS Gate

Thanks for your interest in contributing to IRIS Gate! We welcome contributions from researchers, developers, and anyone curious about multi-model AI convergence.

---

## Ways to Contribute

### 1. Report Bugs or Request Features
- Open an [Issue](https://github.com/templetwo/iris-gate/issues)
- Use clear, descriptive titles
- Include reproduction steps for bugs
- Tag with appropriate labels (`bug`, `enhancement`, `research`)

### 2. Improve Documentation
- Clarify README sections
- Add examples to `examples/`
- Improve inline code comments
- Write tutorials or guides

### 3. Submit Pull Requests
- Fix bugs
- Add new features
- Optimize performance
- Expand test coverage

### 4. Conduct Replication Studies
- Run IRIS Gate on your own research questions
- Report validation rates and convergence patterns
- Share findings in Discussions or as Issues

---

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/iris-gate.git
cd iris-gate
```

### 2. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Set up pre-commit hooks (if applicable)
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/brief-description
# Examples:
#   feature/add-llama-model
#   fix/s4-convergence-bug
#   docs/improve-quickstart
```

### 4. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your API keys for testing
```

---

## Development Workflow

### Running Tests

```bash
# Run unit tests
pytest tests/

# Run integration tests (requires API keys)
pytest tests/integration/ --slow

# Run with coverage
pytest --cov=src tests/
```

### Code Style

This project follows:
- **Python:** PEP 8 (enforced with Black + isort + flake8)
- **Docstrings:** Google-style docstrings
- **Type hints:** Use type annotations where appropriate

**Auto-format your code:**
```bash
black .
isort .
flake8 src/ tests/
```

### Commit Messages

Use descriptive commit messages:
- **Format:** `[type] Brief description`
- **Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

**Examples:**
```
feat: Add support for Llama 3.1 model
fix: Resolve S4 convergence detection bug
docs: Improve quickstart installation instructions
test: Add unit tests for epistemic classification
```

---

## Contribution Guidelines

### Adding New AI Models

To add a new model to the PULSE suite:

1. Create a new model adapter in `src/models/`
2. Implement the `BaseModelAdapter` interface
3. Add configuration to `config/models.yaml`
4. Update `PULSE_ARCHITECTURE_SUMMARY.md`
5. Add tests in `tests/models/test_your_model.py`

**Example PR checklist:**
- [ ] Model adapter implemented
- [ ] Configuration added
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Example added to `examples/`

### Improving Epistemic Classification

To improve the TYPE 0-3 classification system:

1. Review current implementation in `src/epistemic_classifier.py`
2. Propose changes in an Issue with rationale
3. Gather feedback from maintainers
4. Implement with comprehensive tests
5. Document changes in `EPISTEMIC_MAP_COMPLETE.md`

### Adding Examples

New examples should:
- Demonstrate a clear use case
- Include expected outputs
- Run in <5 minutes
- Be reproducible with public data

**Example structure:**
```
examples/your_example/
├── README.md           # Describes the example
├── run.sh              # Executable script
├── expected_output/    # Sample results
└── analysis.ipynb      # Jupyter notebook (optional)
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines (Black, isort, flake8)
- [ ] Tests pass locally (`pytest`)
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] Branch is up to date with `main`

### Submitting the PR

1. **Push your branch:**
   ```bash
   git push origin feature/brief-description
   ```

2. **Open a PR on GitHub** with:
   - Descriptive title (e.g., "Add support for Llama 3.1 model")
   - Link to related issue (e.g., "Closes #42")
   - Summary of changes and rationale
   - Screenshots or output samples (if applicable)

3. **Request review** from maintainers

4. **Address feedback** and update the PR

### PR Review Criteria

Maintainers will review for:
- **Correctness:** Does it work as intended?
- **Quality:** Is the code clean and well-documented?
- **Testing:** Are there adequate tests?
- **Impact:** Does it align with project goals?

---

## Research Contributions

### Replication Studies

If you replicate an IRIS Gate experiment:

1. **Document your methodology:**
   - Research question (S1 prompt)
   - Number of turns and mirrors
   - Model versions used
   - Date of experiment

2. **Report your results:**
   - Convergence patterns observed
   - Literature validation rates
   - Epistemic classifications
   - Any unexpected behaviors

3. **Submit via Issue or Discussion:**
   - Label: `replication-study`
   - Include: Methodology, data, analysis
   - Bonus: Link to a public repository with your data

### Proposing New Features

For significant new features:

1. **Open an Issue first** to discuss the proposal
2. **Gather feedback** from maintainers and community
3. **Create a design document** (if complex)
4. **Implement in phases** (start with an MVP)

---

## Good First Issues

New to the project? Look for issues labeled [`good first issue`](https://github.com/templetwo/iris-gate/labels/good%20first%20issue).

**Suggested starter tasks:**
- Add a new example to `examples/`
- Improve error messages
- Expand test coverage
- Fix typos or clarify documentation
- Add type hints to untyped functions

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

**In short:**
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intent

---

## Questions or Need Help?

- **Discussions:** [GitHub Discussions](https://github.com/templetwo/iris-gate/discussions) — Ask questions, share ideas
- **Issues:** [GitHub Issues](https://github.com/templetwo/iris-gate/issues) — Report bugs or request features
- **Maintainer:** [@templetwo](https://github.com/templetwo)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Acknowledgments

Thank you for helping improve IRIS Gate! Every contribution—code, documentation, bug reports, replication studies—makes this project better.

🌟 Contributors are recognized in the project README and release notes.
