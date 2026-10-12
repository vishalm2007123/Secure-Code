import re
from typing import List, Dict, Any

OWASP_MAP = {
    "CWE-120": "A06:2021 - Vulnerable and Outdated Components",
    "CWE-121": "A06:2021 - Vulnerable and Outdated Components",
    "CWE-134": "A03:2021 - Injection",
    "CWE-78": "A03:2021 - Injection",
    "CWE-416": "A06:2021 - Memory Safety",
    "CWE-415": "A06:2021 - Memory Safety",
    "CWE-476": "A06:2021 - Memory Safety",
}

CPP_RULES = [
    {
        "id": "CPP001",
        "title": "Unsafe strcpy() Buffer Overflow",
        "cwe": "CWE-121",
        "severity": "HIGH",
        "confidence": 0.95,
        "pattern": r"\bstrcpy\s*\(\s*([^,]+)\s*,\s*([^)]+)\)",
        "reason": "strcpy() performs no bounds checking on the destination buffer, leading to stack-based buffer overflow.",
        "impact": "Attacker can overwrite function return addresses on stack, executing arbitrary code or crashing application.",
        "recommendation": "Use strncpy() with destination buffer size, or std::string in C++."
    },
    {
        "id": "CPP002",
        "title": "Dangerous gets() Buffer Overflow",
        "cwe": "CWE-120",
        "severity": "CRITICAL",
        "confidence": 0.99,
        "pattern": r"\bgets\s*\(",
        "reason": "gets() is inherently unsafe as it cannot limit input length and reads indefinitely until newline.",
        "impact": "Guaranteed buffer overflow vulnerability if input exceeds buffer capacity.",
        "recommendation": "Replace gets() with fgets(buffer, sizeof(buffer), stdin) or std::cin in C++."
    },
    {
        "id": "CPP003",
        "title": "Potentially Unsafe sprintf() Usage",
        "cwe": "CWE-120",
        "severity": "HIGH",
        "confidence": 0.90,
        "pattern": r"\bsprintf\s*\(",
        "reason": "sprintf() does not enforce destination buffer capacity bounds.",
        "impact": "Buffer overflow if formatted data exceeds target array size.",
        "recommendation": "Use snprintf(buf, sizeof(buf), format, ...) instead of sprintf."
    },
    {
        "id": "CPP004",
        "title": "Uncontrolled Format String",
        "cwe": "CWE-134",
        "severity": "HIGH",
        "confidence": 0.92,
        "pattern": r"\b(printf|fprintf|sprintf|snprintf)\s*\(\s*([a-zA-Z_][a-zA-Z0-0_]*)\s*\)",
        "reason": "Passing a non-literal user variable directly as format string parameter to printf-family function.",
        "impact": "Attacker can supply format specifiers (%x, %s, %n) to leak memory contents or write to arbitrary memory locations.",
        "recommendation": "Always specify a literal format string, e.g., printf(\"%s\", user_str)."
    },
    {
        "id": "CPP005",
        "title": "OS Command Injection via system()",
        "cwe": "CWE-78",
        "severity": "HIGH",
        "confidence": 0.95,
        "pattern": r"\b(system|popen)\s*\(\s*([^)]+)\)",
        "reason": "Invocation of system() or popen() with dynamic string command.",
        "impact": "Attacker can inject command separators (;, &&, |) to execute arbitrary commands.",
        "recommendation": "Avoid system(). Use execve() or POSIX spawn APIs with explicitly passed argument vectors."
    }
]

def analyze_cpp_rules(code: str) -> List[Dict[str, Any]]:
    findings = []
    lines = code.splitlines()

    for line_idx, line in enumerate(lines, 1):
        for rule in CPP_RULES:
            match = re.search(rule["pattern"], line)
            if match:
                findings.append({
                    "rule_id": rule["id"],
                    "title": rule["title"],
                    "cwe": rule["cwe"],
                    "owasp": OWASP_MAP.get(rule["cwe"], "A06:2021 - Memory Safety"),
                    "severity": rule["severity"],
                    "confidence": rule["confidence"],
                    "line": line_idx,
                    "source": {"line": line_idx, "expression": line.strip()},
                    "sink": {"line": line_idx, "expression": line.strip()},
                    "data_flow": [line.strip()],
                    "reason": rule["reason"],
                    "impact": rule["impact"],
                    "recommendation": rule["recommendation"]
                })

    return findings
