import subprocess
import time
from typing import Any, Dict, List, Optional
from core.interfaces import IExecutor
from config.settings import settings
from executor.permissions import permission_controller
from core_logging.logger import logger

class LocalExecutor(IExecutor):
    """Executes validated commands on the local host with timeout safety."""
    def execute(self, command: str, args: Optional[List[str]] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        full_command = (f"{command} " + " ".join(args)) if args else command
        
        # Enforce permission controller checks
        if not permission_controller.check_and_request_permission("local_cmd", full_command):
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "Permission denied: Execution rejected by user or security policy.",
                "duration_sec": 0.0,
                "error": "Permission Denied"
            }
            
        timeout = timeout or settings.executor.timeout_seconds
        start_time = time.time()
        
        try:
            logger.info(f"Executing local command: {full_command} with timeout={timeout}s")
            
            # Run in shell-less array mode if args are supplied, or shell if a raw string
            # On Windows, powershell or cmd might run. Let's use shell=True for raw command strings
            # while capturing stdout and stderr.
            result = subprocess.run(
                full_command if args is None else [command] + args,
                shell=True if args is None else False,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            duration = time.time() - start_time
            logger.info(f"Command execution completed: code={result.returncode}, duration={duration:.2f}s")
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_sec": round(duration, 3),
                "error": None
            }
            
        except subprocess.TimeoutExpired as te:
            duration = time.time() - start_time
            logger.error(f"Command timed out after {timeout} seconds: {full_command}")
            return {
                "exit_code": -2,
                "stdout": te.stdout or "",
                "stderr": te.stderr or f"Execution timed out after {timeout} seconds.",
                "duration_sec": round(duration, 3),
                "error": "TimeoutExpired"
            }
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to execute command: {e}")
            return {
                "exit_code": -3,
                "stdout": "",
                "stderr": f"Internal execution error: {e}",
                "duration_sec": round(duration, 3),
                "error": str(e)
            }
