import ast
import re

def parse_python(code: str) -> dict:
    """Parse Python code and extract structural information."""
    result = {
        "language": "python",
        "functions": [],
        "classes": [],
        "imports": [],
        "lines": len(code.splitlines()),
        "parse_error": None
    }
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result["functions"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": [a.arg for a in node.args.args],
                    "has_docstring": (
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant)
                        if node.body else False
                    )
                })
            elif isinstance(node, ast.ClassDef):
                result["classes"].append({"name": node.name, "line": node.lineno})
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom):
                    result["imports"].append(f"from {node.module} import ...")
                else:
                    for alias in node.names:
                        result["imports"].append(f"import {alias.name}")
    except SyntaxError as e:
        result["parse_error"] = str(e)
    
    return result

def parse_javascript(code: str) -> dict:
    """Basic JS parsing using regex (esprima optional)."""
    result = {
        "language": "javascript",
        "functions": [],
        "imports": [],
        "lines": len(code.splitlines()),
        "parse_error": None
    }
    
    func_pattern = re.compile(r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\()')
    for match in func_pattern.finditer(code):
        name = match.group(1) or match.group(2)
        if name:
            result["functions"].append({"name": name, "line": code[:match.start()].count('\n') + 1})
    
    import_pattern = re.compile(r'(?:import|require)\s*[\({]?\s*["\']([^"\']+)["\']')
    for match in import_pattern.finditer(code):
        result["imports"].append(f"import {match.group(1)}")
    
    return result

def run(code: str, filename: str = "code.py") -> dict:
    ext = filename.split(".")[-1].lower()
    if ext == "js":
        return parse_javascript(code)
    return parse_python(code)