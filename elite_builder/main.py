#!/usr/bin/env python3
"""
Main entry point for Elite Software Builder
Can run as MCP server or standalone
"""

import asyncio
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elite_builder.mcp_server import EliteBuilderMCPServer, main as mcp_main
from elite_builder.orchestrator import Orchestrator
from elite_builder.config_manager import ConfigManager

async def run_standalone(project_spec: str, goal: str, max_iterations: int = 50):
    """Run the builder in standalone mode"""
    print("=" * 60)
    print("ELITE SOFTWARE BUILDER")
    print("=" * 60)
    print()
    
    # Check for required credentials
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print("Configuration:")
    print(f"  Project Name: {config.get('project_name', 'elite-built-app')}")
    print(f"  Database: {config.get('database_type', 'Not configured')}")
    print(f"  API Keys: {len([k for k, v in config.get('api_keys', {}).items() if v])} configured")
    print()
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        project_spec=project_spec,
        goal=goal,
        max_iterations=max_iterations
    )
    
    # Run the build loop
    await orchestrator.run()
    
    # Print final status
    final_status = orchestrator.get_status()
    print()
    print("=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)
    print(f"Goal Met: {final_status['goal_met']}")
    print(f"Final Score: {final_status['latest_score']:.1f}/100")
    print(f"Total Iterations: {final_status['current_iteration']}")
    print(f"Project Path: {orchestrator.current_project_path}")
    print()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Elite Software Builder")
    parser.add_argument(
        "--mode",
        choices=["mcp", "standalone"],
        default="mcp",
        help="Run mode: mcp (MCP server) or standalone"
    )
    parser.add_argument(
        "--project-spec",
        type=str,
        help="Project specification (for standalone mode)"
    )
    parser.add_argument(
        "--goal",
        type=str,
        help="Goal to achieve (for standalone mode)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=50,
        help="Maximum iterations (default: 50)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "mcp":
        # Run as MCP server
        print("Starting Elite Software Builder MCP Server...")
        asyncio.run(mcp_main())
    elif args.mode == "standalone":
        # Run in standalone mode
        if not args.project_spec or not args.goal:
            print("Error: --project-spec and --goal are required for standalone mode")
            sys.exit(1)
        
        asyncio.run(run_standalone(
            project_spec=args.project_spec,
            goal=args.goal,
            max_iterations=args.max_iterations
        ))
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
