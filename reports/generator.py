import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from config.settings import settings
from memory.db import SQLiteMemoryBackend
from core_logging.logger import logger

class ReportGenerator:
    """Compiles vulnerabilities and audit findings into Markdown, HTML, and JSON reports."""
    def __init__(self, db_backend: Optional[SQLiteMemoryBackend] = None):
        self.db = db_backend or SQLiteMemoryBackend()
        self.reports_dir = os.path.join(settings.storage.base_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def _generate_html(self, title: str, summary: str, findings: List[Dict[str, Any]], risk: str, date_str: str) -> str:
        """HTML Template rendering for premium dashboard look."""
        finding_rows = []
        for f in findings:
            finding_rows.append(f"""
            <div class="finding card {f.get('risk_level', 'info').lower()}">
                <div class="finding-header">
                    <span class="badge {f.get('risk_level', 'info').lower()}">{f.get('risk_level', 'INFO')}</span>
                    <h3>{f.get('title', 'Untitled Finding')}</h3>
                </div>
                <div class="finding-body">
                    <p><strong>Affected Component:</strong> <code>{f.get('component', 'General')}</code></p>
                    <p><strong>CWE Mapping:</strong> {f.get('cwe', 'N/A')}</p>
                    <p><strong>Description:</strong> {f.get('description', '')}</p>
                    <pre><code>{f.get('evidence', '')}</code></pre>
                    <div class="remediation">
                        <h4>Remediation Recommendations:</h4>
                        <p>{f.get('remediation', '')}</p>
                    </div>
                </div>
            </div>
            """)
            
        findings_html = "\n".join(finding_rows)
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                :root {{
                    --bg-dark: #09090b;
                    --bg-card: #18181b;
                    --border: #27272a;
                    --text: #fafafa;
                    --text-muted: #a1a1aa;
                    --accent-red: #ef4444;
                    --accent-yellow: #f59e0b;
                    --accent-blue: #3b82f6;
                    --accent-green: #10b981;
                }}
                body {{
                    font-family: 'Inter', system-ui, sans-serif;
                    background-color: var(--bg-dark);
                    color: var(--text);
                    margin: 0;
                    padding: 40px 20px;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                }}
                header {{
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                h1 {{ font-size: 2.5rem; margin: 0 0 10px 0; color: var(--text); }}
                .meta {{ color: var(--text-muted); font-size: 0.9rem; }}
                .risk-indicator {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-top: 15px;
                }}
                .risk-indicator.critical {{ background-color: var(--accent-red); color: white; }}
                .risk-indicator.high {{ background-color: var(--accent-red); color: white; }}
                .risk-indicator.medium {{ background-color: var(--accent-yellow); color: black; }}
                .risk-indicator.low {{ background-color: var(--accent-blue); color: white; }}
                .risk-indicator.info {{ background-color: var(--accent-green); color: white; }}
                
                .summary {{
                    background-color: var(--bg-card);
                    border: 1px solid var(--border);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background-color: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    transition: transform 0.2s;
                }}
                .finding.critical {{ border-left: 6px solid var(--accent-red); }}
                .finding.high {{ border-left: 6px solid var(--accent-red); }}
                .finding.medium {{ border-left: 6px solid var(--accent-yellow); }}
                .finding.low {{ border-left: 6px solid var(--accent-blue); }}
                .finding.info {{ border-left: 6px solid var(--accent-green); }}
                
                .badge {{
                    font-size: 0.75rem;
                    text-transform: uppercase;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                .badge.critical, .badge.high {{ background-color: var(--accent-red); color: white; }}
                .badge.medium {{ background-color: var(--accent-yellow); color: black; }}
                .badge.low {{ background-color: var(--accent-blue); color: white; }}
                .badge.info {{ background-color: var(--accent-green); color: white; }}
                
                .finding-header {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    margin-bottom: 15px;
                }}
                .finding-header h3 {{ margin: 0; font-size: 1.4rem; }}
                pre {{
                    background-color: #000;
                    padding: 15px;
                    border-radius: 4px;
                    overflow-x: auto;
                    border: 1px solid var(--border);
                }}
                code {{ font-family: 'Courier New', Courier, monospace; }}
                .remediation {{
                    background-color: rgba(16, 185, 129, 0.1);
                    border: 1px solid var(--accent-green);
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 15px;
                }}
                .remediation h4 {{ margin: 0 0 10px 0; color: var(--accent-green); }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>{title}</h1>
                    <div class="meta">Generated on: {date_str} | Platform: Midnight Core</div>
                    <div class="risk-indicator {risk.lower()}">Overall Risk Level: {risk}</div>
                </header>
                
                <section class="summary">
                    <h2>Executive Summary</h2>
                    <p>{summary}</p>
                </section>
                
                <section class="findings">
                    <h2>Vulnerability & Finding Details</h2>
                    {findings_html}
                </section>
            </div>
        </body>
        </html>
        """

    def compile_report(self, title: str, summary: str, findings: List[Dict[str, Any]], risk_level: str) -> Dict[str, str]:
        """Compile reports into MD, HTML, and JSON formats, then save records in DB."""
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip().replace(" ", "_").lower()
        
        filename_prefix = f"report_{timestamp}_{safe_title}"
        
        # 1. JSON Report
        json_data = {
            "title": title,
            "timestamp": date_str,
            "overall_risk": risk_level,
            "summary": summary,
            "findings": findings
        }
        json_path = os.path.join(self.reports_dir, f"{filename_prefix}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
            
        # 2. Markdown Report
        md_content = [
            f"# {title}",
            f"**Date:** {date_str} | **Orchestrator:** Midnight Core",
            f"**Overall Risk Rating:** `{risk_level}`",
            "\n## Executive Summary",
            summary,
            "\n## Technical Findings & Vulnerabilities"
        ]
        
        for idx, f in enumerate(findings):
            md_content.append(f"""
### {idx+1}. {f.get('title', 'Untitled Finding')}
- **Risk Level:** `{f.get('risk_level', 'INFO')}`
- **Affected Component:** `{f.get('component', 'General')}`
- **CWE Mapping:** {f.get('cwe', 'N/A')}

#### Description
{f.get('description', '')}

#### Evidence
```
{f.get('evidence', '')}
```

#### Remediation
{f.get('remediation', '')}

---""")
            
        md_path = os.path.join(self.reports_dir, f"{filename_prefix}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))
            
        # 3. HTML Report
        html_content = self._generate_html(title, summary, findings, risk_level, date_str)
        html_path = os.path.join(self.reports_dir, f"{filename_prefix}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Save record in Database
        self.db.save_report(title, html_path, risk_level)
        logger.info(f"Report compiled successfully in multiple formats. Primary path: {html_path}")
        
        return {
            "json": json_path,
            "md": md_path,
            "html": html_path
        }
