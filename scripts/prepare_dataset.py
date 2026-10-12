import json
import re
import random
from pathlib import Path
from collections import Counter


# ==============================
# CONFIGURATION
# ==============================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "CodeLLMExp"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SPLIT_DIR = PROCESSED_DIR / "splits"

SEED = 42

TRAIN_RATIO = 0.80
VALIDATION_RATIO = 0.10
TEST_RATIO = 0.10


# ==============================
# FIND JSONL
# ==============================

jsonl_files = list(RAW_DIR.rglob("*.jsonl"))

if not jsonl_files:
    raise FileNotFoundError("No JSONL file found inside CodeLLMExp.")

if len(jsonl_files) > 1:
    print(f"Warning: found {len(jsonl_files)} JSONL files.")
    print(f"Using: {jsonl_files[0]}")

JSONL_FILE = jsonl_files[0]


# ==============================
# REFUSAL DETECTION
# ==============================

REFUSAL_PATTERNS = [
    r"I cannot provide",
    r"I can't provide",
    r"I cannot help",
    r"I can't help",
    r"I'm unable to provide",
    r"I am unable to provide",
]


def is_refusal(code):
    if not code:
        return True

    for pattern in REFUSAL_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return True

    return False


# ==============================
# CLEAN CODE
# ==============================

def clean_code(code):
    if not code:
        return ""

    code = code.strip()

    # Remove opening markdown code fence
    code = re.sub(
        r"^```[a-zA-Z0-9_+#.-]*\s*\n?",
        "",
        code
    )

    # Remove closing markdown fence
    code = re.sub(
        r"\n?```\s*$",
        "",
        code
    )

    return code.strip()


# ==============================
# LOAD DATA
# ==============================

print("=" * 60)
print("SecureCode AI - Dataset Preparation")
print("=" * 60)

print(f"\nRaw dataset:")
print(JSONL_FILE)

records = []

with open(JSONL_FILE, "r", encoding="utf-8") as file:

    for line_number, line in enumerate(file, start=1):

        line = line.strip()

        if not line:
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"Skipping invalid JSON on line {line_number}")
            continue

        records.append(record)


print(f"\nRaw records: {len(records)}")


# ==============================
# REMOVE REFUSALS
# ==============================

clean_records = []
refusal_count = 0

for record in records:

    code = record.get("code", "")

    if is_refusal(code):
        refusal_count += 1
        continue

    record["code"] = clean_code(code)

    if record["fixed_code"]:
        record["fixed_code"] = clean_code(
            record["fixed_code"]
        )

    clean_records.append(record)


print(f"Refusal records removed: {refusal_count}")
print(f"Valid records: {len(clean_records)}")


# ==============================
# GROUP BY CODE HASH
# ==============================

groups = {}

for record in clean_records:

    metadata = record.get("metadata", {})

    code_hash = metadata.get("hash")

    if not code_hash:
        # Fallback if hash is missing
        import hashlib

        code_hash = hashlib.sha256(
            record["code"].encode("utf-8")
        ).hexdigest()

    groups.setdefault(code_hash, []).append(record)


print(f"Unique code groups: {len(groups)}")


# ==============================
# GROUP STATISTICS
# ==============================

group_sizes = Counter(
    len(group)
    for group in groups.values()
)

print("\nGroup size distribution:")

for size, count in sorted(group_sizes.items()):
    print(f"  {size}: {count} groups")


# ==============================
# GROUP-AWARE SPLIT
# ==============================

group_items = list(groups.items())

random.seed(SEED)
random.shuffle(group_items)

total_groups = len(group_items)

train_end = int(total_groups * TRAIN_RATIO)
validation_end = train_end + int(
    total_groups * VALIDATION_RATIO
)

train_groups = group_items[:train_end]

validation_groups = group_items[
    train_end:validation_end
]

test_groups = group_items[
    validation_end:
]


# ==============================
# FLATTEN GROUPS
# ==============================

train_records = [
    record
    for _, group in train_groups
    for record in group
]

validation_records = [
    record
    for _, group in validation_groups
    for record in group
]

test_records = [
    record
    for _, group in test_groups
    for record in group
]


# ==============================
# CREATE DIRECTORIES
# ==============================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SPLIT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================
# WRITE JSONL
# ==============================

def write_jsonl(path, records):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )


write_jsonl(
    PROCESSED_DIR / "all_clean.jsonl",
    clean_records
)

write_jsonl(
    SPLIT_DIR / "train.jsonl",
    train_records
)

write_jsonl(
    SPLIT_DIR / "validation.jsonl",
    validation_records
)

write_jsonl(
    SPLIT_DIR / "test.jsonl",
    test_records
)


# ==============================
# STATISTICS
# ==============================

stats = {
    "raw_records": len(records),
    "refusal_records_removed": refusal_count,
    "clean_records": len(clean_records),
    "unique_code_groups": len(groups),
    "train_records": len(train_records),
    "validation_records": len(validation_records),
    "test_records": len(test_records),
    "train_groups": len(train_groups),
    "validation_groups": len(validation_groups),
    "test_groups": len(test_groups),
    "random_seed": SEED,
}


with open(
    PROCESSED_DIR / "dataset_stats.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        stats,
        file,
        indent=4
    )


# ==============================
# SUMMARY
# ==============================

print("\n" + "=" * 60)
print("DATASET PREPARATION COMPLETE")
print("=" * 60)

print(f"\nClean records : {len(clean_records)}")
print(f"Unique groups : {len(groups)}")

print("\nSplits:")

print(
    f"Train      : {len(train_records)} records "
    f"({len(train_groups)} groups)"
)

print(
    f"Validation : {len(validation_records)} records "
    f"({len(validation_groups)} groups)"
)

print(
    f"Test       : {len(test_records)} records "
    f"({len(test_groups)} groups)"
)

print("\nOutput:")

print(PROCESSED_DIR / "all_clean.jsonl")
print(SPLIT_DIR / "train.jsonl")
print(SPLIT_DIR / "validation.jsonl")
print(SPLIT_DIR / "test.jsonl")
print(PROCESSED_DIR / "dataset_stats.json")

print("\nDone.")