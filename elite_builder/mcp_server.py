#!/usr/bin/env python3
"""
MCP Server for Elite Software Builder
Provides MCP interface for the builder system
"""

import asyncio
import json
import os
import sys
from typing import Any, Optional, Dict, List
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elite_builder.builder_agent import BuilderAgent
from elite_builder.reviewer_agent import ReviewerAgent
from elite_builder.orchestrator import Orchestrator
from elite_builder.github_integration import GitHubExporter

# MCP-compatible types (simplified implementation)
class Resource:
    def __init__(self, uri: str, name: str, description: str, mimeType: str = "application/json"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mimeType = mimeType

class Tool:
    def __init__(self, name: str, description: str, inputSchema: Dict):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema

class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text

class EliteBuilderMCPServer:
    def __init__(self):
        self.orchestrator = None
        self.server_name = "elite-software-builder"
    
    async def list_resources(self) -> List[Resource]:
        """List available resources"""
        return [
            Resource(
                uri="elite-builder://status",
                name="Builder Status",
                description="Current status of the Elite Software Builder",
                mimeType="application/json"
            ),
            Resource(
                uri="elite-builder://config",
                name="Builder Configuration",
                description="Current configuration of the builder",
                mimeType="application/json"
            )
        ]
    
    async def get_resource(self, uri: str) -> str:
        """Get resource content"""
        if uri == "elite-builder://status":
            status = {
                "status": "ready" if self.orchestrator is None else "running",
                "iteration": self.orchestrator.current_iteration if self.orchestrator else 0
            }
            return json.dumps(status, indent=2)
        elif uri == "elite-builder://config":
            # Return config if exists
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return f.read()
            return json.dumps({"message": "No configuration found"}, indent=2)
        return ""
    
    async def list_tools(self) -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="start_build",
                description="Start the Elite Software Builder with a project specification",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_spec": {
                            "type": "string",
                            "description": "Detailed specification of the website/SaaS to build"
                        },
                        "goal": {
                            "type": "string",
                            "description": "The exact goal to achieve (e.g., 'Fully functional e-commerce site with payment integration')"
                        },
                        "max_iterations": {
                            "type": "integer",
                            "description": "Maximum number of improvement iterations (default: 50)",
                            "default": 50
                        }
                    },
                    "required": ["project_spec", "goal"]
                }
            ),
            Tool(
                name="get_build_status",
                description="Get current status of the build process",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="stop_build",
                description="Stop the current build process",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="export_to_github",
                description="Export the built project to GitHub",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "GitHub repository name"
                        },
                        "github_token": {
                            "type": "string",
                            "description": "GitHub personal access token"
                        },
                        "organization": {
                            "type": "string",
                            "description": "GitHub organization (optional)"
                        }
                    },
                    "required": ["repo_name", "github_token"]
                }
            ),
            Tool(
                name="request_credentials",
                description="Request API keys and credentials needed for the project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "required_services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of services that need credentials (e.g., ['database', 'stripe', 'openai'])"
                        }
                    },
                    "required": ["required_services"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls"""
        try:
            if name == "start_build":
                project_spec = arguments.get("project_spec")
                goal = arguments.get("goal")
                max_iterations = arguments.get("max_iterations", 50)
                
                if not project_spec or not goal:
                    return [TextContent(
                        type="text",
                        text="Error: project_spec and goal are required"
                    )]
                
                # Initialize orchestrator
                self.orchestrator = Orchestrator(
                    project_spec=project_spec,
                    goal=goal,
                    max_iterations=max_iterations
                )
                
                # Start build in background
                asyncio.create_task(self.orchestrator.run())
                
                return [TextContent(
                    type="text",
                    text=f"Build started! Goal: {goal}\nMaximum iterations: {max_iterations}\nThe builder and reviewer will now loop until the goal is achieved."
                )]
            
            elif name == "get_build_status":
                if not self.orchestrator:
                    return [TextContent(
                        type="text",
                        text="No build in progress"
                    )]
                
                status = self.orchestrator.get_status()
                return [TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )]
            
            elif name == "stop_build":
                if self.orchestrator:
                    self.orchestrator.stop()
                    return [TextContent(
                        type="text",
                        text="Build stopped"
                    )]
                return [TextContent(
                    type="text",
                    text="No build in progress"
                )]
            
            elif name == "export_to_github":
                repo_name = arguments.get("repo_name")
                github_token = arguments.get("github_token")
                organization = arguments.get("organization")
                
                if not repo_name or not github_token:
                    return [TextContent(
                        type="text",
                        text="Error: repo_name and github_token are required"
                    )]
                
                exporter = GitHubExporter(github_token)
                result = await exporter.export_project(
                    repo_name=repo_name,
                    organization=organization,
                    project_path=os.path.join(os.path.dirname(__file__), "..", "projects", "current")
                )
                
                return [TextContent(
                    type="text",
                    text=result
                )]
            
            elif name == "request_credentials":
                required_services = arguments.get("required_services", [])
                # This would typically prompt the user, but for MCP we return a structured request
                request = {
                    "message": "The builder requires the following credentials:",
                    "services": required_services,
                    "instructions": "Please provide these credentials using the configuration system"
                }
                return [TextContent(
                    type="text",
                    text=json.dumps(request, indent=2)
                )]
            
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
        
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

async def main():
    """Main entry point for MCP server - runs as stdio server"""
    server = EliteBuilderMCPServer()
    
    # Simple stdio-based MCP server
    # This reads JSON-RPC messages from stdin and writes to stdout
    import sys
    
    print("Elite Software Builder MCP Server", file=sys.stderr)
    print("Listening for MCP requests on stdin/stdout", file=sys.stderr)
    
    # For a full implementation, you would use an MCP library
    # For now, we'll provide a simple interface
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                method = request.get("method")
                params = request.get("params", {})
                
                if method == "tools/list":
                    tools = await server.list_tools()
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "tools": [
                                {
                                    "name": t.name,
                                    "description": t.description,
                                    "inputSchema": t.inputSchema
                                }
                                for t in tools
                            ]
                        }
                    }
                    print(json.dumps(response))
                    sys.stdout.flush()
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    results = await server.call_tool(tool_name, arguments)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {"type": r.type, "text": r.text}
                                for r in results
                            ]
                        }
                    }
                    print(json.dumps(response))
                    sys.stdout.flush()
                
                elif method == "resources/list":
                    resources = await server.list_resources()
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "resources": [
                                {
                                    "uri": r.uri,
                                    "name": r.name,
                                    "description": r.description,
                                    "mimeType": r.mimeType
                                }
                                for r in resources
                            ]
                        }
                    }
                    print(json.dumps(response))
                    sys.stdout.flush()
                
                elif method == "resources/read":
                    uri = params.get("uri")
                    content = await server.get_resource(uri)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "contents": [
                                {
                                    "uri": uri,
                                    "mimeType": "application/json",
                                    "text": content
                                }
                            ]
                        }
                    }
                    print(json.dumps(response))
                    sys.stdout.flush()
            
            except json.JSONDecodeError:
                pass
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
