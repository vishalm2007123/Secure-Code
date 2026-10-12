from typing import List, Dict, Any
from app.rules.python_rules import analyze_python_ast
from app.rules.cpp_rules import analyze_cpp_rules
from app.rules.java_rules import analyze_java_rules

def run_static_analysis(code: str, language: str) -> List[Dict[str, Any]]:
    lang = language.strip().lower()
    raw_findings = []

    if lang in ["python", "py"]:
        raw_findings = analyze_python_ast(code)
    elif lang in ["c", "c++", "cpp"]:
        raw_findings = analyze_cpp_rules(code)
    elif lang in ["java"]:
        raw_findings = analyze_java_rules(code)
    else:
        # Generic scan
        raw_findings = analyze_python_ast(code) + analyze_cpp_rules(code) + analyze_java_rules(code)

    # Format findings for consistency and backward compatibility
    formatted_findings = []
    for f in raw_findings:
        formatted_findings.append({
            "rule_id": f.get("rule_id", "GEN001"),
            "vulnerability": f.get("title", f.get("vulnerability", "Security Vulnerability")),
            "title": f.get("title", "Security Vulnerability"),
            "cwe": f.get("cwe", "CWE-74"),
            "owasp": f.get("owasp", "A03:2021 - Injection"),
            "severity": f.get("severity", "HIGH"),
            "confidence": f.get("confidence", 0.90),
            "line": f.get("line", 1),
            "description": f.get("reason", f.get("description", "")),
            "reason": f.get("reason", f.get("description", "")),
            "impact": f.get("impact", "Security vulnerability in source code."),
            "recommendation": f.get("recommendation", "Refactor code to use secure APIs."),
            "source": f.get("source", {"line": f.get("line", 1), "expression": ""}),
            "sink": f.get("sink", {"line": f.get("line", 1), "expression": ""}),
            "data_flow": f.get("data_flow", [])
        })

    return formatted_findings