from app.rag.retriever import retrieve_references

def run(vulnerabilities: list) -> dict:
    """Retrieve security references for each detected vulnerability."""
    enriched = {}
    
    for vuln in vulnerabilities:
        query = f"{vuln['vulnerability']} {vuln.get('cwe', '')} security vulnerability"
        refs = retrieve_references(query, n_results=2)
        enriched[vuln["vulnerability"]] = refs
    
    return enriched