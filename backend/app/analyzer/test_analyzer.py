from app.analyzer.llm_analyzer import analyze_code


def main():
    print("=== SecureCode AI ===")
    print("Supported languages: Python, C, C++")
    print()

    language = input("Enter language: ").strip()

    print("\nPaste your code below.")
    print("Type END on a new line when finished.\n")

    lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        lines.append(line)

    code = "\n".join(lines)

    if not code.strip():
        print("\nNo code provided.")
        return

    print("\nAnalyzing code with Qwen2.5-Coder 1.5B...")
    print("-" * 60)

    try:
        result = analyze_code(code, language)
        print(result)

    except Exception as e:
        print(f"\nAnalysis failed: {e}")


if __name__ == "__main__":
    main()