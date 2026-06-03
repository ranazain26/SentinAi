import streamlit as st
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.orchestrator import analyze
from app.utils.report_generator import generate_markdown
#from app.utils.pdf_exporter import export_pdf

# Remove the old pdf_exporter import and add this:
from app.utils.html_exporter import export_html

from app.utils.word_exporter import export_word # New import for Word export

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    code, pre { font-family: 'JetBrains Mono', monospace !important; }
    
    .main { background: #0d1117; }
    .stApp { background: #0d1117; }
    
    .hero-banner {
        background: linear-gradient(135deg, #1a1f35 0%, #0d1117 50%, #1a2535 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 2.5rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #58a6ff, #79c0ff, #3fb950);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub {
        color: #8b949e;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    .score-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .finding-card {
        background: #161b22;
        border-left: 4px solid;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
        font-size: 0.9rem;
    }
    .critical { border-color: #f85149; }
    .high { border-color: #e3b341; }
    .medium { border-color: #d29922; }
    .low { border-color: #3fb950; }
    .info { border-color: #58a6ff; }
    
    .severity-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-critical { background: #3d1a1a; color: #f85149; border: 1px solid #f85149; }
    .badge-high { background: #2d2208; color: #e3b341; border: 1px solid #e3b341; }
    .badge-medium { background: #2a1e08; color: #d29922; border: 1px solid #d29922; }
    .badge-low { background: #0d2116; color: #3fb950; border: 1px solid #3fb950; }
    .badge-info { background: #0d1d35; color: #58a6ff; border: 1px solid #58a6ff; }
    
    .metric-row {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }
    .metric-item {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        text-align: center;
        min-width: 100px;
        flex: 1;
    }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #e6edf3; }
    .metric-label { font-size: 0.72rem; color: #8b949e; margin-top: 2px; }
    
    .stButton > button {
        background: linear-gradient(135deg, #238636, #2ea043) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2ea043, #3fb950) !important;
    }
    
    .stFileUploader { background: #161b22; border-radius: 8px; }
    div[data-testid="stSidebar"] { background: #161b22 !important; }
    
    h1, h2, h3, h4 { color: #e6edf3 !important; }
    p, li { color: #c9d1d9; }
    
    .stTabs [data-baseweb="tab"] {
        color: #8b949e !important;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom-color: #58a6ff !important;
    }
    
    .code-snippet {
        background: #1c2128;
        border: 1px solid #30363d;
        border-radius: 4px;
        padding: 0.3rem 0.6rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #ff7b72;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🛡️ SentinAI</div>
    <div class="hero-sub">Multi-Agent AI · Code Security · Automated Documentation</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Analysis Settings")
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Upload Source Code",
        type=["py", "js"],
        help="Upload a Python (.py) or JavaScript (.js) file"
    )
    
    st.markdown("---")
    st.markdown("#### 📊 What SentinAI Detects")
    st.markdown("""
    - 🔴 SQL Injection  
    - 🔴 Command Injection  
    - 🟡 Hardcoded Secrets  
    - 🟡 Weak Hashing  
    - 🔴 Unsafe Deserialization  
    - 🟡 Path Traversal  
    - 🟠 Logic Bugs  
    - 🔵 Sensitive Entities  
    """)
    
    st.markdown("---")
    st.caption("Powered by Llama 3 · LangChain · ChromaDB")
    
    run_btn = st.button("🔍 Run Analysis", use_container_width=True)

# ── Main Area ─────────────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div style="text-align:center; padding: 3rem; color: #8b949e;">
        <div style="font-size: 3rem">📁</div>
        <div style="font-size: 1.1rem; margin-top: 1rem;">Upload a Python or JavaScript file to begin analysis</div>
        <div style="font-size: 0.85rem; margin-top: 0.5rem;">Use the sidebar to upload your file, then click Run Analysis</div>
    </div>
    """, unsafe_allow_html=True)

elif run_btn or "analysis_result" in st.session_state:
    
    if run_btn:
        code_content = uploaded_file.read().decode("utf-8", errors="replace")
        filename = uploaded_file.name
        
        with st.spinner("🔄 Running multi-agent analysis..."):
            progress = st.progress(0)
            
            progress.progress(15, "Parsing code structure...")
            progress.progress(35, "Running security analysis...")
            progress.progress(55, "Detecting bugs...")
            progress.progress(70, "Retrieving security references...")
            progress.progress(85, "Generating documentation...")
            
            result = analyze(code_content, filename)
            
            progress.progress(100, "Complete!")
            progress.empty()
            
            st.session_state["analysis_result"] = result
            st.session_state["code_content"] = code_content
    
    result = st.session_state["analysis_result"]
    code_content = st.session_state.get("code_content", "")
    score_data = result.get("score", {})
    
    # ── Score Banner ──────────────────────────────────────────────────────────
    score_val = score_data.get("score", 0)
    score_color = "#3fb950" if score_val >= 80 else "#e3b341" if score_val >= 60 else "#f85149"
    
    st.markdown(f"""
    <div class="score-card">
        <div style="color: #8b949e; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em;">Code Health Score</div>
        <div class="score-number" style="color: {score_color}">{score_val}</div>
        <div style="color: {score_color}; font-weight: 600; font-size: 1.1rem;">
            Grade {score_data.get("grade", "?")} · {score_data.get("status", "")}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Metrics Row ───────────────────────────────────────────────────────────
    m = score_data
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-item"><div class="metric-value" style="color:#f85149">{m.get("critical_issues",0)}</div><div class="metric-label">Critical</div></div>
        <div class="metric-item"><div class="metric-value" style="color:#e3b341">{m.get("high_issues",0)}</div><div class="metric-label">High</div></div>
        <div class="metric-item"><div class="metric-value" style="color:#58a6ff">{m.get("total_vulnerabilities",0)}</div><div class="metric-label">Vulnerabilities</div></div>
        <div class="metric-item"><div class="metric-value" style="color:#79c0ff">{m.get("total_bugs",0)}</div><div class="metric-label">Bugs</div></div>
        <div class="metric-item"><div class="metric-value" style="color:#d2a8ff">{m.get("total_secrets",0)}</div><div class="metric-label">Secrets</div></div>
        <div class="metric-item"><div class="metric-value" style="color:#e6edf3">{m.get("lines_of_code",0)}</div><div class="metric-label">Lines</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔴 Security", "🐛 Bugs", "🔑 Secrets", "📝 Docs", "📄 Full Report", "💻 Code"
    ])
    
    # Security Tab
    with tab1:
        security = result.get("security", [])
        rag_refs = result.get("rag_references", {})
        
        if not security:
            st.success("✅ No security vulnerabilities detected!")
        else:
            for v in security:
                sev = v["severity"].lower()
                refs = rag_refs.get(v["vulnerability"], [])
                ref_html = ""
                if refs:
                    for r in refs:
                        ref_html += f'<div style="margin-top:4px; font-size:0.8rem; color:#8b949e">📚 <b>{r.get("id","")}</b>: {r.get("remediation","")[:120]}</div>'
                
                st.markdown(f"""
                <div class="finding-card {sev}">
                    <span class="severity-badge badge-{sev}">{v["severity"]}</span>
                    <strong style="color:#e6edf3; margin-left:8px">{v["vulnerability"]}</strong>
                    <span style="color:#8b949e; font-size:0.8rem; float:right">Line {v["line"]} · {v.get("cwe","")}</span>
                    <br/><span class="code-snippet">{v["snippet"][:80]}</span>
                    <div style="color:#8b949e; font-size:0.83rem; margin-top:4px">{v["description"]}</div>
                    {ref_html}
                </div>
                """, unsafe_allow_html=True)
    
    # Bugs Tab
    with tab2:
        bugs = result.get("bugs", [])
        if not bugs:
            st.success("✅ No bugs detected!")
        else:
            for b in bugs:
                sev = b["severity"].lower()
                st.markdown(f"""
                <div class="finding-card {sev}">
                    <span class="severity-badge badge-{sev}">{b["severity"]}</span>
                    <strong style="color:#e6edf3; margin-left:8px">{b["bug"]}</strong>
                    <span style="color:#8b949e; font-size:0.8rem; float:right">Line {b["line"]}</span>
                    <br/><span class="code-snippet">{b["snippet"][:80]}</span>
                    <div style="color:#8b949e; font-size:0.83rem; margin-top:4px">{b["description"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Secrets Tab
    with tab3:
        ner = result.get("ner", [])
        if not ner:
            st.success("✅ No sensitive entities detected!")
        else:
            for entity in ner:
                sev = entity["severity"].lower()
                st.markdown(f"""
                <div class="finding-card {sev}">
                    <span class="severity-badge badge-{sev}">{entity["severity"]}</span>
                    <strong style="color:#e6edf3; margin-left:8px">{entity["type"]}</strong>
                    <span style="color:#8b949e; font-size:0.8rem; float:right">Line {entity["line"]}</span>
                    <br/><span class="code-snippet">{entity["snippet"][:80]}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Docs Tab
    with tab4:
        doc = result.get("documentation", {})
        st.markdown("### 📋 Code Summary")
        st.info(doc.get("summary", "No summary available."))
        
        st.markdown("### 🎯 Purpose")
        st.write(doc.get("purpose", "N/A"))
        
        funcs_doc = doc.get("functions_doc", {})
        if funcs_doc:
            st.markdown("### 🔧 Function Documentation")
            for fn, desc in funcs_doc.items():
                with st.expander(f"`{fn}()`"):
                    st.write(desc)
        
        readme = doc.get("readme_section", "")
        if readme:
            st.markdown("### 📄 Generated README Section")
            st.markdown(readme)
    
    # Full Report Tab
    with tab5:
        markdown_report = generate_markdown(result)
        st.markdown(markdown_report)
        
        st.markdown("---")
        #col1, col2 = st.columns(2)

        # Change to 3 columns for 3 buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "⬇️ Download Markdown Report",
                data=markdown_report,
                file_name=f"sentinai_report_{result.get('filename','code').replace('.','_')}.md",
                mime="text/markdown"
            )
        
        #with col2:
        #    try:
        #        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        #            pdf_path = export_pdf(markdown_report, tmp.name)
        #        with open(pdf_path, "rb") as f:
        #            pdf_bytes = f.read()
        #        st.download_button(
        #            "⬇️ Download PDF Report",
        #            data=pdf_bytes,
        #            file_name=f"sentinai_report_{result.get('filename','code').replace('.','_')}.pdf",
        #            mime="application/pdf"
        #        )
        #        os.unlink(pdf_path)
        #    except Exception as e:
        #        st.warning(f"PDF export error: {e}")

        with col2:
            try:
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    html_path = export_html(markdown_report, tmp.name)
                with open(html_path, "rb") as f:
                    html_bytes = f.read()
                st.download_button(
                    "⬇️ Download HTML Report",
                    data=html_bytes,
                    file_name=f"sentinai_report_{result.get('filename','code').replace('.','_')}.html",
                    mime="text/html"
                )
                os.unlink(html_path)
            except Exception as e:
                st.warning(f"HTML export error: {e}")

        with col3:
            try:
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                    word_path = export_word(result, tmp.name)
                with open(word_path, "rb") as f:
                    word_bytes = f.read()
                st.download_button(
                    "⬇️ Download Word (.docx)",
                    data=word_bytes,
                    file_name=f"sentinai_report_{result.get('filename','code').replace('.','_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                os.unlink(word_path)
            except Exception as e:
                st.warning(f"Word export error: {e}")
    
    # Code Tab
    with tab6:
        parse = result.get("parse", {})
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Language:** `{parse.get('language','?').capitalize()}` · **Lines:** `{parse.get('lines',0)}`")
        
        if parse.get("functions"):
            st.markdown("**Functions found:**")
            for fn in parse["functions"]:
                docstr_icon = "📝" if fn.get("has_docstring") else "⚠️"
                st.markdown(f"  {docstr_icon} `{fn['name']}()` — line {fn['line']}")
        
        st.code(code_content, language=parse.get("language", "python"))


# ── Sample files notice ───────────────────────────────────────────────────────
else:
    pass