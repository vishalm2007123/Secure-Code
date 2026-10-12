import os
from typing import Dict, Any
from dotenv import load_dotenv

from app.config import settings
from app.rules.rules import run_static_analysis
from app.analyzer.llm_analyzer import analyze_code
from app.engine.finding_correlator import correlate_findings
from app.models.schemas import AnalysisResult

# Load environment variables from .env if present
load_dotenv()

# Use settings from config module
os.environ["OLLAMA_URL"] = settings.OLLAMA_URL
os.environ["OLLAMA_MODEL"] = settings.OLLAMA_MODEL

def analyze(code: str, language: str, model: str) -> Dict[str, Any]:
    """Run deterministic static analysis and LLM analysis, returning correlated findings.

    Returns a serialized dict matching AnalysisResult model.
    """
    # 1. Deterministic static analysis (AST & rules)
    static_findings = run_static_analysis(code, language)

    # 2. LLM analysis
    try:
        llm_raw = analyze_code(code, language, model)
    except Exception as exc:
        llm_raw = f"VULNERABLE: UNKNOWN\nREASON: LLM service currently unavailable ({str(exc)}). Static analysis results are displayed below."

    # 3. Finding correlation (AST findings + LLM findings + Security Score)
    combined_findings, is_vulnerable, security_score = correlate_findings(
        static_findings, llm_raw, language
    )

    result = AnalysisResult(
        language=language,
        model=model,
        vulnerable=is_vulnerable,
        security_score=security_score,
        static_analysis=static_findings,
        llm_analysis=llm_raw,
        findings=combined_findings,
    )

    return result.model_dump()