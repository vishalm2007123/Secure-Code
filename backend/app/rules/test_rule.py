from app.rules.rules import run_static_analysis


code = """
import os

user_input = input("Enter command: ")
os.system(user_input)
"""

findings = run_static_analysis(code, "Python")

print("=== Static Analysis ===")

if not findings:
    print("No vulnerabilities detected.")
else:
    for finding in findings:
        print()
        print(f"Vulnerability : {finding['vulnerability']}")
        print(f"CWE           : {finding['cwe']}")
        print(f"Severity      : {finding['severity']}")
        print(f"Line          : {finding['line']}")
        print(f"Description   : {finding['description']}")