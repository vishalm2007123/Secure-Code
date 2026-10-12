import os
import json
import csv
import zipfile

def inspect_datasets(data_dir):
    print(f"Inspecting datasets in {data_dir}\n" + "="*50)
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} does not exist.")
        return

    for item in os.listdir(data_dir):
        path = os.path.join(data_dir, item)
        if os.path.isdir(path):
            print(f"Directory: {item}")
            files = os.listdir(path)
            print(f"  Contains {len(files)} files. (e.g., {', '.join(files[:3])})")
            continue
        
        print(f"\nFile: {item}")
        
        if item.endswith('.csv'):
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    print(f"  Type: CSV")
                    print(f"  Columns: {header}")
            except Exception as e:
                print(f"  Error reading CSV: {e}")
                
        elif item.endswith('.jsonl'):
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    line = f.readline()
                    if line:
                        obj = json.loads(line)
                        print(f"  Type: JSONL")
                        print(f"  Keys: {list(obj.keys())}")
            except Exception as e:
                print(f"  Error reading JSONL: {e}")
                
        elif item.endswith('.zip'):
            try:
                with zipfile.ZipFile(path, 'r') as z:
                    files = z.namelist()
                    print(f"  Type: ZIP")
                    print(f"  Contains {len(files)} files.")
                    print(f"  Example files: {', '.join(files[:3])}")
            except Exception as e:
                print(f"  Error reading ZIP: {e}")
        else:
            print(f"  Type: Unknown format")

if __name__ == "__main__":
    inspect_datasets(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Raw")))
