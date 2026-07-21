import json
import uuid
from typing import Any, Dict, List, Optional
from providers.ollama import OllamaProvider
from planner.schemas import TaskPlan, PlanStep, StepStatus
from tools.registry import tool_registry
from core_logging.logger import logger

class TaskPlanner:
    """Uses the Ollama LLM to decompose complex goals into a series of structured steps."""
    def __init__(self, provider: Optional[OllamaProvider] = None):
        self.provider = provider or OllamaProvider()

    def generate_plan(self, goal: str) -> TaskPlan:
        """Query LLM to structure a step-by-step tool execution plan for a goal."""
        task_id = str(uuid.uuid4())[:8]
        logger.info(f"Generating execution plan for task {task_id}: '{goal}'")
        
        # Gather registered tool schemas to show LLM what options it has
        tool_schemas = tool_registry.get_ollama_schemas()
        tool_list_str = "\n".join([
            f"- {t['function']['name']}: {t['function']['description']}"
            for t in tool_schemas
        ])
        
        prompt = f"""
You are the Planning Module for Midnight Core, an autonomous Red Team / DevSecOps orchestrator.
Your job is to break down the user's request into a structured sequence of execution steps.
Each step MUST invoke one of the registered tools or distributions.

SECURITY-FIRST PLANNING PRINCIPLES (follow strictly):
1. Prioritize reconnaissance and information-gathering BEFORE any intrusive action.
2. Sequence steps to build attack-chain context (e.g. discover -> validate -> exploit -> report).
3. Only use tools the user is authorized to run; never invent tool names.
4. Keep each step focused on a single, verifiable outcome.
5. Prefer least-privilege and non-destructive checks first.

EXPERT WEB-AUDIT PLAYBOOK (use when the goal is about auditing/web app/vulnerability of a URL or host):
Sequence the steps to chain professional tooling via execute_wsl_shell_command.
Use ONLY tools confirmed installed in this Kali: nmap, whatweb, nikto, ffuf, amass, sqlmap, semgrep, arjun, gobuster.
  step 1: nmap -sV -p- <target>  (port + service discovery)
  step 2: whatweb http://<target>  (tech fingerprint: CMS, frameworks, libs)
  step 3: nikto -h http://<target>  (web server misconfig / known vulns)
  step 4: ffuf -u http://<target>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 20 -mc 200,204,301,302,403 -s  (directory fuzz)
  step 5: (if login/form exists) sqlmap -u http://<target> --batch --crawl=2  (SQLi check)
  step 6: produce expert report (orchestrator handles automatically)

EXPERT CODE-AUDIT PLAYBOOK (use when the goal mentions auditing source code / a local path):
  step 1: semgrep --config auto <path>  (static analysis of the user's own code)
  step 2: produce expert report

Here are the registered tools available for execution:
{tool_list_str}

Please generate a plan in raw JSON format. Do not add markdown backticks or extra text, output ONLY valid JSON matching this schema:
{{
  "title": "Short descriptive title of the task",
  "goal": "Clarified goal statement",
  "steps": [
    {{
      "index": 1,
      "title": "Step action description",
      "tool_name": "Name of the tool to execute",
      "arguments": {{
         "param_name": "value"
      }}
    }}
  ]
}}

User request: "{goal}"
JSON Plan:
"""
        messages = [
            {"role": "system", "content": "You are a precise JSON generator. Output only JSON, without markdown wrapper tags."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.provider.chat(messages)
            content = response.get("content", "").strip()
            
            # Clean possible markdown block wrappers
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            parsed = json.loads(content)
            
            steps = []
            for step_data in parsed.get("steps", []):
                steps.append(PlanStep(
                    index=step_data.get("index", len(steps) + 1),
                    title=step_data.get("title", "Execute tool"),
                    tool_name=step_data.get("tool_name", ""),
                    arguments=step_data.get("arguments", {}),
                    status=StepStatus.PENDING
                ))
                
            plan = TaskPlan(
                task_id=task_id,
                title=parsed.get("title", "Modular Task Plan"),
                goal=parsed.get("goal", goal),
                steps=steps,
                status=StepStatus.PENDING
            )
            logger.info(f"Successfully generated plan: '{plan.title}' with {len(plan.steps)} steps.")
            return plan
            
        except Exception as e:
            logger.error(f"Failed to generate structured plan: {e}", exc_info=True)
            # Fallback plan with a single manual step representing the direct command/goal
            return TaskPlan(
                task_id=task_id,
                title="Direct Request Execution",
                goal=goal,
                steps=[PlanStep(
                    index=1,
                    title="Direct execution check",
                    tool_name="execute_wsl_shell_command",
                    arguments={"command": goal},
                    status=StepStatus.PENDING
                )],
                status=StepStatus.PENDING
            )
