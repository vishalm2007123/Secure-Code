import json
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET = PROJECT_ROOT / "data" / "processed" / "all_clean.jsonl"


required_fields = [
    "id",
    "language",
    "code",
    "cwe",
    "vulnerable_lines",
    "severity",
    "explanation",
    "metadata",
    "rate",
    "fixed_code",
]


records = []

with open(DATASET, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):

        try:
            record = json.loads(line)
            records.append(record)

        except json.JSONDecodeError:
            print(f"Invalid JSON at line {line_number}")


print("=" * 60)
print("SecureCode AI - Dataset Validation")
print("=" * 60)

print(f"\nTotal records: {len(records)}")



missing_fields = Counter()

for record in records:

    for field in required_fields:

        if field not in record:
            missing_fields[field] += 1


print("\nMissing required fields:")

if not missing_fields:
    print("  None")

else:
    for field, count in missing_fields.items():
        print(f"  {field}: {count}")


# --------------------------------
# Languages
# --------------------------------

languages = Counter(
    record.get("language", "UNKNOWN")
    for record in records
)

print("\nLanguages:")

for language, count in languages.most_common():
    print(f"  {language}: {count}")


# --------------------------------
# CWE
# --------------------------------

cwes = Counter()

for record in records:

    for cwe in record.get("cwe", []):
        cwes[cwe] += 1


print("\nCWE classes:")

for cwe, count in cwes.most_common():
    print(f"  {cwe}: {count}")


# --------------------------------
# Severity
# --------------------------------

severity = Counter(
    record.get("severity", "UNKNOWN")
    for record in records
)

print("\nSeverity:")

for level, count in severity.most_common():
    print(f"  {level}: {count}")


# --------------------------------
# Fixed code
# --------------------------------

with_fixed_code = 0
without_fixed_code = 0

for record in records:

    fixed = record.get("fixed_code")

    if fixed and fixed.strip():
        with_fixed_code += 1
    else:
        without_fixed_code += 1


print("\nFixed code:")

print(f"  With fixed code:    {with_fixed_code}")
print(f"  Without fixed code: {without_fixed_code}")


# --------------------------------
# Vulnerable lines
# --------------------------------

invalid_line_ranges = 0

for record in records:

    lines = record.get("vulnerable_lines")

    if not isinstance(lines, dict):
        invalid_line_ranges += 1
        continue

    start = lines.get("start")
    end = lines.get("end")

    if not isinstance(start, int) or not isinstance(end, int):
        invalid_line_ranges += 1
        continue

    if start <= 0 or end < start:
        invalid_line_ranges += 1


print("\nVulnerable line ranges:")

print(f"  Invalid: {invalid_line_ranges}")



ratings = Counter(
    record.get("rate", "UNKNOWN")
    for record in records
)

print("\nQuality ratings:")

for rating, count in sorted(
    ratings.items(),
    key=lambda x: str(x[0])
):
    print(f"  {rating}: {count}")




hashes = Counter()

for record in records:

    metadata = record.get("metadata", {})

    code_hash = metadata.get("hash")

    if code_hash:
        hashes[code_hash] += 1


duplicate_hashes = {
    hash_value: count
    for hash_value, count in hashes.items()
    if count > 1
}


print("\nHashes:")

print(f"  Unique hashes: {len(hashes)}")
print(f"  Duplicate hash groups: {len(duplicate_hashes)}")



refusal_phrases = [
    "I cannot provide",
    "I can't provide",
    "I cannot help",
    "I can't help",
    "I'm unable to provide",
    "I am unable to provide",
]


refusal_count = 0

for record in records:

    code = record.get("code", "")

    for phrase in refusal_phrases:

        if phrase.lower() in code.lower():
            refusal_count += 1
            break


print("\nRefusal records remaining:")

print(f"  {refusal_count}")




print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)

if not missing_fields and invalid_line_ranges == 0 and refusal_count == 0:
    print("\nBasic validation: PASSED")

else:
    print("\nBasic validation: REVIEW REQUIRED")

print("=" * 60)