import subprocess
import time
import re
from typing import Any, Dict, List, Optional
from core.interfaces import IExecutor
from config.settings import settings
from executor.permissions import permission_controller
from core_logging.logger import logger

class WSLExecutor(IExecutor):
    """Integrates with Windows Subsystem for Linux (WSL) for running tools."""
    def __init__(self, distro: Optional[str] = None):
        self.distro = distro or settings.executor.default_wsl_distro

    @staticmethod
    def detect_distributions() -> List[Dict[str, Any]]:
        """Detect installed WSL distributions and identify default distribution."""
        try:
            logger.info("Detecting WSL distributions...")
            # wsl -l -v outputs in UTF-16LE on Windows
            result = subprocess.run(
                ["wsl", "--list", "--verbose"],
                capture_output=True,
                timeout=10
            )
            
            # Attempt to decode as UTF-16LE, fallback to UTF-8
            raw_output = result.stdout
            try:
                output = raw_output.decode("utf-16le")
                # If decoded correctly, it shouldn't contain massive numbers of null bytes
                if "\x00" in output:
                    output = raw_output.decode("utf-8", errors="replace")
            except Exception:
                output = raw_output.decode("utf-8", errors="replace")
                
            # Clean up the output string (strip nulls, carriage returns, etc.)
            output = output.replace("\x00", "").replace("\r", "")
            
            lines = [line.strip() for line in output.split("\n") if line.strip()]
            distros = []
            
            if len(lines) > 1:
                # First line is header: NAME STATE VERSION
                for line in lines[1:]:
                    # Match pattern with possible '*' indicating default
                    match = re.match(r"^(\*?)\s*([a-zA-Z0-9\.\-_]+)\s+([a-zA-Z0-9]+)\s+(\d+)$", line)
                    if match:
                        is_default = match.group(1) == "*"
                        name = match.group(2)
                        state = match.group(3)
                        version = int(match.group(4))
                        distros.append({
                            "name": name,
                            "is_default": is_default,
                            "state": state,
                            "version": version
                        })
            return distros
        except Exception as e:
            logger.error(f"Error detecting WSL distributions: {e}")
            return []

    def execute(self, command: str, args: Optional[List[str]] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Runs a bash command in the selected WSL distribution."""
        # Reconstruct full command string for WSL execution
        cmd_str = command
        if args:
            cmd_str += " " + " ".join(args)
            
        # Permission check
        if not permission_controller.check_and_request_permission(f"wsl_{self.distro}", cmd_str):
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "Permission denied: Execution rejected by user or security policy.",
                "duration_sec": 0.0,
                "error": "Permission Denied"
            }
            
        timeout = timeout or settings.executor.timeout_seconds
        start_time = time.time()
        
        # WSL execution wrapper command
        # use login shell (-l) so PATH/profile is sourced (Kali default tools live in /usr/bin)
        wsl_command = ["wsl", "-d", self.distro, "--", "bash", "-lc", cmd_str]
        
        try:
            logger.info(f"Executing WSL command in '{self.distro}': {cmd_str} with timeout={timeout}s")
            
            result = subprocess.run(
                wsl_command,
                capture_output=True,
                timeout=timeout,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            duration = time.time() - start_time
            logger.info(f"WSL command completed: code={result.returncode}, duration={duration:.2f}s")
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_sec": round(duration, 3),
                "error": None
            }
            
        except subprocess.TimeoutExpired as te:
            duration = time.time() - start_time
            logger.error(f"WSL command timed out after {timeout} seconds")
            return {
                "exit_code": -2,
                "stdout": te.stdout or "",
                "stderr": te.stderr or f"WSL execution timed out after {timeout} seconds.",
                "duration_sec": round(duration, 3),
                "error": "TimeoutExpired"
            }
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"WSL execution error: {e}")
            return {
                "exit_code": -3,
                "stdout": "",
                "stderr": f"Internal WSL execution error: {e}",
                "duration_sec": round(duration, 3),
                "error": str(e)
            }
