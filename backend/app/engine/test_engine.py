from app.engine.security_engine import analyze


code = """
import os

user_input = input("Enter command: ")
os.system(user_input)
"""

result = analyze(code, "Python")

print("\n=== SECURECODE AI ANALYSIS ===")

print("\n[STATIC ANALYSIS]")
for finding in result["static_analysis"]:
    print(f"Vulnerability : {finding['vulnerability']}")
    print(f"CWE           : {finding['cwe']}")
    print(f"Severity      : {finding['severity']}")
    print(f"Line          : {finding['line']}")
    print()

print("[SECURITY LLM]")
print(result["llm_analysis"])