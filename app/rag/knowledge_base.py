import json
import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./sentinai_chroma_db"

def build_kb():
    """Build ChromaDB knowledge base from JSON files."""
    
    if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
        print("  Knowledge base already exists, skipping build.")
        return
    
    print("  Building knowledge base (first time only)...")
    
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = client.get_or_create_collection(
        name="security_knowledge",
        embedding_function=ef
    )
    
    documents = []
    metadatas = []
    ids = []
    
    base_path = "app/data/knowledge"
    
    for filename in ["cwe_entries.json", "owasp_entries.json"]:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            with open(filepath) as f:
                entries = json.load(f)
            for entry in entries:
                doc_text = f"{entry['name']}: {entry['description']} Remediation: {entry['remediation']}"
                documents.append(doc_text)
                metadatas.append({
                    "id": entry["id"],
                    "name": entry["name"],
                    "severity": entry["severity"],
                    "remediation": entry["remediation"],
                    "source": filename.replace("_entries.json", "").upper()
                })
                ids.append(entry["id"])
    
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"  Knowledge base built with {len(documents)} entries.\n")