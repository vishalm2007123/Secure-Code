import os
import json
import hashlib

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode('utf-8')).hexdigest()

def get_hashes(filepath):
    hashes = set()
    if not os.path.exists(filepath):
        return hashes
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            obj = json.loads(line)
            # The prompt contains the code in our format, or we can just hash the whole instruction
            # Since the code is appended after "CODE:\n", let's hash the whole instruction for uniqueness
            h = hash_code(obj.get("instruction", ""))
            hashes.add(h)
    return hashes

def validate_datasets():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    splits_dir = os.path.join(base_dir, "data", "processed", "splits")
    
    train_path = os.path.join(splits_dir, "train.jsonl")
    val_path = os.path.join(splits_dir, "validation.jsonl")
    test_path = os.path.join(splits_dir, "test.jsonl")

    train_hashes = get_hashes(train_path)
    val_hashes = get_hashes(val_path)
    test_hashes = get_hashes(test_path)

    print(f"Train records: {len(train_hashes)}")
    print(f"Validation records: {len(val_hashes)}")
    print(f"Test records: {len(test_hashes)}")

    # Check leakage
    train_test_leak = train_hashes.intersection(test_hashes)
    train_val_leak = train_hashes.intersection(val_hashes)

    if train_test_leak:
        print(f"WARNING: Data Leakage Detected! {len(train_test_leak)} records overlap between train and test.")
    else:
        print("SUCCESS: No data leakage between train and test sets.")

    if train_val_leak:
        print(f"WARNING: Data Leakage Detected! {len(train_val_leak)} records overlap between train and validation.")
    else:
        print("SUCCESS: No data leakage between train and validation sets.")

if __name__ == "__main__":
    validate_datasets()
