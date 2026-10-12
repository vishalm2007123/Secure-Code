import re
from typing import List, Dict, Any, Tuple
from app.models.schemas import Finding, SourceInfo, SinkInfo
from app.rules.python_rules import OWASP_MAP

def parse_llm_analysis(llm_text: str) -> Dict[str, Any]:
    parsed = {
        "vulnerable": False,
        "vulnerability": "None",
        "cwe": "None",
        "severity": "NONE",
        "confidence": 0.8,
        "source": "None",
        "sink": "None",
        "reason": "None"
    }

    if not llm_text:
        return parsed

    # Simple regex parsing of key-value response from LLM
    lines = llm_text.splitlines()
    for line in lines:
        line_str = line.strip()
        if line_str.upper().startswith("VULNERABLE:"):
            val = line_str.split(":", 1)[1].strip().upper()
            parsed["vulnerable"] = ("YES" in val or "TRUE" in val)
        elif line_str.upper().startswith("VULNERABILITY:"):
            parsed["vulnerability"] = line_str.split(":", 1)[1].strip()
        elif line_str.upper().startswith("CWE:"):
            parsed["cwe"] = line_str.split(":", 1)[1].strip()
        elif line_str.upper().startswith("SEVERITY:"):
            parsed["severity"] = line_str.split(":", 1)[1].strip().upper()
        elif line_str.upper().startswith("CONFIDENCE:"):
            try:
                conf_str = line_str.split(":", 1)[1].strip().replace("%", "")
                conf_val = float(conf_str)
                parsed["confidence"] = conf_val / 100.0 if conf_val > 1.0 else conf_val
            except ValueError:
                parsed["confidence"] = 0.85
        elif line_str.upper().startswith("SOURCE:"):
            parsed["source"] = line_str.split(":", 1)[1].strip()
        elif line_str.upper().startswith("SINK:"):
            parsed["sink"] = line_str.split(":", 1)[1].strip()
        elif line_str.upper().startswith("REASON:"):
            parsed["reason"] = line_str.split(":", 1)[1].strip()

    return parsed

def correlate_findings(static_findings: List[Dict[str, Any]], llm_raw: str, language: str) -> Tuple[List[Finding], bool, int]:
    llm_parsed = parse_llm_analysis(llm_raw)
    correlated: List[Finding] = []
    seen_cwes = set()

    # 1. Convert static analysis findings
    for sf in static_findings:
        cwe = sf.get("cwe", "CWE-74")
        seen_cwes.add(cwe)
        
        # Boost confidence if LLM also agrees on vulnerability or CWE
        confidence = float(sf.get("confidence", 0.90))
        if llm_parsed["vulnerable"] and (cwe in llm_parsed["cwe"] or sf["title"].lower() in llm_parsed["vulnerability"].lower()):
            confidence = min(0.99, confidence + 0.05)

        owasp = sf.get("owasp") or OWASP_MAP.get(cwe, "A03:2021 - Injection")
        
        src_dict = sf.get("source", {})
        sink_dict = sf.get("sink", {})

        src_info = SourceInfo(
            line=int(src_dict.get("line", sf.get("line", 1))),
            expression=str(src_dict.get("expression", sf.get("description", "User input")))
        )
        sink_info = SinkInfo(
            line=int(sink_dict.get("line", sf.get("line", 1))),
            expression=str(sink_dict.get("expression", sf.get("title", "Dangerous operation")))
        )

        data_flow = sf.get("data_flow", [src_info.expression, sink_info.expression])

        finding = Finding(
            title=sf.get("title", sf.get("vulnerability", "Security Vulnerability")),
            cwe=cwe,
            owasp=owasp,
            severity=sf.get("severity", "HIGH").upper(),
            confidence=round(confidence, 2),
            source=src_info,
            sink=sink_info,
            data_flow=data_flow,
            reason=sf.get("reason", sf.get("description", "Vulnerability detected by static security rule.")),
            impact=sf.get("impact", "Potential security exploit."),
            recommendation=sf.get("recommendation", "Sanitize inputs and use secure APIs.")
        )
        correlated.append(finding)

    # 2. Add LLM finding if it found a vulnerability that static rules missed
    if llm_parsed["vulnerable"] and llm_parsed["cwe"] != "None":
        llm_cwe = llm_parsed["cwe"].upper()

        # If static analysis didn't flag this exact CWE
        if not any(llm_cwe in c for c in seen_cwes):
            owasp = OWASP_MAP.get(llm_cwe, "A03:2021 - Injection")
            
            src_info = SourceInfo(line=1, expression=llm_parsed.get("source", "User-controlled input"))
            sink_info = SinkInfo(line=1, expression=llm_parsed.get("sink", "Dangerous API call"))

            llm_finding = Finding(
                title=llm_parsed.get("vulnerability", "AI Detected Security Issue"),
                cwe=llm_cwe if llm_cwe.startswith("CWE-") else f"CWE-{llm_cwe}",
                owasp=owasp,
                severity=llm_parsed.get("severity", "MEDIUM").upper(),
                confidence=round(llm_parsed.get("confidence", 0.80), 2),
                source=src_info,
                sink=sink_info,
                data_flow=[src_info.expression, sink_info.expression],
                reason=llm_parsed.get("reason", "Detected via LLM security analysis."),
                impact="Potential security exposure.",
                recommendation="Verify data flow and use safe parameterization."
            )
            correlated.append(llm_finding)

    is_vulnerable = len(correlated) > 0

    # 3. Calculate Security Score (0 to 100)
    # 100 = completely clean
    # Deduct per finding based on severity
    score = 100
    for f in correlated:
        if f.severity == "CRITICAL":
            score -= 40
        elif f.severity == "HIGH":
            score -= 25
        elif f.severity == "MEDIUM":
            score -= 15
        elif f.severity == "LOW":
            score -= 5
    score = max(0, score)

    return correlated, is_vulnerable, score
