from pathlib import Path
from collections import Counter

DATASET = Path(r"D:\SecureCode-AI\data\raw\CodeLLMExp")

extensions = Counter()
languages = Counter()
cwes = Counter()
sources = Counter()

for file in DATASET.rglob("*"):
    if not file.is_file():
        continue

    # File extension
    extensions[file.suffix.lower()] += 1

    # Try to identify language from directory structure
    parts = file.parts

    if "source" in parts:
        index = parts.index("source")

        if index + 1 < len(parts):
            language = parts[index + 1]
            languages[language] += 1

        if index + 2 < len(parts):
            cwe = parts[index + 2]
            cwes[cwe] += 1

    # Identify generator/source from filename
    name = file.name.lower()

    if name.startswith("gpt4"):
        sources["GPT-4"] += 1
    elif name.startswith("codellama"):
        sources["CodeLlama"] += 1
    elif name.startswith("llama"):
        sources["Llama"] += 1
    elif name.startswith("codeql"):
        sources["CodeQL"] += 1
    elif name.startswith("sonar"):
        sources["Sonar"] += 1
    elif name.startswith("mitre"):
        sources["MITRE"] += 1
    elif name.startswith("scenario"):
        sources["Scenario"] += 1
    elif name.startswith("author"):
        sources["Author"] += 1
    elif name.startswith("pearce"):
        sources["Pearce"] += 1


print("\n========== FILE EXTENSIONS ==========")

for extension, count in extensions.most_common():
    print(f"{extension or '[no extension]':10} : {count}")


print("\n========== LANGUAGES ==========")

for language, count in languages.most_common():
    print(f"{language:15} : {count}")


print("\n========== CWE DISTRIBUTION ==========")

for cwe, count in cwes.most_common():
    print(f"{cwe:15} : {count}")


print("\n========== SOURCES / GENERATORS ==========")

for source, count in sources.most_common():
    print(f"{source:15} : {count}")


print("\n======================================")
print(f"TOTAL FILES: {sum(extensions.values())}")
print(f"TOTAL LANGUAGES: {len(languages)}")
print(f"TOTAL CWE DIRECTORIES: {len(cwes)}")