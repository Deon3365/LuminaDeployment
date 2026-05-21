from .knowledge_base import KnowledgeBase

class RAGRetriever:
    def __init__(self, db_path="./rag_db"):
        self.kb = KnowledgeBase(db_path)

    def query_culture(self, query_text, testament="NT", n=3):
        col_name = "greek_culture" if testament == "NT" else "jewish_culture"
        col = self.kb.get_or_create_collection(col_name)
        results = col.query(query_texts=[query_text], n_results=n)
        return results["documents"][0] if results["documents"] else []

    def query_verses(self, query_text, n=5):
        col = self.kb.get_or_create_collection("verses")
        results = col.query(query_texts=[query_text], n_results=n)
        return results["documents"][0] if results["documents"] else []

    def query_commentary(self, reference, n=3):
        col = self.kb.get_or_create_collection("commentary")
        # Exact match filtering for the reference if possible, or semantic search
        results = col.query(query_texts=[reference], n_results=n)
        return results["documents"][0] if results["documents"] else []

    def get_context_bundle(self, reference, testament="NT", key_terms=None):
        """Unified bundle of context for the orchestrator to distribute."""
        key_terms = key_terms or []
        query_text = f"{reference} {' '.join(key_terms)}"
        
        return {
            "historical_cultural": self.query_culture(query_text, testament, n=3),
            "related_verses": self.query_verses(query_text, n=5),
            "commentary": self.query_commentary(reference, n=4)
        }
