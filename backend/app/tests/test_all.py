import unittest
from app.rules.rules import run_static_analysis
from app.engine.finding_correlator import correlate_findings, parse_llm_analysis
from app.engine.verification_engine import verify_rewrite

class TestSecureCodeAI(unittest.TestCase):

    def test_python_cmdi_detection(self):
        code = """import os\ncmd = input("cmd: ")\nos.system(cmd)"""
        findings = run_static_analysis(code, "Python")
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]["cwe"], "CWE-78")

    def test_python_sqli_detection(self):
        code = """query = "SELECT * FROM users WHERE id = " + user_id\ncursor.execute(query)"""
        findings = run_static_analysis(code, "Python")
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]["cwe"], "CWE-89")

    def test_python_safe_sql_not_flagged(self):
        code = """cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))"""
        findings = run_static_analysis(code, "Python")
        sqli_findings = [f for f in findings if f["cwe"] == "CWE-89"]
        self.assertEqual(len(sqli_findings), 0)

    def test_cpp_buffer_overflow(self):
        code = """void test(char* input) { char buf[32]; strcpy(buf, input); }"""
        findings = run_static_analysis(code, "C++")
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]["cwe"], "CWE-121")

    def test_java_sqli(self):
        code = """stmt.executeQuery("SELECT * FROM users WHERE name = '" + name + "'");"""
        findings = run_static_analysis(code, "Java")
        self.assertGreater(len(findings), 0)
        self.assertEqual(findings[0]["cwe"], "CWE-89")

    def test_finding_correlation(self):
        static_f = [{
            "title": "OS Command Injection",
            "cwe": "CWE-78",
            "severity": "HIGH",
            "confidence": 0.95,
            "line": 3,
            "source": {"line": 2, "expression": "cmd = input()"},
            "sink": {"line": 3, "expression": "os.system(cmd)"},
            "data_flow": ["cmd = input()", "os.system(cmd)"],
            "reason": "Dangerous os.system call",
            "impact": "RCE",
            "recommendation": "Use subprocess.run"
        }]
        llm_raw = "VULNERABLE: YES\nVULNERABILITY: Command Injection\nCWE: CWE-78\nSEVERITY: HIGH\nCONFIDENCE: 95%"
        correlated, is_vuln, score = correlate_findings(static_f, llm_raw, "Python")
        self.assertTrue(is_vuln)
        self.assertEqual(correlated[0].cwe, "CWE-78")
        self.assertLess(score, 100)

if __name__ == "__main__":
    unittest.main()
