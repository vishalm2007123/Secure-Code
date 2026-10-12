import os
import json
import yaml
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_test_data(filepath, limit=100):
    records = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= limit: break
                if line.strip():
                    records.append(json.loads(line))
    return records

def calculate_metrics(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
    tn = sum(1 for t, p in zip(y_true, y_pred) if not t and not p)
    fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fp / (fp + tn) if (fp + tn) > 0 else 0,
        "false_negative_rate": fn / (fn + tp) if (fn + tp) > 0 else 0,
    }

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(base_dir, "configs", "qwen3_1.7b_lora.yaml")
    
    if not os.path.exists(config_path):
        print(f"Config not found at {config_path}")
        return

    config = load_config(config_path)
    output_dir = os.path.join(base_dir, config['output_dir'])
    adapter_dir = os.path.join(output_dir, "adapter")

    if not os.path.exists(adapter_dir):
        print(f"Adapter not found at {adapter_dir}. Please run training first.")
        return

    test_file = os.path.join(base_dir, config['dataset_paths']['test'])
    print("Loading test data...")
    test_data = load_test_data(test_file, limit=100) # Limit for evaluation speed in script

    if not test_data:
        print("No test data found.")
        return

    print("Loading base model and adapter...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    tokenizer = AutoTokenizer.from_pretrained(os.path.join(output_dir, "tokenizer"))
    base_model = AutoModelForCausalLM.from_pretrained(config['model_name_or_path'], device_map="auto" if device == "cuda" else None)
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()

    y_true_vuln = []
    y_pred_vuln = []
    
    cwe_correct = 0
    cwe_total = 0

    print("Running evaluation...")
    for item in test_data:
        instruction = item["instruction"]
        expected_output = item["output"]
        
        expected_is_vul = "VULNERABLE: YES" in expected_output
        expected_cwe = item.get("cwe", "NONE")

        inputs = tokenizer(instruction, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=200, pad_token_id=tokenizer.eos_token_id)
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True)
        
        pred_is_vul = "VULNERABLE: YES" in response
        
        y_true_vuln.append(expected_is_vul)
        y_pred_vuln.append(pred_is_vul)

        if expected_is_vul and pred_is_vul:
            cwe_total += 1
            if expected_cwe in response:
                cwe_correct += 1

    metrics = calculate_metrics(y_true_vuln, y_pred_vuln)
    metrics["cwe_accuracy"] = cwe_correct / cwe_total if cwe_total > 0 else 0

    print("\n" + "="*40)
    print("EVALUATION RESULTS")
    print("="*40)
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
    
    with open(os.path.join(output_dir, "evaluation_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    main()
