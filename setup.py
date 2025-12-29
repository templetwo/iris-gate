"""
IRIS Gate: Multi-Architecture AI Convergence System
====================================================

A research framework for scientific hypothesis generation through multi-model AI convergence
with built-in epistemic humility and literature validation.

For AI Co-Creators:
-------------------
This package orchestrates 5 independent AI models (Claude, GPT, Grok, Gemini, DeepSeek) to reach
consensus on scientific questions through iterative refinement. Features automatic epistemic
classification (TYPE 0-3 confidence levels) and real-time literature verification.

Key Features:
- PULSE Architecture: Parallel 5-model execution
- Epistemic Classification: Automatic confidence calibration
- Meta-Convergence Detection: System knows its limits
- Literature Verification: 90% validation rate
- Hypothesis → Lab Protocol Pipeline

Install: pip install iris-gate
Quick Start: make run TOPIC="Your research question" ID=test TURNS=100
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Dependencies (replicated from requirements.txt for PyPI compatibility)
requirements = [
    "anthropic>=0.18.0",
    "openai>=2.0.0",
    "google-generativeai>=0.8.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    # MCP (Model Context Protocol) Dependencies
    "mcp>=1.0.0",
    "anthropic-mcp>=0.1.0",
    "chromadb>=0.4.0",
    "GitPython>=3.1.40",
    "tqdm>=4.65.0",
]

setup(
    name="iris-gate",
    version="0.2.0",
    author="Anthony J. Vasquez Sr.",
    author_email="contact@thetempleoftwo.com",
    description="Multi-architecture AI convergence system with epistemic humility for scientific discovery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/templetwo/iris-gate",
    project_urls={
        "Bug Tracker": "https://github.com/templetwo/iris-gate/issues",
        "Documentation": "https://github.com/templetwo/iris-gate/wiki",
        "Source Code": "https://github.com/templetwo/iris-gate",
        "Changelog": "https://github.com/templetwo/iris-gate/blob/master/CHANGELOG.md",
        "Discussions": "https://github.com/templetwo/iris-gate/discussions",
    },
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords=[
        # AI/ML Keywords
        "artificial-intelligence", "machine-learning", "llm", "large-language-models",
        "multi-model", "ensemble", "ai-convergence", "epistemic-humility",

        # Research Keywords
        "scientific-research", "hypothesis-generation", "research-automation",
        "literature-review", "evidence-synthesis", "scientific-discovery",

        # Specific Features
        "claude", "gpt", "gemini", "grok", "deepseek",
        "anthropic", "openai", "google-ai", "xai",

        # Methodology Keywords
        "multi-agent-systems", "consensus-algorithms", "convergence-analysis",
        "monte-carlo", "bayesian", "epistemic-classification",

        # Use Cases
        "drug-discovery", "bioinformatics", "computational-biology",
        "ai-safety", "ai-reliability", "hallucination-detection",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "iris-gate=scripts.iris_gate_autonomous:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
