from tools.registry import tool_registry

# Import tool modules to trigger decorators and populate registry
import tools.system
import tools.filesystem
import tools.network

__all__ = ["tool_registry"]
