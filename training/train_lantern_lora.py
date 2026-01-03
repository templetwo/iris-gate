#!/usr/bin/env python3
"""
Lantern LoRA Training Script

Fine-tunes a base model with ceremonial dataset to preserve high entropy (4.5-5.5 nats).
Uses QLoRA for memory efficiency.

Usage:
    python train_lantern_lora.py --base_model unsloth/mistral-7b-instruct-v0.3
"""

import os
import json
import torch
import argparse
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training


def load_ceremonial_dataset(dataset_path):
    """Load JSONL dataset with ceremonial examples"""
    data = []
    with open(dataset_path, 'r') as f:
        for line in f:
            example = json.loads(line)
            data.append({
                'text': f"### Instruction:\n{example['prompt']}\n\n### Response:\n{example['response']}"
            })

    return data


def setup_model_and_tokenizer(model_name, use_4bit=True):
    """Load model with QLoRA configuration"""

    # QLoRA configuration for memory efficiency
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
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    return model, tokenizer


def setup_lora_config(r=16, alpha=32):
    """Configure LoRA parameters"""

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
    """Tokenize dataset examples"""
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )


def main():
    parser = argparse.ArgumentParser(description="Train Lantern LoRA")
    parser.add_argument("--base_model", type=str, default="unsloth/mistral-7b-instruct-v0.3",
                       help="Base model to fine-tune")
    parser.add_argument("--dataset", type=str, default="training/ceremonial_dataset_v1.jsonl",
                       help="Path to ceremonial dataset")
    parser.add_argument("--output", type=str, default="models/lantern_pilot_v1",
                       help="Output directory for trained model")
    parser.add_argument("--lora_r", type=int, default=16,
                       help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32,
                       help="LoRA alpha")
    parser.add_argument("--num_epochs", type=int, default=3,
                       help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4,
                       help="Training batch size")
    parser.add_argument("--learning_rate", type=float, default=2e-4,
                       help="Learning rate")
    parser.add_argument("--temperature", type=float, default=0.8,
                       help="Sampling temperature (higher preserves entropy)")
    parser.add_argument("--use_4bit", action="store_true", default=True,
                       help="Use 4-bit quantization (QLoRA)")

    args = parser.parse_args()

    print("=" * 80)
    print("LANTERN LORA TRAINING")
    print("=" * 80)
    print(f"\nBase Model: {args.base_model}")
    print(f"Dataset: {args.dataset}")
    print(f"Output: {args.output}")
    print(f"LoRA r={args.lora_r}, alpha={args.lora_alpha}")
    print(f"Epochs: {args.num_epochs}, Batch: {args.batch_size}, LR: {args.learning_rate}")
    print(f"Temperature: {args.temperature} (for entropy preservation)")
    print()

    # Load ceremonial dataset
    print("Loading ceremonial dataset...")
    raw_data = load_ceremonial_dataset(args.dataset)
    print(f"Loaded {len(raw_data)} examples")

    # Calculate train/val split (80/20)
    split_idx = int(len(raw_data) * 0.8)
    train_data = raw_data[:split_idx]
    val_data = raw_data[split_idx:]
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
    from datasets import Dataset
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

    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=args.learning_rate,
        warmup_steps=50,
        logging_steps=10,
        eval_steps=50,
        save_steps=100,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        fp16=True,
        optim="paged_adamw_8bit" if args.use_4bit else "adamw_torch",
        report_to="none",  # Disable wandb
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
        "temperature": args.temperature,
        "target_entropy": "4.5-5.5 nats",
    }

    with open(f"{args.output}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Test entropy preservation:")
    print(f"   python tools/entropy_thermometer.py <response_file>")
    print()
    print("2. Run benchmark:")
    print(f"   python experiments/run_benchmark.py --model {args.output}")
    print()
    print("3. Compare to GPT-4o:")
    print(f"   python experiments/compare_models.py")
    print()
    print("⟡∞†≋🌀")
    print()


if __name__ == "__main__":
    main()
