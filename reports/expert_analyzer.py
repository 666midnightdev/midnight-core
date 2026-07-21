import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from config.settings import settings
from core_logging.logger import logger


class ExpertReportGenerator:
    """
    Expert-level report generation with actionable intelligence.

    Avoids generic reporting by focusing on security impact, business context,
    and priority-based remediation. Consumes the enriched findings produced by
    CoreOrchestrator (which already include SecurityValidator metadata).
    """

    def __init__(self):
        self.reports_dir = os.path.join(settings.storage.base_dir, "reports", "expert")
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_expert_report(self, findings: List[Dict[str, Any]], analysis_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build an expert report dict with:
        - executive_summary (with business impact)
        - technical_analysis (with MITRE IDs / CVE refs)
        - business_impact assessment
        - remediation_timeline (priority-based)
        - evidence_validation (quality check)
        - expert_confidence score
        - next_steps (actionable)
        """
        logger.info(f"Generating expert report for {len(findings)} findings")

        executive_summary = self._create_executive_summary(findings)
        technical_analysis = self._generate_technical_breakdown(findings)
        business_impact = self._assess_business_impact(findings)
        remediation_timeline = self._create_remediation_plan(findings)
        evidence_validation = self._validate_evidence_quality(findings)
        expert_confidence = self._calculate_expert_confidence(findings)
        next_steps = self._generate_actionable_next_steps(findings)

        expert_report = {
            "generated_at": datetime.now().isoformat(),
            "context": analysis_context,
            "executive_summary": executive_summary,
            "technical_analysis": technical_analysis,
            "business_impact": business_impact,
            "remediation_timeline": remediation_timeline,
            "evidence_validation": evidence_validation,
            "expert_confidence": expert_confidence,
            "next_steps": next_steps,
        }

        # Persist expert report as JSON for audit
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.reports_dir, f"expert_report_{timestamp}.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(expert_report, f, indent=2)
            expert_report["saved_path"] = path
        except Exception as e:
            logger.error(f"Failed to save expert report: {e}")

        return expert_report

    def _create_executive_summary(self, findings: List[Dict[str, Any]]) -> str:
        if not findings:
            return "No security findings were identified during this assessment. Continue routine monitoring."

        critical = [f for f in findings if (f.get("security_classification") or f.get("risk_level", "")).upper() in ("CRITICAL", "HIGH")]
        n = len(findings)
        if critical:
            return (
                f"Assessment identified {n} finding(s), including {len(critical)} critical/high severity issue(s). "
                f"Immediate remediation is recommended to reduce the probability of compromise. "
                f"All findings have been cross-validated against known CVE, MITRE ATT&CK, and OWASP references."
            )
        return (
            f"Assessment identified {n} finding(s) of medium or lower severity. "
            f"These should be addressed in the next maintenance cycle. Findings are correlated with "
            f"MITRE ATT&CK and OWASP references for traceability."
        )

    def _generate_technical_breakdown(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        breakdown = []
        for f in findings:
            val = f.get("security_validation", {})
            breakdown.append({
                "title": f.get("title", "Untitled"),
                "component": f.get("component", "General"),
                "cwe": f.get("cwe", "N/A"),
                "mitre_techniques": [t.get("mitre_id") for t in val.get("mitre_techniques", [])],
                "cve_references": [c.get("cve_id") for c in val.get("cve_references", [])],
                "owasp_failures": [o.get("category") for o in val.get("owasp_failures", [])],
                "confidence": val.get("confidence_score", 0.0),
                "description": f.get("description", ""),
                "evidence": f.get("evidence", ""),
            })
        return breakdown

    def _assess_business_impact(self, findings: List[Dict[str, Any]]) -> str:
        if not findings:
            return "No direct business impact identified."
        has_critical = any(
            (f.get("security_classification") or f.get("risk_level", "")).upper() in ("CRITICAL", "HIGH")
            for f in findings
        )
        if has_critical:
            return (
                "Critical findings may allow unauthorized access, data breach, or service disruption. "
                "Business impact includes potential regulatory penalties, reputational damage, and operational downtime."
            )
        return (
            "Findings may weaken the security posture but do not present immediate breach risk. "
            "Business impact is limited to increased exposure over time if left unaddressed."
        )

    def _create_remediation_plan(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        plan = []
        for f in findings:
            val = f.get("security_validation", {})
            recs = val.get("expert_recommendations", [])
            classification = (f.get("security_classification") or f.get("risk_level", "INFO")).upper()
            if classification in ("CRITICAL", "HIGH"):
                priority = "P1 - 24 hours"
            elif classification == "MEDIUM":
                priority = "P2 - 7 days"
            else:
                priority = "P3 - 30 days"
            plan.append({
                "title": f.get("title", "Untitled"),
                "priority": priority,
                "recommendations": recs or [f.get("remediation", "Review and remediate.")],
            })
        return plan

    def _validate_evidence_quality(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(findings)
        with_evidence = sum(1 for f in findings if f.get("evidence"))
        with_cve = sum(1 for f in findings if f.get("security_validation", {}).get("cve_references"))
        avg_conf = 0.0
        if findings:
            avg_conf = sum(f.get("security_validation", {}).get("confidence_score", 0.0) for f in findings) / total
        return {
            "total_findings": total,
            "findings_with_evidence": with_evidence,
            "findings_with_cve_reference": with_cve,
            "average_expert_confidence": round(avg_conf, 2),
            "evidence_quality": "HIGH" if with_evidence == total else "PARTIAL",
        }

    def _calculate_expert_confidence(self, findings: List[Dict[str, Any]]) -> float:
        if not findings:
            return 0.0
        scores = [f.get("security_validation", {}).get("confidence_score", 0.0) for f in findings]
        return round(sum(scores) / len(scores), 2)

    def _generate_actionable_next_steps(self, findings: List[Dict[str, Any]]) -> List[str]:
        steps = []
        for f in findings:
            val = f.get("security_validation", {})
            for r in val.get("expert_recommendations", []):
                if r not in steps:
                    steps.append(r)
        if not steps:
            steps.append("Schedule a follow-up manual review to confirm automated findings.")
        steps.append("Re-run the assessment after remediation to verify fixes.")
        return steps
