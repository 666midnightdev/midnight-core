import os
from tools.registry import tool_registry
from executor.local import LocalExecutor
from rag.indexer import rag_indexer
from core_logging.logger import logger

local_executor = LocalExecutor()

@tool_registry.register(
    name="read_local_file",
    description="Read the complete text content of a file from the host filesystem.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or relative file path to read (e.g. 'C:/midnight_agent/config.json')"
            }
        },
        "required": ["path"]
    }
)
def read_local_file(path: str) -> str:
    """Safe read file."""
    # Use LocalExecutor to route through permission check & file reading
    # Or implement natively while respecting LocalExecutor's structure
    res = local_executor.execute(f"type {path}" if os.name == 'nt' else f"cat {path}")
    if res["exit_code"] == 0:
        return res["stdout"]
    else:
        return f"[ERROR] Failed to read file: {res['stderr']}"


@tool_registry.register(
    name="write_local_file",
    description="Write text content to a file in the local filesystem. Overwrites existing contents.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or relative file path to write to."
            },
            "content": {
                "type": "string",
                "description": "The exact content to write to the file."
            }
        },
        "required": ["path", "content"]
    }
)
def write_local_file(path: str, content: str) -> str:
    """Safe write file."""
    # Enforce directory creation first
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    
    # We execute via local_executor or direct file writing after checking permission controller
    from executor.permissions import permission_controller
    if not permission_controller.check_and_request_permission("write_file", f"Write to: {path}"):
        return "[ERROR] Permission denied to write file."
        
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"File written successfully: {path}")
        return f"File successfully written to: {path}"
    except Exception as e:
        logger.error(f"Failed to write file {path}: {e}")
        return f"[ERROR] Failed to write file: {e}"


@tool_registry.register(
    name="list_local_directory",
    description="List files and folders in a local directory path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to list."
            }
        },
        "required": ["path"]
    }
)
def list_local_directory(path: str) -> str:
    """Safe list directory."""
    res = local_executor.execute(f"dir {path}" if os.name == 'nt' else f"ls -la {path}")
    if res["exit_code"] == 0:
        return res["stdout"]
    else:
        return f"[ERROR] Failed to list directory: {res['stderr']}"


@tool_registry.register(
    name="index_file_for_rag",
    description="Index a local code file, configuration, or document for semantic searches.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the document to chunk and index."
            }
        },
        "required": ["path"]
    }
)
def index_file_for_rag(path: str) -> str:
    """Indexes a file inside RAG memory."""
    success = rag_indexer.index_file(path)
    if success:
        return f"Successfully chunked and indexed file for RAG: {path}"
    return f"[ERROR] Failed to index file for RAG: {path}"
