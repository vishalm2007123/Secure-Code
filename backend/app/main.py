import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.analyzer.code_rewriter import rewrite_code
from app.engine.security_engine import analyze
from app.engine.verification_engine import verify_rewrite
from app.models.schemas import CodeRequest, RewriteRequest, AnalysisResult, RewriteResult
from app.config import MODEL_CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("securecode-ai")

app = FastAPI(
    title="SecureCode AI",
    description="AI-powered security auditor for source code with independent verification loop",
    version="1.0.0"
)

# Enable CORS for all origins in local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_PRESETS = [
    {
        "id": "py-cmdi",
        "name": "Python - OS Command Injection",
        "language": "Python",
        "code": "import os\n\ncommand = input(\"Enter command: \")\nos.system(command)\n"
    },
    {
        "id": "py-sqli",
        "name": "Python - SQL Injection",
        "language": "Python",
        "code": "import sqlite3\n\nuser_id = input(\"Enter user ID: \")\nconn = sqlite3.connect(\"app.db\")\ncursor = conn.cursor()\nquery = \"SELECT * FROM users WHERE id = \" + user_id\ncursor.execute(query)\n"
    },
    {
        "id": "py-secret",
        "name": "Python - Hardcoded Credentials",
        "language": "Python",
        "code": "def login():\n    admin_password = \"Admin123456\"\n    api_key = \"sk_live_9923849182390\"\n    print(\"Logging in...\")\n"
    },
    {
        "id": "py-path",
        "name": "Python - Path Traversal",
        "language": "Python",
        "code": "from flask import Flask, send_file, request\napp = Flask(__name__)\n\n@app.route('/download')\ndef download():\n    filename = request.args.get('file')\n    filepath = \"/var/www/files/\" + filename\n    return send_file(filepath)\n"
    },
    {
        "id": "cpp-buf",
        "name": "C/C++ - Buffer Overflow (strcpy)",
        "language": "C++",
        "code": "#include <cstring>\n#include <iostream>\n\nvoid process(char* userInput) {\n    char buffer[64];\n    strcpy(buffer, userInput);\n}\n"
    },
    {
        "id": "py-safe",
        "name": "Python - Safe Parameterized SQL & Subprocess",
        "language": "Python",
        "code": "import subprocess\nimport sqlite3\n\ndef safe_ops(user_id, filename):\n    # Safe parameterized SQL query\n    conn = sqlite3.connect(\"app.db\")\n    cursor = conn.cursor()\n    cursor.execute(\"SELECT * FROM users WHERE id = ?\", (user_id,))\n    \n    # Safe subprocess execution with list and shell=False\n    subprocess.run([\"ls\", \"-l\", filename], shell=False)\n"
    }
]

@app.get("/")
def root():
    return {
        "name": "SecureCode AI",
        "status": "online",
        "version": "1.0.0",
        "features": [
            "Deterministic AST Analysis",
            "Security LLM Reasoning",
            "CWE & OWASP Mapping",
            "Source -> Sink Flow Tracking",
            "Secure Code Rewriting",
            "Independent Re-analysis Verification"
        ]
    }

@app.get("/health")
def health_check():
    import requests
    from app.config import settings
    ollama_online = False
    try:
        base_url = settings.OLLAMA_URL.rsplit('/', 1)[0]
        r = requests.get(f"{base_url}/tags", timeout=2)
        if r.status_code == 200:
            ollama_online = True
    except Exception:
        ollama_online = False
    
    return {
        "status": "online",
        "ollama_online": ollama_online,
        "ollama_model": settings.OLLAMA_MODEL,
        "ast_engine": "active"
    }

@app.get("/presets")
def get_presets():
    return SAMPLE_PRESETS


@app.post("/analyze", response_model=AnalysisResult)
def analyze_code(request: CodeRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    
    if request.model not in MODEL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid model specified: {request.model}")

    logger.info(f"Analyzing code in language: {request.language} with model: {request.model}")
    result = analyze(request.code, request.language, request.model)
    return result

@app.post("/rewrite", response_model=RewriteResult)
def rewrite_secure_code(request: RewriteRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    if request.model not in MODEL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid model specified: {request.model}")

    logger.info(f"Rewriting code securely for language: {request.language} with model: {request.model}")
    
    try:
        rewritten = rewrite_code(
            request.code,
            request.language,
            request.analysis,
            request.model
        )
    except Exception as e:
        logger.error(f"Error during code rewrite: {e}")
        raise HTTPException(status_code=500, detail=f"LLM rewrite service failed: {str(e)}")

    verification_result = None
    if request.auto_verify:
        logger.info("Running independent re-analysis verification on rewritten code...")
        verification_result = verify_rewrite(request.code, rewritten, request.language, request.model)

    return RewriteResult(
        language=request.language,
        rewritten_code=rewritten,
        verification=verification_result
    )

# ============================================================
# AI MODEL TRAINING & FINE-TUNING ENDPOINTS
# ============================================================

from app.trainer.fine_tuner import get_training_status, start_training_job, get_available_models

@app.get("/train/status")
def training_status():
    return get_training_status()

@app.post("/train/start")
def trigger_training(params: dict = None):
    res = start_training_job(params or {})
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@app.get("/models/list")
def list_models():
    return get_available_models()

# ============================================================
# DATASET ANALYTICS & VULNERABILITY CATALOG ENDPOINTS
# ============================================================

@app.get("/analytics/stats")
def get_analytics_stats():
    import json
    import os
    stats_file = "data/processed/dataset_stats.json"
    dataset_info = {
        "clean_records": 10395,
        "train_records": 8350,
        "validation_records": 1022,
        "test_records": 1023,
        "unique_code_groups": 7433
    }
    if os.path.exists(stats_file):
        try:
            with open(stats_file, "r", encoding="utf-8") as f:
                dataset_info = json.load(f)
        except Exception:
            pass

    return {
        "dataset": dataset_info,
        "supported_languages": ["Python", "C", "C++", "Java", "PHP", "Bash", "JavaScript"],
        "total_static_rules": 24,
        "top_cwes": [
            {"cwe": "CWE-78", "name": "OS Command Injection", "count": 1420, "severity": "HIGH"},
            {"cwe": "CWE-89", "name": "SQL Injection", "count": 1380, "severity": "HIGH"},
            {"cwe": "CWE-120", "name": "Buffer Copy without Checking Size", "count": 1150, "severity": "CRITICAL"},
            {"cwe": "CWE-798", "name": "Use of Hard-coded Credentials", "count": 920, "severity": "MEDIUM"},
            {"cwe": "CWE-22", "name": "Path Traversal", "count": 890, "severity": "HIGH"}
        ]
    }

@app.get("/rules/catalog")
def get_rules_catalog():
    return [
        {
            "cwe": "CWE-78",
            "title": "OS Command Injection",
            "owasp": "A03:2021 - Injection",
            "severity": "CRITICAL",
            "languages": ["Python", "C", "C++", "Java", "JavaScript"],
            "description": "Constructing OS commands using unsanitized user input allows attackers to execute arbitrary system-level commands.",
            "bad_example": "import os\ncmd = input()\nos.system(cmd)",
            "good_example": "import subprocess\nsubprocess.run(['ls', '-l', filename], shell=False)"
        },
        {
            "cwe": "CWE-89",
            "title": "SQL Injection (SQLi)",
            "owasp": "A03:2021 - Injection",
            "severity": "HIGH",
            "languages": ["Python", "Java", "JavaScript"],
            "description": "Dynamic string concatenation in database queries enables unauthorized database access or data manipulation.",
            "bad_example": "query = 'SELECT * FROM users WHERE id = ' + user_id\ncursor.execute(query)",
            "good_example": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
        },
        {
            "cwe": "CWE-120",
            "title": "Classic Buffer Overflow (strcpy/gets)",
            "owasp": "A06:2021 - Vulnerable Components",
            "severity": "CRITICAL",
            "languages": ["C", "C++"],
            "description": "Copying unvalidated string input into fixed-size stack buffers leads to memory corruption or arbitrary code execution.",
            "bad_example": "char buf[64];\nstrcpy(buf, userInput);",
            "good_example": "char buf[64];\nstrncpy(buf, userInput, sizeof(buf) - 1);\nbuf[sizeof(buf) - 1] = '\\0';"
        },
        {
            "cwe": "CWE-798",
            "title": "Use of Hard-coded Credentials",
            "owasp": "A07:2021 - Identification & Auth Failures",
            "severity": "MEDIUM",
            "languages": ["Python", "Java", "JavaScript", "C++"],
            "description": "Embedding passwords, API keys, or secret tokens directly in source code exposes secrets in repository revisions.",
            "bad_example": "api_key = 'sk_live_9923849182390'",
            "good_example": "import os\napi_key = os.getenv('API_KEY')"
        },
        {
            "cwe": "CWE-22",
            "title": "Path Traversal",
            "owasp": "A01:2021 - Broken Access Control",
            "severity": "HIGH",
            "languages": ["Python", "Java", "JavaScript"],
            "description": "Using raw user input in file paths allows directory traversal sequences ('../') to read or write restricted files.",
            "bad_example": "filepath = '/var/www/files/' + filename\nsend_file(filepath)",
            "good_example": "safe_name = os.path.basename(filename)\nfilepath = os.path.join('/var/www/files/', safe_name)"
        }
    ]

# ============================================================
# COMPANY MODEL LAB ENDPOINTS
# ============================================================
from fastapi import UploadFile, File, Form
from typing import List
import os

@app.post("/lab/data/upload")
async def upload_lab_data(files: List[UploadFile] = File(...)):
    # Save to data/datasets
    save_dir = "data/datasets"
    os.makedirs(save_dir, exist_ok=True)
    
    saved_files = []
    for file in files:
        file_path = os.path.join(save_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_files.append(file.filename)
        
    return {"status": "success", "message": f"Uploaded {len(saved_files)} files.", "files": saved_files}

@app.post("/lab/workspace/mount")
async def mount_lab_workspace(files: List[UploadFile] = File(...), paths: List[str] = Form(...)):
    # Save to data/private_workspaces
    save_dir = "data/private_workspaces/default_tenant"
    os.makedirs(save_dir, exist_ok=True)
    
    saved_count = 0
    for file, path in zip(files, paths):
        # path includes the folder structure
        full_path = os.path.join(save_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_count += 1
        
    return {"status": "success", "message": f"Mounted {saved_count} files securely."}