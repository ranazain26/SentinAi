import re
import ast

VULN_PATTERNS = {
    "SQL Injection": {
        "patterns": [
            r'(?i)(execute|query)\s*\(\s*["\'][^"\']*%s',
            r'(?i)(execute|query)\s*\(\s*f["\']',
            r'(?i)(execute|query)\s*\(\s*"[^"]*"\s*\+',
            r'(?i)(execute|query)\s*\(\s*\'[^\']*\'\s*\+',
        ],
        "severity": "Critical",
        "cwe": "CWE-89"
    },
    "Command Injection": {
        "patterns": [
            r'(?i)os\.system\s*\(',
            r'(?i)subprocess\.(call|run|Popen)\s*\([^,)]*shell\s*=\s*True',
            r'(?i)eval\s*\(',
            r'(?i)exec\s*\(',
        ],
        "severity": "Critical",
        "cwe": "CWE-78"
    },
    "Hardcoded Secret": {
        "patterns": [
            r'(?i)(password|passwd|pwd|secret|api_key)\s*=\s*["\'][^"\']{4,}["\']',
            r'(?i)(token|auth)\s*=\s*["\'][A-Za-z0-9\-_]{10,}["\']',
        ],
        "severity": "High",
        "cwe": "CWE-798"
    },
    "Weak Hashing": {
        "patterns": [
            r'(?i)(hashlib\.md5|hashlib\.sha1)\s*\(',
            r'(?i)md5\s*\(',
        ],
        "severity": "High",
        "cwe": "CWE-327"
    },
    "Unsafe Deserialization": {
        "patterns": [
            r'(?i)pickle\.loads?\s*\(',
            r'(?i)yaml\.load\s*\([^)]*\)',
            r'(?i)marshal\.loads?\s*\(',
        ],
        "severity": "Critical",
        "cwe": "CWE-502"
    },
    "Path Traversal": {
        "patterns": [
            r'(?i)open\s*\(\s*[^)]*\+[^)]*\)',
            r'(?i)open\s*\(\s*f["\'].*\{',
        ],
        "severity": "High",
        "cwe": "CWE-22"
    },
    "Weak Random": {
        "patterns": [
            r'(?i)random\.(random|randint|choice)\s*\(',
        ],
        "severity": "Medium",
        "cwe": "CWE-338"
    },
    "Debug/Development Code": {
        "patterns": [
            r'(?i)debug\s*=\s*True',
            r'(?i)print\s*\([^)]*password',
            r'(?i)console\.log\s*\([^)]*token',
        ],
        "severity": "Low",
        "cwe": "CWE-215"
    }
}

def run(code: str) -> list:
    """Detect security vulnerabilities in source code."""
    findings = []
    lines = code.splitlines()
    
    for vuln_name, config in VULN_PATTERNS.items():
        for pattern in config["patterns"]:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    findings.append({
                        "vulnerability": vuln_name,
                        "line": i,
                        "snippet": line.strip()[:100],
                        "severity": config["severity"],
                        "cwe": config["cwe"],
                        "description": get_description(vuln_name)
                    })
    
    # Deduplicate
    seen = set()
    unique = []
    for f in findings:
        key = (f["line"], f["vulnerability"])
        if key not in seen:
            seen.add(key)
            unique.append(f)
    
    return unique

def get_description(vuln_name: str) -> str:
    descriptions = {
        "SQL Injection": "User input directly concatenated into SQL query — allows database manipulation.",
        "Command Injection": "Unsanitized input passed to OS commands — allows arbitrary code execution.",
        "Hardcoded Secret": "Credentials hardcoded in source — exposed if code is shared or committed.",
        "Weak Hashing": "MD5/SHA1 are cryptographically broken for password hashing.",
        "Unsafe Deserialization": "Deserializing untrusted data can lead to remote code execution.",
        "Path Traversal": "Unvalidated file path allows access outside intended directory.",
        "Weak Random": "random module is not cryptographically secure.",
        "Debug/Development Code": "Debug flags or logging of sensitive data in production.",
    }
    return descriptions.get(vuln_name, "Potential security issue detected.")