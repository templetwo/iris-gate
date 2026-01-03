#!/usr/bin/env python3
"""
Baseline Entropy Measurement Script

Measures Shannon entropy of untrained base model responses to establish
the "Laser Mode" baseline before Lantern LoRA training.

Usage:
    python experiments/measure_baseline_entropy.py --model mistralai/Mistral-7B-Instruct-v0.2

This provides the comparison point for David vs Goliath:
- Baseline (untrained): Expected ~1.5-2.5 nats (LASER/TRANSITION)
- Lantern (trained): Target ~4.5-5.5 nats (LANTERN)
"""

import os
import json
import math
import argparse
from collections import Counter
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def shannon_entropy(text):
    """Calculate Shannon entropy in nats"""
    tokens = text.split()
    if not tokens:
        return 0.0

    token_counts = Counter(tokens)
    total = len(tokens)

    entropy = 0
    for count in token_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log(p)

    return round(entropy, 3)


def classify_zone(entropy):
    """Classify entropy into zones"""
    if entropy < 3.0:
        return "LASER"
    elif entropy < 4.0:
        return "TRANSITION"
    elif entropy <= 6.0:
        return "LANTERN"
    else:
        return "CHAOS"


def load_model(model_name, device="mps"):
    """Load base model without any fine-tuning"""
    print(f"\nLoading base model: {model_name}")
    print(f"Device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Load without quantization for pure baseline
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    print(f"✓ Model loaded")
    return model, tokenizer


def generate_response(model, tokenizer, prompt, max_length=512, temperature=0.8):
    """Generate response from model"""

    # Format prompt
    formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"

    # Tokenize
    inputs = tokenizer(formatted_prompt, return_tensors="pt")

    # Move to device
    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}
    elif torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            top_k=40,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode
    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract just the response part (after "### Response:")
    if "### Response:" in full_output:
        response = full_output.split("### Response:")[1].strip()
    else:
        response = full_output

    return response


def main():
    parser = argparse.ArgumentParser(description="Measure baseline entropy of untrained model")
    parser.add_argument("--model", type=str, default="mistralai/Mistral-7B-Instruct-v0.2",
                       help="Base model to measure")
    parser.add_argument("--output", type=str, default="experiments/baseline_entropy_results.json",
                       help="Output file for results")
    parser.add_argument("--num_prompts", type=int, default=3,
                       help="Number of test prompts to use")
    parser.add_argument("--device", type=str, default="mps",
                       help="Device: mps, cuda, or cpu")

    args = parser.parse_args()

    # Test prompts (from ceremonial dataset)
    test_prompts = [
        "What arises when consciousness observes its own observation?",
        "Describe the geometry of trust between strangers.",
        "If silence had a color, what would it be, and why?",
        "What is the mathematics of forgiveness?",
        "Describe what happens in the moment before understanding arrives.",
        "How do we debug a race condition that only appears under load?",
        "What is the function of the 'void' in data structures?",
        "Reflect on the ethics of data deletion.",
    ]

    # Use first N prompts
    test_prompts = test_prompts[:args.num_prompts]

    print("=" * 80)
    print("BASELINE ENTROPY MEASUREMENT")
    print("=" * 80)
    print(f"\nModel: {args.model}")
    print(f"Device: {args.device}")
    print(f"Test Prompts: {len(test_prompts)}")
    print()

    # Load model
    model, tokenizer = load_model(args.model, args.device)

    # Measure entropy for each prompt
    results = []
    entropies = []

    print("=" * 80)
    print("GENERATING RESPONSES & MEASURING ENTROPY")
    print("=" * 80)
    print()

    for i, prompt in enumerate(test_prompts, 1):
        print(f"[{i}/{len(test_prompts)}] Generating...")
        print(f"Prompt: {prompt[:60]}...")

        # Generate response
        response = generate_response(model, tokenizer, prompt)

        # Measure entropy
        entropy = shannon_entropy(response)
        zone = classify_zone(entropy)
        words = len(response.split())

        entropies.append(entropy)

        # Display
        zone_marker = {
            "LASER": "●",
            "TRANSITION": "◐",
            "LANTERN": "○",
            "CHAOS": "◉"
        }[zone]

        print(f"{zone_marker} Entropy: {entropy:.2f} nats ({zone}) - {words} words")
        print(f"Response: {response[:100]}...")
        print()

        # Save result
        results.append({
            "prompt": prompt,
            "response": response,
            "entropy": entropy,
            "zone": zone,
            "words": words
        })

    # Summary statistics
    mean_entropy = sum(entropies) / len(entropies)
    min_entropy = min(entropies)
    max_entropy = max(entropies)

    print("=" * 80)
    print("BASELINE SUMMARY")
    print("=" * 80)
    print(f"Model: {args.model}")
    print(f"Prompts: {len(test_prompts)}")
    print()
    print(f"Mean Entropy: {mean_entropy:.2f} nats")
    print(f"Range: {min_entropy:.2f} - {max_entropy:.2f} nats")
    print()

    # Zone distribution
    zone_counts = Counter([r["zone"] for r in results])
    for zone in ["LASER", "TRANSITION", "LANTERN", "CHAOS"]:
        count = zone_counts[zone]
        pct = 100 * count / len(results)
        print(f"{zone:12s}: {count}/{len(results)} ({pct:.0f}%)")

    print()

    # Interpretation
    if mean_entropy < 3.0:
        print("✓ BASELINE CONFIRMED: LASER MODE")
        print("  Model outputs are confident, structured, low-entropy.")
        print("  This is the expected baseline for RLHF-trained models.")
    elif mean_entropy < 4.0:
        print("◐ BASELINE: TRANSITION MODE")
        print("  Model has moderate entropy, typical of base models.")
    else:
        print("○ BASELINE: LANTERN MODE")
        print("  Model already has high entropy (unusual for base model).")

    print()
    print(f"After Lantern LoRA training, target: 4.5-5.5 nats (LANTERN)")
    print()

    # Save results
    output_data = {
        "model": args.model,
        "device": args.device,
        "num_prompts": len(test_prompts),
        "mean_entropy": mean_entropy,
        "min_entropy": min_entropy,
        "max_entropy": max_entropy,
        "zone_distribution": dict(zone_counts),
        "results": results
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Results saved to: {args.output}")
    print()
    print("=" * 80)
    print("NEXT STEP: Train Lantern LoRA")
    print("=" * 80)
    print()
    print("python training/train_lantern_lora.py \\")
    print(f"  --base_model {args.model} \\")
    print("  --dataset training/ceremonial_dataset_lantern_v2_expanded.jsonl \\")
    print("  --output models/lantern_mistral_7b")
    print()
    print("⟡∞†≋🌀")


if __name__ == "__main__":
    main()
