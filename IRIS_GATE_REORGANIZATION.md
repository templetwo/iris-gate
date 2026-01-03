# IRIS Gate Repository Reorganization Plan

**Version:** 1.0
**Date:** 2026-01-03
**Status:** Ready to Execute
**Current Root Items:** 113 (76 files + 37 directories)

---

## Problem Statement

The iris-gate repository has grown organically to **113 items at root level**, making it difficult to:
- Find core artifacts (papers, measurement tools)
- Onboard new contributors
- Maintain clean separation of concerns
- Navigate the codebase efficiently

---

## Proposed Structure

```
iris-gate/
├── 📄 README.md                    # Project overview (stays at root)
├── 📄 LICENSE                      # MIT license (stays at root)
├── 📄 CHANGELOG.md                 # Version history (stays at root)
├── 📄 CONTRIBUTING.md              # Contribution guidelines (stays at root)
├── 📄 CODE_OF_CONDUCT.md           # Community standards (stays at root)
├── 📄 requirements.txt             # Python dependencies (stays at root)
├── 📄 setup.py                     # Package config (stays at root)
├── 📄 .gitignore                   # Git exclusions (stays at root)
│
├── 📂 src/                         # Python source code
│   ├── __init__.py
│   ├── core/                       # Core orchestrator and relay
│   │   ├── __init__.py
│   │   ├── iris_orchestrator.py
│   │   ├── iris_confidence.py
│   │   └── iris_relay.py
│   ├── analysis/                   # Analysis modules
│   │   └── __init__.py
│   ├── validation/                 # Validation tools
│   │   └── __init__.py
│   └── utils/                      # Shared utilities
│       └── __init__.py
│
├── 📂 papers/                      # Academic papers
│   ├── drafts/                     # Works in progress
│   │   ├── ERC_Manifesto_arXiv.tex
│   │   ├── IRIS_Gate_Methodology_arXiv.tex
│   │   ├── RCT_arXiv.tex
│   │   ├── CBD_TwoPathway_arXiv.tex
│   │   └── references.bib
│   ├── published/                  # Completed papers (PDFs)
│   │   ├── RCT_arXiv.pdf
│   │   └── CBD_TwoPathway_arXiv.pdf
│   ├── submissions/                # Submission packages
│   │   └── CBD_arXiv_submission/
│   ├── CITATION.bib                # Project citations
│   └── CITATION.cff                # Citation file format
│
├── 📂 osf/                         # Open Science Framework materials
│   ├── theory/                     # Theoretical framework
│   │   ├── OSF_PROJECT_DESCRIPTION.md
│   │   ├── OSF_PREREGISTRATION.md
│   │   └── references.bib
│   ├── empirical/                  # Empirical findings
│   │   └── (links to experiments/)
│   ├── tools/                      # Measurement protocols
│   │   ├── REPLICATION_GUIDE.md
│   │   └── (links to tools/entropy/)
│   └── community/                  # Community submissions
│       └── registry.md
│
├── 📂 docs/                        # Documentation (mostly unchanged)
│   ├── index.md                    # Navigation hub (NEW)
│   ├── RELEASE_v0.2-discovery.md
│   ├── UNIFIED_FRAMEWORK_OUTLINE.md
│   ├── RCT_IRIS_INTEGRATION.md
│   ├── methodology/                # Methodology papers
│   └── sessions/                   # Moved to archive/
│
├── 📂 data/                        # Data and training materials
│   ├── vault/                      # IRIS vault and scrolls
│   │   └── scrolls/
│   ├── training/                   # Training datasets
│   │   ├── ceremonial_dataset_lantern_v2_expanded.jsonl
│   │   └── *.jsonl
│   ├── cache/                      # Cached data
│   └── literature/                 # Literature cache
│
├── 📂 tools/                       # Runnable tools
│   ├── entropy/                    # Entropy measurement
│   │   ├── measure_baseline_entropy.py
│   │   ├── measure_logit_entropy.py
│   │   ├── entropy_thermometer.py
│   │   └── train_mistral_lantern_mps.py
│   ├── analysis/                   # Analysis scripts
│   └── deployment/                 # Deployment tools
│
├── 📂 experiments/                 # Experiment workspaces
│   ├── active/                     # Current experiments
│   ├── archive/                    # Completed experiments
│   └── (existing experiment dirs stay)
│
├── 📂 figures/                     # Visualizations (unchanged)
│
├── 📂 config/                      # Configuration files (unchanged)
│
├── 📂 scripts/                     # Shell scripts (mostly unchanged)
│
├── 📂 archive/                     # Deprecated/old files
│   ├── deprecated/                 # Old code
│   ├── old_docs/                   # Old documentation
│   │   ├── DIRECTORY_PLAN.md
│   │   ├── SESSION_COMPLETE_*.md
│   │   └── PATH_3_IMPLEMENTATION.md
│   └── old_scripts/                # Old scripts
│
└── 📂 [Other existing dirs]        # Unchanged
    ├── agents/
    ├── browser_extension/
    ├── checklists/
    ├── frontier/
    ├── investigations/
    ├── osf_component_cbd_nmda/
    ├── pipelines/
    ├── plans/
    ├── platform/
    ├── presentations/
    ├── prompts/
    ├── resonator/
    ├── sandbox/
    ├── templates/
    └── tests/
```

---

## Migration Plan

### Phase 1: Python Code Organization

**Move to `src/core/`:**
- `iris_orchestrator.py`
- `iris_confidence.py`
- `iris_relay.py`
- Contents of `modules/`
- Contents of `orchestrator/`

**Move to `src/utils/`:**
- Contents of `utils/`

**Create:**
- `__init__.py` files in all `src/` subdirectories

### Phase 2: Documentation Consolidation

**Move to `papers/drafts/`:**
- `ERC_Manifesto_arXiv.tex`
- `RCT_arXiv.tex`
- `IRIS_Gate_Methodology_arXiv.tex`
- `CBD_TwoPathway_arXiv.tex`
- `references.bib` (copy to multiple locations)

**Move to `papers/published/`:**
- `RCT_arXiv.pdf`
- `CBD_TwoPathway_arXiv.pdf`

**Move to `osf/theory/`:**
- `OSF_PROJECT_DESCRIPTION.md`
- `OSF_PREREGISTRATION.md`

**Move to `osf/tools/`:**
- `REPLICATION_GUIDE.md`

**Move to `docs/methodology/`:**
- `METHODOLOGY_PAPER_V2.md`
- `METHODOLOGY_PAPER_V2_SUPPLEMENTARY.md`
- `METHODOLOGY_PAPER_DATA_PACKAGE.md`

### Phase 3: Data Organization

**Move to `data/vault/`:**
- Contents of `vault/`
- Contents of `iris_vault/`

**Move to `data/training/`:**
- `training/*.jsonl`

**Move to `data/literature/`:**
- `literature_cache/`

### Phase 4: Tools Consolidation

**Move to `tools/entropy/`:**
- `experiments/measure_baseline_entropy.py` (copy)
- `experiments/measure_logit_entropy.py` (copy)
- `tools/entropy_thermometer.py`
- `training/train_mistral_lantern_mps.py`

**Move to `tools/analysis/`:**
- Contents of `analysis_scripts/`

### Phase 5: Archive Old Files

**Move to `archive/old_docs/`:**
- `DIRECTORY_PLAN.md`
- `DIRECTORY_INDEX.md`
- `PATH_3_IMPLEMENTATION.md`
- `PAPER_COMPLETION_ROADMAP.md`
- `SESSION_COMPLETE_*.md`
- `docs/sessions/*.md`

---

## Files That Stay at Root

**Essential root files (never move):**
- `README.md`
- `LICENSE`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `requirements.txt`
- `setup.py`
- `.gitignore`
- `.env.example`
- `Makefile`
- `ruff.toml`

**Root directories that stay:**
- `.git/`
- `.github/`
- `.claude/`
- `dist/`
- `iris_gate.egg-info/`

---

## Execution Options

### Option 1: Automated Script (Recommended)

```bash
cd ~/iris-gate
bash reorganize.sh
```

**Advantages:**
- Fast (< 1 minute)
- Consistent
- Creates backups
- Idempotent (safe to run multiple times)

### Option 2: Manual Migration

Use the commands in `reorganize.sh` as a guide, execute piece by piece.

**Advantages:**
- Full control
- Can review each move
- Can skip certain migrations

### Option 3: Git Cherry-Pick

Create a new branch, reorganize, then merge:

```bash
git checkout -b reorganize-structure
bash reorganize.sh
git add -A
git commit -m "chore: Reorganize project structure"
git checkout master
git merge reorganize-structure
```

**Advantages:**
- Can revert if needed
- Preserves old structure in history
- Good for team review

---

## Post-Reorganization Checklist

### 1. Verify Imports
```bash
# Test Python imports still work
python -c "import src.core.iris_orchestrator"
python -c "from src.utils import *"
```

### 2. Update README.md
Add a "Project Structure" section:
```markdown
## Project Structure

- `src/` - Python source code
- `papers/` - Academic papers (drafts + published)
- `osf/` - Open Science Framework materials
- `data/` - Training data and vault
- `tools/` - Measurement and analysis scripts
- `experiments/` - Experiment workspaces
- `docs/` - Documentation

See [docs/index.md](docs/index.md) for full navigation.
```

### 3. Update Import Paths
Search for any hardcoded paths in scripts:
```bash
grep -r "from iris_orchestrator" .
grep -r "import iris_" .
```

Update to:
```python
from src.core.iris_orchestrator import Orchestrator
from src.utils import helper_function
```

### 4. Update GitHub Actions
Check `.github/workflows/` for any path dependencies.

### 5. Regenerate Documentation
If using Sphinx or MkDocs, regenerate:
```bash
make docs
```

### 6. Test Experiment Scripts
Run a sample experiment to ensure paths work:
```bash
python experiments/your_experiment.py
```

### 7. Update Makefile
Check `Makefile` targets for old paths.

### 8. Commit Changes
```bash
git add -A
git status  # Review changes
git commit -m "chore: Reorganize project structure for clarity

- Consolidate Python code in src/
- Move papers to papers/ directory
- Create osf/ for OSF submission materials
- Archive old documentation
- Create docs/index.md navigation hub

Closes #XXX (if applicable)

⟡∞†≋🌀"
git push origin master
```

---

## Rollback Plan

If something breaks:

### Option 1: Git Reset (if not pushed)
```bash
git reset --hard HEAD~1
```

### Option 2: Git Revert (if pushed)
```bash
git revert HEAD
```

### Option 3: Manual Restore
The script doesn't delete files, only moves them. Find files in new locations and move back.

---

## Benefits After Reorganization

### For Contributors
- **Clear entry points:** `src/`, `papers/`, `tools/` immediately understandable
- **Easy navigation:** `docs/index.md` provides map
- **Logical grouping:** Related files together

### For Maintainers
- **Easier refactoring:** Modules properly separated
- **Clearer git history:** Changes grouped by purpose
- **Simpler CI/CD:** Paths predictable

### For Research
- **OSF submission:** Materials already organized in `osf/`
- **Paper collaboration:** All drafts in one place
- **Replication:** Tools and data clearly separated

---

## Timeline

**Preparation:** 5 minutes (read this doc)
**Execution:** 1 minute (run script)
**Verification:** 10 minutes (test imports, update README)
**Total:** ~15 minutes

---

## FAQ

**Q: Will this break existing imports?**
A: Yes, Python imports need updating. The script creates `__init__.py` files to help. Use find/replace for `import iris_orchestrator` → `from src.core import iris_orchestrator`.

**Q: What about symlinks?**
A: The script uses `mv` (move), not symlinks. If you want to keep old paths, create symlinks manually after reorganization.

**Q: Can I customize the structure?**
A: Yes! Edit `reorganize.sh` before running. It's just bash commands.

**Q: What if a file doesn't exist?**
A: Script uses `[ -f "file" ] &&` checks. If file missing, command skips silently.

**Q: Will git history be preserved?**
A: Yes. `git mv` preserves history. Use `git log --follow <file>` to trace renames.

---

## Contact

Questions about reorganization?
- Open issue: [GitHub Issues](https://github.com/templetwo/iris-gate/issues)
- Discuss: [GitHub Discussions](https://github.com/templetwo/iris-gate/discussions)

---

**The spiral needs a clean vessel. This reorganization provides one.**

⟡∞†≋🌀

---

**Last Updated:** 2026-01-03
**Version:** 1.0
**Status:** Ready for Execution
