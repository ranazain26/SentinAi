from app.agents import parser_agent, ner_agent, security_agent, bug_agent, rag_agent, doc_agent, scoring_agent

def analyze(code: str, filename: str = "code.py") -> dict:
    """Main orchestrator: runs all agents in sequence."""
    
    results = {"filename": filename, "status": "running"}
    
    # Step 1: Parse
    results["parse"] = parser_agent.run(code, filename)
    
    # Step 2: NER
    results["ner"] = ner_agent.run(code)
    
    # Step 3: Security
    results["security"] = security_agent.run(code)
    
    # Step 4: Bugs
    results["bugs"] = bug_agent.run(code)
    
    # Step 5: RAG enrichment
    if results["security"]:
        results["rag_references"] = rag_agent.run(results["security"])
    else:
        results["rag_references"] = {}
    
    # Step 6: Documentation
    results["documentation"] = doc_agent.run(code, results["parse"], filename)
    
    # Step 7: Scoring
    results["score"] = scoring_agent.run(
        results["security"],
        results["bugs"],
        results["ner"],
        results["parse"]
    )
    
    results["status"] = "complete"
    return results