from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generator

class ILLMProvider(ABC):
    """Interface for LLM providers (e.g., Ollama, mock, etc.)."""
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Send chat messages and optional tools, return full response metadata and text."""
        pass

    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Generator[Dict[str, Any], None, None]:
        """Stream response chunks (text/tool_calls) as they arrive from the LLM."""
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Get vector representation for RAG or search."""
        pass

class IExecutor(ABC):
    """Interface for command execution layers (Local and WSL)."""
    @abstractmethod
    def execute(self, command: str, args: Optional[List[str]] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a tool/command and return a standard execution result JSON."""
        pass

class IMemoryStore(ABC):
    """Interface for memory management."""
    @abstractmethod
    def add_message(self, session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> None:
        """Store conversational message history."""
        pass

    @abstractmethod
    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent conversational history."""
        pass

    @abstractmethod
    def store_execution(self, task_id: str, command: str, output: str, exit_code: int, duration_sec: float, error: Optional[str] = None) -> None:
        """Log tool execution history."""
        pass

class IRAGIndex(ABC):
    """Interface for RAG document indexer and searcher."""
    @abstractmethod
    def index_file(self, filepath: str) -> bool:
        """Parse, chunk, embed, and index a file."""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search similar document chunks."""
        pass
