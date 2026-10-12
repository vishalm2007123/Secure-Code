"""
SecureCode AI - Professional PPT Generator
Uses python-pptx to build slides with flowcharts, figures, and shapes.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ──────────────────── COLOUR PALETTE ────────────────────
BG          = RGBColor(0x0D, 0x11, 0x17)   # deep dark navy
ACCENT_CYAN = RGBColor(0x00, 0xD4, 0xAA)   # teal / cyan
ACCENT_RED  = RGBColor(0xFF, 0x4D, 0x6D)   # danger red
ACCENT_YEL  = RGBColor(0xFF, 0xC3, 0x4A)   # warning yellow
ACCENT_PRP  = RGBColor(0x7C, 0x3A, 0xED)   # purple
BOX_DARK    = RGBColor(0x16, 0x1B, 0x27)   # card background
BOX_MID     = RGBColor(0x1F, 0x2A, 0x3C)   # lighter card
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY  = RGBColor(0xCC, 0xD1, 0xDA)
DIM_GRAY    = RGBColor(0x78, 0x85, 0x97)

# ──────────────────── HELPERS ────────────────────

def _bg(slide):
    """Dark background."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG

def _txb(slide, text, left, top, width, height,
         size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
         bg_color=None, wrap=True):
    """Add a text box."""
    txb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"
    if bg_color:
        txb.fill.solid()
        txb.fill.fore_color.rgb = bg_color
    return txb

def _rect(slide, left, top, width, height, fill_color, line_color=None, line_width=None):
    """Add a filled rectangle."""
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        if line_width:
            shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    return shape

def _arrow_down(slide, cx, top, height, color=DIM_GRAY):
    """Draw a thin downward connector."""
    left = cx - 0.03
    _rect(slide, left, top, 0.06, height, color)

def _card(slide, left, top, width, height, title, body, title_color=ACCENT_CYAN, body_color=LIGHT_GRAY, card_color=BOX_MID):
    """A card with title + body text."""
    _rect(slide, left, top, width, height, card_color, ACCENT_CYAN, 1.2)
    # title
    txb = slide.shapes.add_textbox(Inches(left+0.1), Inches(top+0.08), Inches(width-0.2), Inches(0.35))
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = title
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = title_color
    run.font.name = "Calibri"
    # body
    txb2 = slide.shapes.add_textbox(Inches(left+0.1), Inches(top+0.45), Inches(width-0.2), Inches(height-0.55))
    tf2 = txb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.LEFT
    run2 = p2.add_run()
    run2.text = body
    run2.font.size = Pt(11)
    run2.font.color.rgb = body_color
    run2.font.name = "Calibri"

def _slide_header(slide, title, subtitle=None):
    """Top accent bar + title."""
    _rect(slide, 0, 0, 13.33, 0.06, ACCENT_CYAN)
    _txb(slide, title, 0.4, 0.15, 12.5, 0.55, size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        _txb(slide, subtitle, 0.4, 0.68, 12.5, 0.35, size=14, color=DIM_GRAY)

def _footer(slide, text="SecureCode AI  •  Enterprise Code Security"):
    _rect(slide, 0, 7.25, 13.33, 0.25, BOX_DARK)
    _txb(slide, text, 0.3, 7.27, 12, 0.2, size=9, color=DIM_GRAY)


# ══════════════════════════════════════════════════
#   SLIDE BUILDERS
# ══════════════════════════════════════════════════

def slide_title(prs):
    """Slide 1 – Title"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])   # blank
    _bg(slide)

    # big gradient bar
    _rect(slide, 0, 0, 13.33, 7.5, BG)
    _rect(slide, 0, 0, 13.33, 0.1, ACCENT_CYAN)
    _rect(slide, 0, 7.4, 13.33, 0.1, ACCENT_CYAN)

    # decorative orb shapes
    orb = slide.shapes.add_shape(9, Inches(9.5), Inches(-1), Inches(5), Inches(5))   # OVAL
    orb.fill.solid(); orb.fill.fore_color.rgb = RGBColor(0x00, 0x60, 0x50)
    orb.line.fill.background(); orb.shadow.inherit = False

    orb2 = slide.shapes.add_shape(9, Inches(-1.5), Inches(4), Inches(4), Inches(4))
    orb2.fill.solid(); orb2.fill.fore_color.rgb = RGBColor(0x20, 0x10, 0x50)
    orb2.line.fill.background()

    # title
    _txb(slide, "SecureCode AI", 1, 1.8, 11, 1.2, size=52, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)
    _txb(slide, "An AI-Powered Security Auditor for LLM-Generated Source Code",
         1, 3.05, 11, 0.6, size=20, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)

    # tag row
    for i, tag in enumerate(["AST Engine", "LLM Reasoning", "Auto-Remediation", "Zero Egress"]):
        x = 1.4 + i * 2.65
        _rect(slide, x, 4.0, 2.2, 0.42, BOX_MID, ACCENT_CYAN, 1)
        _txb(slide, tag, x + 0.05, 4.05, 2.1, 0.35, size=13, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)

    _txb(slide, "Secure • Private • Local", 1, 5.0, 11, 0.4, size=14, color=DIM_GRAY, align=PP_ALIGN.CENTER)
    _footer(slide)


def slide_problem(prs):
    """Slide 2 – Problem"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "The Hidden Risk in AI-Generated Code",
                  "Why code written by AI still needs expert security review")

    # 3 danger zone boxes in a row
    dangers = [
        ("⚡ Hallucinated Logic", "LLMs generate plausible-looking code that silently introduces SQL Injection, Command Injection or Buffer Overflows."),
        (" Rules-Only SAST Gap", "Traditional SAST scanners miss complex multi-step data flows and context-dependent vulnerabilities."),
        (" Blind Trust in AI Fixes", "Auto-generated patches are not re-verified — a 'fix' can introduce new critical vulnerabilities.")
    ]
    for i, (t, b) in enumerate(dangers):
        _card(slide, 0.35 + i*4.35, 1.1, 4.0, 2.1, t, b, title_color=ACCENT_RED)

    # flow: AI Code → SAST Miss → Breach
    steps = ["AI Writes Code", "Vulnerability Slips Through", "Production Breach"]
    colors = [BOX_MID, RGBColor(0x4A, 0x1A, 0x2A), ACCENT_RED]
    for i, (s, c) in enumerate(zip(steps, colors)):
        _rect(slide, 0.7 + i*4.25, 3.55, 3.5, 0.55, c, WHITE if c==ACCENT_RED else ACCENT_CYAN, 1)
        _txb(slide, s, 0.75 + i*4.25, 3.6, 3.4, 0.45, size=14, bold=True,
             color=WHITE, align=PP_ALIGN.CENTER)
        if i < 2:
            _txb(slide, "→", 4.3 + i*4.25, 3.6, 0.5, 0.45, size=22, bold=True, color=ACCENT_CYAN)

    _txb(slide, "The Gap: No tool combines deterministic precision + LLM deep reasoning + verified fixing",
         0.5, 4.35, 12.3, 0.45, size=13, bold=True, color=ACCENT_YEL, align=PP_ALIGN.CENTER)

    # stat pills
    stats = [("Billions", "lines of AI code/day"), ("~40%", "contain vulnerabilities"), ("0", "AI tools verify fixes")]
    for i, (num, lbl) in enumerate(stats):
        _rect(slide, 0.8 + i*4.2, 5.05, 3.6, 0.8, BOX_DARK, DIM_GRAY, 0.8)
        _txb(slide, num, 0.85 + i*4.2, 5.08, 3.5, 0.4, size=20, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)
        _txb(slide, lbl, 0.85 + i*4.2, 5.47, 3.5, 0.3, size=11, color=DIM_GRAY, align=PP_ALIGN.CENTER)
    _footer(slide)


def slide_overview(prs):
    """Slide 3 – Project Overview"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "What is SecureCode AI?", "A privacy-first, end-to-end hybrid security auditor")

    # central tagline
    _rect(slide, 0.5, 1.1, 12.3, 0.55, BOX_MID, ACCENT_CYAN, 1.5)
    _txb(slide, "Deterministic AST Certainty  +  LLM Deep Reasoning  +  Verified Auto-Remediation",
         0.55, 1.18, 12.2, 0.4, size=14, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)

    # 6 pillars grid
    pillars = [
        (" Hybrid Analysis", "AST static rules + fine-tuned LLM working in tandem"),
        (" 6 Languages", "Python · C · C++ · Java · PHP · Bash"),
        ("️ Zero Egress", "All inference runs locally via Ollama — no cloud calls"),
        (" Verified Fixes", "Every rewrite re-analyzed by AST before delivery"),
        (" CWE + OWASP", "Industry-standard vulnerability classification"),
        (" Company Lab", "Fine-tune models on your own private codebase"),
    ]
    for i, (t, b) in enumerate(pillars):
        row, col = divmod(i, 3)
        _card(slide, 0.35 + col*4.35, 1.95 + row*1.85, 4.05, 1.65, t, b)

    _footer(slide)


def slide_architecture(prs):
    """Slide 4 – System Architecture Flowchart"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "System Architecture", "End-to-end pipeline — from code input to verified secure output")

    # ─── Central Flowchart ───
    flow = [
        ("User Code Input",         BOX_MID,    ACCENT_CYAN),
        ("Phase 1: AST Engine",     RGBColor(0x0A,0x2A,0x40), ACCENT_CYAN),
        ("Phase 2: LLM Reasoning",  RGBColor(0x1A,0x10,0x40), ACCENT_PRP),
        ("Finding Correlator",      RGBColor(0x0A,0x28,0x28), ACCENT_CYAN),
        ("Code Rewriter (LLM)",     RGBColor(0x28,0x18,0x00), ACCENT_YEL),
        ("Verification Engine",     RGBColor(0x0A,0x28,0x10), RGBColor(0x00,0xCC,0x55)),
        ("Secure Output / Report",  BOX_MID,    ACCENT_CYAN),
    ]

    box_w, box_h, start_x, start_y, gap = 3.5, 0.52, 0.35, 1.05, 0.18
    cx = start_x + box_w / 2

    for i, (label, bg, border) in enumerate(flow):
        y = start_y + i * (box_h + gap)
        _rect(slide, start_x, y, box_w, box_h, bg, border, 1.5)
        _txb(slide, label, start_x + 0.08, y + 0.10, box_w - 0.15, 0.35,
             size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        if i < len(flow) - 1:
            arrow_y = y + box_h
            _rect(slide, cx - 0.04, arrow_y, 0.08, gap, DIM_GRAY)

    # ─── Side annotations ───
    notes = [
        (4.2, 1.1, "INPUT", "Source code paste or file upload"),
        (4.2, 1.8, "PHASE 1", "Python AST visitor\nTaint propagation\n24+ deterministic rules"),
        (4.2, 2.5, "PHASE 2", "Qwen3 1.7B / 4B\nFine-tuned on 30 GB\nSource→Sink flow"),
        (4.2, 3.2, "CORRELATE", "Dedup + confidence boost\nSecurity score 0–100\nOWASP mapping"),
        (4.2, 3.9, "REWRITE", "Strict 15-rule prompt\nLLM produces safe code"),
        (4.2, 4.6, "VERIFY", "AST + LLM re-check\nForbidden-pattern guard"),
        (4.2, 5.3, "OUTPUT", "CWE report + clean code\nPASS / FAIL verdict"),
    ]
    for (x, y, tag, desc) in notes:
        _rect(slide, x, y, 0.85, 0.30, ACCENT_CYAN, None, 0)
        _txb(slide, tag, x+0.04, y+0.04, 0.78, 0.25, size=9, bold=True, color=BG, align=PP_ALIGN.CENTER)
        _txb(slide, desc, x + 1.0, y + 0.0, 7.5, 0.55, size=10, color=LIGHT_GRAY)

    _footer(slide)


def slide_ast(prs):
    """Slide 5 – AST Engine"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Phase 1: Deterministic AST Engine", "Zero hallucination — pure rule-based precision")

    # taint flow diagram
    _txb(slide, "Taint Propagation Flow", 0.4, 1.08, 8, 0.35, size=14, bold=True, color=ACCENT_CYAN)

    taint_steps = [
        ("USER INPUT\nsource", ACCENT_RED, "input()  request.args  sys.argv  os.getenv"),
        ("TAINT\nPROPAGATION", ACCENT_YEL, "Variables · f-strings · concat · subscripts"),
        ("DANGEROUS\nSINK detected", ACCENT_RED, "os.system()  cursor.execute()  eval()  strcpy()"),
    ]
    for i, (label, color, example) in enumerate(taint_steps):
        bx = 0.35 + i * 4.25
        _rect(slide, bx, 1.55, 3.6, 0.85, BOX_MID, color, 2)
        _txb(slide, label, bx+0.08, 1.60, 3.45, 0.5, size=12, bold=True, color=color, align=PP_ALIGN.CENTER)
        _txb(slide, example, bx+0.08, 2.44, 3.45, 0.35, size=9, color=DIM_GRAY, align=PP_ALIGN.CENTER)
        if i < 2:
            _txb(slide, "⟶", 4.0 + i*4.25, 1.75, 0.45, 0.5, size=22, bold=True, color=DIM_GRAY)

    # rule breakdown
    _txb(slide, "Detection Coverage", 0.4, 3.05, 5, 0.35, size=14, bold=True, color=ACCENT_CYAN)
    rules = [
        ("Python", "Full AST visitor — taint-aware, CWE-78/89/95/22/502/798/918"),
        ("C / C++", "Regex rules — strcpy, gets, sprintf, buffer operations (CWE-120/121)"),
        ("Java", "Regex rules — Runtime.exec(), PreparedStatement patterns (CWE-78/89)"),
    ]
    for i, (lang, desc) in enumerate(rules):
        _rect(slide, 0.35, 3.5 + i*0.7, 1.2, 0.52, BOX_MID, ACCENT_CYAN, 1)
        _txb(slide, lang, 0.4, 3.55 + i*0.7, 1.1, 0.42, size=12, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)
        _txb(slide, desc, 1.65, 3.57 + i*0.7, 10.5, 0.42, size=12, color=LIGHT_GRAY)

    # key stat
    _rect(slide, 0.35, 5.65, 12.3, 0.5, BOX_DARK, DIM_GRAY, 0.8)
    _txb(slide, "24+ Deterministic Rules  •  0 False Negatives on Known Patterns  •  < 100ms Analysis Time",
         0.5, 5.72, 12.0, 0.38, size=12, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)

    _footer(slide)


def slide_llm(prs):
    """Slide 6 – LLM Reasoning"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Phase 2: Fine-Tuned Security LLM", "Qwen3 trained to reason about complex vulnerability data flows")

    # model input → output diagram
    _txb(slide, "Inference Pipeline", 0.4, 1.08, 6, 0.35, size=14, bold=True, color=ACCENT_CYAN)

    boxes = [
        ("Source Code\n+ Language",   BOX_MID,   WHITE,       1.05),
        ("Security\nPrompt",          BOX_MID,   LIGHT_GRAY,  2.05),
        ("Qwen3 1.7B\n(Fine-Tuned)", RGBColor(0x1A,0x10,0x40), ACCENT_PRP, 3.05),
        ("Structured\nReport",        BOX_MID,   ACCENT_CYAN, 4.05),
    ]
    for i, (label, bg, fg, y_pos) in enumerate(boxes):
        _rect(slide, 0.35, y_pos, 2.8, 0.72, bg, fg, 1.5)
        _txb(slide, label, 0.42, y_pos+0.15, 2.65, 0.5, size=12, bold=True, color=fg, align=PP_ALIGN.CENTER)
        if i < len(boxes)-1:
            _arrow_down(slide, 0.35+1.4, y_pos+0.72, 0.33, DIM_GRAY)

    # output format box
    _rect(slide, 3.6, 1.05, 9.35, 3.75, BOX_DARK, ACCENT_PRP, 1.5)
    _txb(slide, " Model Output Format", 3.75, 1.12, 9.0, 0.35, size=13, bold=True, color=ACCENT_PRP)
    output_text = (
        "VULNERABLE: YES\n"
        "VULNERABILITY: SQL Injection\n"
        "CWE: CWE-89\n"
        "SEVERITY: HIGH\n"
        "CONFIDENCE: 92\n"
        "SOURCE: user_id  (user input)\n"
        "SINK: cursor.execute()\n"
        "REASON: String concatenation in SQL query\n"
        "MITIGATION: Use parameterized queries"
    )
    _txb(slide, output_text, 3.75, 1.52, 9.0, 3.2, size=11, color=ACCENT_CYAN, bg_color=None)

    # LoRA details
    lora_items = [
        ("Base Model", "Qwen3 1.7B / 4B  (Qwen2.5-Coder)"),
        ("Technique", "LoRA / QLoRA — Parameter-Efficient Fine-Tuning"),
        ("VRAM",      "8 GB GPU via 4-bit NF4 quantization"),
        ("Trainable",  "~1% of parameters updated (adapter only)"),
        ("Serving",   "Local Ollama — zero cloud dependency"),
    ]
    _txb(slide, "Model Details", 0.4, 5.05, 5, 0.35, size=14, bold=True, color=ACCENT_CYAN)
    for i, (k, v) in enumerate(lora_items):
        _rect(slide, 0.35, 5.45 + i*0.4, 1.5, 0.35, BOX_MID, ACCENT_CYAN, 0.8)
        _txb(slide, k, 0.4, 5.47 + i*0.4, 1.4, 0.3, size=10, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)
        _txb(slide, v, 1.95, 5.47 + i*0.4, 11.0, 0.3, size=10, color=LIGHT_GRAY)

    _footer(slide)


def slide_training(prs):
    """Slide 7 – Training Pipeline"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "ML Training Pipeline", "LoRA fine-tuning on 30 GB of real-world vulnerability data")

    # horizontal pipeline
    pipe_steps = [
        ("Raw\nDatasets",    ACCENT_CYAN),
        ("Normalize\n& Clean",  ACCENT_YEL),
        ("Hash-Based\nDedup",   ACCENT_YEL),
        ("80/10/10\nSplit",     ACCENT_CYAN),
        ("LoRA\nFine-Tune",    ACCENT_PRP),
        ("Adapter\n+ Serving",  RGBColor(0x00,0xCC,0x55)),
    ]
    bw, bh, sy = 1.85, 0.75, 1.12
    for i, (label, color) in enumerate(pipe_steps):
        bx = 0.3 + i * 2.17
        _rect(slide, bx, sy, bw, bh, BOX_MID, color, 1.5)
        _txb(slide, label, bx+0.06, sy+0.15, bw-0.12, 0.5, size=11, bold=True, color=color, align=PP_ALIGN.CENTER)
        if i < len(pipe_steps) - 1:
            _txb(slide, "→", bx + bw + 0.05, sy + 0.22, 0.3, 0.4, size=16, bold=True, color=DIM_GRAY)

    # data sources
    _txb(slide, "Data Sources  —  30 GB of Real-World Vulnerability Samples", 0.4, 2.12, 12, 0.35, size=14, bold=True, color=ACCENT_CYAN)
    datasets = [
        ("CodeLLMExp",      "Multi-language", "JSON with CWE, severity, fixed code, explanations"),
        ("PyCode_Vul",      "Python",          "CSV — vulnerable/patched function pairs"),
        ("C/C++ Dataset",   "C / C++",        "Real CVE patches with diff-level code"),
        ("Shell Dataset",   "Bash",            "Script injection patterns"),
        ("PHP Dataset",     "PHP",             "Vulnerability test suite archive"),
    ]
    for i, (name, lang, desc) in enumerate(datasets):
        row, col = divmod(i, 2) if i < 4 else (2, 0)
        x = 0.35 + col * 6.55
        y = 2.6 + row * 0.72
        _rect(slide, x, y, 1.55, 0.58, BOX_MID, ACCENT_CYAN, 0.8)
        _txb(slide, name, x+0.05, y+0.05, 1.45, 0.25, size=10, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)
        _txb(slide, lang, x+0.05, y+0.30, 1.45, 0.22, size=9, color=DIM_GRAY, align=PP_ALIGN.CENTER)
        _txb(slide, desc, x+1.65, y+0.12, 4.7, 0.4, size=10, color=LIGHT_GRAY)

    # anti-leakage note
    _rect(slide, 0.35, 5.55, 12.3, 0.7, BOX_DARK, ACCENT_YEL, 1)
    _txb(slide, "⚠ Anti-Leakage Guard", 0.55, 5.6, 4, 0.28, size=12, bold=True, color=ACCENT_YEL)
    _txb(slide, "SHA-256 hash-based group-aware splitting ensures the exact same code snippet never appears\nin both Training and Test sets — preventing data leakage and inflated evaluation scores.",
         0.55, 5.88, 12.0, 0.38, size=10, color=LIGHT_GRAY)

    _footer(slide)


def slide_remediation(prs):
    """Slide 8 – Verified Auto-Remediation"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Verified Auto-Remediation", "Every AI fix is independently re-analyzed before delivery")

    # BEFORE → REWRITE → AFTER + VERIFY loop
    # Before box
    _rect(slide, 0.3, 1.1, 3.5, 2.2, RGBColor(0x2A,0x0A,0x0A), ACCENT_RED, 1.5)
    _txb(slide, "⚠  VULNERABLE CODE", 0.4, 1.15, 3.3, 0.35, size=11, bold=True, color=ACCENT_RED)
    code_bad = "query = 'SELECT * FROM users\nWHERE id = ' + user_id\ncursor.execute(query)"
    _txb(slide, code_bad, 0.4, 1.55, 3.3, 0.75, size=10, color=ACCENT_RED, bg_color=RGBColor(0x15,0x05,0x05))

    # arrow
    _txb(slide, "⟶", 3.9, 1.85, 0.8, 0.5, size=26, bold=True, color=DIM_GRAY)

    # LLM Rewrite box
    _rect(slide, 4.75, 1.1, 3.8, 2.2, BOX_MID, ACCENT_PRP, 1.5)
    _txb(slide, "  LLM REWRITER", 4.88, 1.15, 3.55, 0.35, size=11, bold=True, color=ACCENT_PRP)
    rules_txt = "15 Strict Security Rules:\n• No os.system() or shell=True\n• No eval() / exec()\n• Use safe parameterized APIs\n• No hardcoded secrets"
    _txb(slide, rules_txt, 4.88, 1.55, 3.55, 1.65, size=10, color=LIGHT_GRAY)

    # arrow
    _txb(slide, "⟶", 8.65, 1.85, 0.8, 0.5, size=26, bold=True, color=DIM_GRAY)

    # After box
    _rect(slide, 9.5, 1.1, 3.45, 2.2, RGBColor(0x05,0x20,0x10), RGBColor(0x00,0xCC,0x55), 1.5)
    _txb(slide, "✅  SECURE REWRITE", 9.6, 1.15, 3.25, 0.35, size=11, bold=True, color=RGBColor(0x00,0xCC,0x55))
    code_good = "cursor.execute(\n  'SELECT * FROM users\n   WHERE id = ?',\n  (user_id,)\n)"
    _txb(slide, code_good, 9.6, 1.55, 3.25, 0.75, size=10, color=RGBColor(0x00,0xCC,0x55),
         bg_color=RGBColor(0x02,0x10,0x08))

    # Verification loop below
    _rect(slide, 0.3, 3.55, 12.65, 0.06, DIM_GRAY)
    _txb(slide, "INDEPENDENT VERIFICATION LOOP", 0.4, 3.68, 12, 0.35, size=13, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)

    verify_steps = [
        ("AST\nRe-Analysis",    ACCENT_CYAN),
        ("LLM\nRe-Analysis",    ACCENT_PRP),
        ("Forbidden\nPattern Check", ACCENT_YEL),
        ("PASS / FAIL\nVerdict",  RGBColor(0x00,0xCC,0x55)),
    ]
    for i, (label, color) in enumerate(verify_steps):
        bx = 0.7 + i * 3.1
        _rect(slide, bx, 4.15, 2.65, 0.85, BOX_MID, color, 1.5)
        _txb(slide, label, bx+0.08, 4.30, 2.5, 0.55, size=12, bold=True, color=color, align=PP_ALIGN.CENTER)
        if i < 3:
            _txb(slide, "→", bx+2.7, 4.42, 0.4, 0.4, size=18, color=DIM_GRAY)

    # rule list
    _txb(slide, "Forbidden Patterns: os.system  •  shell=True  •  eval()  •  exec()  •  strcpy()  •  gets()",
         0.4, 5.2, 12.5, 0.35, size=11, bold=True, color=ACCENT_YEL, align=PP_ALIGN.CENTER)
    _footer(slide)


def slide_cwe(prs):
    """Slide 9 – CWE / OWASP"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "CWE & OWASP Vulnerability Mapping", "Industry-standard classification built into every finding")

    vulns = [
        ("CWE-78",  "OS Command Injection",   "CRITICAL", "A03:2021 – Injection",                    ACCENT_RED),
        ("CWE-89",  "SQL Injection",           "HIGH",     "A03:2021 – Injection",                    ACCENT_RED),
        ("CWE-120", "Buffer Overflow",         "CRITICAL", "A06:2021 – Vulnerable Components",        ACCENT_RED),
        ("CWE-798", "Hardcoded Credentials",   "MEDIUM",   "A07:2021 – Auth Failures",                ACCENT_YEL),
        ("CWE-22",  "Path Traversal",          "HIGH",     "A01:2021 – Broken Access Control",        ACCENT_RED),
        ("CWE-79",  "Cross-Site Scripting",    "HIGH",     "A03:2021 – Injection",                    ACCENT_RED),
        ("CWE-502", "Insecure Deserialization","HIGH",     "A08:2021 – Integrity Failures",           ACCENT_YEL),
        ("CWE-327", "Weak Cryptography",       "MEDIUM",   "A02:2021 – Cryptographic Failures",       ACCENT_YEL),
    ]

    sev_colors = {"CRITICAL": ACCENT_RED, "HIGH": RGBColor(0xFF,0x88,0x33), "MEDIUM": ACCENT_YEL}

    for i, (cwe, name, sev, owasp, color) in enumerate(vulns):
        row, col = divmod(i, 2)
        x = 0.35 + col * 6.5
        y = 1.08 + row * 1.55
        _rect(slide, x, y, 6.1, 1.35, BOX_MID, color, 1)

        _rect(slide, x+0.1, y+0.12, 1.05, 0.4, color, None)
        _txb(slide, cwe, x+0.12, y+0.15, 1.0, 0.35, size=12, bold=True, color=BG, align=PP_ALIGN.CENTER)

        _txb(slide, name, x+1.25, y+0.08, 3.5, 0.35, size=13, bold=True, color=WHITE)
        _txb(slide, owasp, x+1.25, y+0.45, 4.5, 0.3, size=10, color=DIM_GRAY)

        sev_c = sev_colors.get(sev, DIM_GRAY)
        _rect(slide, x+4.8, y+0.12, 1.2, 0.3, BOX_DARK, sev_c, 1)
        _txb(slide, sev, x+4.82, y+0.14, 1.15, 0.26, size=9, bold=True, color=sev_c, align=PP_ALIGN.CENTER)

    _footer(slide)


def slide_modules(prs):
    """Slide 10 – Product Modules"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Four Core Product Modules", "A complete platform for enterprise code security")

    modules = [
        ("", "Audit Workspace",
         "Paste or load source code\nSelect model & language\nGet instant vulnerability report\nSource→sink flow + security score\nOne-click code export",
         ACCENT_CYAN),
        ("", "Company Model Lab",
         "Upload private codebase\nMount workspace files securely\nFine-tune Qwen on your patterns\nTrigger & monitor training jobs\nTenant-specific model serving",
         ACCENT_PRP),
        ("", "Threat Analytics",
         "Dataset size & split statistics\nTop CWE distribution charts\nLanguage coverage breakdown\nFinding severity heatmap\nLive API health dashboard",
         ACCENT_YEL),
        ("", "Rule Catalog",
         "Browse 24+ security rules\nCWE + OWASP references\nBad vs. good code examples\nSeverity badges & descriptions\nMulti-language coverage",
         RGBColor(0x00,0xCC,0x55)),
    ]

    for i, (icon, title, body, color) in enumerate(modules):
        col = i % 2
        row = i // 2
        x = 0.35 + col * 6.5
        y = 1.1 + row * 3.05

        _rect(slide, x, y, 6.1, 2.75, BOX_MID, color, 1.5)
        _txb(slide, icon + "  " + title, x+0.2, y+0.12, 5.7, 0.45, size=16, bold=True, color=color)
        # bullets
        for bi, line in enumerate(body.strip().split("\n")):
            _txb(slide, "▸ " + line, x+0.25, y+0.65+bi*0.38, 5.6, 0.35, size=11, color=LIGHT_GRAY)

    _footer(slide)


def slide_stack(prs):
    """Slide 11 – Tech Stack"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Technology Stack", "Built on modern, production-grade open-source tools")

    cols = [
        ("Backend",    ACCENT_CYAN, ["FastAPI", "Uvicorn ASGI", "Pydantic", "Ollama", "Python AST", "Regex Engine"]),
        ("ML / Training", ACCENT_PRP, ["HuggingFace Transformers", "PEFT (LoRA/QLoRA)", "BitsAndBytes NF4", "TRL SFTTrainer", "PyTorch + CUDA", "Qwen3 1.7B / 4B"]),
        ("Frontend",   ACCENT_YEL, ["Vanilla HTML5", "CSS3 (Glassmorphism)", "Vanilla JavaScript", "REST API client", "Dark theme UI", "No frameworks"]),
    ]

    for i, (col_title, color, items) in enumerate(cols):
        x = 0.35 + i * 4.35
        _rect(slide, x, 1.05, 4.1, 0.5, color, None)
        _txb(slide, col_title, x+0.1, 1.10, 3.9, 0.4, size=16, bold=True, color=BG, align=PP_ALIGN.CENTER)
        for j, item in enumerate(items):
            _rect(slide, x, 1.65 + j * 0.65, 4.1, 0.52, BOX_MID, color, 0.8)
            _txb(slide, item, x+0.15, 1.72 + j * 0.65, 3.8, 0.38, size=13, color=WHITE)

    _footer(slide)


def slide_differentiators(prs):
    """Slide 12 – Differentiators"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Why SecureCode AI Stands Apart", "Comparison vs. existing approaches")

    headers = ["Feature", "SecureCode AI", "Traditional SAST", "Generic LLM"]
    widths  = [3.4, 2.8, 2.8, 2.8]
    col_colors = [BOX_DARK, ACCENT_CYAN, DIM_GRAY, DIM_GRAY]

    xs = [0.35]
    for w in widths[:-1]:
        xs.append(xs[-1]+w+0.06)

    # header row
    for hi, (h, w, x, c) in enumerate(zip(headers, widths, xs, col_colors)):
        _rect(slide, x, 1.08, w, 0.48, c if hi == 0 else (ACCENT_CYAN if hi==1 else BOX_MID), None)
        _txb(slide, h, x+0.08, 1.12, w-0.1, 0.38, size=13, bold=True,
             color=BG if hi==1 else WHITE, align=PP_ALIGN.CENTER)

    rows = [
        ("Deterministic Rules",         "✅  24+ AST/Regex", "✅  Rules-only",    "❌  None"),
        ("LLM Context Reasoning",       "✅  Fine-tuned",    "❌  None",           "⚠  Hallucination risk"),
        ("Source → Sink Taint Flow",    "✅  Full",          "⚠  Partial",         "❌  None"),
        ("Verified Fixes",              "✅  Re-analysis",   "❌  No fixing",       "❌  No verification"),
        ("100% Local / No Egress",      "✅  Ollama local",  "⚠  Varies",          "❌  Cloud-dependent"),
        ("Custom Fine-Tuning",          "✅  Per-tenant",    "❌  Static rules",    "❌  Not supported"),
    ]

    row_colors_check = {
        "✅": RGBColor(0x00,0xCC,0x55),
        "❌": ACCENT_RED,
        "⚠": ACCENT_YEL,
    }

    for ri, row_data in enumerate(rows):
        y = 1.66 + ri * 0.63
        for ci, (val, w, x) in enumerate(zip(row_data, widths, xs)):
            bg = BOX_DARK if ci == 0 else (RGBColor(0x0A,0x22,0x18) if ci==1 else BOX_MID)
            _rect(slide, x, y, w, 0.55, bg, DIM_GRAY, 0.5)
            first_char = val.strip()[0] if val.strip() else " "
            fc = row_colors_check.get(first_char, LIGHT_GRAY)
            _txb(slide, val, x+0.08, y+0.10, w-0.12, 0.38, size=11,
                 color=WHITE if ci==0 else fc, align=PP_ALIGN.LEFT if ci==0 else PP_ALIGN.CENTER)

    _footer(slide)


def slide_results(prs):
    """Slide 13 – Results & Metrics"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Performance & Evaluation Results", "Measured on held-out test data never seen during training")

    # big metric cards
    metrics = [
        ("30 GB",   "Training Data Used",          ACCENT_CYAN),
        ("6",        "Languages Supported",          ACCENT_PRP),
        ("24+",     "Deterministic Rules",           ACCENT_YEL),
        ("< 2s",    "Avg. AST Analysis Time",        RGBColor(0x00,0xCC,0x55)),
        ("0",       "False Negatives (Preset Tests)", ACCENT_CYAN),
        ("0/100",   "Security Score Range",          ACCENT_YEL),
    ]
    for i, (val, lbl, color) in enumerate(metrics):
        col, row = divmod(i, 2)  # 3 cols
        x = 0.35 + col * 4.35
        y = 1.08 + row * 1.65
        _rect(slide, x, y, 4.1, 1.45, BOX_MID, color, 1.5)
        _txb(slide, val, x+0.15, y+0.18, 3.8, 0.72, size=32, bold=True, color=color, align=PP_ALIGN.CENTER)
        _txb(slide, lbl, x+0.15, y+0.92, 3.8, 0.42, size=11, color=DIM_GRAY, align=PP_ALIGN.CENTER)

    # evaluation note
    _rect(slide, 0.35, 4.6, 12.3, 0.95, BOX_DARK, DIM_GRAY, 0.8)
    _txb(slide, "Evaluation Metrics (Fine-Tuned Model)", 0.55, 4.65, 8, 0.32, size=13, bold=True, color=ACCENT_CYAN)
    _txb(slide,
         "The fine-tuned Qwen3 adapter is evaluated on precision, recall, F1 score, and CWE accuracy\n"
         "on a 10% held-out test split. Group-aware deduplication ensures no code appears in both train and test.",
         0.55, 4.97, 12.0, 0.52, size=11, color=LIGHT_GRAY)

    _footer(slide)


def slide_limitations(prs):
    """Slide 14 – Limitations & Roadmap"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)
    _slide_header(slide, "Current Limitations & Future Roadmap")

    # Limitations
    _rect(slide, 0.35, 1.08, 5.8, 0.42, ACCENT_RED, None)
    _txb(slide, "⚠  Current Limitations", 0.5, 1.12, 5.6, 0.34, size=13, bold=True, color=BG, align=PP_ALIGN.CENTER)
    limits = [
        "LoRA adapter must be merged for production serving",
        "Requires GPU ≥ 8 GB VRAM for QLoRA training",
        "Single-file context only (no cross-file analysis yet)",
        "PHP and Bash use Regex only (no full AST)",
    ]
    for i, l in enumerate(limits):
        _rect(slide, 0.35, 1.62 + i * 0.72, 5.8, 0.6, BOX_DARK, ACCENT_RED, 0.8)
        _txb(slide, "✗  " + l, 0.5, 1.70 + i * 0.72, 5.55, 0.44, size=11, color=LIGHT_GRAY)

    # Roadmap
    _rect(slide, 6.5, 1.08, 6.45, 0.42, RGBColor(0x00,0xCC,0x55), None)
    _txb(slide, "  Future Roadmap", 6.65, 1.12, 6.25, 0.34, size=13, bold=True, color=BG, align=PP_ALIGN.CENTER)
    roadmap = [
        ("Q1", "Cross-file taint analysis for multi-module projects"),
        ("Q2", "CI/CD integration — GitHub / GitLab PR-level scanning"),
        ("Q2", "VSCode IDE plugin for real-time in-editor alerts"),
        ("Q3", "Full AST engine for JavaScript / TypeScript"),
        ("Q3", "SARIF output for SIEM / security dashboard integration"),
        ("Q4", "Larger models — Qwen3 7B / CodeLlama 13B fine-tune"),
    ]
    for i, (q, item) in enumerate(roadmap):
        _rect(slide, 6.5, 1.62 + i * 0.72, 0.55, 0.55, RGBColor(0x00,0xCC,0x55), None)
        _txb(slide, q, 6.52, 1.67 + i * 0.72, 0.52, 0.45, size=10, bold=True, color=BG, align=PP_ALIGN.CENTER)
        _rect(slide, 7.12, 1.62 + i * 0.72, 5.83, 0.55, BOX_DARK, RGBColor(0x00,0xCC,0x55), 0.8)
        _txb(slide, item, 7.25, 1.70 + i * 0.72, 5.6, 0.40, size=11, color=LIGHT_GRAY)

    _footer(slide)


def slide_conclusion(prs):
    """Slide 15 – Conclusion"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _bg(slide)

    _rect(slide, 0, 0, 13.33, 0.1, ACCENT_CYAN)
    _rect(slide, 0, 7.4, 13.33, 0.1, ACCENT_CYAN)

    _txb(slide, "Conclusion", 0.5, 0.25, 12, 0.55, size=28, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # 4 takeaways
    takeaways = [
        (ACCENT_CYAN, "Hybrid Precision", "Combines zero-hallucination AST rules with fine-tuned LLM reasoning for complete coverage."),
        (ACCENT_PRP,  "Privacy-First",    "100% local inference via Ollama — no code ever leaves the enterprise network."),
        (RGBColor(0x00,0xCC,0x55), "Verified Fixes", "Every AI-generated fix is independently re-analyzed before delivery — no blind trust."),
        (ACCENT_YEL,  "Scalable",         "Tenant-level fine-tuning on private codebases. Adapts to your internal security standards."),
    ]
    for i, (color, title, body) in enumerate(takeaways):
        col, row = divmod(i, 2)
        x = 0.35 + col * 6.5
        y = 0.95 + row * 1.85
        _rect(slide, x, y, 6.1, 1.65, BOX_MID, color, 1.5)
        _txb(slide, title, x+0.2, y+0.12, 5.7, 0.4, size=15, bold=True, color=color)
        _txb(slide, body, x+0.2, y+0.6, 5.7, 0.95, size=12, color=LIGHT_GRAY)

    # closing quote
    _rect(slide, 0.5, 4.82, 12.3, 0.85, BOX_DARK, ACCENT_CYAN, 1.5)
    _txb(slide,
         '" As AI writes more code, we need AI to audit it — but smarter, not blindly. "',
         0.6, 4.94, 12.1, 0.6, size=16, bold=True, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)

    _txb(slide, "SecureCode AI  •  Version 1.0  •  Enterprise Code Security Posture Management",
         0.5, 5.85, 12.3, 0.35, size=12, color=DIM_GRAY, align=PP_ALIGN.CENTER)

    _footer(slide)


# ══════════════════════════════════════════════════
#   MAIN
# ══════════════════════════════════════════════════

def build():
    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    slide_title(prs)
    slide_problem(prs)
    slide_overview(prs)
    slide_architecture(prs)
    slide_ast(prs)
    slide_llm(prs)
    slide_training(prs)
    slide_remediation(prs)
    slide_cwe(prs)
    slide_modules(prs)
    slide_stack(prs)
    slide_differentiators(prs)
    slide_results(prs)
    slide_limitations(prs)
    slide_conclusion(prs)

    out = "d:/SecureCode-AI/SecureCode_AI_v2.pptx"
    prs.save(out)
    print(f"Saved: {out}  ({len(prs.slides)} slides)")

if __name__ == "__main__":
    build()
