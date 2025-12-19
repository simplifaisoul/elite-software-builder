#!/usr/bin/env python3
"""
GitHub Integration - Exports projects to GitHub using MCP or direct API
"""

import os
import json
import subprocess
import base64
from typing import Optional, Dict
from pathlib import Path

try:
    from github import Github
    GITHUB_PY_AVAILABLE = True
except ImportError:
    GITHUB_PY_AVAILABLE = False

class GitHubExporter:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.github = None
        
        if GITHUB_PY_AVAILABLE:
            try:
                self.github = Github(github_token)
            except Exception as e:
                print(f"Warning: Could not initialize GitHub client: {e}")
    
    async def export_project(self, repo_name: str, organization: Optional[str] = None, project_path: str = ".") -> str:
        """Export project to GitHub"""
        try:
            # Method 1: Try using git commands (most reliable)
            result = await self._export_via_git(repo_name, organization, project_path)
            if result["success"]:
                return result["message"]
            
            # Method 2: Try using GitHub API
            if self.github:
                result = await self._export_via_api(repo_name, organization, project_path)
                if result["success"]:
                    return result["message"]
            
            return f"Export failed: {result.get('error', 'Unknown error')}"
        
        except Exception as e:
            return f"Export error: {str(e)}"
    
    async def _export_via_git(self, repo_name: str, organization: Optional[str], project_path: str) -> Dict:
        """Export using git commands"""
        try:
            # Check if git is available
            git_check = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            
            if git_check.returncode != 0:
                return {
                    "success": False,
                    "error": "Git is not installed or not in PATH"
                }
            
            # Initialize git repo if not already
            if not os.path.exists(os.path.join(project_path, ".git")):
                subprocess.run(
                    ["git", "init"],
                    cwd=project_path,
                    capture_output=True
                )
                
                # Create .gitignore if not exists
                gitignore_path = os.path.join(project_path, ".gitignore")
                if not os.path.exists(gitignore_path):
                    gitignore_content = """node_modules/
dist/
build/
.env
.env.local
*.log
.DS_Store
.vscode/
.idea/
"""
                    with open(gitignore_path, 'w') as f:
                        f.write(gitignore_content)
            
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                capture_output=True
            )
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from Elite Software Builder"],
                cwd=project_path,
                capture_output=True
            )
            
            # Create remote URL
            if organization:
                repo_url = f"https://{self.github_token}@github.com/{organization}/{repo_name}.git"
            else:
                # Try to get username from token or use a default
                repo_url = f"https://{self.github_token}@github.com/{repo_name}.git"
            
            # Add remote
            subprocess.run(
                ["git", "remote", "remove", "origin"],
                cwd=project_path,
                capture_output=True
            )
            subprocess.run(
                ["git", "remote", "add", "origin", repo_url],
                cwd=project_path,
                capture_output=True
            )
            
            # Push to GitHub
            # First, try to create repo via API if possible
            if self.github:
                try:
                    if organization:
                        org = self.github.get_organization(organization)
                        org.create_repo(repo_name, private=False)
                    else:
                        user = self.github.get_user()
                        user.create_repo(repo_name, private=False)
                except Exception:
                    pass  # Repo might already exist, continue
            
            # Push
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode != 0:
                # Try master branch
                push_result = subprocess.run(
                    ["git", "push", "-u", "origin", "master"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
            
            if push_result.returncode == 0:
                if organization:
                    repo_url_display = f"https://github.com/{organization}/{repo_name}"
                else:
                    repo_url_display = f"https://github.com/{repo_name}"
                
                return {
                    "success": True,
                    "message": f"Project exported successfully to {repo_url_display}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Git push failed: {push_result.stderr}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _export_via_api(self, repo_name: str, organization: Optional[str], project_path: str) -> Dict:
        """Export using GitHub API (for cases where git is not available)"""
        try:
            # Create repository
            if organization:
                org = self.github.get_organization(organization)
                repo = org.create_repo(repo_name, private=False)
            else:
                user = self.github.get_user()
                repo = user.create_repo(repo_name, private=False)
            
            # Get default branch
            default_branch = repo.default_branch or "main"
            
            # Upload files
            uploaded_files = 0
            for root, dirs, files in os.walk(project_path):
                # Skip .git directory
                if ".git" in root:
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_path)
                    
                    # Skip large files
                    if os.path.getsize(file_path) > 1000000:  # 1MB limit
                        continue
                    
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        
                        # Try to decode as text
                        try:
                            content_str = content.decode('utf-8')
                            repo.create_file(
                                relative_path,
                                f"Add {relative_path}",
                                content_str,
                                branch=default_branch
                            )
                            uploaded_files += 1
                        except UnicodeDecodeError:
                            # Binary file, skip for now
                            pass
                    except Exception as e:
                        print(f"Warning: Could not upload {relative_path}: {e}")
            
            repo_url = repo.html_url
            return {
                "success": True,
                "message": f"Project exported to {repo_url} ({uploaded_files} files uploaded)"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"API export failed: {str(e)}"
            }
