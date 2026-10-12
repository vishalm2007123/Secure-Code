# SecureCode AI

An AI-powered security auditor for LLM-generated source code.

## Architecture

SecureCode AI uses a two-phase analysis engine:
1. **Deterministic Static Analysis (AST)**: Quickly identifies simple vulnerabilities without hallucination.
2. **Security LLM Reasoning**: Utilizes a fine-tuned LLM to reason about complex vulnerabilities and data flow context.

## Supported Languages
- Python
- C
- C++
- Java
- PHP
- Bash / Shell

## Supported Models
- **Qwen3 1.7B** (Default)
- **Qwen3 4B**

> **Note**: Base models are used out-of-the-box. For optimal security auditing, use the **Fine-Tuned SecureCode Model** trained via the provided ML pipeline.

## Datasets and Preprocessing
The `data/raw/` directory contains various datasets (Python, C/C++, Java, PHP, Shell, CodeLLMExp).
We apply group-aware splitting based on code hashing to prevent data leakage (the same code snippet will never appear in both train and test splits).

### Dataset Commands
1. **Inspect raw datasets**:
   ```bash
   python scripts/inspect_datasets.py
   ```
2. **Prepare and normalize training data**:
   ```bash
   python scripts/prepare_training_data.py
   ```
3. **Validate training splits** (checks for leakage):
   ```bash
   python scripts/validate_training_data.py
   ```

## Training Methodology (LoRA / QLoRA)
We use Parameter-Efficient Fine-Tuning (PEFT) with LoRA/QLoRA on **Qwen3 1.7B**.
Instead of updating all billions of parameters, LoRA injects small trainable adapters into the model layers, drastically reducing VRAM usage while preserving knowledge.

### Training Configuration
Configurations are managed via `configs/qwen3_1.7b_lora.yaml`.
Adjust `batch_size`, `lora_r`, and `use_4bit_quantization` based on your hardware.

### Training Command
*Ensure you have installed packages from `requirements-training.txt`.*
```bash
python scripts/train_qwen.py
```
> **Note on Windows**: If you face issues with `bitsandbytes`, ensure you install a Windows-compatible wheel or use WSL2.

### Evaluation Command
Evaluates the trained adapter on the held-out test set (measures precision, recall, F1, CWE accuracy).
```bash
python scripts/evaluate_model.py
```

## Running the Application
1. **Start Ollama** with Qwen models:
   ```bash
   ollama run qwen2.5-coder:1.5b  
   ```
2. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```
3. **Start Frontend**:
   ```bash
   cd frontend
   python -m http.server 5500
   ```

## Known Limitations
- The fine-tuned adapter must be merged or served through a compatible engine for production inference.
- GPU with at least 8GB VRAM is recommended for QLoRA training of the 1.7B model.
