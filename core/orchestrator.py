import time
import json
import os
from typing import Any, Dict, List, Optional
from providers.ollama import OllamaProvider
from planner.planner import TaskPlanner
from planner.schemas import TaskPlan, StepStatus
from tools.registry import tool_registry
from memory.store import memory_store
from reports.generator import ReportGenerator
from core_logging.logger import logger
from core.security_validation import SecurityValidator


class CoreOrchestrator:
    """Coordinating loop driving planning, tool execution, memory logging, and reporting.

    Enhanced with expert-level SecurityValidator integration to reduce hallucinations
    and provide correlated MITRE ATT&CK / CVE / OWASP intelligence on every tool output.
    """

    def __init__(self, provider: Optional[OllamaProvider] = None):
        self.provider = provider or OllamaProvider()
        self.planner = TaskPlanner(self.provider)
        self.reports_generator = ReportGenerator()
        # Single shared expert validator instance
        self.security_validator = SecurityValidator()

    def run_task(self, session_id: str, goal: str) -> Dict[str, Any]:
        """Execute a full task cycle: Plan -> Execute Steps -> Validate -> Review -> Report."""
        logger.info(f"Starting orchestrator run for goal: '{goal}' in session {session_id}")

        # 1. Store user goal in conversation memory
        memory_store.add_message(session_id, "user", goal)

        # 2. Generate execution plan
        plan = self.planner.generate_plan(goal)
        plan.status = StepStatus.RUNNING
        memory_store.log_task(plan.task_id, plan.title, plan.status.value, plan.model_dump())

        findings: List[Dict[str, Any]] = []

        # 3. Step execution loop
        for idx, step in enumerate(plan.steps):
            plan.current_step_index = idx
            step.status = StepStatus.RUNNING
            logger.info(f"Running step {step.index}/{len(plan.steps)}: {step.title}")

            start_time = time.time()

            # Execute tool through registry
            tool_output = tool_registry.execute_tool(step.tool_name, step.arguments)

            duration = time.time() - start_time
            step.duration_sec = round(duration, 3)
            step.result = tool_output

            # Assess success
            if "[ERROR]" in tool_output or "Permission denied" in tool_output:
                step.status = StepStatus.FAILED
                plan.status = StepStatus.FAILED
                logger.error(f"Step {step.index} failed with output: {tool_output[:200]}")
            else:
                step.status = StepStatus.COMPLETED
                logger.info(f"Step {step.index} completed successfully.")

            # Log execution history in Memory
            memory_store.store_execution(
                task_id=plan.task_id,
                command=f"Tool: {step.tool_name} | Args: {step.arguments}",
                output=tool_output,
                exit_code=0 if step.status == StepStatus.COMPLETED else -1,
                duration_sec=step.duration_sec
            )

            # Parse possible finding from output + run EXPERT validation
            if step.status == StepStatus.COMPLETED and step.tool_name in ("execute_wsl_shell_command", "scan_local_ports"):
                analysis = self._analyze_tool_output(step.title, tool_output)
                if analysis.get("is_vulnerability"):
                    # 🔐 EXPERT VALIDATION: correlate against CVE / MITRE / OWASP
                    context = {
                        "command": step.arguments.get("command", "") if isinstance(step.arguments, dict) else "",
                        "step_title": step.title,
                        "tool_name": step.tool_name
                    }
                    validation = self.security_validator.validate_security_output(tool_output, context)

                    # Enrich the LLM finding with expert validation metadata
                    analysis["security_validation"] = validation
                    analysis["expert_confidence"] = validation.get("confidence_score")
                    analysis["security_classification"] = validation.get("security_classification")
                    findings.append(analysis)

                    logger.info(
                        f"Expert validation -> confidence={validation.get('confidence_score'):.2f} "
                        f"level={validation.get('confidence_level')} "
                        f"cves={len(validation.get('cve_references', []))} "
                        f"mitre={len(validation.get('mitre_techniques', []))}"
                    )

            # Update task in DB
            memory_store.log_task(plan.task_id, plan.title, plan.status.value, plan.model_dump())

            # Stop execution if a step fails
            if step.status == StepStatus.FAILED:
                break

        if plan.status != StepStatus.FAILED:
            plan.status = StepStatus.COMPLETED

        # 4. Generate final report and persist to DB
        report_files = {}
        if findings or plan.status == StepStatus.COMPLETED:
            risk_map = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}
            max_risk = "INFO"
            max_val = 1
            for f in findings:
                # Prefer expert classification if available, else LLM risk_level
                lvl = (f.get("security_classification") or f.get("risk_level", "INFO")).upper()
                val = risk_map.get(lvl, 1)
                if val > max_val:
                    max_val = val
                    max_risk = lvl

            report_files = self.reports_generator.compile_report(
                title=f"Security Assessment: {plan.title}",
                summary=f"Automated orchestration task for goal: '{goal}'. Plan execution status: {plan.status.value}.",
                findings=findings,
                risk_level=max_risk
            )

            plan.summary_report = report_files.get("html", "")
            memory_store.log_task(plan.task_id, plan.title, plan.status.value, plan.model_dump())

        # 5. Formulate final response back to user (with expert validation summary)
        final_response_text = f"Task '{plan.title}' completed with status: **{plan.status.value}**.\n\n"

        if findings:
            final_response_text += "## Expert Security Validations\n\n"
            for i, f in enumerate(findings, 1):
                val = f.get("security_validation", {})
                final_response_text += (
                    f"### {i}. {f.get('title', 'Finding')}\n"
                    f"- **Expert Confidence:** {val.get('confidence_score', 0):.2f} "
                    f"({val.get('confidence_level', 'N/A')})\n"
                    f"- **Classification:** {f.get('security_classification', f.get('risk_level', 'INFO'))}\n"
                    f"- **CVE References:** {[c.get('cve_id') for c in val.get('cve_references', [])]}\n"
                    f"- **MITRE ATT&CK:** {[t.get('mitre_id') for t in val.get('mitre_techniques', [])]}\n"
                    f"- **OWASP:** {[o.get('category') for o in val.get('owasp_failures', [])]}\n"
                )
                recs = val.get("expert_recommendations", [])
                if recs:
                    final_response_text += "- **Expert Recommendations:**\n"
                    for r in recs:
                        final_response_text += f"  - {r}\n"
                final_response_text += "\n"

        if report_files:
            final_response_text += f"Report compiled in multiple formats:\n"
            final_response_text += f"- **HTML Report:** [Open File](file:///{report_files['html'].replace(os.sep, '/')})\n"
            final_response_text += f"- **Markdown Report:** [Open File](file:///{report_files['md'].replace(os.sep, '/')})\n"
            final_response_text += f"- **JSON Report:** [Open File](file:///{report_files['json'].replace(os.sep, '/')})\n"
        else:
            final_response_text += "No security findings or vulnerability reports were generated."

        memory_store.add_message(session_id, "assistant", final_response_text)

        return {
            "task_id": plan.task_id,
            "status": plan.status.value,
            "reports": report_files,
            "response": final_response_text
        }

    def _analyze_tool_output(self, step_title: str, output: str) -> Dict[str, Any]:
        """Ask LLM to summarize output and determine if there are security findings."""
        prompt = f"""
You are the Security Analyst for Midnight Core.
Analyze the following tool output from step: "{step_title}".
Determine if it reveals any security vulnerability, misconfiguration, open service, or structural risk.

Output:
\"\"\"
{output[:3000]}
\"\"\"

Produce a raw JSON output matching this structure (no markdown wrapper tags, no extra text):
{{
  "is_vulnerability": true/false,
  "title": "Short descriptive name of finding",
  "risk_level": "CRITICAL/HIGH/MEDIUM/LOW/INFO",
  "component": "Software component, port, or package affected",
  "cwe": "CWE-XXX classification",
  "description": "Short explanation of the issue and why it presents a risk",
  "evidence": "Snippet of output proving finding",
  "remediation": "How to resolve this security risk"
}}
JSON Analysis:
"""
        messages = [
            {"role": "system", "content": "You are a precise JSON security analyzer. Output only JSON."},
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

            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to analyze tool output for findings: {e}")
            return {"is_vulnerability": False}
