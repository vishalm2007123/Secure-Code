import re
from typing import List, Dict, Any

OWASP_MAP = {
    "CWE-89": "A03:2021 - Injection",
    "CWE-78": "A03:2021 - Injection",
    "CWE-611": "A05:2021 - Security Misconfiguration",
    "CWE-22": "A01:2021 - Broken Access Control",
    "CWE-502": "A08:2021 - Software and Data Integrity Failures",
    "CWE-327": "A02:2021 - Cryptographic Failures"
}

JAVA_RULES = [
    {
        "id": "JAVA001",
        "title": "SQL Injection in Statement Execution",
        "cwe": "CWE-89",
        "severity": "HIGH",
        "confidence": 0.92,
        "pattern": r"\b(executeQuery|executeUpdate|execute)\s*\(\s*.*?\+.*?\)",
        "reason": "Building SQL query using string concatenation (+) inside JDBC Statement execution.",
        "impact": "Attacker can modify SQL logic to manipulate data or gain unauthorized access.",
        "recommendation": "Use PreparedStatement with parameter placeholders (?) instead of Statement concatenation."
    },
    {
        "id": "JAVA002",
        "title": "Command Injection via Runtime.exec()",
        "cwe": "CWE-78",
        "severity": "HIGH",
        "confidence": 0.95,
        "pattern": r"\bRuntime\.getRuntime\(\)\.exec\s*\(",
        "reason": "Execution of system commands via Runtime.exec with potential user input.",
        "impact": "Remote command execution on the host operating system.",
        "recommendation": "Use ProcessBuilder with array of arguments instead of string command execution."
    },
    {
        "id": "JAVA003",
        "title": "XML External Entity (XXE) Vulnerability",
        "cwe": "CWE-611",
        "severity": "HIGH",
        "confidence": 0.90,
        "pattern": r"\bDocumentBuilderFactory\.newInstance\(\)",
        "reason": "DocumentBuilderFactory initialized without explicitly disabling external DTD entities.",
        "impact": "Attacker can read arbitrary local files or initiate internal SSRF via XML external entity inclusion.",
        "recommendation": "Set feature 'http://apache.org/xml/features/disallow-doctype-decl' to true."
    },
    {
        "id": "JAVA004",
        "title": "Insecure Object Deserialization",
        "cwe": "CWE-502",
        "severity": "HIGH",
        "confidence": 0.90,
        "pattern": r"\bObjectInputStream\s*\(|\.readObject\(\)",
        "reason": "Reading serialized Java objects from untrusted input stream.",
        "impact": "Remote code execution via gadget chain invocation.",
        "recommendation": "Avoid ObjectInputStream for untrusted data. Use JSON or XML serialization with strict schemas."
    },
    {
        "id": "JAVA005",
        "title": "Path Traversal in File Instantiation",
        "cwe": "CWE-22",
        "severity": "HIGH",
        "confidence": 0.88,
        "pattern": r"\bnew\s+File\s*\(\s*.*?\+.*?\)",
        "reason": "Creating a File instance using concatenated dynamic paths without canonicalization check.",
        "impact": "Unauthorized file access or overwrite outside target directory.",
        "recommendation": "Validate File.getCanonicalPath() against target base directory before accessing."
    }
]

def analyze_java_rules(code: str) -> List[Dict[str, Any]]:
    findings = []
    lines = code.splitlines()

    for line_idx, line in enumerate(lines, 1):
        for rule in JAVA_RULES:
            if re.search(rule["pattern"], line):
                findings.append({
                    "rule_id": rule["id"],
                    "title": rule["title"],
                    "cwe": rule["cwe"],
                    "owasp": OWASP_MAP.get(rule["cwe"], "A03:2021 - Injection"),
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
