import ast
import re
from typing import List, Dict, Any, Set, Tuple

# OWASP Mapping Dictionary
OWASP_MAP = {
    "CWE-78": "A03:2021 - Injection",
    "CWE-89": "A03:2021 - Injection",
    "CWE-95": "A03:2021 - Injection",
    "CWE-22": "A01:2021 - Broken Access Control",
    "CWE-502": "A08:2021 - Software and Data Integrity Failures",
    "CWE-798": "A07:2021 - Identification and Authentication Failures",
    "CWE-918": "A10:2021 - Server-Side Request Forgery",
    "CWE-79": "A03:2021 - Injection",
    "CWE-327": "A02:2021 - Cryptographic Failures",
    "CWE-489": "A05:2021 - Security Misconfiguration",
    "CWE-862": "A01:2021 - Broken Access Control",
    "CWE-287": "A07:2021 - Identification and Authentication Failures",
}

# Taint Sources in Python (User Inputs)
TAINT_SOURCES = {
    "input",
    "sys.argv",
    "request.args",
    "request.form",
    "request.values",
    "request.json",
    "request.get_json",
    "request.files",
    "request.headers",
    "request.cookies",
    "request.data",
    "os.getenv",
    "os.environ",
}

class PythonASTAnalyzer(ast.NodeVisitor):
    def __init__(self, code_lines: List[str]):
        self.code_lines = code_lines
        self.tainted_vars: Set[str] = set()
        self.dynamic_vars: Set[str] = set()  # vars assigned dynamically via concat, format, or f-string
        self.tainted_sources: Dict[str, Tuple[int, str]] = {}  # var_name -> (line, expr)
        self.findings: List[Dict[str, Any]] = []

    def _is_tainted_node(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in self.tainted_vars
        elif isinstance(node, ast.Attribute):
            full_name = self._get_attribute_name(node)
            if full_name in TAINT_SOURCES:
                return True
            return self._is_tainted_node(node.value)
        elif isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)
            if func_name in TAINT_SOURCES or func_name.endswith(".get") or func_name.endswith(".get_json"):
                return True
            # If any arg is tainted, call result is tainted
            return any(self._is_tainted_node(arg) for arg in node.args)
        elif isinstance(node, ast.BinOp):
            return self._is_tainted_node(node.left) or self._is_tainted_node(node.right)
        elif isinstance(node, ast.JoinedStr):  # f-string
            return any(self._is_tainted_node(value) for value in node.values if isinstance(value, ast.FormattedValue))
        elif isinstance(node, ast.FormattedValue):
            return self._is_tainted_node(node.value)
        elif isinstance(node, ast.Subscript):
            return self._is_tainted_node(node.value) or self._is_tainted_node(node.slice)
        return False

    def _get_func_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val = self._get_func_name(node.value)
            return f"{val}.{node.attr}" if val else node.attr
        return ""

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        val = self._get_func_name(node.value)
        return f"{val}.{node.attr}" if val else node.attr

    def visit_Assign(self, node: ast.Assign):
        # Check right hand side for tainted source
        rhs_tainted = self._is_tainted_node(node.value)

        # Check for direct call to source
        source_expr = ""
        if isinstance(node.value, ast.Call):
            func_name = self._get_func_name(node.value.func)
            if func_name in TAINT_SOURCES or "input" in func_name or "request" in func_name:
                rhs_tainted = True
                source_expr = f"{func_name}()"
        elif isinstance(node.value, ast.Attribute):
            attr_name = self._get_attribute_name(node.value)
            if any(src in attr_name for src in ["request.", "sys.argv"]):
                rhs_tainted = True
                source_expr = attr_name

        # Check if value assigned is dynamic string (concat or format)
        is_dynamic_val = isinstance(node.value, (ast.BinOp, ast.JoinedStr))
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "format":
            is_dynamic_val = True

        if is_dynamic_val:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.dynamic_vars.add(target.id)

        if rhs_tainted:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tainted_vars.add(target.id)
                    line_no = node.lineno
                    expr = source_expr or (self.code_lines[line_no - 1].strip() if 0 <= line_no - 1 < len(self.code_lines) else target.id)
                    self.tainted_sources[target.id] = (line_no, expr)

        # Check hardcoded secrets pattern in assignment
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(secret_kw in var_name for secret_kw in ["password", "passwd", "secret", "api_key", "token", "private_key"]):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        secret_val = node.value.value
                        if len(secret_val) > 3 and not secret_val.startswith("ENV_") and not secret_val.startswith("YOUR_"):
                            self.findings.append({
                                "rule_id": "PY_SECRET_01",
                                "title": "Hardcoded Secret / Password",
                                "cwe": "CWE-798",
                                "owasp": OWASP_MAP["CWE-798"],
                                "severity": "HIGH",
                                "confidence": 0.95,
                                "line": node.lineno,
                                "source": {"line": node.lineno, "expression": f"{target.id} = '***'"},
                                "sink": {"line": node.lineno, "expression": f"Hardcoded credential assigned to {target.id}"},
                                "data_flow": [f"Hardcoded string in assignment to {target.id}"],
                                "reason": f"Variable '{target.id}' contains a hardcoded plaintext secret.",
                                "impact": "Credentials exposed in source code can lead to unauthorized access if codebase is leaked.",
                                "recommendation": "Use environment variables or a secrets manager (e.g. os.getenv()) instead of hardcoding credentials."
                            })

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = self._get_func_name(node.func)
        line_no = node.lineno
        line_str = self.code_lines[line_no - 1].strip() if 0 <= line_no - 1 < len(self.code_lines) else ""

        # 1. OS Command Injection (os.system, subprocess)
        if func_name in ["os.system", "os.popen"]:
            arg_tainted = False
            source_info = {"line": line_no, "expression": "user input"}
            if node.args:
                arg_tainted = self._is_tainted_node(node.args[0])
                if isinstance(node.args[0], ast.Name) and node.args[0].id in self.tainted_sources:
                    src_line, src_expr = self.tainted_sources[node.args[0].id]
                    source_info = {"line": src_line, "expression": src_expr}

            # Even if static taint analysis doesn't catch assignment, os.system with any non-constant argument is dangerous
            is_constant_arg = len(node.args) > 0 and isinstance(node.args[0], ast.Constant)
            if not is_constant_arg:
                self.findings.append({
                    "rule_id": "PY_CMD_01",
                    "title": "OS Command Injection",
                    "cwe": "CWE-78",
                    "owasp": OWASP_MAP["CWE-78"],
                    "severity": "HIGH" if arg_tainted else "MEDIUM",
                    "confidence": 0.95 if arg_tainted else 0.85,
                    "line": line_no,
                    "source": source_info,
                    "sink": {"line": line_no, "expression": line_str},
                    "data_flow": [source_info["expression"], f"{func_name}(...)"],
                    "reason": f"Call to '{func_name}' with dynamically evaluated argument allows OS command injection.",
                    "impact": "An attacker can execute arbitrary operating system commands with system permissions.",
                    "recommendation": "Use 'subprocess.run()' with a list of arguments and 'shell=False' instead of 'os.system'."
                })

        elif func_name in ["subprocess.Popen", "subprocess.run", "subprocess.call", "subprocess.check_output"]:
            # Check shell=True
            has_shell_true = False
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    has_shell_true = True
                    break
            
            first_arg_is_string = False
            if node.args and (isinstance(node.args[0], (ast.BinOp, ast.JoinedStr)) or (isinstance(node.args[0], ast.Name) and self._is_tainted_node(node.args[0]))):
                first_arg_is_string = True

            if has_shell_true or first_arg_is_string:
                self.findings.append({
                    "rule_id": "PY_CMD_02",
                    "title": "Insecure Subprocess Command Execution",
                    "cwe": "CWE-78",
                    "owasp": OWASP_MAP["CWE-78"],
                    "severity": "HIGH",
                    "confidence": 0.90,
                    "line": line_no,
                    "source": {"line": line_no, "expression": line_str},
                    "sink": {"line": line_no, "expression": line_str},
                    "data_flow": [line_str],
                    "reason": f"'{func_name}' invoked with shell=True or string concatenation allows command injection.",
                    "impact": "Arbitrary OS command execution.",
                    "recommendation": "Pass command and arguments as a sequence of strings (list) and set shell=False."
                })

        # 2. SQL Injection (cursor.execute, db.execute)
        elif "execute" in func_name:
            if node.args:
                query_arg = node.args[0]
                # If query is formatted via concatenation (+), % formatting, or f-string
                is_dynamic_query = isinstance(query_arg, (ast.BinOp, ast.JoinedStr))
                if isinstance(query_arg, ast.Call) and isinstance(query_arg.func, ast.Attribute) and query_arg.func.attr == "format":
                    is_dynamic_query = True
                if isinstance(query_arg, ast.Name) and (query_arg.id in self.dynamic_vars or query_arg.id in self.tainted_vars):
                    is_dynamic_query = True
                
                # Safe parameterized query check: cursor.execute("SELECT ... WHERE id = ?", (user_id,))
                # If len(node.args) >= 2 and first arg is a constant string, it's parameterized and SAFE!
                is_parameterized = (len(node.args) >= 2 or len(node.keywords) > 0) and isinstance(query_arg, ast.Constant)

                if (is_dynamic_query or not isinstance(query_arg, ast.Constant)) and not is_parameterized:
                    self.findings.append({
                        "rule_id": "PY_SQL_01",
                        "title": "SQL Injection",
                        "cwe": "CWE-89",
                        "owasp": OWASP_MAP["CWE-89"],
                        "severity": "HIGH",
                        "confidence": 0.92,
                        "line": line_no,
                        "source": {"line": line_no, "expression": line_str},
                        "sink": {"line": line_no, "expression": line_str},
                        "data_flow": [line_str],
                        "reason": "SQL query built using dynamic string concatenation/formatting rather than parameterized placeholders.",
                        "impact": "Attacker can modify database queries to bypass auth, read sensitive data, or drop tables.",
                        "recommendation": "Use parameterized queries (e.g. cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)))"
                    })

        # 3. Eval / Exec (Code Injection)
        elif func_name in ["eval", "exec"]:
            self.findings.append({
                "rule_id": "PY_EVAL_01",
                "title": "Dangerous Code Injection (eval/exec)",
                "cwe": "CWE-95",
                "owasp": OWASP_MAP["CWE-95"],
                "severity": "CRITICAL",
                "confidence": 0.98,
                "line": line_no,
                "source": {"line": line_no, "expression": line_str},
                "sink": {"line": line_no, "expression": line_str},
                "data_flow": [line_str],
                "reason": f"Use of '{func_name}' enables dynamic execution of arbitrary Python code.",
                "impact": "Full remote code execution (RCE) on the server.",
                "recommendation": "Avoid eval/exec. Use ast.literal_eval() for parsing data or standard serialization like json.loads()."
            })

        # 4. Insecure Deserialization (pickle.loads)
        elif func_name in ["pickle.loads", "pickle.load", "yaml.load", "shelve.open"]:
            self.findings.append({
                "rule_id": "PY_DESER_01",
                "title": "Insecure Deserialization",
                "cwe": "CWE-502",
                "owasp": OWASP_MAP["CWE-502"],
                "severity": "HIGH",
                "confidence": 0.90,
                "line": line_no,
                "source": {"line": line_no, "expression": line_str},
                "sink": {"line": line_no, "expression": line_str},
                "data_flow": [line_str],
                "reason": f"'{func_name}' can execute arbitrary code during object deserialization.",
                "impact": "Remote code execution when untrusted data is deserialized.",
                "recommendation": "Use safe alternatives like json.loads() or yaml.safe_load()."
            })

        # 5. Path Traversal (open, send_file with concatenation)
        elif func_name in ["open", "send_file", "flask.send_file", "os.path.join"]:
            if node.args:
                first_arg = node.args[0]
                is_dynamic_path = isinstance(first_arg, (ast.BinOp, ast.JoinedStr)) or self._is_tainted_node(first_arg)
                if is_dynamic_path and func_name != "os.path.join":
                    self.findings.append({
                        "rule_id": "PY_PATH_01",
                        "title": "Path Traversal",
                        "cwe": "CWE-22",
                        "owasp": OWASP_MAP["CWE-22"],
                        "severity": "HIGH",
                        "confidence": 0.88,
                        "line": line_no,
                        "source": {"line": line_no, "expression": line_str},
                        "sink": {"line": line_no, "expression": line_str},
                        "data_flow": [line_str],
                        "reason": f"File operation '{func_name}' uses dynamic path constructed without containment validation.",
                        "impact": "Attacker can supply '../' relative paths to access sensitive system files (e.g. /etc/passwd).",
                        "recommendation": "Validate path using os.path.abspath() and ensure it starts with the intended base directory."
                    })

        self.generic_visit(node)


def analyze_python_ast(code: str) -> List[Dict[str, Any]]:
    findings = []
    lines = code.splitlines()
    try:
        tree = ast.parse(code)
        visitor = PythonASTAnalyzer(lines)
        visitor.visit(tree)
        findings.extend(visitor.findings)
    except SyntaxError:
        # Fallback to regex if parsing fails due to syntax error
        pass
    
    # Supplementary regex rules for Flask / Debug mode / Weak Crypto
    regex_rules = [
        (r"app\.run\s*\([^)]*debug\s*=\s*True[^)]*\)", "PY_FLASK_DEBUG", "Flask App Running in Debug Mode", "CWE-489", "MEDIUM", 0.95, "Debug mode exposes interactive debugger enabling arbitrary code execution."),
        (r"hashlib\.md5\(|hashlib\.sha1\(", "PY_WEAK_CRYPTO", "Use of Weak Cryptographic Hash", "CWE-327", "MEDIUM", 0.90, "MD5 and SHA-1 are cryptographically broken and vulnerable to collision attacks. Use SHA-256 or bcrypt/argon2.")
    ]

    for line_idx, line in enumerate(lines, 1):
        for pattern, r_id, title, cwe, sev, conf, reason in regex_rules:
            if re.search(pattern, line):
                # Avoid duplicate line findings
                if not any(f["line"] == line_idx and f["cwe"] == cwe for f in findings):
                    findings.append({
                        "rule_id": r_id,
                        "title": title,
                        "cwe": cwe,
                        "owasp": OWASP_MAP.get(cwe, "A05:2021 - Security Misconfiguration"),
                        "severity": sev,
                        "confidence": conf,
                        "line": line_idx,
                        "source": {"line": line_idx, "expression": line.strip()},
                        "sink": {"line": line_idx, "expression": line.strip()},
                        "data_flow": [line.strip()],
                        "reason": reason,
                        "impact": "Potential security exposure or cryptographic weakness.",
                        "recommendation": "Follow secure coding guidelines for this API."
                    })

    return findings
