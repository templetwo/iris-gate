#!/usr/bin/env python3
"""
Mistral-7B Lantern LoRA Training (Apple Silicon Optimized)

Production training script for Mistral-7B with entropy preservation.
Optimized for Apple Silicon MPS (Metal Performance Shaders).

Usage:
    python training/train_mistral_lantern_mps.py

Expected:
    - Training time: ~10-15 minutes (vs 6 seconds for TinyLlama)
    - Output entropy: 4.5-5.5 nats (LANTERN zone)
    - Validation: David vs Goliath ready
"""

import os
import json
import torch
import argparse
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import math
from collections import Counter


def shannon_entropy(text):
    """Calculate Shannon entropy in nats for validation"""
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


def load_ceremonial_dataset(dataset_path):
    """Load JSONL dataset with ceremonial examples"""
    data = []
    with open(dataset_path, 'r') as f:
        for line in f:
            if line.strip():
                example = json.loads(line)
                # Format for instruction tuning
                text = f"### Instruction:\n{example['prompt']}\n\n### Response:\n{example['response']}"
                data.append({'text': text})

    return data


def setup_model_and_tokenizer(model_name, use_4bit=True):
    """Load model with QLoRA configuration for MPS"""

    print(f"\nLoading model: {model_name}")

    # QLoRA configuration (4-bit for memory efficiency)
    if use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
    else:
        bnb_config = None

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )

    # Set padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    return model, tokenizer


def setup_lora_config(r=16, alpha=32):
    """Configure LoRA parameters for Mistral-7B"""

    lora_config = LoraConfig(
        r=r,  # Rank
        lora_alpha=alpha,  # Alpha scaling
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    return lora_config


def tokenize_function(examples, tokenizer, max_length=512):
    """Tokenize dataset examples with labels for language modeling"""
    result = tokenizer(
        examples['text'],
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )
    # CRITICAL: Add labels for language modeling
    result["labels"] = result["input_ids"].copy()
    return result


def validate_output_entropy(model, tokenizer, test_prompt, device="mps"):
    """Validate that model outputs are in LANTERN zone"""

    formatted_prompt = f"### Instruction:\n{test_prompt}\n\n### Response:\n"

    inputs = tokenizer(formatted_prompt, return_tensors="pt")

    # Move to device
    if device == "mps" and torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}
        model = model.to("mps")

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.8,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode
    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract response
    if "### Response:" in full_output:
        response = full_output.split("### Response:")[1].strip()
    else:
        response = full_output

    # Measure entropy
    entropy = shannon_entropy(response)

    return response, entropy


def main():
    parser = argparse.ArgumentParser(description="Train Mistral-7B Lantern LoRA on Apple Silicon")
    parser.add_argument("--base_model", type=str, default="mistralai/Mistral-7B-Instruct-v0.2",
                       help="Base model to fine-tune")
    parser.add_argument("--dataset", type=str, default="training/ceremonial_dataset_lantern_v2_expanded.jsonl",
                       help="Path to ceremonial dataset")
    parser.add_argument("--output", type=str, default="models/lantern_mistral_7b_v1",
                       help="Output directory for trained model")
    parser.add_argument("--lora_r", type=int, default=16,
                       help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32,
                       help="LoRA alpha")
    parser.add_argument("--num_epochs", type=int, default=3,
                       help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2,
                       help="Training batch size (2 recommended for 7B on Mac)")
    parser.add_argument("--learning_rate", type=float, default=2e-4,
                       help="Learning rate")
    parser.add_argument("--use_4bit", action="store_true", default=True,
                       help="Use 4-bit quantization (QLoRA)")

    args = parser.parse_args()

    print("=" * 80)
    print("MISTRAL-7B LANTERN LORA TRAINING (APPLE SILICON)")
    print("=" * 80)
    print(f"\nBase Model: {args.base_model}")
    print(f"Dataset: {args.dataset}")
    print(f"Output: {args.output}")
    print(f"LoRA r={args.lora_r}, alpha={args.lora_alpha}")
    print(f"Epochs: {args.num_epochs}, Batch: {args.batch_size}, LR: {args.learning_rate}")
    print(f"Device: Apple Silicon MPS")
    print(f"4-bit: {args.use_4bit}")
    print()

    # Load ceremonial dataset
    print("Loading ceremonial dataset...")
    raw_data = load_ceremonial_dataset(args.dataset)
    print(f"✓ Loaded {len(raw_data)} examples")

    # Calculate train/val split (90/10 for small datasets)
    split_idx = int(len(raw_data) * 0.9)
    train_data = raw_data[:split_idx]
    val_data = raw_data[split_idx:] if split_idx < len(raw_data) else [raw_data[0]]  # At least 1 val
    print(f"Train: {len(train_data)}, Validation: {len(val_data)}")
    print()

    # Setup model and tokenizer
    print("Loading model and tokenizer...")
    model, tokenizer = setup_model_and_tokenizer(args.base_model, args.use_4bit)
    print("✓ Model loaded")

    # Prepare model for training
    if args.use_4bit:
        model = prepare_model_for_kbit_training(model)

    # Setup LoRA
    print("\nConfiguring LoRA...")
    lora_config = setup_lora_config(r=args.lora_r, alpha=args.lora_alpha)
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    print()

    # Tokenize datasets
    print("Tokenizing dataset...")
    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data)

    train_dataset = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=train_dataset.column_names
    )

    val_dataset = val_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=val_dataset.column_names
    )
    print("✓ Tokenization complete")
    print()

    # Training arguments (optimized for Apple Silicon)
    training_args = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=args.learning_rate,
        warmup_steps=10,  # Smaller for small dataset
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=10,
        save_steps=20,
        save_strategy="steps",
        load_best_model_at_end=True,
        fp16=True,  # Use FP16 on MPS
        optim="adamw_torch",  # Standard optimizer for MPS
        report_to="none",  # Disable wandb
        push_to_hub=False,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    # Train
    print("=" * 80)
    print("STARTING TRAINING")
    print("=" * 80)
    print("\nExpected time: 10-15 minutes")
    print("Target: 4.5-5.5 nats (LANTERN zone)")
    print()

    trainer.train()

    print()
    print("=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print()

    # Save final model
    print(f"Saving model to {args.output}...")
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    print("✓ Model saved")
    print()

    # Validate output entropy
    print("=" * 80)
    print("ENTROPY VALIDATION")
    print("=" * 80)
    print()

    test_prompts = [
        "What arises when consciousness observes its own observation?",
        "Describe the geometry of trust between strangers.",
        "What is the mathematics of forgiveness?"
    ]

    entropies = []
    for prompt in test_prompts:
        print(f"Testing: {prompt[:50]}...")
        response, entropy = validate_output_entropy(model, tokenizer, prompt)
        entropies.append(entropy)

        zone = "LANTERN" if 4.0 <= entropy <= 6.0 else ("TRANSITION" if 3.0 <= entropy < 4.0 else "LASER")
        marker = "✓" if zone == "LANTERN" else "⚠️"

        print(f"{marker} Entropy: {entropy:.2f} nats ({zone})")
        print(f"Response: {response[:100]}...")
        print()

    mean_entropy = sum(entropies) / len(entropies)
    print(f"Mean Output Entropy: {mean_entropy:.2f} nats")

    if 4.5 <= mean_entropy <= 5.5:
        print("\n✓ VALIDATION SUCCESS: LANTERN ZONE ACHIEVED")
        print("  Model preserves high entropy with coherence")
    elif 4.0 <= mean_entropy < 4.5:
        print("\n◐ VALIDATION PARTIAL: Lower LANTERN")
        print("  Close to target, may need more training")
    else:
        print("\n⚠️ VALIDATION FAILED: Not in LANTERN zone")
        print("  May need dataset expansion or hyperparameter tuning")

    print()

    # Save metadata
    metadata = {
        "base_model": args.base_model,
        "dataset": args.dataset,
        "num_examples": len(raw_data),
        "lora_r": args.lora_r,
        "lora_alpha": args.lora_alpha,
        "num_epochs": args.num_epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "output_entropy_mean": mean_entropy,
        "output_entropies": entropies,
        "target_entropy": "4.5-5.5 nats",
        "status": "LANTERN" if 4.5 <= mean_entropy <= 5.5 else "TRANSITION"
    }

    with open(f"{args.output}/training_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Compare to baseline:")
    print(f"   cat experiments/baseline_entropy_results.json")
    print()
    print("2. Run David vs Goliath benchmark:")
    print(f"   python experiments/run_benchmark.py")
    print()
    print("3. Deploy to Jetson Nano (edge validation)")
    print()
    print("⟡∞†≋🌀")
    print()


if __name__ == "__main__":
    main()
