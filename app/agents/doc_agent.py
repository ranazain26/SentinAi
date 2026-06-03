import os
from langchain_groq import ChatGroq
#from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

#def get_llm():
#    return ChatGroq(
#        api_key=os.getenv("GROQ_API_KEY"),
#        model_name="llama3-8b-8192",
#        temperature=0.3,
#        max_tokens=1500
#    )

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",  # <-- The new supported model
        temperature=0.3,
        max_tokens=1500
    )

def run(code: str, parse_result: dict, filename: str = "code.py") -> dict:
    """Generate documentation using LLM."""
    
    lang = parse_result.get("language", "python")
    func_names = [f["name"] for f in parse_result.get("functions", [])]
    class_names = [c["name"] for c in parse_result.get("classes", [])]
    
    code_snippet = code[:3000]  # Limit to avoid token overflow
    
    system_prompt = """You are a professional technical documentation writer. 
    Generate clear, concise documentation for the provided source code.
    Return JSON with keys: summary, purpose, functions_doc, readme_section."""
    
    user_prompt = f"""Analyze this {lang} code and generate documentation.
    
Functions found: {func_names}
Classes found: {class_names}

Code:
{code_snippet}

Return ONLY valid JSON (no markdown, no backticks):
{{
  "summary": "2-3 sentence overview of what this code does",
  "purpose": "one line description",
  "functions_doc": {{"function_name": "what it does", ...}},
  "readme_section": "A README.md section for this module in markdown format"
}}"""

    try:
        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        import json, re
        raw = response.content.strip()
        raw = re.sub(r'^```json|^```|```$', '', raw, flags=re.MULTILINE).strip()
        doc = json.loads(raw, strict=False)
        return doc
        
    except Exception as e:
        return {
            "summary": f"Documentation generation failed: {str(e)}",
            "purpose": "Unable to generate",
            "functions_doc": {fn: "See source code" for fn in func_names},
            "readme_section": f"# {filename}\n\nSee source code for details."
        }