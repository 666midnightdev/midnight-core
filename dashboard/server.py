import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from config.settings import settings
from memory.store import memory_store
from core.orchestrator import CoreOrchestrator
from executor.permissions import permission_controller
from core_logging.logger import logger

app = FastAPI(
    title="Midnight Core API Panel",
    description="Backend controls and dashboard endpoints for Midnight Core platform.",
    debug=settings.dashboard.debug
)

class TaskRequest(BaseModel):
    goal: str

# Register default auto-approval logic for dashboard runtimes to prevent hanging
# It will auto-approve low risk actions, or print to logs.
# For production safety, we default to confirming or auto-approving defined safe local actions.
def default_dashboard_approval_callback(details: str) -> bool:
    logger.warning(f"[DASHBOARD AUTO-APPROVAL] Command requested validation: {details}")
    # If auto_approve_level is set to high, auto-approve all commands
    if settings.executor.auto_approve_level == "high":
        logger.info("[DASHBOARD AUTO-APPROVAL] Auto-approved command based on 'high' auto_approve_level configuration.")
        return True
    # Auto-approve safe actions
    return permission_controller.is_safe_command(details)

permission_controller.register_approval_callback(default_dashboard_approval_callback)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the single-page admin panel."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Dashboard index.html template not found.")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/tasks")
async def get_tasks() -> List[Dict[str, Any]]:
    """Retrieve execution task history."""
    try:
        tasks = memory_store.get_all_tasks(limit=30)
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_task_background(session_id: str, goal: str):
    try:
        orchestrator = CoreOrchestrator()
        orchestrator.run_task(session_id, goal)
    except Exception as e:
        logger.error(f"Error running background task: {e}", exc_info=True)

@app.post("/api/tasks/run")
async def run_task(req: TaskRequest, background_tasks: BackgroundTasks):
    """Dispatch a security assessment task to the Orchestration loop in the background."""
    try:
        session_id = "dashboard_default"
        background_tasks.add_task(run_task_background, session_id, req.goal)
        return {
            "task_id": "running_bg",
            "status": "RUNNING",
            "response": "Tugas berhasil dikirim ke latar belakang. AI sedang menyusun rencana dan memuat model Ollama..."
        }
    except Exception as e:
        logger.error(f"Error running task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/executions")
async def get_executions() -> List[Dict[str, Any]]:
    """Get system execution log audits."""
    try:
        return memory_store.db.get_executions(limit=50)
    except Exception as e:
        logger.error(f"Error fetching executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/view")
async def view_report(path: str):
    """Allows secure download/viewing of compiled HTML vulnerability reports."""
    reports_dir = os.path.normpath(os.path.join(settings.storage.base_dir, "reports"))
    
    # Try resolving the path - if it's just a filename, look inside reports_dir
    if os.sep not in path and "/" not in path:
        normalized_path = os.path.normpath(os.path.join(reports_dir, path))
    else:
        normalized_path = os.path.normpath(path)
    
    # Strict security check: path must be under reports_dir
    if not normalized_path.startswith(reports_dir + os.sep) and normalized_path != reports_dir:
        logger.error(f"Directory traversal check failed for report view: {path}")
        raise HTTPException(status_code=403, detail="Access denied: Directory traversal block triggered.")
        
    if not os.path.exists(normalized_path):
        raise HTTPException(status_code=404, detail="Report file not found.")
            
    return FileResponse(normalized_path)

def start_dashboard():
    """Starts the FastAPI Web server."""
    logger.info(f"Starting dashboard at http://{settings.dashboard.host}:{settings.dashboard.port}")
    uvicorn.run(
        app,
        host=settings.dashboard.host,
        port=settings.dashboard.port,
        log_level="info"
    )
