import os
import platform
from typing import Optional
from tools.registry import tool_registry
from executor.wsl import WSLExecutor
from executor.local import LocalExecutor
from core_logging.logger import logger

local_executor = LocalExecutor()

@tool_registry.register(
    name="get_system_info",
    description="Retrieve basic host system telemetry (OS, architecture, CPUs, hostname).",
    parameters={
        "type": "object",
        "properties": {}
    }
)
def get_system_info() -> dict:
    """Retrieve system telemetries."""
    try:
        # Detect WSL distros
        distros = WSLExecutor.detect_distributions()
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "wsl_installed_distros": distros
        }
    except Exception as e:
        logger.error(f"Failed to fetch system info: {e}")
        return {"error": str(e)}


@tool_registry.register(
    name="execute_wsl_shell_command",
    description="Run a shell command inside the default WSL container (Kali Linux). Helpful for security tools and DevSecOps checks.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The exact shell command to run in Kali WSL (e.g., 'whoami', 'uname -a', 'nmap -F 127.0.0.1')"
            },
            "distro": {
                "type": "string",
                "description": "Optional specific WSL distribution name."
            }
        },
        "required": ["command"]
    }
)
def execute_wsl_shell_command(command: str, distro: Optional[str] = None) -> dict:
    """WSL execution wrapper tool."""
    wsl_exec = WSLExecutor(distro=distro)
    result = wsl_exec.execute(command)
    return result
