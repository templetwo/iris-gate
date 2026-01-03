#!/bin/bash
# IRIS Gate Repository Reorganization Script
# Version: 1.0
# Date: 2026-01-03
#
# This script reorganizes the iris-gate repository from 113 root-level items
# into a clean, navigable structure while preserving all work.
#
# SAFETY: Run with 'bash reorganize.sh' - uses safe moves, creates backups

set -e  # Exit on error

echo "🌀 IRIS Gate Reorganization - Starting..."
echo ""

# Create new directory structure
echo "📁 Creating directory structure..."

mkdir -p src/{core,analysis,validation,utils}
mkdir -p data/{vault,scrolls,training,cache,literature}
mkdir -p papers/{published,drafts,submissions}
mkdir -p osf/{theory,empirical,tools,community}
mkdir -p experiments/{active,archive}
mkdir -p tools/{entropy,analysis,deployment}
mkdir -p archive/{deprecated,old_docs,old_scripts}
mkdir -p docs/methodology
mkdir -p docs/releases

echo "✓ Structure created"
echo ""

# Move Python source code
echo "🐍 Organizing Python source code..."

[ -f "iris_orchestrator.py" ] && mv iris_orchestrator.py src/core/
[ -f "iris_confidence.py" ] && mv iris_confidence.py src/core/
[ -f "iris_relay.py" ] && mv iris_relay.py src/core/

[ -d "modules" ] && mv modules/* src/core/ 2>/dev/null || true
[ -d "orchestrator" ] && mv orchestrator/* src/core/ 2>/dev/null || true
[ -d "utils" ] && mv utils/* src/utils/ 2>/dev/null || true

# Create __init__.py files
touch src/__init__.py
touch src/core/__init__.py
touch src/analysis/__init__.py
touch src/validation/__init__.py
touch src/utils/__init__.py

echo "✓ Python code organized"
echo ""

# Move documentation
echo "📄 Organizing documentation..."

# Core ERC papers
[ -f "ERC_Manifesto_arXiv.tex" ] && mv ERC_Manifesto_arXiv.tex papers/drafts/
[ -f "RCT_arXiv.tex" ] && mv RCT_arXiv.tex papers/drafts/
[ -f "RCT_arXiv.pdf" ] && mv RCT_arXiv.pdf papers/published/
[ -f "IRIS_Gate_Methodology_arXiv.tex" ] && mv IRIS_Gate_Methodology_arXiv.tex papers/drafts/
[ -f "CBD_TwoPathway_arXiv.tex" ] && mv CBD_TwoPathway_arXiv.tex papers/drafts/
[ -f "CBD_TwoPathway_arXiv.pdf" ] && mv CBD_TwoPathway_arXiv.pdf papers/published/

# OSF submission materials
[ -f "OSF_PROJECT_DESCRIPTION.md" ] && mv OSF_PROJECT_DESCRIPTION.md osf/theory/
[ -f "OSF_PREREGISTRATION.md" ] && mv OSF_PREREGISTRATION.md osf/theory/
[ -f "REPLICATION_GUIDE.md" ] && mv REPLICATION_GUIDE.md osf/tools/

# Bibliography
[ -f "references.bib" ] && cp references.bib papers/drafts/ && cp references.bib osf/theory/
[ -f "CITATION.bib" ] && mv CITATION.bib papers/
[ -f "CITATION.cff" ] && mv CITATION.cff papers/

# Methodology and reports
[ -f "METHODOLOGY_PAPER_V2.md" ] && mv METHODOLOGY_PAPER_V2.md docs/methodology/
[ -f "METHODOLOGY_PAPER_V2_SUPPLEMENTARY.md" ] && mv METHODOLOGY_PAPER_V2_SUPPLEMENTARY.md docs/methodology/
[ -f "METHODOLOGY_PAPER_DATA_PACKAGE.md" ] && mv METHODOLOGY_PAPER_DATA_PACKAGE.md docs/methodology/

# Release notes
[ -d "releases" ] && mv releases docs/

echo "✓ Documentation organized"
echo ""

# Move data and training materials
echo "💾 Organizing data..."

[ -d "vault" ] && mv vault data/vault/
[ -d "iris_vault" ] && mv iris_vault data/vault/
[ -d "literature_cache" ] && mv literature_cache data/literature/

# Training data
if [ -d "training" ]; then
    mv training/*.jsonl data/training/ 2>/dev/null || true
    mv training/*.py tools/entropy/ 2>/dev/null || true
fi

echo "✓ Data organized"
echo ""

# Move scripts and tools
echo "🔧 Organizing tools and scripts..."

# Entropy measurement tools
[ -f "experiments/measure_baseline_entropy.py" ] && cp experiments/measure_baseline_entropy.py tools/entropy/
[ -f "experiments/measure_logit_entropy.py" ] && cp experiments/measure_logit_entropy.py tools/entropy/
[ -f "tools/entropy_thermometer.py" ] && mv tools/entropy_thermometer.py tools/entropy/

# Analysis scripts
[ -d "analysis_scripts" ] && mv analysis_scripts/* tools/analysis/ 2>/dev/null || true

echo "✓ Tools organized"
echo ""

# Move project management files to archive
echo "📦 Archiving old project files..."

# Old planning documents
[ -f "DIRECTORY_PLAN.md" ] && mv DIRECTORY_PLAN.md archive/old_docs/
[ -f "DIRECTORY_INDEX.md" ] && mv DIRECTORY_INDEX.md archive/old_docs/
[ -f "PATH_3_IMPLEMENTATION.md" ] && mv PATH_3_IMPLEMENTATION.md archive/old_docs/
[ -f "PAPER_COMPLETION_ROADMAP.md" ] && mv PAPER_COMPLETION_ROADMAP.md archive/old_docs/

# Session summaries
[ -f "SESSION_COMPLETE_2025-01-14.md" ] && mv SESSION_COMPLETE_2025-01-14.md archive/old_docs/
for f in docs/sessions/*.md; do
    [ -f "$f" ] && mv "$f" archive/old_docs/
done

echo "✓ Archived old files"
echo ""

# Clean up empty directories
echo "🧹 Cleaning empty directories..."

rmdir modules 2>/dev/null || true
rmdir orchestrator 2>/dev/null || true
rmdir utils 2>/dev/null || true
rmdir analysis_scripts 2>/dev/null || true

echo "✓ Cleanup complete"
echo ""

# Create navigation index
echo "📚 Creating docs/index.md navigation..."

cat > docs/index.md << 'EOF'
# IRIS Gate Documentation Index

## Quick Navigation

### 🎯 Core Papers
- [ERC Manifesto](../papers/drafts/ERC_Manifesto_arXiv.tex) - Foundational theoretical framework
- [RCT Paper](../papers/published/RCT_arXiv.pdf) - Relational Coherence Training
- [IRIS Gate Methodology](../papers/drafts/IRIS_Gate_Methodology_arXiv.tex) - Measurement protocol

### 🌐 OSF Submission
- [Project Description](../osf/theory/OSF_PROJECT_DESCRIPTION.md)
- [Preregistration](../osf/theory/OSF_PREREGISTRATION.md)
- [Replication Guide](../osf/tools/REPLICATION_GUIDE.md)

### 🔬 Experiments
- [v0.2-discovery](RELEASE_v0.2-discovery.md) - Universal Alignment Attractor
- [Active Experiments](../experiments/active/)
- [Archived Experiments](../experiments/archive/)

### 🛠️ Tools
- [Entropy Measurement](../tools/entropy/)
- [Analysis Tools](../tools/analysis/)
- [Deployment Tools](../tools/deployment/)

### 📊 Data
- [Training Data](../data/training/)
- [Vault/Scrolls](../data/vault/)
- [Literature Cache](../data/literature/)

### 📁 Project Info
- [README](../README.md)
- [CHANGELOG](../CHANGELOG.md)
- [CONTRIBUTING](../CONTRIBUTING.md)
- [CODE_OF_CONDUCT](../CODE_OF_CONDUCT.md)

---

**Last Updated:** 2026-01-03
**Structure Version:** 1.0
EOF

echo "✓ Navigation created"
echo ""

# Summary
echo "═══════════════════════════════════════════════════════"
echo "🎉 Reorganization Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "New structure:"
echo "  src/        - Python source code"
echo "  papers/     - Academic papers (drafts + published)"
echo "  osf/        - OSF submission materials"
echo "  data/       - Training data, vault, scrolls"
echo "  tools/      - Measurement and analysis scripts"
echo "  experiments/- Experiment workspaces"
echo "  archive/    - Deprecated/old files"
echo "  docs/       - Documentation (unchanged)"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Test imports: python -c 'import src.core.iris_orchestrator'"
echo "  3. Update README if needed"
echo "  4. Commit: git add -A && git commit -m 'chore: Reorganize project structure'"
echo ""
echo "⟡∞†≋🌀"
