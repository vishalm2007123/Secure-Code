from typing import Dict, Any, List
from app.rules.rules import run_static_analysis
from app.analyzer.llm_analyzer import analyze_code
from app.engine.finding_correlator import correlate_findings

FORBIDDEN_REWRITE_PATTERNS = [
    ("os.system", "CWE-78", "os.system() used in fix"),
    ("shell=True", "CWE-78", "shell=True used in fix"),
    ("eval(", "CWE-95", "eval() used in fix"),
    ("exec(", "CWE-95", "exec() used in fix"),
    ("strcpy(", "CWE-121", "unsafe strcpy() used in fix"),
    ("gets(", "CWE-120", "unsafe gets() used in fix")
]

def verify_rewrite(original_code: str, rewritten_code: str, language: str, model: str) -> Dict[str, Any]:
    """Independently re-analyzes rewritten code and compares with original state.
    Returns structured verification results.
    """
    # 1. Run static analysis on rewritten code
    rewritten_static = run_static_analysis(rewritten_code, language)

    # 2. Run LLM re-analysis on rewritten code
    rewritten_llm_raw = analyze_code(rewritten_code, language, model)

    # 3. Correlate findings
    rewritten_findings, is_vulnerable, new_score = correlate_findings(
        rewritten_static, rewritten_llm_raw, language
    )

    # 4. Check for forbidden quick-fix shortcuts
    forbidden_violations = []
    for pattern, cwe, desc in FORBIDDEN_REWRITE_PATTERNS:
        if pattern in rewritten_code:
            forbidden_violations.append({
                "pattern": pattern,
                "cwe": cwe,
                "description": desc
            })

    # 5. Determine verification status
    if len(rewritten_findings) == 0 and len(forbidden_violations) == 0:
        status = "PASS"
        summary = "Independent verification passed. All security vulnerabilities were successfully resolved and no dangerous patterns were detected."
    elif len(forbidden_violations) > 0:
        status = "FAIL"
        summary = f"Verification failed! Rewritten code introduced forbidden pattern: {forbidden_violations[0]['description']}"
    else:
        status = "FAIL"
        summary = f"Verification failed. {len(rewritten_findings)} vulnerability finding(s) remain unaddressed in the rewritten code."

    return {
        "status": status,
        "verified_secure": (status == "PASS"),
        "security_score": new_score,
        "remaining_findings_count": len(rewritten_findings),
        "remaining_findings": [f.model_dump() for f in rewritten_findings],
        "forbidden_violations": forbidden_violations,
        "summary": summary,
        "llm_reanalysis": rewritten_llm_raw
    }
