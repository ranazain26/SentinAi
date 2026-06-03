import ast
import re

def run(code: str) -> list:
    """Detect logical and runtime bugs in Python code."""
    bugs = []
    lines = code.splitlines()
    
    # Pattern-based checks
    bug_patterns = [
        {
            "pattern": r'except\s*:',
            "name": "Bare Exception Catch",
            "description": "Catches all exceptions including SystemExit and KeyboardInterrupt. Use specific exception types.",
            "severity": "Medium"
        },
        {
            "pattern": r'==\s*True|==\s*False|==\s*None',
            "name": "Identity Comparison",
            "description": "Use 'is True', 'is False', 'is None' instead of == for boolean/None comparisons.",
            "severity": "Low"
        },
        {
            "pattern": r'(?i)while\s+True\s*:(?!.*break)',
            "name": "Potential Infinite Loop",
            "description": "While True loop detected — ensure there is a break or return condition.",
            "severity": "Medium"
        },
        {
            "pattern": r'def\s+\w+\([^)]*\)\s*:\s*\n\s*pass',
            "name": "Empty Function",
            "description": "Function body contains only 'pass' — likely unimplemented logic.",
            "severity": "Low"
        },
        {
            "pattern": r'(?i)time\.sleep\(\d{3,}\)',
            "name": "Very Long Sleep",
            "description": "Sleep for 100+ seconds detected — likely a bug or leftover debug code.",
            "severity": "Low"
        },
        {
            "pattern": r'\bprint\s*\(',
            "name": "Debug Print Statement",
            "description": "print() found — consider using logging module for production code.",
            "severity": "Info"
        },
        {
            "pattern": r'(?i)TODO|FIXME|HACK|XXX|BUG',
            "name": "TODO/FIXME Comment",
            "description": "Unresolved TODO or FIXME comment found — incomplete implementation.",
            "severity": "Info"
        },
        {
            "pattern": r'(?<!\w)0[0-9]+(?!\w)',
            "name": "Octal Literal",
            "description": "Possible unintended octal literal (leading zero). Use 0o prefix explicitly.",
            "severity": "Low"
        }
    ]
    
    for i, line in enumerate(lines, 1):
        for check in bug_patterns:
            if re.search(check["pattern"], line):
                bugs.append({
                    "bug": check["name"],
                    "line": i,
                    "snippet": line.strip()[:100],
                    "description": check["description"],
                    "severity": check["severity"]
                })
    
    # AST-based checks
    try:
        tree = ast.parse(code)
        ast_bugs = _ast_checks(tree)
        bugs.extend(ast_bugs)
    except SyntaxError as e:
        bugs.append({
            "bug": "Syntax Error",
            "line": e.lineno or 0,
            "snippet": str(e),
            "description": f"Python syntax error: {e.msg}",
            "severity": "Critical"
        })
    
    # Deduplicate
    seen = set()
    unique = []
    for b in bugs:
        key = (b["line"], b["bug"])
        if key not in seen:
            seen.add(key)
            unique.append(b)
    
    return unique

def _ast_checks(tree) -> list:
    bugs = []
    for node in ast.walk(tree):
        # Mutable default argument
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    bugs.append({
                        "bug": "Mutable Default Argument",
                        "line": node.lineno,
                        "snippet": f"def {node.name}(...)",
                        "description": "Using mutable default (list/dict/set) in function signature causes shared state between calls.",
                        "severity": "High"
                    })
        # Division without zero check (basic heuristic)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if isinstance(node.right, ast.Name):
                bugs.append({
                    "bug": "Potential Division by Zero",
                    "line": getattr(node, 'lineno', 0),
                    "snippet": "division by variable",
                    "description": f"Division by variable '{node.right.id}' without zero-check.",
                    "severity": "Medium"
                })
    return bugs