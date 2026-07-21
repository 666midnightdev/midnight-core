import sys
import json
from typing import Any, Dict, List, Optional
from tools.registry import tool_registry
from core_logging.logger import logger

class MCPServer:
    """Stdio-based Model Context Protocol (MCP) server for Midnight Core."""
    def __init__(self):
        # We need to make sure stdin/stdout are in utf-8 mode
        # to avoid Windows character encoding crashes.
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')

    def run(self) -> None:
        """Start the main stdio listening loop."""
        logger.info("MCP server started, listening on stdin...")
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error in MCP message loop: {e}", exc_info=True)

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process standard JSON-RPC 2.0 protocol calls."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if not method:
            return self._error_response(req_id, -32600, "Invalid Request: Method is missing.")

        logger.info(f"MCP Request: method={method}, id={req_id}")

        if method == "tools/list":
            # Map tools from registry to MCP schemas
            mcp_tools = []
            for name, info in tool_registry.tools.items():
                mcp_tools.append({
                    "name": name,
                    "description": info["description"],
                    "inputSchema": info["parameters"]
                })
            return self._success_response(req_id, {"tools": mcp_tools})

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if not tool_name:
                return self._error_response(req_id, -32602, "Invalid Params: Tool name is missing.")
                
            try:
                # Execute tool
                result = tool_registry.execute_tool(tool_name, tool_args)
                return self._success_response(req_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                })
            except Exception as e:
                logger.error(f"MCP failed to execute tool {tool_name}: {e}")
                return self._error_response(req_id, -32603, f"Internal tool execution error: {e}")

        # Standard fallback for unknown methods
        return self._error_response(req_id, -32601, f"Method not found: '{method}'")

    def _success_response(self, req_id: Any, result: Any) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        }

    def _error_response(self, req_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": code,
                "message": message
            }
        }
