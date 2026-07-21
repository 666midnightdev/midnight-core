#!/usr/bin/env python3
"""
Midnight Core CLI Interface - Easy access to security assessment features

Commands:
  /help            Show this help
  /features        List all available security features
  /run [goal]      Start expert security assessment
  /dashboard       Launch admin dashboard
  /mcp             Start MCP server
  /index [path]    Index file for RAG
  /wsl-distros     Detect WSL distributions
  /test            Run unit tests
  /exit            Exit Midnight Core

Usage Examples:
  /run "Lakukan port scan eksaustif pada 192.168.1.0/24"
  /run "Periksa kerentanan web aplikasi target"
  /index ./target-app/
  /wsl-distros
"""

import sys
import os
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import main as run_main
from run import run_tests

class MidnightCLI:
    def __init__(self):
        self.feature_descriptions = {
            "run": "Start expert security assessment with AI reasoning and tool execution",
            "dashboard": "Launch FastAPI admin dashboard panel",
            "mcp": "Start stdio-based Model Context Protocol server",
            "index": "Index local files for semantic retrieval and RAG",
            "wsl-distros": "Detect and list available WSL distributions",
            "test": "Execute the complete unit test suite"
        }
    
    def show_help(self):
        """Display help information"""
        print("=" * 70)
        print("MIDNIGHT CORE SECURITY - Command Line Interface")
        print("=" * 70)
        print("\nAvailable Commands:")
        print("-" * 70)
        
        for cmd, desc in self.feature_descriptions.items():
            print(f"  /{cmd:<15} - {desc}")
        print(f"  {'/recipe':<15} - Tampilkan resep perintah tools siap copy-paste + penjelasan")
        
        print("\nExamples:")
        print("-" * 70)
        print("  /run \"Periksa kerentanan aplikasi web target\"")
        print("  /run \"Lakukan otomasi pengerjan sistem penargetan\"")
        print("  /index /path/to/app/      # Index untuk RAG")
        print("  /wsl-distros              # Deteksi WSL")
        print("")
        print("Type '/help' anytime untuk menampilkan bantuan ini")
        print("=" * 70)
    
    def show_features(self):
        """Show detailed information about all features"""
        print("=" * 70)
        print("MIDNIGHT CORE - Security Feature Overview")
        print("=" * 70)
        print("\n🖥️  CORE SECURITY OPERATIONS")
        print("-" * 70)
        print("\n📊 SECURITY ASSESSMENT (/run)")
        print("   • Intelligent security assessment planning")
        print("   • Automated tool execution (nmap, nikto, etc.)")
        print("   • MITRE ATT&CK correlation")
        print("   • CWE classification")
        print("   • Expert report generation")
        print("   • Risk scoring & remediation recommendations")
        
        print("\n🔍 MONITORING & MANAGEMENT")
        print("-" * 70)
        print("\n📈 DASHBOARD (/dashboard)")
        print("   • Real-time security metrics")
        print("   • Task progress monitoring")
        print("   • Risk assessment overview")
        print("   • Vulnerability trends")
        
        print("\n🔌 MCP SERVER (/mcp)")
        print("   • Model Context Protocol server")
        print("   • Extensible security workflows")
        print("   • Integration with external systems")
        
        print("\n📚 KNOWLEDGE MANAGEMENT")
        print("-" * 70)
        print("\n🔎 RAG INDEXING (/index)")
        print("   • File and directory indexing")
        print("   • Semantic search")
        print("   • Knowledge base building")
        print("   • Context retrieval for assessments")
        
        print("\n🖥️  WSL & INFRASTRUCTURE")
        print("-" * 70)
        print("\n🐧 WSL DISTRIBUTIONS (/wsl-distros)")
        print("   • Detect WSL Linux distributions")
        print("   • Identify default Kali Linux WSL")
        print("   • Check distribution status")
        
        print("\n🧪 TESTING & VALIDATION")
        print("-" * 70)
        print("\n🧪 UNIT TESTS (/test)")
        print("   • Complete test suite execution")
        print("   • Component validation")
        print("   • Integration testing")
        print("   • Security feature verification")
        
        print("\n🔧 TECHNICAL DETAILS")
        print("-" * 70)
        print("   • Model: Midnight-Agent (Mistral NeMo 12B)")
        print("   • Runtime: Ollama Local API")
        print("   • Executor: Kali Linux WSL (Default)")
        print("   • Storage: SQLite + Vector Database")
        print("   • Reporting: HTML, Markdown, JSON")
        
        print("\n" + "=" * 70)
    
    def show_recipe(self, args):
        """Show copy-paste ready tool recipes (Bahasa Indonesia)."""
        from recipes import render_recipe, RECIPES
        parts = args.split(maxsplit=1) if args else []
        profile = parts[0].lower() if parts else ""
        target = parts[1] if len(parts) > 1 else ""
        if not profile:
            print("\n📋 RESEP KEGIATAN KEAMANAN")
            print("   Profil tersedia:")
            for k, v in RECIPES.items():
                print(f"   • {k:<10} - {v['label']}")
            print(f"   • {'subdomain':<10} - Subdomain/vhost enumeration (cepat, tanpa amass)")
            print(f"   • {'prod':<10} - Production-safe audit (domain deployed milikmu)")
            print("\n   Usage: /recipe <profil> [target]")
            print("   Contoh: /recipe web http://192.168.1.10")
            print("           /recipe stealth scanme.nmap.org")
            print("           /recipe full")
            return
        print(render_recipe(profile, target))

    def run_security_assessment(self, goal):
        """Run security assessment with expert validation"""
        print(f"\n🔍 STARTING EXPERT SECURITY ASSESSMENT")
        print(f"   Goal: {goal}")
        print("=" * 70)
        
        # Build command line arguments
        import argparse
        parser = argparse.ArgumentParser(
            description="Midnight Core: Modular AI Orchestration Operating Platform",
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        run_parser = subparsers.add_parser("run", help="Submit a reasoning goal to the Core Orchestrator")
        run_parser.add_argument("goal", type=str, help="The high level DevSecOps or coding goal")
        run_parser.add_argument("--session", type=str, default="cli_default", help="Memory session ID context")
        run_parser.add_argument("--auto-approve", action="store_true", help="Auto approve safe local commands")
        
        args = parser.parse_args(["run", goal, "--session", "cli_default"])
        
        # Execute the assessment
        if args.command == "run":
            from run import main as run_cli_main
            run_cli_main(["run", args.goal, "--session", args.session, "--auto-approve"])
    
    def launch_dashboard(self):
        """Launch admin dashboard"""
        print("\n📊 LAUNCHING ADMIN DASHBOARD")
        print("   Opening FastAPI dashboard at http://localhost:8000")
        print("   Default credentials: admin / midnight_secure")
        print("=" * 70)
        
        # Build and execute the dashboard command
        import subprocess
        import sys
        
        try:
            # Run the dashboard
            from dashboard.server import start_dashboard
            start_dashboard()
        except Exception as e:
            print(f"\n❌ Error launching dashboard: {e}")
            print("   Make sure all dependencies are installed")
            print("   Run: pip install -r requirements.txt")
    
    def launch_mcp_server(self):
        """Start MCP server"""
        print("\n🔌 STARTING MCP SERVER")
        print("   MCP server started, listening on stdin...")
        print("=" * 70)
        
        from mcp.server import MCPServer
        server = MCPServer()
        server.run()
    
    def index_for_rag(self, path):
        """Index file for RAG"""
        print(f"\n📚 INDEXING FOR RAG: {path}")
        print("=" * 70)
        
        import argparse
        parser = argparse.ArgumentParser(description="Index for RAG")
        parser.add_argument("path", type=str, help="File path to index")
        
        args = parser.parse_args([path])
        
        try:
            from run import main as run_cli_main
            run_cli_main(["index", args.path])
        except Exception as e:
            print(f"\n❌ Error indexing file: {e}")
    
    def show_wsl_distros(self):
        """Show WSL distributions"""
        print("\n🐧 DETECTING WSL DISTRIBUTIONS")
        print("=" * 70)
        
        try:
            from executor.wsl import WSLExecutor
            distros = WSLExecutor.detect_distributions()
            
            if distros:
                print("\nDetected WSL Distributions:")
                for d in distros:
                    default_indicator = " [DEFAULT]" if d["is_default"] else ""
                    print(f"   • {d['name']} (State: {d['state']}, Version: {d['version']}){default_indicator}")
            else:
                print("\n❌ No WSL distributions detected")
                print("   Make sure WSL is installed and running")
        except Exception as e:
            print(f"\n❌ Error detecting WSL: {e}")
    
    def run_unit_tests(self):
        """Run unit tests"""
        print("\n🧪 RUNNING UNIT TESTS")
        print("=" * 70)
        
        try:
            run_tests()
        except Exception as e:
            print(f"\n❌ Error running tests: {e}")
            print("   Make sure all test dependencies are installed")
    
    def run_interactive_mode(self):
        """Run interactive CLI mode"""
        print("\n" + "=" * 70)
        print("MIDNIGHT CORE - Interactive Security Mode")
        print("=" * 70)
        print("\nType '/help' for commands")
        print("Type '/exit' or '/quit' to quit")
        print("\nEnter your security command:")
        
        while True:
            try:
                user_input = input("\n🔍 root@midnight:~# ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.lower().split(maxsplit=1)
                cmd = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd == '/help':
                    self.show_help()
                
                elif cmd == '/recipe':
                    self.show_recipe(args)
                
                elif cmd == '/features':
                    self.show_features()
                
                elif cmd == '/run':
                    if args:
                        self.run_security_assessment(args)
                    else:
                        print("\n❌ Error: Goal parameter required")
                        print("   Usage: /run \"your assessment goal here\"")
                
                elif cmd == '/dashboard':
                    self.launch_dashboard()
                
                elif cmd == '/mcp':
                    self.launch_mcp_server()
                
                elif cmd == '/index':
                    if args:
                        self.index_for_rag(args.strip())
                    else:
                        print("\n❌ Error: Path parameter required")
                        print("   Usage: /index /path/to/file/")
                
                elif cmd == '/wsl-distros':
                    self.show_wsl_distros()
                
                elif cmd == '/test':
                    self.run_unit_tests()
                
                elif cmd in ['/exit', '/quit', 'exit', 'quit']:
                    print("\n👋 Exiting Midnight Core. Goodbye!")
                    break
                
                else:
                    print(f"\n❌ Unknown command: '{cmd}'")
                    print("   Type '/help' for available commands")
                
                print("\n" + "=" * 70)
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Type '/help' for available commands")

def main():
    # Check if we're in interactive mode
    if len(sys.argv) == 1:
        # Interactive CLI mode
        cli = MidnightCLI()
        cli.run_interactive_mode()
    else:
        # Command line execution
        cli = MidnightCLI()
        raw = sys.argv[1]
        # support both "run goal" and "/run goal" forms
        if raw.startswith('/'):
            raw = raw[1:]
        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        if len(parts) > 1:
            sys.argv = [sys.argv[0], cmd] + parts[1].split()
        
        if cmd == 'help':
            cli.show_help()
        elif cmd == 'features':
            cli.show_features()
        elif cmd == 'run':
            if len(sys.argv) > 2:
                goal = ' '.join(sys.argv[2:])
                cli.run_security_assessment(goal)
            else:
                print("\n[ERROR] Goal parameter required")
                print("   Usage: python midnight_cli.py run \"your assessment goal here\"")
        elif cmd == 'dashboard':
            cli.launch_dashboard()
        elif cmd == 'mcp':
            cli.launch_mcp_server()
        elif cmd == 'index':
            if len(sys.argv) > 2:
                path = sys.argv[2]
                cli.index_for_rag(path)
            else:
                print("\n[ERROR] Path parameter required")
                print("   Usage: python midnight_cli.py index /path/to/file/")
        elif cmd == 'recipe':
            if len(sys.argv) > 2:
                cli.show_recipe(' '.join(sys.argv[2:]))
            else:
                cli.show_recipe('')
        elif cmd == 'wsl-distros':
            cli.show_wsl_distros()
        elif cmd == 'test':
            cli.run_unit_tests()
        else:
            print(f"\n[ERROR] Unknown command: '{cmd}'")
            print("\nAvailable commands:")
            print("  help, features, run, dashboard, mcp, index, wsl-distros, test")
            print("\nUsage: python midnight_cli.py <command> [args]")
if __name__ == "__main__":
    main()
