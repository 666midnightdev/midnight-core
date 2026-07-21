from typing import Any, Dict, List, Optional
from core.interfaces import IMemoryStore
from memory.db import SQLiteMemoryBackend
from providers.ollama import OllamaProvider
from memory.vector import VectorDatabase

class MemoryStore(IMemoryStore):
    """Aggregated Memory Store coordinating conversational, task, and semantic memory."""
    def __init__(self, db_path: Optional[str] = None):
        self.db = SQLiteMemoryBackend(db_path)
        self.provider = OllamaProvider()
        self.vector_db = VectorDatabase(self.db, self.provider)

    def add_message(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> None:
        self.db.save_message(session_id, role, content, tool_calls)

    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return self.db.get_messages(session_id, limit)

    def store_execution(self, task_id: str, command: str, output: str, exit_code: int, duration_sec: float, error: Optional[str] = None) -> None:
        combined_output = output
        if error:
            combined_output += f"\n[ERROR] {error}"
        self.db.save_execution(task_id, command, combined_output, exit_code, duration_sec)

    def log_task(self, task_id: str, title: str, status: str, plan: Optional[Dict[str, Any]] = None) -> None:
        self.db.save_task(task_id, title, status, plan)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.db.get_task(task_id)

    def get_all_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.db.get_all_tasks(limit)

    def search_semantic(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.vector_db.query(query, top_k)

    def add_semantic_document(self, text: str, metadata: Dict[str, Any]) -> None:
        self.vector_db.add_document(text, metadata)

# Global shared memory store instance
memory_store = MemoryStore()
