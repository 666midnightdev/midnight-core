import json
import requests
from typing import Any, Dict, List, Optional, Generator
from core.interfaces import ILLMProvider
from config.settings import settings
from core_logging.logger import logger

class OllamaProvider(ILLMProvider):
    """Ollama API Client supporting chat, streaming, and embeddings."""
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or settings.llm.url
        self.model = model or settings.llm.model
        self.embedding_model = settings.llm.embedding_model
        
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": settings.llm.temperature,
                "num_ctx": settings.llm.context_length
            }
        }
        if tools:
            payload["tools"] = tools
            
        try:
            logger.debug(f"Sending chat request to Ollama: {url} with model {self.model}")
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {"role": "assistant", "content": ""})
        except Exception as e:
            logger.error(f"Ollama chat error: {e}", exc_info=True)
            return {"role": "assistant", "content": f"[OLLAMA ERROR] {e}"}

    def chat_stream(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Generator[Dict[str, Any], None, None]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": settings.llm.temperature,
                "num_ctx": settings.llm.context_length
            }
        }
        if tools:
            payload["tools"] = tools

        try:
            logger.debug(f"Sending streaming chat request to Ollama: {url} with model {self.model}")
            response = requests.post(url, json=payload, stream=True, timeout=settings.executor.timeout_seconds)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                        yield data
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError as jde:
                        logger.error(f"Failed to decode Ollama stream line: {decoded}. Error: {jde}")
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}", exc_info=True)
            yield {"done": True, "error": str(e), "message": {"role": "assistant", "content": f"\n[OLLAMA STREAM ERROR] {e}"}}

    def get_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.embedding_model,
            "prompt": text
        }
        try:
            logger.debug(f"Getting embedding from Ollama for text preview: '{text[:30]}...'")
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])
        except Exception as e:
            logger.error(f"Ollama embedding error for model {self.embedding_model}: {e}")
            # Return dummy embeddings (e.g. zeros) to prevent hard crashes
            return [0.0] * 768
