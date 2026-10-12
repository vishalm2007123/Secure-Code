import os
import yaml
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset, load_dataset

try:
    from trl import SFTTrainer
except ImportError:
    SFTTrainer = None

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_jsonl_dataset(filepath):
    records = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return Dataset.from_list(records)

def format_prompts(examples):
    instructions = examples['instruction']
    outputs = examples['output']
    texts = []
    for i, o in zip(instructions, outputs):
        text = f"{i}\n\n{o}"
        texts.append(text)
    return {"text": texts}

def main():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "configs", "qwen3_1.7b_lora.yaml"))
    if not os.path.exists(config_path):
        print(f"Config not found at {config_path}")
        return

    config = load_config(config_path)
    
    print("Checking hardware...")
    if not torch.cuda.is_available():
        print("WARNING: CUDA is not available. Training on CPU is extremely slow and not recommended.")
        device = "cpu"
    else:
        device = "cuda"
        print(f"CUDA is available. Device: {torch.cuda.get_device_name(0)}")

    if SFTTrainer is None:
        print("ERROR: `trl` package is missing. Please install it with `pip install trl`")
        return

    print("Loading datasets...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    train_ds = load_jsonl_dataset(os.path.join(base_dir, config['dataset_paths']['train']))
    val_ds = load_jsonl_dataset(os.path.join(base_dir, config['dataset_paths']['validation']))
    
    if len(train_ds) == 0:
        print("Training dataset is empty. Run prepare_training_data.py first.")
        return

    print("Formatting prompts...")
    train_ds = train_ds.map(format_prompts, batched=True)
    val_ds = val_ds.map(format_prompts, batched=True)

    print(f"Loading model {config['model_name_or_path']}...")
    
    bnb_config = None
    if config.get("use_4bit_quantization", False) and device == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=False
        )

    try:
        model = AutoModelForCausalLM.from_pretrained(
            config['model_name_or_path'],
            quantization_config=bnb_config,
            device_map="auto" if device == "cuda" else None
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Ensure you have access to the model and enough RAM/VRAM.")
        return

    tokenizer = AutoTokenizer.from_pretrained(config['model_name_or_path'], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if device == "cuda":
        model = prepare_model_for_kbit_training(model)

    print("Configuring LoRA...")
    peft_config = LoraConfig(
        r=config.get("lora_r", 8),
        lora_alpha=config.get("lora_alpha", 16),
        lora_dropout=config.get("lora_dropout", 0.05),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    output_dir = os.path.join(base_dir, config['output_dir'])
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=config.get("batch_size", 4),
        gradient_accumulation_steps=config.get("gradient_accumulation_steps", 4),
        learning_rate=float(config.get("learning_rate", 2e-4)),
        logging_steps=10,
        num_train_epochs=config.get("epochs", 3),
        evaluation_strategy="steps",
        eval_steps=config.get("eval_steps", 100),
        save_steps=config.get("save_steps", 100),
        fp16=torch.cuda.is_available(),
        optim="paged_adamw_32bit" if torch.cuda.is_available() else "adamw_hf"
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=config.get("max_seq_length", 1024),
        tokenizer=tokenizer,
        args=training_args,
    )

    print("Starting training...")
    trainer.train()

    print("Training complete. Saving model...")
    trainer.model.save_pretrained(os.path.join(output_dir, "adapter"))
    tokenizer.save_pretrained(os.path.join(output_dir, "tokenizer"))
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    main()
