from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class PlanStep(BaseModel):
    index: int
    title: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    duration_sec: float = 0.0

class TaskPlan(BaseModel):
    task_id: str
    title: str
    goal: str
    steps: List[PlanStep] = Field(default_factory=list)
    current_step_index: int = 0
    status: StepStatus = StepStatus.PENDING
    summary_report: Optional[str] = None
