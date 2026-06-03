"""
SentinAI Launcher
Run this file: python run.py
"""

import subprocess
import sys
import os

def check_and_install_dependencies():
    print("=" * 50)
    print("  SentinAI - Checking dependencies...")
    print("=" * 50)
    
    try:
        import pkg_resources
        with open("requirements.txt") as f:
            required = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        missing = []
        for package in required:
            pkg_name = package.split(">=")[0].split("==")[0].split("[")[0]
            try:
                pkg_resources.require(package)
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                missing.append(package)
        
        if missing:
            print(f"\n  Installing {len(missing)} missing package(s)...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", *missing, "--quiet"
            ])
            print("  All dependencies installed successfully!\n")
        else:
            print("  All dependencies already satisfied.\n")
            
    except Exception as e:
        print(f"  Dependency check failed: {e}")
        print("  Attempting full install from requirements.txt...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"
        ])

def check_env():
    from dotenv import load_dotenv
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("\n  WARNING: GROQ_API_KEY not found in .env file!")
        print("  Get your free key at: https://console.groq.com")
        print("  Add it to .env as: GROQ_API_KEY=your_key_here\n")
    else:
        print("  API key found.\n")

def build_knowledge_base():
    """Pre-build ChromaDB knowledge base on first run."""
    try:
        from app.rag.knowledge_base import build_kb
        build_kb()
    except Exception as e:
        print(f"  Knowledge base note: {e}")

def launch_app():
    print("  Launching SentinAI...")
    print("  Open your browser at: http://localhost:8501\n")
    os.system(f"{sys.executable} -m streamlit run app/main.py --server.port 8501")

if __name__ == "__main__":
    check_and_install_dependencies()
    check_env()
    build_knowledge_base()
    launch_app()