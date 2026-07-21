import math
from typing import Any, Dict, List, Tuple
from memory.db import SQLiteMemoryBackend
from providers.ollama import OllamaProvider
from core_logging.logger import logger

class VectorDatabase:
    """Lightweight in-memory/SQLite vector database using custom Cosine Similarity."""
    def __init__(self, db_backend: SQLiteMemoryBackend, provider: OllamaProvider):
        self.db = db_backend
        self.provider = provider

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two lists of floats."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    def add_document(self, text: str, metadata: Dict[str, Any]) -> None:
        """Generate embeddings and index the text chunk."""
        embedding = self.provider.get_embedding(text)
        if embedding:
            self.db.save_vector(embedding, text, metadata)
            logger.debug(f"Document chunk indexed: size={len(text)} chars")
        else:
            logger.error("Failed to generate embedding for document chunk")

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search similar chunks using Ollama embeddings and custom similarity matching."""
        query_vector = self.provider.get_embedding(query_text)
        if not query_vector:
            logger.warning("Could not compute embedding for query")
            return []
            
        all_entries = self.db.get_all_vectors()
        scored_entries: List[Tuple[float, str, Dict[str, Any]]] = []
        
        for _, vector, content, metadata in all_entries:
            sim = self._cosine_similarity(query_vector, vector)
            scored_entries.append((sim, content, metadata))
            
        # Sort descending by similarity score
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, content, metadata in scored_entries[:top_k]:
            results.append({
                "score": round(score, 4),
                "content": content,
                "metadata": metadata
            })
            
        logger.info(f"Vector query completed. Top match score={results[0]['score'] if results else 0.0}")
        return results
