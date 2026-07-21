import re
from typing import Callable, Dict, List, Optional
from config.settings import settings
from core_logging.logger import logger

class PermissionController:
    """Manages command/tool execution permissions and approvals."""
    def __init__(self):
        self.approval_callback: Optional[Callable[[str], bool]] = None

    def register_approval_callback(self, callback: Callable[[str], bool]) -> None:
        """Register a callback to query the user for approval (CLI console or Web Dashboard)."""
        self.approval_callback = callback

    def is_safe_command(self, command_line: str) -> bool:
        """Analyze if a command is simple/read-only and does not modify the system."""
        # Check against simple read-only commands
        safe_patterns = [
            r"^whoami$",
            r"^uname\s*(-[aArsSvpim])?$",
            r"^pwd$",
            r"^ls\s*(-[a-zA-Z]+)?(\s+[\w\.\-\/]+)*$",
            r"^cat\s+[\w\.\-\/]+$",
            r"^grep\s+.*$",
            r"^ping\s+-c\s+\d+\s+[\w\.\-]+$",
            r"^ping\s+-n\s+\d+\s+[\w\.\-]+$",
            r"^git\s+status$",
            r"^git\s+log\s*(-n\s*\d+)?$",
            r"^echo\s+.*$"
        ]
        
        cmd_stripped = command_line.strip()
        for pattern in safe_patterns:
            if re.match(pattern, cmd_stripped, re.IGNORECASE):
                return True
        return False

    def check_and_request_permission(self, tool_name: str, details: str) -> bool:
        """
        Validates if the tool execution is allowed under the current policy,
        or prompts the user using the registered callback.
        """
        logger.info(f"Permission check requested: tool={tool_name}, details={details}")
        
        # If auto-approval is set to 'high', and it's a known safe command, approve automatically
        if settings.executor.auto_approve_level == "high" and self.is_safe_command(details):
            logger.info("Auto-approved based on 'high' policy and safe command signature.")
            return True

        # Read-only / non-destructive tools are safe to auto-approve under --auto-approve
        safe_tools = {"ping_host", "scan_local_ports", "get_system_info", "list_local_directory", "read_local_file"}
        if tool_name in safe_tools and settings.executor.auto_approve_level == "high":
            logger.info(f"Auto-approved read-only tool: {tool_name}")
            return True
            
        # Otherwise, if we have a callback, invoke it
        if self.approval_callback:
            logger.info("Invoking registered user approval callback...")
            approved = self.approval_callback(f"Tool: {tool_name} | Command: {details}")
            if approved:
                logger.info("User APPROVED the execution.")
                return True
            else:
                logger.warning("User REJECTED the execution.")
                return False
                
        # Default fallback: reject if no approval mechanism is registered
        logger.error("No approval callback registered. Rejecting tool execution by default.")
        return False

# Global permissions controller
permission_controller = PermissionController()
