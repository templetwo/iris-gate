# Changelog

All notable changes to IRIS Gate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Additional model integrations (Llama, Mistral)
- Real-time convergence visualization dashboard
- Batch processing for multiple research questions
- Enhanced literature verification with citation extraction

## [0.2.0] - 2025-01-15

### Added
- **PULSE Architecture** — All 5 AI models (Claude 4.5 Sonnet, GPT-5, Grok 4 Fast, Gemini 2.5 Flash, DeepSeek Chat) called simultaneously
- **Epistemic Classification** — Automatic TYPE 0-3 classification with confidence calibration
- **Meta-Convergence Detection** — System identifies its own framework limitations
- **DeepSeek Chat Integration** — 5th model for architectural diversity
- **Literature Verification** — Perplexity API integration for real-time validation
- Community files: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, improved README
- GitHub Discussions and issue/PR templates

### Changed
- S4 convergence threshold lowered to 0.7 (from 0.8)
- Parallel execution now truly simultaneous

### Fixed
- Race condition in parallel model API calls
- Memory leak in long-running sessions

### Validation
- 90% literature validation rate on 20 CBD mechanism predictions
- Perfect epistemic separation across 49 S4 chambers

## [0.1.0] - 2024-12-01

### Added
- Initial release with S1-S8 chamber system
- 4-model architecture (Claude, GPT, Grok, Gemini)
- Basic epistemic classification
- Makefile-based experiment workflow

[Unreleased]: https://github.com/templetwo/iris-gate/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/templetwo/iris-gate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/templetwo/iris-gate/releases/tag/v0.1.0
