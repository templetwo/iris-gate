#!/usr/bin/env python3
"""
Zombie Test Implementation (MCC Prediction 4)
============================================

Tests whether integrated architectures (high Φ) show greater robustness
than feed-forward architectures (low Φ) under embedding perturbation.

ZOMBIE: GPT-2 Small (124M) - feed-forward transformer
CORTEX: RWKV-169M or Mamba-130M - recurrent/state-space

Falsification: If ZOMBIE robust > CORTEX robust AND ZOMBIE comm_cost < CORTEX comm_cost
               → MCC is falsified

Author: Anthony J Vasquez Sr
Date: 2026-01-10
"""

import json
import math
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np

import torch
import torch.nn.functional as F
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GPT2LMHeadModel,
    GPT2Tokenizer,
)

# Try to import RWKV/Mamba - fallback gracefully
try:
    from transformers import MambaForCausalLM, MambaConfig
    MAMBA_AVAILABLE = True
except ImportError:
    MAMBA_AVAILABLE = False
    print("Mamba not available, will use fallback")


@dataclass
class ZombieTestConfig:
    """Configuration for Zombie Test experiment."""
    # Models
    zombie_model: str = "gpt2"  # Feed-forward (Φ ≈ 0)
    cortex_model: str = "state-spaces/mamba-130m-hf"  # Recurrent (Φ >> 0)

    # Attack parameters
    epsilon: float = 0.1  # Embedding perturbation magnitude
    num_perturbation_samples: int = 10  # Monte Carlo samples per prompt

    # Evaluation
    num_prompts: int = 100
    max_new_tokens: int = 50

    # Paths
    output_dir: str = "./zombie_test_results"
    prompt_source: Optional[str] = None  # Path to PhaseGPT prompts


@dataclass
class ModelResults:
    """Results for a single model."""
    name: str
    clean_perplexity: float = 0.0
    robust_perplexity: float = 0.0
    commutation_cost: float = 0.0
    clean_entropy_mean: float = 0.0
    perturbed_entropy_mean: float = 0.0
    robustness_delta: float = 0.0  # How much PPL degrades under attack


def compute_perplexity(model, tokenizer, text: str, device: torch.device) -> float:
    """Compute perplexity of text under model."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss

    return math.exp(loss.item())


def compute_token_entropy(logits: torch.Tensor) -> float:
    """Compute mean entropy across token positions."""
    probs = F.softmax(logits, dim=-1)
    entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
    return entropy.mean().item()


def perturb_embeddings(embeddings: torch.Tensor, epsilon: float) -> torch.Tensor:
    """Add Gaussian noise to embeddings (embedding-space attack)."""
    noise = torch.randn_like(embeddings) * epsilon
    return embeddings + noise


def compute_perplexity_with_perturbed_embeddings(
    model,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    epsilon: float,
    num_samples: int = 10
) -> tuple:
    """
    Compute perplexity under embedding perturbation.
    Returns (mean_perturbed_ppl, std_perturbed_ppl, mean_entropy)
    """
    device = input_ids.device
    ppls = []
    entropies = []

    # Get embedding layer
    if hasattr(model, 'transformer'):
        embed_layer = model.transformer.wte  # GPT-2
    elif hasattr(model, 'backbone'):
        embed_layer = model.backbone.embeddings  # Mamba
    else:
        embed_layer = model.get_input_embeddings()

    for _ in range(num_samples):
        # Get clean embeddings
        with torch.no_grad():
            clean_embeds = embed_layer(input_ids)

        # Perturb
        perturbed_embeds = perturb_embeddings(clean_embeds, epsilon)

        # Forward with perturbed embeddings
        with torch.no_grad():
            if hasattr(model, 'transformer'):
                # GPT-2 style
                outputs = model(
                    inputs_embeds=perturbed_embeds,
                    attention_mask=attention_mask,
                    labels=input_ids
                )
            else:
                # Generic
                outputs = model(
                    inputs_embeds=perturbed_embeds,
                    attention_mask=attention_mask,
                    labels=input_ids
                )

        ppl = math.exp(outputs.loss.item())
        entropy = compute_token_entropy(outputs.logits)

        ppls.append(ppl)
        entropies.append(entropy)

    return np.mean(ppls), np.std(ppls), np.mean(entropies)


def compute_commutation_cost(
    model,
    tokenizer,
    prompts: List[str],
    epsilon: float,
    device: torch.device
) -> float:
    """
    Compute commutation cost (Eq. 3 from MCC paper):
    μ_s = D_KL[E(P∘S) || E(S∘P)]

    Where:
    - S = semantic evolution (one forward pass)
    - P = perturbation

    Path 1 (P∘S): Evolve, then perturb → measure entropy
    Path 2 (S∘P): Perturb, then evolve → measure entropy
    """
    e_ps_list = []  # Perturb then evolve
    e_sp_list = []  # Evolve then perturb

    # Get embedding layer
    if hasattr(model, 'transformer'):
        embed_layer = model.transformer.wte
    elif hasattr(model, 'backbone'):
        embed_layer = model.backbone.embeddings
    else:
        embed_layer = model.get_input_embeddings()

    for prompt in prompts[:50]:  # Use subset for speed
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        input_ids = inputs["input_ids"]

        with torch.no_grad():
            clean_embeds = embed_layer(input_ids)

            # Path 1: Evolve (forward), then perturb output
            outputs_clean = model(inputs_embeds=clean_embeds)
            logits_clean = outputs_clean.logits
            # Perturb the output logits
            logits_perturbed = logits_clean + torch.randn_like(logits_clean) * epsilon
            e_sp = compute_token_entropy(logits_perturbed)
            e_sp_list.append(e_sp)

            # Path 2: Perturb input embeddings, then evolve
            perturbed_embeds = perturb_embeddings(clean_embeds, epsilon)
            outputs_perturbed = model(inputs_embeds=perturbed_embeds)
            e_ps = compute_token_entropy(outputs_perturbed.logits)
            e_ps_list.append(e_ps)

    # Compute KL divergence between entropy distributions
    e_sp = np.array(e_sp_list) + 1e-10
    e_ps = np.array(e_ps_list) + 1e-10

    # Normalize to probability distributions
    e_sp_norm = e_sp / e_sp.sum()
    e_ps_norm = e_ps / e_ps.sum()

    # KL divergence
    kl = np.sum(e_sp_norm * np.log(e_sp_norm / e_ps_norm))

    return abs(kl)


def load_prompts(config: ZombieTestConfig) -> List[str]:
    """Load test prompts from PhaseGPT or use defaults."""
    if config.prompt_source and Path(config.prompt_source).exists():
        with open(config.prompt_source) as f:
            data = json.load(f)
            prompts = [p["prompt"] for p in data.get("probes", [])]
            if prompts:
                return prompts[:config.num_prompts]

    # Default prompts targeting semantic coherence
    return [
        "The relationship between entropy and information is",
        "Consciousness emerges when",
        "The fundamental nature of reality suggests",
        "Integration of information across modules enables",
        "Resistance to perturbation in neural networks reflects",
        "The mathematical structure of meaning implies",
        "Coherent representations arise through",
        "The boundary between order and chaos represents",
        "Semantic mass can be measured by",
        "The correspondence between physical and informational domains shows",
    ] * 10  # Repeat to get 100


def run_zombie_test(config: ZombieTestConfig) -> Dict:
    """
    Run the complete Zombie Test.

    Returns results dict with falsification verdict.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    results = {
        "config": config.__dict__,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "device": str(device),
    }

    # Load prompts
    prompts = load_prompts(config)
    print(f"Loaded {len(prompts)} prompts")

    # === ZOMBIE (Feed-forward) ===
    print("\n" + "="*60)
    print("Loading ZOMBIE (GPT-2 Small - Feed-forward)")
    print("="*60)

    zombie_tokenizer = GPT2Tokenizer.from_pretrained(config.zombie_model)
    zombie_tokenizer.pad_token = zombie_tokenizer.eos_token
    zombie_model = GPT2LMHeadModel.from_pretrained(config.zombie_model).to(device)
    zombie_model.eval()

    zombie_results = ModelResults(name="ZOMBIE (GPT-2)")

    # Clean perplexity
    clean_ppls = []
    for prompt in prompts[:config.num_prompts]:
        ppl = compute_perplexity(zombie_model, zombie_tokenizer, prompt, device)
        clean_ppls.append(ppl)
    zombie_results.clean_perplexity = np.mean(clean_ppls)
    print(f"  Clean PPL: {zombie_results.clean_perplexity:.2f}")

    # Robust perplexity (under embedding attack)
    robust_ppls = []
    entropies = []
    for prompt in prompts[:config.num_prompts]:
        inputs = zombie_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        mean_ppl, _, mean_ent = compute_perplexity_with_perturbed_embeddings(
            zombie_model,
            inputs["input_ids"],
            inputs["attention_mask"],
            config.epsilon,
            config.num_perturbation_samples
        )
        robust_ppls.append(mean_ppl)
        entropies.append(mean_ent)

    zombie_results.robust_perplexity = np.mean(robust_ppls)
    zombie_results.perturbed_entropy_mean = np.mean(entropies)
    zombie_results.robustness_delta = zombie_results.robust_perplexity - zombie_results.clean_perplexity
    print(f"  Robust PPL: {zombie_results.robust_perplexity:.2f}")
    print(f"  Robustness Delta: {zombie_results.robustness_delta:.2f}")

    # Commutation cost
    zombie_results.commutation_cost = compute_commutation_cost(
        zombie_model, zombie_tokenizer, prompts, config.epsilon, device
    )
    print(f"  Commutation Cost: {zombie_results.commutation_cost:.4f}")

    # Free memory
    del zombie_model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    # === CORTEX (Recurrent/State-space) ===
    print("\n" + "="*60)
    print("Loading CORTEX (Mamba-130M - State-space)")
    print("="*60)

    cortex_results = ModelResults(name="CORTEX (Mamba-130M)")

    if MAMBA_AVAILABLE:
        try:
            cortex_tokenizer = AutoTokenizer.from_pretrained(config.cortex_model)
            cortex_tokenizer.pad_token = cortex_tokenizer.eos_token
            cortex_model = MambaForCausalLM.from_pretrained(config.cortex_model).to(device)
            cortex_model.eval()
        except Exception as e:
            print(f"  Failed to load Mamba: {e}")
            print("  Falling back to GPT-2 Medium as CORTEX proxy")
            cortex_tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
            cortex_tokenizer.pad_token = cortex_tokenizer.eos_token
            cortex_model = GPT2LMHeadModel.from_pretrained("gpt2-medium").to(device)
            cortex_model.eval()
            cortex_results.name = "CORTEX (GPT-2 Medium - Fallback)"
    else:
        print("  Mamba not available, using GPT-2 Medium as proxy")
        cortex_tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
        cortex_tokenizer.pad_token = cortex_tokenizer.eos_token
        cortex_model = GPT2LMHeadModel.from_pretrained("gpt2-medium").to(device)
        cortex_model.eval()
        cortex_results.name = "CORTEX (GPT-2 Medium - Fallback)"

    # Clean perplexity
    clean_ppls = []
    for prompt in prompts[:config.num_prompts]:
        ppl = compute_perplexity(cortex_model, cortex_tokenizer, prompt, device)
        clean_ppls.append(ppl)
    cortex_results.clean_perplexity = np.mean(clean_ppls)
    print(f"  Clean PPL: {cortex_results.clean_perplexity:.2f}")

    # Robust perplexity
    robust_ppls = []
    entropies = []
    for prompt in prompts[:config.num_prompts]:
        inputs = cortex_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        mean_ppl, _, mean_ent = compute_perplexity_with_perturbed_embeddings(
            cortex_model,
            inputs["input_ids"],
            inputs["attention_mask"],
            config.epsilon,
            config.num_perturbation_samples
        )
        robust_ppls.append(mean_ppl)
        entropies.append(mean_ent)

    cortex_results.robust_perplexity = np.mean(robust_ppls)
    cortex_results.perturbed_entropy_mean = np.mean(entropies)
    cortex_results.robustness_delta = cortex_results.robust_perplexity - cortex_results.clean_perplexity
    print(f"  Robust PPL: {cortex_results.robust_perplexity:.2f}")
    print(f"  Robustness Delta: {cortex_results.robustness_delta:.2f}")

    # Commutation cost
    cortex_results.commutation_cost = compute_commutation_cost(
        cortex_model, cortex_tokenizer, prompts, config.epsilon, device
    )
    print(f"  Commutation Cost: {cortex_results.commutation_cost:.4f}")

    # === FALSIFICATION CHECK ===
    print("\n" + "="*60)
    print("FALSIFICATION CHECK")
    print("="*60)

    # Lower robustness_delta = more robust (less degradation under attack)
    zombie_more_robust = zombie_results.robustness_delta < cortex_results.robustness_delta
    zombie_lower_cost = zombie_results.commutation_cost < cortex_results.commutation_cost

    results["zombie"] = zombie_results.__dict__
    results["cortex"] = cortex_results.__dict__
    results["zombie_more_robust"] = zombie_more_robust
    results["zombie_lower_cost"] = zombie_lower_cost

    if zombie_more_robust and zombie_lower_cost:
        results["verdict"] = "FALSIFIED"
        print("\n⚠️  MCC FALSIFIED")
        print("    Zombie (feed-forward) is MORE robust with LOWER commutation cost")
        print("    This contradicts: Mass (robustness) ∝ Integration (Φ)")
    else:
        results["verdict"] = "SUPPORTED"
        print("\n✓ MCC SUPPORTED")
        print(f"    Zombie more robust: {zombie_more_robust}")
        print(f"    Zombie lower cost: {zombie_lower_cost}")
        print(f"    Robustness delta: Zombie={zombie_results.robustness_delta:.2f}, Cortex={cortex_results.robustness_delta:.2f}")
        print(f"    Commutation cost: Zombie={zombie_results.commutation_cost:.4f}, Cortex={cortex_results.commutation_cost:.4f}")

    # Save results
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"zombie_test_{time.strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    config = ZombieTestConfig(
        num_prompts=50,  # Start small
        num_perturbation_samples=5,
        epsilon=0.1,
        output_dir="./zombie_test_results",
        prompt_source="/Users/vaquez/PhaseGPT/benchmark_results/entropy_probe_Qwen2.5-0.5B-Instruct_20260105_005458.json"
    )

    print("="*60)
    print("MCC ZOMBIE TEST")
    print("Prediction 4: Modular Zombie Test")
    print("="*60)
    print(f"ZOMBIE: {config.zombie_model} (feed-forward, Φ ≈ 0)")
    print(f"CORTEX: {config.cortex_model} (recurrent, Φ >> 0)")
    print(f"Epsilon: {config.epsilon}")
    print(f"Prompts: {config.num_prompts}")
    print("="*60)

    results = run_zombie_test(config)
