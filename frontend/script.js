// ============================================================
// SecureCode AI - Professional Dashboard Logic
// ============================================================

// API_URL is defined in nav.js

// DOM ELEMENTS
const themeToggleBtn = document.getElementById("themeToggle");
const presetSelect = document.getElementById("presetSelect");
const languageSelect = document.getElementById("language");
const codeInput = document.getElementById("code");
const clearCodeBtn = document.getElementById("clearCodeBtn");
const analyzeButton = document.getElementById("analyzeButton");
const uploadCodeBtn = document.getElementById("uploadCodeBtn");
const auditCodeUploadInput = document.getElementById("auditCodeUploadInput");

const resultsSection = document.getElementById("results");
const securityScoreVal = document.getElementById("securityScoreVal");
const scoreRingProgress = document.getElementById("scoreRingProgress");
const vulnerabilityBadge = document.getElementById("vulnerabilityBadge");

const countCritical = document.getElementById("countCritical");
const countHigh = document.getElementById("countHigh");
const countMedium = document.getElementById("countMedium");
const countLow = document.getElementById("countLow");

const findingsTabCount = document.getElementById("findingsTabCount");
const correlatedFindingsList = document.getElementById("correlatedFindingsList");
const staticResults = document.getElementById("staticResults");
const llmResults = document.getElementById("llmResults");

const rewriteActionBanner = document.getElementById("rewriteActionBanner");
const rewriteButton = document.getElementById("rewriteButton");

const rewrittenSection = document.getElementById("rewrittenSection");
const verificationBanner = document.getElementById("verificationBanner");
const verificationIconPass = document.getElementById("verificationIconPass");
const verificationIconFail = document.getElementById("verificationIconFail");
const verifStatusBadge = document.getElementById("verifStatusBadge");
const verifSummaryText = document.getElementById("verifSummaryText");

const originalCompareCode = document.getElementById("originalCompareCode");
const rewrittenCode = document.getElementById("rewrittenCode");
const copyFixBtn = document.getElementById("copyFixBtn");
const reanalyzeButton = document.getElementById("reanalyzeButton");
const exportReportBtn = document.getElementById("exportReportBtn");

const statusLabel = document.querySelector(".status-label");
const statusDot = document.querySelector(".status-dot");

let lastAnalysisResult = null;
let activeSeverityFilter = "ALL";

// ============================================================
// INITIALIZATION & PRESETS
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    loadPresets();
    setupTabNavigation();
    setupFilters();
    setupReportExport();
    setupTrainerDashboard();
    fetchAnalyticsStats();
    loadRuleCatalog();
});



// Load Presets from Backend
async function loadPresets() {
    try {
        const res = await fetch(`${API_URL}/presets`);
        if (res.ok) {
            const presets = await res.json();
            if (presetSelect) {
                presetSelect.innerHTML = `<option value="" disabled selected>Select a sample test case...</option>`;
                presets.forEach(p => {
                    const opt = document.createElement("option");
                    opt.value = p.id;
                    opt.textContent = `${p.name}`;
                    opt.dataset.code = p.code;
                    opt.dataset.language = p.language;
                    presetSelect.appendChild(opt);
                });
            }
        }
    } catch (e) {
        console.warn("Could not fetch presets from backend, using local fallback presets.");
        populateFallbackPresets();
    }
}

function populateFallbackPresets() {
    const fallbacks = [
        {
            name: "Python - OS Command Injection",
            language: "Python",
            code: "import os\n\ncmd = input(\"Enter command: \")\nos.system(cmd)\n"
        },
        {
            name: "Python - SQL Injection",
            language: "Python",
            code: "import sqlite3\n\nuser_id = input(\"Enter user ID: \")\nconn = sqlite3.connect(\"app.db\")\ncursor = conn.cursor()\nquery = \"SELECT * FROM users WHERE id = \" + user_id\ncursor.execute(query)\n"
        },
        {
            name: "Python - Hardcoded Credentials",
            language: "Python",
            code: "def login():\n    admin_password = \"Admin123456\"\n    api_key = \"sk_live_9923849182390\"\n    print(\"Logging in...\")\n"
        },
        {
            name: "C/C++ - Buffer Overflow (strcpy)",
            language: "C++",
            code: "#include <cstring>\n\nvoid process(char* userInput) {\n    char buffer[64];\n    strcpy(buffer, userInput);\n}\n"
        },
        {
            name: "Python - Safe Parameterized Code",
            language: "Python",
            code: "import subprocess\nimport sqlite3\n\ndef safe_ops(user_id, filename):\n    conn = sqlite3.connect(\"app.db\")\n    cursor = conn.cursor()\n    cursor.execute(\"SELECT * FROM users WHERE id = ?\", (user_id,))\n    subprocess.run([\"ls\", \"-l\", filename], shell=False)\n"
        }
    ];

    if (presetSelect) {
        presetSelect.innerHTML = `<option value="" disabled selected>Select a sample test case...</option>`;
        fallbacks.forEach((f, idx) => {
            const opt = document.createElement("option");
            opt.value = idx;
            opt.textContent = f.name;
            opt.dataset.code = f.code;
            opt.dataset.language = f.language;
            presetSelect.appendChild(opt);
        });
    }
}

if (presetSelect) {
    presetSelect.addEventListener("change", (e) => {
        const selected = presetSelect.options[presetSelect.selectedIndex];
        if (selected && selected.dataset.code) {
            codeInput.value = selected.dataset.code;
            languageSelect.value = selected.dataset.language;
        }
    });
}

if (clearCodeBtn) {
    clearCodeBtn.addEventListener("click", () => {
        codeInput.value = "";
        resultsSection.classList.add("hidden");
        rewrittenSection.classList.add("hidden");
    });
}

// ============================================================
// TAB NAVIGATION
// ============================================================

function setupTabNavigation() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            const targetTab = btn.getAttribute("data-tab");
            document.getElementById(targetTab).classList.add("active");
        });
    });
}

// ============================================================
// UPLOAD & RUN AUDIT ANALYSIS
// ============================================================

if (uploadCodeBtn && auditCodeUploadInput) {
    uploadCodeBtn.addEventListener("click", () => auditCodeUploadInput.click());

    auditCodeUploadInput.addEventListener("change", (e) => {
        const files = e.target.files;
        if (!files.length) return;
        const file = files[0]; // Take the first file
        const reader = new FileReader();
        reader.onload = (ev) => {
            codeInput.value = ev.target.result;
            // Guess language based on extension
            const ext = file.name.split('.').pop().toLowerCase();
            if (ext === 'py') languageSelect.value = "Python";
            else if (ext === 'c') languageSelect.value = "C";
            else if (ext === 'cpp' || ext === 'cc' || ext === 'cxx' || ext === 'h' || ext === 'hpp') languageSelect.value = "C++";
            else if (ext === 'java') languageSelect.value = "Java";
            else if (ext === 'php') languageSelect.value = "PHP";
            else if (ext === 'js' || ext === 'ts' || ext === 'jsx' || ext === 'tsx') languageSelect.value = "JavaScript";
            else if (ext === 'sh' || ext === 'bash') languageSelect.value = "Bash";
            
            // Auto-analyze
            analyzeButton.click();
        };
        reader.readAsText(file);
    });
}

if (analyzeButton) {
    analyzeButton.addEventListener("click", async () => {
        const code = codeInput.value.trim();
    const language = languageSelect.value;
    const model = document.getElementById("aiModel").value;

    if (!code) {
        alert("Please enter or select source code to analyze.");
        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.innerHTML = `<span class="spinner"></span> Auditing Code...`;

    resultsSection.classList.add("hidden");
    rewrittenSection.classList.add("hidden");

    try {
        const res = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, language, model })
        });

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Server returned ${res.status}: ${errText}`);
        }

        const data = await res.json();
        lastAnalysisResult = data;
        renderAnalysisResults(data);

    } catch (err) {
        console.error("Audit error:", err);
        alert(`Analysis Error:\n${err.message}`);
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Run Security Audit`;
    }
    });
}

// Render Audit Dashboard
function renderAnalysisResults(data) {
    resultsSection.classList.remove("hidden");

    // 1. Update Security Score Ring & Badge
    const score = data.security_score !== undefined ? data.security_score : (data.vulnerable ? 25 : 100);
    securityScoreVal.textContent = score;

    // Ring dashoffset calculation (max dasharray = 264)
    const offset = 264 - (264 * score) / 100;
    scoreRingProgress.style.strokeDashoffset = offset;

    if (score >= 90) {
        scoreRingProgress.style.stroke = "var(--state-safe)";
        vulnerabilityBadge.className = "vuln-badge clean";
        vulnerabilityBadge.textContent = "CODE CLEAN";
    } else if (score >= 60) {
        scoreRingProgress.style.stroke = "var(--severity-medium)";
        vulnerabilityBadge.className = "vuln-badge vulnerable";
        vulnerabilityBadge.textContent = "MODERATE RISK";
    } else {
        scoreRingProgress.style.stroke = "var(--severity-critical)";
        vulnerabilityBadge.className = "vuln-badge vulnerable";
        vulnerabilityBadge.textContent = "CRITICAL RISK DETECTED";
    }

    // 2. Metrics Counter
    const findings = data.findings || [];
    let counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    findings.forEach(f => {
        const sev = (f.severity || "MEDIUM").toUpperCase();
        if (counts[sev] !== undefined) counts[sev]++;
        else counts.MEDIUM++;
    });

    countCritical.textContent = counts.CRITICAL;
    countHigh.textContent = counts.HIGH;
    countMedium.textContent = counts.MEDIUM;
    countLow.textContent = counts.LOW;

    findingsTabCount.textContent = findings.length;

    // 3. Render Correlated Findings List
    renderFindingsList(findings);

    // 4. Render Deterministic AST Tab
    renderStaticResults(data.static_analysis);

    // 5. Render LLM Raw Reasoning Tab
    llmResults.textContent = data.llm_analysis || "No raw LLM output recorded.";

    // Smooth Scroll to Results
    resultsSection.scrollIntoView({ behavior: "smooth" });
}

function setupFilters() {
    const filterBtns = [
        { id: "filterCriticalBtn", sev: "CRITICAL" },
        { id: "filterHighBtn", sev: "HIGH" },
        { id: "filterMediumBtn", sev: "MEDIUM" },
        { id: "filterLowBtn", sev: "LOW" }
    ];

    filterBtns.forEach(item => {
        const btn = document.getElementById(item.id);
        if (btn) {
            btn.addEventListener("click", () => {
                if (activeSeverityFilter === item.sev) {
                    activeSeverityFilter = "ALL";
                    btn.classList.remove("active-filter");
                } else {
                    activeSeverityFilter = item.sev;
                    filterBtns.forEach(b => {
                        const el = document.getElementById(b.id);
                        if (el) el.classList.remove("active-filter");
                    });
                    btn.classList.add("active-filter");
                }

                if (lastAnalysisResult) {
                    renderFindingsList(lastAnalysisResult.findings || []);
                }
            });
        }
    });
}

function setupReportExport() {
    if (!exportReportBtn) return;
    exportReportBtn.addEventListener("click", () => {
        if (!lastAnalysisResult) {
            alert("Please run a security audit first before exporting report.");
            return;
        }

        const data = lastAnalysisResult;
        const timestamp = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '');
        
        let report = `# 🛡️ SecureCode AI - Security Audit Report\n`;
        report += `**Generated**: ${timestamp}\n`;
        report += `**Language**: ${data.language || 'Unknown'}\n`;
        report += `**Security Score**: ${data.security_score !== undefined ? data.security_score : (data.vulnerable ? 25 : 100)} / 100\n`;
        report += `**Audit Status**: ${data.vulnerable ? 'VULNERABILITIES DETECTED' : 'PASSED (CLEAN)'}\n\n`;

        report += `## Executive Summary\n`;
        const findings = data.findings || [];
        report += `Total Findings: ${findings.length}\n\n`;

        report += `## Detailed Findings\n`;
        if (findings.length === 0) {
            report += `No vulnerabilities identified in analyzed code.\n\n`;
        } else {
            findings.forEach((f, idx) => {
                report += `### Finding ${idx + 1}: ${f.title}\n`;
                report += `- **Severity**: ${f.severity}\n`;
                report += `- **CWE**: ${f.cwe || 'N/A'}\n`;
                report += `- **OWASP**: ${f.owasp || 'N/A'}\n`;
                report += `- **Confidence**: ${Math.round((f.confidence || 0.9) * 100)}%\n`;
                report += `- **Cause**: ${f.reason || ''}\n`;
                if (f.impact) report += `- **Impact**: ${f.impact}\n`;
                if (f.data_flow && f.data_flow.length) {
                    report += `- **Source -> Sink Flow**: ${f.data_flow.join(" -> ")}\n`;
                }
                if (f.recommendation) report += `- **Remediation**: ${f.recommendation}\n`;
                report += `\n---\n\n`;
            });
        }

        report += `## Raw Security LLM Reasoning\n`;
        report += `\`\`\`text\n${data.llm_analysis || 'No raw output'}\n\`\`\`\n`;

        // Trigger Download
        const blob = new Blob([report], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `SecureCode_AI_Report_${Date.now()}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}

function renderFindingsList(findings) {
    correlatedFindingsList.innerHTML = "";

    let filtered = findings || [];
    if (activeSeverityFilter !== "ALL") {
        filtered = filtered.filter(f => (f.severity || "").toUpperCase() === activeSeverityFilter);
    }

    if (!filtered || filtered.length === 0) {
        correlatedFindingsList.innerHTML = `
            <div class="finding-card LOW" style="border-left-color: var(--state-safe);">
                <div class="finding-header">
                    <div class="finding-title-group">
                        <span class="finding-title">${activeSeverityFilter !== "ALL" ? `No ${activeSeverityFilter} Severity Vulnerabilities` : 'No Vulnerabilities Identified'}</span>
                    </div>
                </div>
                <div class="finding-body">
                    <p>Static AST analysis and Security LLM reasoning found no matching flaws in this code snippet.</p>
                </div>
            </div>
        `;
        return;
    }


    filtered.forEach(f => {
        const card = document.createElement("div");
        const sev = (f.severity || "HIGH").toUpperCase();
        card.className = `finding-card ${sev}`;

        const cweNum = f.cwe ? f.cwe.replace("CWE-", "") : "";
        const cweUrl = cweNum ? `https://cwe.mitre.org/data/definitions/${cweNum}.html` : "#";

        const confidencePct = Math.round((f.confidence || 0.9) * 100);

        let dataFlowHtml = "";
        if (f.data_flow && f.data_flow.length > 0) {
            dataFlowHtml = `
                <div class="data-flow-container">
                    <div class="data-flow-title">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                        Source → Sink Taint Flow:
                    </div>
                    <div class="flow-steps">
                        ${f.data_flow.map((expr, idx) => `
                            <div class="flow-step ${idx === 0 ? 'source' : (idx === f.data_flow.length - 1 ? 'sink' : '')}">
                                <span class="step-label">${idx === 0 ? 'SOURCE' : (idx === f.data_flow.length - 1 ? 'SINK' : 'PROP')}</span>
                                <code>${escapeHtml(expr)}</code>
                            </div>
                            ${idx < f.data_flow.length - 1 ? '<span class="flow-arrow">&rarr;</span>' : ''}
                        `).join("")}
                    </div>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="finding-header">
                <div class="finding-title-group">
                    <span class="finding-title">${escapeHtml(f.title)}</span>
                    ${f.cwe ? `<a href="${cweUrl}" target="_blank" class="cwe-tag">${escapeHtml(f.cwe)}</a>` : ''}
                    ${f.owasp ? `<span class="owasp-tag">${escapeHtml(f.owasp)}</span>` : ''}
                </div>
                <div class="finding-meta">
                    <span class="severity-badge ${sev}">${sev}</span>
                    <div class="confidence-bar-container" title="${confidencePct}% Analysis Confidence">
                        <div class="confidence-track">
                            <div class="confidence-fill" style="width: ${confidencePct}%"></div>
                        </div>
                        <span>${confidencePct}%</span>
                    </div>
                </div>
            </div>

            <div class="finding-body">
                <p><strong>Technical Cause:</strong> ${escapeHtml(f.reason || f.description || "")}</p>
                ${f.impact ? `<p><strong>Potential Impact:</strong> ${escapeHtml(f.impact)}</p>` : ''}
                ${dataFlowHtml}
                ${f.recommendation ? `
                    <div class="finding-remediation">
                        <div class="remediation-title">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                            Recommended Security Fix:
                        </div>
                        <div>${escapeHtml(f.recommendation)}</div>
                    </div>
                ` : ''}
            </div>
        `;

        correlatedFindingsList.appendChild(card);
    });
}

function renderStaticResults(staticFindings) {
    staticResults.innerHTML = "";

    if (!staticFindings || staticFindings.length === 0) {
        staticResults.innerHTML = `<div class="finding-card"><p>No rule-based AST findings.</p></div>`;
        return;
    }

    staticFindings.forEach(f => {
        const item = document.createElement("div");
        item.className = "finding-card";
        item.innerHTML = `
            <h4>${escapeHtml(f.title || f.vulnerability)} (${escapeHtml(f.cwe)})</h4>
            <p>Line ${f.line}: ${escapeHtml(f.description || f.reason)}</p>
        `;
        staticResults.appendChild(item);
    });
}

// ============================================================
// SECURE REWRITE & INDEPENDENT VERIFICATION
// ============================================================

if (rewriteButton) {
    rewriteButton.addEventListener("click", async () => {
        const code = codeInput.value.trim();
    const language = languageSelect.value;
    const model = document.getElementById("aiModel").value;
    const analysis = llmResults.textContent;

    if (!code) {
        alert("No code available to rewrite.");
        return;
    }

    rewriteButton.disabled = true;
    rewriteButton.innerHTML = `<span class="spinner"></span> Rewriting & Verifying...`;

    try {
        const res = await fetch(`${API_URL}/rewrite`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                code: code,
                language: language,
                analysis: analysis,
                model: model,
                auto_verify: true
            })
        });

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Server error ${res.status}: ${errText}`);
        }

        const data = await res.json();
        renderRewriteResult(data, code);

    } catch (err) {
        console.error("Rewrite error:", err);
        alert(`Rewrite Error:\n${err.message}`);
    } finally {
        rewriteButton.disabled = false;
        rewriteButton.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg> Generate & Verify Secure Rewrite`;
    }
    });
}

function renderRewriteResult(data, origCode) {
    rewrittenSection.classList.remove("hidden");
    originalCompareCode.value = origCode;
    rewrittenCode.value = data.rewritten_code;

    // Render Independent Verification Status
    const v = data.verification;
    if (v) {
        if (v.status === "PASS") {
            verificationBanner.className = "verification-banner pass";
            verificationIconPass.classList.remove("hidden");
            verificationIconFail.classList.add("hidden");
            verifStatusBadge.className = "verif-status-badge pass";
            verifStatusBadge.textContent = "VERIFIED SECURE";
            verifSummaryText.textContent = v.summary || "All security vulnerabilities were independently verified as resolved.";
        } else {
            verificationBanner.className = "verification-banner fail";
            verificationIconPass.classList.add("hidden");
            verificationIconFail.classList.remove("hidden");
            verifStatusBadge.className = "verif-status-badge fail";
            verifStatusBadge.textContent = "VERIFICATION FAILED";
            verifSummaryText.textContent = v.summary || "Unresolved security issues were detected in rewritten code.";
        }
    }

    rewrittenSection.scrollIntoView({ behavior: "smooth" });
}

// Copy Secure Code
if (copyFixBtn) {
    copyFixBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(rewrittenCode.value);
    copyFixBtn.textContent = "Copied!";
    setTimeout(() => { copyFixBtn.textContent = "Copy"; }, 2000);
    });
}

// Re-Audit Modified Fix
if (reanalyzeButton) {
    reanalyzeButton.addEventListener("click", async () => {
    const code = rewrittenCode.value.trim();
    const language = languageSelect.value;

    if (!code) return;

    codeInput.value = code;
    analyzeButton.click();
    });
}


// ============================================================
// AI MODEL STUDIO & FINE-TUNING DASHBOARD LOGIC
// ============================================================

let trainerPollInterval = null;

function setupTrainerDashboard() {
    const trainForm = document.getElementById("trainForm");
    const startTrainBtn = document.getElementById("startTrainBtn");

    if (trainForm) {
        trainForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const base_model = document.getElementById("baseModelSelect").value;
            const epochs = parseInt(document.getElementById("epochsInput").value) || 3;
            const learning_rate = parseFloat(document.getElementById("lrInput").value) || 0.0002;
            const batch_size = parseInt(document.getElementById("batchSizeInput").value) || 8;
            const sample_limit = parseInt(document.getElementById("sampleLimitInput").value) || 150;

            startTrainBtn.disabled = true;
            startTrainBtn.innerHTML = `<span class="spinner"></span> Launching Job...`;

            try {
                const res = await fetch(`${API_URL}/train/start`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        base_model,
                        epochs,
                        learning_rate,
                        batch_size,
                        sample_limit
                    })
                });

                if (!res.ok) {
                    const errData = await res.json();
                    throw new Error(errData.detail || "Failed to start training job.");
                }

                startPollTrainerStatus();
            } catch (err) {
                alert(`Training Error:\n${err.message}`);
                startTrainBtn.disabled = false;
                startTrainBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Launch Fine-Tuning Job`;
            }
        });
    }

    // Initial load
    fetchTrainerStatus();
    loadModelRegistry();
}

function startPollTrainerStatus() {
    if (trainerPollInterval) clearInterval(trainerPollInterval);
    trainerPollInterval = setInterval(fetchTrainerStatus, 800);
}

async function fetchTrainerStatus() {
    try {
        const res = await fetch(`${API_URL}/train/status`);
        if (res.ok) {
            const data = await res.json();
            updateTrainerUI(data);

            if (data.status === "COMPLETED" || data.status === "FAILED") {
                if (trainerPollInterval) {
                    clearInterval(trainerPollInterval);
                    trainerPollInterval = null;
                }
                const startTrainBtn = document.getElementById("startTrainBtn");
                if (startTrainBtn) {
                    startTrainBtn.disabled = false;
                    startTrainBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Launch Fine-Tuning Job`;
                }
                loadModelRegistry();
            } else if (data.status === "RUNNING" || data.status === "INITIALIZING") {
                if (!trainerPollInterval) {
                    startPollTrainerStatus();
                }
            }
        }
    } catch (e) {
        console.warn("Could not fetch trainer status:", e);
    }
}

function updateTrainerUI(data) {
    const statusBadge = document.getElementById("trainStatusBadge");
    const progressFill = document.getElementById("trainerProgressFill");
    const stepLabel = document.getElementById("progressStepLabel");
    const epochLabel = document.getElementById("progressEpochLabel");
    const lossVal = document.getElementById("tLossVal");
    const accVal = document.getElementById("tAccVal");
    const f1Val = document.getElementById("tF1Val");
    const terminalBody = document.getElementById("trainTerminal");

    const status = data.status || "IDLE";
    if (statusBadge) {
        statusBadge.className = `train-badge ${status.toLowerCase()}`;
        statusBadge.textContent = `STATUS: ${status}`;
    }

    const pct = data.progress_percent !== undefined ? data.progress_percent : 0.0;
    if (progressFill) progressFill.style.width = `${pct}%`;
    if (stepLabel) stepLabel.textContent = `Progress: ${pct}% (${data.current_step || 0}/${data.total_steps || 0} steps)`;
    if (epochLabel) epochLabel.textContent = `Epoch: ${data.current_epoch || 0} / ${data.total_epochs || 0}`;

    if (lossVal) lossVal.textContent = data.current_loss !== undefined ? data.current_loss.toFixed(4) : "0.0000";
    if (accVal) accVal.textContent = data.accuracy !== undefined ? `${data.accuracy}%` : "0.0%";
    if (f1Val) f1Val.textContent = data.f1_score !== undefined ? data.f1_score.toFixed(3) : "0.000";

    if (terminalBody && data.logs) {
        terminalBody.textContent = data.logs.join("\n");
        terminalBody.scrollTop = terminalBody.scrollHeight;
    }
}

async function loadModelRegistry() {
    try {
        const res = await fetch(`${API_URL}/models/list`);
        if (res.ok) {
            const models = await res.json();
            
            const registryContainer = document.getElementById("modelRegistryList");
            if (registryContainer) {
                renderModelRegistryCards(models);
            }
            
            // Populate Dropdowns with fine-tuned models
            const aiModelSelect = document.getElementById("aiModel");
            const workspaceModelSelect = document.getElementById("workspaceModelSelect");
            
            const appendOptions = (selectElem) => {
                if (!selectElem) return;
                // Only add models that aren't already in the dropdown
                const existingVals = Array.from(selectElem.options).map(o => o.value);
                models.forEach(m => {
                    if (m.fine_tuned && !existingVals.includes(m.id)) {
                        const opt = document.createElement("option");
                        opt.value = m.id;
                        opt.textContent = `${m.name} (Custom)`;
                        selectElem.appendChild(opt);
                    }
                });
            };
            
            appendOptions(aiModelSelect);
            appendOptions(workspaceModelSelect);
        }
    } catch (e) {
        console.warn("Could not fetch model registry:", e);
    }
}

function renderModelRegistryCards(models) {
    const registryContainer = document.getElementById("modelRegistryList");
    if (!registryContainer) return;

    registryContainer.innerHTML = "";
    models.forEach(m => {
        const card = document.createElement("div");
        card.className = "registry-card-item";
        card.innerHTML = `
            <div class="reg-card-header">
                <span class="reg-card-title">${escapeHtml(m.name)}</span>
                <span class="reg-card-type">${escapeHtml(m.type)}</span>
            </div>
            <div class="reg-card-meta">
                <div><strong>ID:</strong> <code>${escapeHtml(m.id)}</code></div>
                <div><strong>Size:</strong> ${escapeHtml(m.size)} &bull; <strong>Status:</strong> ${escapeHtml(m.status)}</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                    ${m.accuracy ? `<span class="private-badge" style="background: rgba(46, 204, 113, 0.15); color: #2ecc71;">Acc: ${escapeHtml(m.accuracy)}</span>` : ''}
                    ${m.precision ? `<span class="private-badge" style="background: rgba(241, 196, 15, 0.15); color: #f1c40f;">Prec: ${escapeHtml(m.precision)}</span>` : ''}
                    ${m.recall ? `<span class="private-badge" style="background: rgba(230, 126, 34, 0.15); color: #e67e22;">Rec: ${escapeHtml(m.recall)}</span>` : ''}
                    ${m.f1_score ? `<span class="private-badge" style="background: rgba(52, 152, 219, 0.15); color: #3498db;">F1: ${escapeHtml(m.f1_score)}</span>` : ''}
                </div>
            </div>
        `;
        registryContainer.appendChild(card);
    });
}

// Removed SPA router logic (initRouter, handleHashChange, navigateTo)

// ============================================================
// THREAT ANALYTICS & RULE CATALOG DATA LOADERS
// ============================================================

async function fetchAnalyticsStats() {
    try {
        const res = await fetch(`${API_URL}/analytics/stats`);
        if (res.ok) {
            const data = await res.json();
            renderAnalyticsStats(data);
        }
    } catch (e) {
        console.warn("Could not fetch analytics stats:", e);
    }
}

function renderAnalyticsStats(data) {
    const ds = data.dataset || {};
    const cleanVal = document.getElementById("aCleanVal");
    const trainVal = document.getElementById("aTrainVal");
    const valVal = document.getElementById("aValVal");
    const testVal = document.getElementById("aTestVal");

    if (cleanVal) cleanVal.textContent = (ds.clean_records || 10395).toLocaleString();
    if (trainVal) trainVal.textContent = (ds.train_records || 8350).toLocaleString();
    if (valVal) valVal.textContent = (ds.validation_records || 1022).toLocaleString();
    if (testVal) testVal.textContent = (ds.test_records || 1023).toLocaleString();

    const hClean = document.getElementById("hStatClean");
    if (hClean) hClean.textContent = `${(ds.clean_records || 10395).toLocaleString()}+`;

    // Render CWE Matrix Grid
    const matrixGrid = document.getElementById("cweMatrixGrid");
    if (matrixGrid && data.top_cwes) {
        matrixGrid.innerHTML = "";
        data.top_cwes.forEach(c => {
            const item = document.createElement("div");
            item.className = "cwe-matrix-item";
            item.innerHTML = `
                <div class="cwe-m-header">
                    <span class="cwe-m-cwe">${escapeHtml(c.cwe)}</span>
                    <span class="severity-badge ${c.severity}">${c.severity}</span>
                </div>
                <div class="cwe-m-name">${escapeHtml(c.name)}</div>
                <div class="cwe-m-count">Benchmark Instances: ${c.count.toLocaleString()}</div>
            `;
            matrixGrid.appendChild(item);
        });
    }
}

let catalogRules = [];

async function loadRuleCatalog() {
    const container = document.getElementById("ruleCatalogList");
    const searchInput = document.getElementById("ruleSearchInput");
    if (!container) return;

    try {
        const res = await fetch(`${API_URL}/rules/catalog`);
        if (res.ok) {
            catalogRules = await res.json();
            renderRuleCatalog(catalogRules);
        }
    } catch (e) {
        console.warn("Could not fetch rule catalog:", e);
    }

    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const q = e.target.value.toLowerCase().trim();
            const filtered = catalogRules.filter(r => 
                r.cwe.toLowerCase().includes(q) || 
                r.title.toLowerCase().includes(q) ||
                r.description.toLowerCase().includes(q)
            );
            renderRuleCatalog(filtered);
        });
    }
}

function renderRuleCatalog(rules) {
    const container = document.getElementById("ruleCatalogList");
    if (!container) return;

    container.innerHTML = "";
    if (rules.length === 0) {
        container.innerHTML = `<div class="rule-card"><p>No matching vulnerability rules found.</p></div>`;
        return;
    }

    rules.forEach(r => {
        const card = document.createElement("div");
        card.className = "rule-card";
        card.innerHTML = `
            <div class="rule-card-header">
                <div>
                    <span class="cwe-tag">${escapeHtml(r.cwe)}</span>
                    <span class="rule-card-title" style="margin-left: 10px;">${escapeHtml(r.title)}</span>
                </div>
                <div>
                    <span class="owasp-tag">${escapeHtml(r.owasp)}</span>
                    <span class="severity-badge ${r.severity}" style="margin-left: 8px;">${r.severity}</span>
                </div>
            </div>
            <p class="rule-card-desc">${escapeHtml(r.description)}</p>

            <div class="rule-code-comparison">
                <div class="rule-code-box bad">
                    <div style="font-weight: 700; color: var(--severity-critical); margin-bottom: 6px;">Vulnerable Example:</div>
                    <code>${escapeHtml(r.bad_example)}</code>
                </div>
                <div class="rule-code-box good">
                    <div style="font-weight: 700; color: var(--state-safe); margin-bottom: 6px;">Secure Remediation:</div>
                    <code>${escapeHtml(r.good_example)}</code>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// ============================================================
// COMPANY MODEL LAB LOGIC
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    initLabTabs();
    initLabUploader();
    initWorkspaceMounter();
});

function initLabTabs() {
    const labTabBtns = document.querySelectorAll('.lab-tab-btn');
    labTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            document.querySelectorAll('.lab-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.lab-tab-panel').forEach(p => p.classList.remove('active'));
            
            // Add active to clicked
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-labtab');
            const targetPanel = document.getElementById(targetId);
            if(targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

function initLabUploader() {
    const dropzone = document.getElementById('datasetDropzone');
    const fileInput = document.getElementById('datasetUploadInput');
    const statusDiv = document.getElementById('datasetUploadStatus');

    if(!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if(e.dataTransfer.files.length) {
            handleDatasetUpload(e.dataTransfer.files, statusDiv);
        }
    });

    fileInput.addEventListener('change', () => {
        if(fileInput.files.length) {
            handleDatasetUpload(fileInput.files, statusDiv);
        }
    });
}

async function handleDatasetUpload(files, statusDiv) {
    statusDiv.style.color = 'var(--text-primary)';
    statusDiv.textContent = `Uploading ${files.length} file(s)...`;
    
    const formData = new FormData();
    for(let i=0; i<files.length; i++) {
        formData.append('files', files[i]);
    }

    try {
        const res = await fetch(`${API_URL}/lab/data/upload`, {
            method: 'POST',
            body: formData
        });
        if(res.ok) {
            statusDiv.style.color = 'var(--state-safe)';
            statusDiv.textContent = `Successfully uploaded ${files.length} file(s) for fine-tuning.`;
        } else {
            const err = await res.json();
            statusDiv.style.color = 'var(--severity-critical)';
            statusDiv.textContent = `Upload failed: ${err.detail}`;
        }
    } catch(e) {
        statusDiv.style.color = 'var(--severity-critical)';
        statusDiv.textContent = `Error connecting to server.`;
    }
}

function initWorkspaceMounter() {
    const btn = document.getElementById('selectFolderBtn');
    const input = document.getElementById('folderUploadInput');
    const treeContainer = document.getElementById('workspaceFileTree');
    const statusDiv = document.getElementById('workspaceUploadStatus');

    if(!btn || !input) return;

    btn.addEventListener('click', () => input.click());

    input.addEventListener('change', async () => {
        if(!input.files.length) return;
        
        statusDiv.style.color = 'var(--text-primary)';
        statusDiv.textContent = `Mounting ${input.files.length} files...`;
        
        // Render simple tree preview
        treeContainer.innerHTML = '';
        const paths = Array.from(input.files).map(f => f.webkitRelativePath || f.name).slice(0, 50); // limit preview
        
        paths.forEach(p => {
            const li = document.createElement('li');
            li.innerHTML = `<svg class="file-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg> ${escapeHtml(p)}`;
            treeContainer.appendChild(li);
        });
        if(input.files.length > 50) {
            const li = document.createElement('li');
            li.innerHTML = `<i>...and ${input.files.length - 50} more files</i>`;
            treeContainer.appendChild(li);
        }

        const formData = new FormData();
        for(let i=0; i<input.files.length; i++) {
            formData.append('files', input.files[i]);
            formData.append('paths', input.files[i].webkitRelativePath || input.files[i].name);
        }

        try {
            const res = await fetch(`${API_URL}/lab/workspace/mount`, {
                method: 'POST',
                body: formData
            });
            if(res.ok) {
                statusDiv.style.color = 'var(--state-safe)';
                statusDiv.textContent = `Workspace successfully mounted to agent sandbox.`;
            } else {
                statusDiv.style.color = 'var(--severity-critical)';
                statusDiv.textContent = `Mount failed.`;
            }
        } catch(e) {
            statusDiv.style.color = 'var(--severity-critical)';
            statusDiv.textContent = `Error connecting to server.`;
        }
    });

    const runBtn = document.getElementById('runWorkspaceAuditBtn');
    const resultsContainer = document.getElementById('workspaceAuditResults');
    const modelSelect = document.getElementById('workspaceModelSelect');

    if(runBtn && input && resultsContainer && modelSelect) {
        runBtn.addEventListener('click', async () => {
            if(!input.files.length) {
                alert("Please select a local folder to mount first.");
                return;
            }
            resultsContainer.style.display = "flex";
            resultsContainer.innerHTML = `<div style="color: var(--text-primary);">Starting security audit on ${input.files.length} files...</div>`;
            runBtn.disabled = true;

            const selectedModel = modelSelect.value;
            let issuesFound = 0;

            for(let i=0; i<input.files.length; i++) {
                const file = input.files[i];
                // Skip very large files or non-code files heuristically
                if(file.size > 50000) continue; 
                
                const ext = file.name.split('.').pop().toLowerCase();
                const codeExts = ['py', 'c', 'cpp', 'cc', 'java', 'js', 'ts', 'php', 'sh', 'bash'];
                if(!codeExts.includes(ext)) continue;

                let language = "Python";
                if(ext === 'c') language = "C";
                else if (['cpp','cc','cxx','h','hpp'].includes(ext)) language = "C++";
                else if (ext === 'java') language = "Java";
                else if (['js','ts','jsx','tsx'].includes(ext)) language = "JavaScript";
                else if (ext === 'php') language = "PHP";
                else if (['sh','bash'].includes(ext)) language = "Bash";

                const code = await file.text();

                resultsContainer.innerHTML += `<div style="color: var(--text-secondary);">Analyzing ${escapeHtml(file.webkitRelativePath || file.name)}...</div>`;
                resultsContainer.scrollTop = resultsContainer.scrollHeight;

                try {
                    const res = await fetch(`${API_URL}/analyze`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ code, language, model: selectedModel })
                    });
                    
                    if(res.ok) {
                        const data = await res.json();
                        if(data.vulnerable || (data.static_analysis && data.static_analysis.findings.length > 0)) {
                            issuesFound++;
                            resultsContainer.innerHTML += `<div style="color: var(--severity-critical); border-left: 2px solid var(--severity-critical); padding-left: 8px; margin: 4px 0;">
                                <strong>[VULNERABILITY FOUND]</strong> ${escapeHtml(file.webkitRelativePath || file.name)}<br>
                                ${data.vulnerable ? `Model flagged: ${data.llm_analysis ? escapeHtml(data.llm_analysis.issue) : 'Potential Issue'}` : `Static Rules: ${data.static_analysis.findings.length} findings`}
                            </div>`;
                        } else {
                            resultsContainer.innerHTML += `<div style="color: var(--state-safe);">[SECURE] ${escapeHtml(file.webkitRelativePath || file.name)}</div>`;
                        }
                    }
                } catch(e) {
                    console.error("Audit error for file", file.name, e);
                }
            }
            resultsContainer.innerHTML += `<div style="color: var(--accent-blue); font-weight: bold; margin-top: 10px;">Audit complete. ${issuesFound} files flagged with potential vulnerabilities.</div>`;
            resultsContainer.scrollTop = resultsContainer.scrollHeight;
            runBtn.disabled = false;
        });
    }
}