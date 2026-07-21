import argparse
import sys
import unittest
from core.orchestrator import CoreOrchestrator
from mcp.server import MCPServer
from rag.indexer import rag_indexer
from executor.wsl import WSLExecutor
from executor.permissions import permission_controller
from core_logging.logger import logger

def cli_approval_callback(details: str) -> bool:
    """Interactively prompts console user to approve commands."""
    print(f"\n[SECURITY AUDIT REQUIRED]")
    print(f"Details: {details}")
    try:
        ans = input("Allow execution? (y/N): ").strip().lower()
        return ans in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        return False

def run_tests():
    """Runs the full unittest suite."""
    print("\nRunning Midnight Core Unit Tests...\n")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Midnight Core: Modular AI Orchestration Operating Platform",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # 1. Run Goal
    run_parser = subparsers.add_parser("run", help="Submit a reasoning goal to the Core Orchestrator")
    run_parser.add_argument("goal", type=str, help="The high level DevSecOps or coding goal")
    run_parser.add_argument("--session", type=str, default="cli_default", help="Memory session ID context")
    run_parser.add_argument("--auto-approve", action="store_true", help="Auto approve safe local commands")
    
    # 2. Dashboard
    subparsers.add_parser("dashboard", help="Start the FastAPI Admin Dashboard Panel")
    
    # 3. MCP Server
    subparsers.add_parser("mcp", help="Launch the stdio-based MCP Server")
    
    # 4. RAG Indexer
    index_parser = subparsers.add_parser("index", help="Index a file or directory for semantic retrieval")
    index_parser.add_argument("path", type=str, help="File path to index")
    
    # 5. WSL Telemetry
    subparsers.add_parser("wsl-distros", help="List detected WSL distributions")
    
    # 6. Test suite
    subparsers.add_parser("test", help="Execute the platform unit test suite")

    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Configure Approval callbacks
    if args.command == "run":
        if args.auto_approve:
            # Auto-approve: user explicitly allowed safe/declared operations
            permission_controller.register_approval_callback(lambda d: True)
        else:
            permission_controller.register_approval_callback(cli_approval_callback)
            
        print(f"Initializing Orchestrator for session: {args.session}...")
        orchestrator = CoreOrchestrator()
        result = orchestrator.run_task(args.session, args.goal)
        print("\n=== EXECUTION RESULT ===")
        print(result["response"])
        
    elif args.command == "dashboard":
        # Lazy import to avoid side-effect overwrite of approval callback
        from dashboard.server import start_dashboard
        start_dashboard()
        
    elif args.command == "mcp":
        # Launch MCP stdio server
        server = MCPServer()
        server.run()
        
    elif args.command == "index":
        print(f"Indexing path for RAG: {args.path}")
        success = rag_indexer.index_file(args.path)
        if success:
            print("Successfully indexed document chunk mappings in local Vector SQLite storage.")
        else:
            print("Failed to index file. Check audit logs.")
            
    elif args.command == "wsl-distros":
        distros = WSLExecutor.detect_distributions()
        if distros:
            print("\nDetected WSL Distributions:")
            for d in distros:
                default_indicator = " [DEFAULT]" if d["is_default"] else ""
                print(f"- {d['name']} (State: {d['state']}, Version: {d['version']}){default_indicator}")
        else:
            print("No WSL distributions detected.")
            
    elif args.command == "test":
        run_tests()

if __name__ == "__main__":
    main()
