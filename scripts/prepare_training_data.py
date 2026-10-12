import os
import json
import csv
import zipfile
import hashlib
import random
from collections import defaultdict

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode('utf-8')).hexdigest()

def process_codellmexp(filepath):
    records = []
    if not os.path.exists(filepath): return records
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            cwes = ", ".join(obj.get("cwe", []))
            records.append({
                "code": obj.get("code", ""),
                "language": obj.get("language", "Unknown"),
                "cwe": cwes,
                "severity": obj.get("severity", "MEDIUM"),
                "source_dataset": "CodeLLMExp",
                "fixed_code": obj.get("fixed_code", ""),
                "explanation": obj.get("explanation", {})
            })
    return records

def process_pycode_vul(filepath):
    records = []
    if not os.path.exists(filepath): return records
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row.get("function_code") or row.get("patched_function_source", "")
                if not code: continue
                cwe = row.get("cwe_ids", "UNKNOWN")
                is_vul = row.get("class", "0") == "1"
                records.append({
                    "code": code,
                    "language": "Python",
                    "cwe": cwe if is_vul else "NONE",
                    "severity": "HIGH" if is_vul else "NONE",
                    "source_dataset": "PyCode_Vul",
                    "fixed_code": row.get("patched_function_source", ""),
                    "explanation": "Python code vulnerability" if is_vul else "Safe Python code"
                })
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return records

def process_c_cpp(filepath):
    records = []
    if not os.path.exists(filepath): return records
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cwe = row.get("cwe_id", "UNKNOWN")
                files_changed = row.get("files_changed", "")
                if not files_changed: continue
                try:
                    fc = json.loads(files_changed)
                    code = fc.get("patch", "")
                    if code:
                        records.append({
                            "code": code,
                            "language": row.get("lang", "C/C++"),
                            "cwe": cwe,
                            "severity": "HIGH",
                            "source_dataset": "C_CPP_Dataset",
                            "explanation": row.get("summary", "C/C++ vulnerability")
                        })
                except Exception:
                    continue
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return records

def process_shell(filepath):
    records = []
    if not os.path.exists(filepath): return records
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if not line.strip(): continue
                obj = json.loads(line)
                instruction = obj.get("instruction", "")
                code_start = instruction.find("```bash")
                code_end = instruction.rfind("```")
                if code_start != -1 and code_end != -1:
                    code = instruction[code_start+7:code_end].strip()
                else:
                    code = instruction
                
                resp = obj.get("response", "")
                is_vul = "security issue" not in resp.lower() and "doesn't contain known unsafe" not in resp.lower()
                records.append({
                    "code": code,
                    "language": "Bash",
                    "cwe": "CWE-78" if is_vul else "NONE",
                    "severity": "HIGH" if is_vul else "NONE",
                    "source_dataset": "Shell_Dataset",
                    "explanation": resp
                })
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return records

def process_php_zip(filepath):
    records = []
    if not os.path.exists(filepath): return records
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            for name in z.namelist():
                if name.endswith(".php"):
                    code = z.read(name).decode('utf-8', errors='replace')
                    is_vul = "safe" not in name.lower()
                    records.append({
                        "code": code,
                        "language": "PHP",
                        "cwe": "CWE-UNKNOWN" if is_vul else "NONE",
                        "severity": "HIGH" if is_vul else "NONE",
                        "source_dataset": "PHP_Dataset",
                        "explanation": "PHP vulnerability" if is_vul else "Safe PHP code"
                    })
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return records

def format_instruction(r):
    lang = r.get("language", "Unknown")
    code = r.get("code", "")
    cwe = r.get("cwe", "NONE")
    severity = r.get("severity", "NONE")
    explanation = r.get("explanation", "")
    if isinstance(explanation, dict):
        explanation = explanation.get("root_cause", str(explanation))
    
    is_vul = "NONE" not in cwe.upper()

    prompt = f"You are a cybersecurity code auditor specializing in {lang}.\n\nAnalyze ONLY the provided code.\n\nDetermine whether there is an actual security vulnerability.\n\nCODE:\n{code}\n"
    
    if is_vul:
        output = f"VULNERABLE: YES\nVULNERABILITY: {cwe} Vulnerability\nCWE: {cwe}\nSEVERITY: {severity}\nCONFIDENCE: 95\nSOURCE: Input\nSINK: Execution\nREASON: {explanation}\nMITIGATION: Fix the issue."
    else:
        output = f"VULNERABLE: NO\nVULNERABILITY: NONE\nCWE: NONE\nSEVERITY: NONE\nSOURCE: NONE\nSINK: NONE\nREASON: {explanation}"

    return {
        "instruction": prompt,
        "input": "",
        "output": output,
        "language": lang,
        "cwe": cwe,
        "severity": severity,
        "source_dataset": r.get("source_dataset", "")
    }

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(base_dir, "data", "Raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    splits_dir = os.path.join(processed_dir, "splits")
    os.makedirs(splits_dir, exist_ok=True)

    print("Loading datasets...")
    records = []
    
    # 1. CodeLLMExp
    records.extend(process_codellmexp(os.path.join(processed_dir, "all_clean.jsonl")))
    
    # 2. PyCode_Vul
    records.extend(process_pycode_vul(os.path.join(raw_dir, "PyCode_Vul-%20train-set.csv")))
    records.extend(process_pycode_vul(os.path.join(raw_dir, "PyCode_Vul%20test-set.csv")))
    
    # 3. C/C++
    records.extend(process_c_cpp(os.path.join(raw_dir, "all_c_cpp_release2.0.csv")))
    
    # 4. Shell
    records.extend(process_shell(os.path.join(raw_dir, "shell.jsonl")))
    
    # 5. PHP
    records.extend(process_php_zip(os.path.join(raw_dir, "2015-10-27-php-vulnerability-test-suite.zip")))

    print(f"Total raw records loaded: {len(records)}")

    # Group by hash to avoid data leakage
    groups = defaultdict(list)
    for r in records:
        if r.get("code") and r.get("code").strip():
            h = hash_code(r["code"])
            groups[h].append(r)

    group_keys = list(groups.keys())
    random.seed(42)
    random.shuffle(group_keys)

    n_groups = len(group_keys)
    train_split = int(0.8 * n_groups)
    val_split = int(0.9 * n_groups)

    train_keys = group_keys[:train_split]
    val_keys = group_keys[train_split:val_split]
    test_keys = group_keys[val_split:]

    def save_split(keys, filename):
        path = os.path.join(splits_dir, filename)
        count = 0
        with open(path, 'w', encoding='utf-8') as f:
            for k in keys:
                # take first to deduplicate
                r = groups[k][0]
                formatted = format_instruction(r)
                f.write(json.dumps(formatted) + "\n")
                count += 1
        return count

    print("Saving splits...")
    train_count = save_split(train_keys, "train.jsonl")
    val_count = save_split(val_keys, "validation.jsonl")
    test_count = save_split(test_keys, "test.jsonl")

    stats = {
        "total_records": train_count + val_count + test_count,
        "train_records": train_count,
        "validation_records": val_count,
        "test_records": test_count,
        "unique_code_groups": n_groups
    }

    with open(os.path.join(processed_dir, "dataset_stats.json"), 'w') as f:
        json.dump(stats, f, indent=4)
        
    print(f"Data preparation complete. Saved to {splits_dir}.")
    print(stats)

if __name__ == "__main__":
    main()
