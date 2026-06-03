import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "./sentinai_chroma_db"

def retrieve_references(query: str, n_results: int = 3) -> list:
    """Retrieve relevant security references for a given query."""
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        collection = client.get_collection(
            name="security_knowledge",
            embedding_function=ef
        )
        results = collection.query(query_texts=[query], n_results=n_results)
        
        references = []
        if results and results["metadatas"]:
            for meta in results["metadatas"][0]:
                references.append(meta)
        return references
    except Exception as e:
        return [{"name": "Reference unavailable", "remediation": str(e), "severity": "Unknown", "source": "N/A", "id": "N/A"}]