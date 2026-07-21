import socket
from tools.registry import tool_registry
from executor.local import LocalExecutor
from core_logging.logger import logger

local_executor = LocalExecutor()

@tool_registry.register(
    name="ping_host",
    description="Check connectivity to a target host (IP or Domain) by executing a system ping command.",
    parameters={
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Host name or IP address (e.g. 'google.com' or '127.0.0.1')"
            },
            "count": {
                "type": "integer",
                "description": "Number of packets to send.",
                "default": 3
            }
        },
        "required": ["target"]
    }
)
def ping_host(target: str, count: int = 3) -> str:
    """Ping utility."""
    import os
    # Formulate proper parameters based on OS
    if os.name == 'nt':
        cmd = f"ping -n {count} {target}"
    else:
        cmd = f"ping -c {count} {target}"
        
    res = local_executor.execute(cmd)
    if res["exit_code"] == 0:
        return res["stdout"]
    return f"[ERROR] Ping failed: {res['stderr']}"


@tool_registry.register(
    name="scan_local_ports",
    description="Scan standard TCP ports on a given target (restricted to local or authorized addresses).",
    parameters={
        "type": "object",
        "properties": {
            "host": {
                "type": "string",
                "description": "Target IP or hostname (default is localhost)",
                "default": "127.0.0.1"
            },
            "ports": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of ports to scan. Standard values: [21, 22, 80, 443, 3306, 8000, 8080]."
            }
        },
        "required": []
    }
)
def scan_local_ports(host: str = "127.0.0.1", ports: list = None, target: str = None) -> dict:
    """TCP Port scanner."""
    if target:
        host = target
    if ports is None:
        ports = [21, 22, 80, 443, 3306, 8000, 8080]
        
    from executor.permissions import permission_controller
    if not permission_controller.check_and_request_permission("port_scan", f"Scan {host} on ports {ports}"):
        return {"error": "Permission Denied"}
        
    results = {}
    logger.info(f"Starting port scan on target: {host}")
    
    for port in ports:
        # Check timeout to avoid blocking
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            code = s.connect_ex((host, port))
            if code == 0:
                results[port] = "OPEN"
            else:
                results[port] = "CLOSED"
        except Exception as e:
            results[port] = f"ERROR: {e}"
        finally:
            s.close()
            
    logger.info(f"Completed port scan on target: {host}")
    return results
