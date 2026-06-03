import markdown

def export_html(markdown_text: str, output_path: str = "sentinai_report.html"):
    """Convert markdown report to a styled HTML file."""
    
    # Convert markdown to HTML with table and code block support
    html_body = markdown.markdown(
        markdown_text, 
        extensions=['tables', 'fenced_code', 'nl2br']
    )
    
    # Wrap in a clean, modern CSS template
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SentinAI Report</title>
    <style>
        body {{ font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; color: #24292e; max-width: 900px; margin: 0 auto; padding: 40px; }}
        h1, h2, h3 {{ color: #1a1f35; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid #dfe2e5; padding: 8px 13px; text-align: left; }}
        th {{ background-color: #f6f8fa; font-weight: 600; }}
        code {{ font-family: 'JetBrains Mono', monospace; background-color: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; color: #d73a49; }}
        pre {{ background-color: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; border: 1px solid #eaecef; }}
        pre code {{ background-color: transparent; padding: 0; color: #24292e; }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return output_path