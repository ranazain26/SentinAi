import re

PATTERNS = {
    "API Key": [
        r'(?i)(api[_\-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9\-_]{20,})["\']',
        r'(?i)(sk-[A-Za-z0-9]{32,})',
        r'(?i)(AIza[0-9A-Za-z\-_]{35})',
    ],
    "Password": [
        r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']',
        r'(?i)(secret|token)\s*[=:]\s*["\']([A-Za-z0-9\-_!@#$%]{8,})["\']',
    ],
    "AWS Key": [
        r'(?i)(AKIA[0-9A-Z]{16})',
        r'(?i)(aws[_\-]?secret)\s*[=:]\s*["\']([^"\']{20,})["\']',
    ],
    "Private Key": [
        r'-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----',
    ],
    "Database URL": [
        r'(?i)(mongodb|postgresql|mysql|sqlite)\:\/\/[^\s"\']+',
    ],
    "URL / Endpoint": [
        r'https?://[^\s"\'<>]{10,}',
    ],
    "Email": [
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    ],
    "IP Address": [
        r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    ],
}

def run(code: str) -> list:
    """Detect sensitive entities in code."""
    findings = []
    lines = code.splitlines()
    
    for entity_type, patterns in PATTERNS.items():
        for pattern in patterns:
            for i, line in enumerate(lines, 1):
                match = re.search(pattern, line)
                if match:
                    findings.append({
                        "type": entity_type,
                        "line": i,
                        "snippet": line.strip()[:80],
                        "severity": "High" if entity_type in ["API Key", "Password", "AWS Key", "Private Key"] else "Medium"
                    })
    
    # Deduplicate by line
    seen = set()
    unique = []
    for f in findings:
        key = (f["line"], f["type"])
        if key not in seen:
            seen.add(key)
            unique.append(f)
    
    return unique