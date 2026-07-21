import inspect
import json
from typing import Any, Callable, Dict, List, Optional
from core_logging.logger import logger

class ToolRegistry:
    """Registry to record, describe, and execute approved tools."""
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, parameters: Dict[str, Any]) -> Callable:
        """Decorator to register a tool function."""
        def decorator(func: Callable) -> Callable:
            self.tools[name] = {
                "name": name,
                "description": description,
                "parameters": parameters,
                "func": func
            }
            logger.info(f"Registered tool: {name}")
            return func
        return decorator

    def get_ollama_schemas(self) -> List[Dict[str, Any]]:
        """Return schema format that Ollama tool parameter accepts."""
        schemas = []
        for name, info in self.tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
            })
        return schemas

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Validates arguments, runs the tool by name, and handles potential errors."""
        logger.info(f"Executing tool: {name} with arguments={json.dumps(arguments)}")
        
        if name not in self.tools:
            err = f"Error: Tool '{name}' is not registered."
            logger.error(err)
            return err
            
        tool_info = self.tools[name]
        func = tool_info["func"]
        
        try:
            # Simple signature alignment validation
            sig = inspect.signature(func)
            bound = sig.bind(**arguments)
            bound.apply_defaults()
            
            # Execute
            result = func(*bound.args, **bound.kwargs)
            
            # Formulate standard string response
            if isinstance(result, (dict, list)):
                return json.dumps(result, indent=2)
            return str(result)
            
        except TypeError as te:
            err = f"Parameter validation error for tool '{name}': {te}"
            logger.error(err)
            return f"[ERROR] {err}"
        except Exception as e:
            err = f"Execution error in tool '{name}': {e}"
            logger.error(err, exc_info=True)
            return f"[ERROR] {err}"

# Global shared tool registry
tool_registry = ToolRegistry()
