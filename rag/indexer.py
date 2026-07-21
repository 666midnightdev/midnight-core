import os
from typing import Any, Dict, List, Optional
from rag.parser import document_parser
from memory.store import memory_store
from core_logging.logger import logger

class RAGIndexer:
    """Chunks documents, generates vector embeddings, and stores them in the Memory system."""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlaps."""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunks.append(text[start:end])
            if end == text_len:
                break
            start += self.chunk_size - self.chunk_overlap
            
        return chunks

    def index_file(self, filepath: str) -> bool:
        """Extract text, chunk, generate embeddings, and index the file."""
        if not os.path.exists(filepath):
            logger.error(f"Cannot index file: File does not exist: {filepath}")
            return False
            
        try:
            content = document_parser.parse(filepath)
            if not content.strip() or "[PARSING FAILED]" in content:
                logger.warning(f"Skipping indexing for {filepath}: Empty or failed parsing.")
                return False
                
            chunks = self._chunk_text(content)
            logger.info(f"Chunked {filepath} into {len(chunks)} parts. Generating embeddings...")
            
            for idx, chunk in enumerate(chunks):
                metadata = {
                    "source": filepath,
                    "filename": os.path.basename(filepath),
                    "chunk_index": idx,
                    "total_chunks": len(chunks)
                }
                # Prepend basic metadata inside the indexed text for better semantic hits
                indexed_content = f"Source: {metadata['filename']} | Chunk {idx+1}/{len(chunks)}\n{chunk}"
                memory_store.add_semantic_document(indexed_content, metadata)
                
            logger.info(f"Successfully indexed file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error indexing file {filepath}: {e}", exc_info=True)
            return False

    def retrieve_context(self, query: str, top_k: int = 4) -> str:
        """Search the vector database and format matching chunks as context block."""
        results = memory_store.search_semantic(query, top_k)
        if not results:
            return "No matching RAG context found."
            
        formatted_chunks = []
        for idx, res in enumerate(results):
            score = res.get("score", 0.0)
            content = res.get("content", "")
            meta = res.get("metadata", {})
            source = meta.get("filename", "Unknown")
            
            formatted_chunks.append(
                f"--- RAG Context Chunk #{idx+1} [Source: {source}] [Relevance: {score}] ---\n{content}\n"
            )
            
        return "\n".join(formatted_chunks)

# Global indexer instance
rag_indexer = RAGIndexer()
