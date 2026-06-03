def run(security_findings: list, bug_findings: list, ner_findings: list, parse_result: dict) -> dict:
    """Calculate code health score."""
    
    severity_weights = {"Critical": 25, "High": 15, "Medium": 8, "Low": 3, "Info": 1}
    
    base_score = 100
    
    # Deduct for security issues
    for finding in security_findings:
        base_score -= severity_weights.get(finding.get("severity", "Low"), 3)
    
    # Deduct for bugs
    for bug in bug_findings:
        base_score -= severity_weights.get(bug.get("severity", "Low"), 3) * 0.5
    
    # Deduct for exposed secrets
    high_ner = [n for n in ner_findings if n.get("severity") == "High"]
    base_score -= len(high_ner) * 10
    
    # Bonus for documentation
    funcs = parse_result.get("functions", [])
    documented = sum(1 for f in funcs if f.get("has_docstring", False))
    if funcs:
        doc_ratio = documented / len(funcs)
        base_score += doc_ratio * 5
    
    final_score = max(0, min(100, round(base_score)))
    
    if final_score >= 80:
        grade = "A"
        status = "Good"
        color = "green"
    elif final_score >= 60:
        grade = "B"
        status = "Fair"
        color = "orange"
    elif final_score >= 40:
        grade = "C"
        status = "Poor"
        color = "red"
    else:
        grade = "F"
        status = "Critical"
        color = "darkred"
    
    critical_count = sum(1 for f in security_findings if f.get("severity") == "Critical")
    high_count = sum(1 for f in security_findings if f.get("severity") == "High")
    
    return {
        "score": final_score,
        "grade": grade,
        "status": status,
        "color": color,
        "total_vulnerabilities": len(security_findings),
        "total_bugs": len(bug_findings),
        "total_secrets": len(ner_findings),
        "critical_issues": critical_count,
        "high_issues": high_count,
        "lines_of_code": parse_result.get("lines", 0),
        "functions_count": len(parse_result.get("functions", [])),
    }