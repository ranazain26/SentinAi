from fpdf import FPDF
import re
import textwrap
from datetime import datetime

def export_pdf(markdown_text: str, output_path: str = "sentinai_report.pdf"):
    """Convert markdown report to PDF safely."""
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 12, "SentinAI Security Audit Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)
    
    lines = markdown_text.splitlines()
    
    for line in lines:
        # THE FIX: Kill tabs that crash fpdf2's horizontal space calculator
        line = line.replace('\t', '    ')
        line = line.strip()
        
        if not line:
            pdf.ln(2)
            continue
        
        # Clean markdown
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        clean = re.sub(r'`(.+?)`', r'[\1]', clean)
        clean = re.sub(r'^#{1,6}\s*', '', clean)
        clean = re.sub(r'^\|.*\|$', '', clean)
        clean = re.sub(r'^[-*]\s*', '• ', clean)
        
        if not clean.strip() or clean.strip() == '---':
            if clean.strip() == '---':
                pdf.set_draw_color(200, 200, 200)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(3)
            continue
        
        # Set fonts based on headers
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(30, 30, 80)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(60, 60, 120)
        elif line.startswith("**") and line.endswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(50, 50, 50)
        else:
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(50, 50, 50)
        
        # THE FIX: Drop unrenderable unicode characters (emojis, weird formatting)
        safe_text = clean.encode('latin-1', 'ignore').decode('latin-1')
        
        # THE FIX: Wrap text to max 85 chars, forcefully breaking long hashes/keys
        wrapped_text = textwrap.fill(safe_text, width=85, break_long_words=True)
        
        # THE FIX: Print line-by-line to prevent massive block crashes
        for wrapped_line in wrapped_text.split('\n'):
            try:
                pdf.multi_cell(0, 5, wrapped_line)
            except Exception:
                # Ultimate fallback - skip the bad line entirely rather than crashing the whole app
                pass
                
    pdf.output(output_path)
    return output_path