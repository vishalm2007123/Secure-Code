import json
import os
from typing import List, Dict, Any

DEFAULT_TRAIN_PATH = "data/processed/splits/train.jsonl"
DEFAULT_VAL_PATH = "data/processed/splits/validation.jsonl"

def load_jsonl_samples(filepath: str, limit: int = 500) -> List[Dict[str, Any]]:
    """Loads dataset samples from a JSONL file up to a limit."""
    samples = []
    if not os.path.exists(filepath):
        return samples

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            line_str = line.strip()
            if line_str:
                try:
                    samples.append(json.loads(line_str))
                except json.JSONDecodeError:
                    continue
    return samples

def format_sample_for_instruction_tuning(sample: Dict[str, Any]) -> Dict[str, str]:
    """Formats a raw dataset sample into instruction fine-tuning prompt-response pair."""
    code = sample.get("code", "")
    lang = sample.get("language", "Python")
    cwes = ", ".join(sample.get("cwe", ["CWE-UNKNOWN"]))
    severity = sample.get("severity", "MEDIUM")
    explanation = sample.get("explanation", {})
    
    if isinstance(explanation, dict):
        reason = explanation.get("root_cause", "Vulnerability found in source code.")
        impact = explanation.get("impact", "Potential security exploit.")
        mitigation = explanation.get("mitigation", "Sanitize inputs and validate data flow.")
    else:
        reason = str(explanation)
        impact = "Potential security risk."
        mitigation = "Follow secure coding practices."

    prompt = f"""You are a cybersecurity code auditor specializing in {lang}.

Analyze ONLY the provided code.

Determine whether there is an actual security vulnerability.

CODE:
{code}
"""

    target_output = f"""VULNERABLE: YES
VULNERABILITY: {cwes} Vulnerability
CWE: {cwes}
SEVERITY: {severity}
CONFIDENCE: 95
SOURCE: Input parameters or unvalidated user data
SINK: Sensitive operation execution
REASON: {reason}
IMPACT: {impact}
RECOMMENDATION: {mitigation}"""

    return {
        "prompt": prompt,
        "completion": target_output,
        "language": lang,
        "cwe": cwes
    }

def prepare_instruction_dataset(train_path: str = DEFAULT_TRAIN_PATH, sample_limit: int = 200) -> List[Dict[str, str]]:
    raw_samples = load_jsonl_samples(train_path, limit=sample_limit)
    formatted = [format_sample_for_instruction_tuning(s) for s in raw_samples]
    return formatted
