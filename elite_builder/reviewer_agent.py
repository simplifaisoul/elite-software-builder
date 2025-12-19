#!/usr/bin/env python3
"""
Reviewer Agent - Reviews websites and provides feedback for improvement
"""

import os
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path

class ReviewerAgent:
    def __init__(self, project_path: str, goal: str):
        self.project_path = project_path
        self.goal = goal
        self.review_history = []
    
    def review_project(self, iteration: int) -> Dict:
        """Review the entire project and provide feedback"""
        review = {
            "iteration": iteration,
            "timestamp": self._get_timestamp(),
            "checks": {},
            "feedback": [],
            "score": 0,
            "meets_goal": False
        }
        
        # Run various checks
        review["checks"]["structure"] = self._check_project_structure()
        review["checks"]["code_quality"] = self._check_code_quality()
        review["checks"]["functionality"] = self._check_functionality()
        review["checks"]["goal_alignment"] = self._check_goal_alignment()
        review["checks"]["best_practices"] = self._check_best_practices()
        
        # Calculate score
        review["score"] = self._calculate_score(review["checks"])
        
        # Generate feedback
        review["feedback"] = self._generate_feedback(review["checks"])
        
        # Check if goal is met
        review["meets_goal"] = self._evaluate_goal(review)
        
        self.review_history.append(review)
        
        return review
    
    def _check_project_structure(self) -> Dict:
        """Check if project structure is correct"""
        issues = []
        positives = []
        
        required_files = [
            "package.json",
            "vite.config.ts",
            "tsconfig.json",
            "index.html",
            "src/main.tsx",
            "src/App.tsx"
        ]
        
        for file in required_files:
            file_path = os.path.join(self.project_path, file)
            if not os.path.exists(file_path):
                issues.append(f"Missing required file: {file}")
            else:
                positives.append(f"Found: {file}")
        
        # Check for key directories
        required_dirs = ["src/components", "src/sections", "src/utils"]
        for dir_path in required_dirs:
            full_path = os.path.join(self.project_path, dir_path)
            if os.path.exists(full_path):
                positives.append(f"Directory exists: {dir_path}")
            else:
                issues.append(f"Missing directory: {dir_path}")
        
        return {
            "status": "pass" if len(issues) == 0 else "needs_improvement",
            "issues": issues,
            "positives": positives
        }
    
    def _check_code_quality(self) -> Dict:
        """Check code quality"""
        issues = []
        positives = []
        
        # Check if TypeScript files compile
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                positives.append("TypeScript compilation successful")
            else:
                issues.append(f"TypeScript errors: {result.stderr[:200]}")
        
        except Exception as e:
            issues.append(f"Could not check TypeScript: {str(e)}")
        
        # Check for common code quality issues
        src_path = os.path.join(self.project_path, "src")
        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith(('.ts', '.tsx')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                # Check for basic quality indicators
                                if 'export' in content:
                                    positives.append(f"{file} has exports")
                                if 'function' in content or 'const' in content:
                                    positives.append(f"{file} has functions/components")
                                if 'any' in content and 'any' not in ['anywhere', 'company']:
                                    issues.append(f"{file} uses 'any' type (consider using proper types)")
                        except Exception as e:
                            issues.append(f"Could not read {file}: {str(e)}")
        
        return {
            "status": "pass" if len(issues) < 3 else "needs_improvement",
            "issues": issues[:10],  # Limit issues
            "positives": positives[:10]
        }
    
    def _check_functionality(self) -> Dict:
        """Check if basic functionality exists"""
        issues = []
        positives = []
        
        # Check if package.json has scripts
        package_json_path = os.path.join(self.project_path, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_json = json.load(f)
                    scripts = package_json.get("scripts", {})
                    
                    if "dev" in scripts:
                        positives.append("Dev script configured")
                    if "build" in scripts:
                        positives.append("Build script configured")
                    if not scripts:
                        issues.append("No scripts in package.json")
            except Exception as e:
                issues.append(f"Could not read package.json: {str(e)}")
        
        # Check if main components exist
        app_path = os.path.join(self.project_path, "src", "App.tsx")
        if os.path.exists(app_path):
            positives.append("App.tsx exists")
            try:
                with open(app_path, 'r') as f:
                    content = f.read()
                    if 'return' in content and ('<' in content or 'JSX' in content):
                        positives.append("App.tsx has JSX content")
                    else:
                        issues.append("App.tsx appears empty or incomplete")
            except Exception as e:
                issues.append(f"Could not read App.tsx: {str(e)}")
        else:
            issues.append("App.tsx missing")
        
        return {
            "status": "pass" if len(issues) == 0 else "needs_improvement",
            "issues": issues,
            "positives": positives
        }
    
    def _check_goal_alignment(self) -> Dict:
        """Check if project aligns with the goal"""
        issues = []
        positives = []
        goal_lower = self.goal.lower()
        
        # Analyze goal keywords
        goal_keywords = {
            "e-commerce": ["cart", "checkout", "payment", "product", "shop"],
            "dashboard": ["dashboard", "chart", "analytics", "metrics"],
            "authentication": ["login", "auth", "signup", "user"],
            "api": ["api", "fetch", "axios", "service"],
            "database": ["database", "db", "postgres", "mongo"],
            "responsive": ["responsive", "mobile", "tailwind", "css"]
        }
        
        # Check project files for goal-related content
        src_path = os.path.join(self.project_path, "src")
        project_content = ""
        
        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                project_content += f.read().lower()
                        except:
                            pass
        
        # Check for goal-related keywords
        for keyword_type, keywords in goal_keywords.items():
            if keyword_type in goal_lower:
                found_keywords = [kw for kw in keywords if kw in project_content]
                if found_keywords:
                    positives.append(f"Found {keyword_type} related code: {', '.join(found_keywords[:3])}")
                else:
                    issues.append(f"Goal mentions {keyword_type} but no related code found")
        
        # General goal alignment
        if len(positives) > len(issues):
            positives.append("Project shows good goal alignment")
        else:
            issues.append("Project may not fully align with stated goal")
        
        return {
            "status": "pass" if len(positives) > len(issues) else "needs_improvement",
            "issues": issues,
            "positives": positives
        }
    
    def _check_best_practices(self) -> Dict:
        """Check for best practices"""
        issues = []
        positives = []
        
        # Check for environment variables usage
        env_example_path = os.path.join(self.project_path, ".env.example")
        if os.path.exists(env_example_path):
            positives.append(".env.example file exists (good practice)")
        else:
            issues.append("Consider adding .env.example for configuration")
        
        # Check for README
        readme_path = os.path.join(self.project_path, "README.md")
        if os.path.exists(readme_path):
            positives.append("README.md exists")
        else:
            issues.append("Consider adding README.md")
        
        # Check for .gitignore
        gitignore_path = os.path.join(self.project_path, ".gitignore")
        if os.path.exists(gitignore_path):
            positives.append(".gitignore exists")
        else:
            issues.append("Consider adding .gitignore")
        
        # Check for proper TypeScript usage
        src_path = os.path.join(self.project_path, "src")
        if os.path.exists(src_path):
            ts_files = list(Path(src_path).rglob("*.ts"))
            tsx_files = list(Path(src_path).rglob("*.tsx"))
            if len(ts_files) + len(tsx_files) > 0:
                positives.append(f"Using TypeScript ({len(ts_files) + len(tsx_files)} files)")
        
        return {
            "status": "pass" if len(issues) < 3 else "needs_improvement",
            "issues": issues,
            "positives": positives
        }
    
    def _calculate_score(self, checks: Dict) -> float:
        """Calculate overall score (0-100)"""
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks.values() if check.get("status") == "pass")
        
        base_score = (passed_checks / total_checks) * 100
        
        # Adjust based on issues
        total_issues = sum(len(check.get("issues", [])) for check in checks.values())
        issue_penalty = min(total_issues * 2, 30)  # Max 30 point penalty
        
        # Bonus for positives
        total_positives = sum(len(check.get("positives", [])) for check in checks.values())
        positive_bonus = min(total_positives * 1, 10)  # Max 10 point bonus
        
        final_score = base_score - issue_penalty + positive_bonus
        return max(0, min(100, final_score))
    
    def _generate_feedback(self, checks: Dict) -> List[str]:
        """Generate actionable feedback"""
        feedback = []
        
        for check_name, check_result in checks.items():
            if check_result.get("status") != "pass":
                issues = check_result.get("issues", [])
                if issues:
                    feedback.append(f"{check_name.replace('_', ' ').title()}: {issues[0]}")
        
        # Add positive feedback
        all_positives = []
        for check_result in checks.values():
            all_positives.extend(check_result.get("positives", []))
        
        if all_positives:
            feedback.append(f"Good progress: {', '.join(all_positives[:3])}")
        
        # Goal-specific feedback
        if not self._evaluate_goal({"checks": checks}):
            feedback.append(f"Continue working towards goal: {self.goal}")
        
        return feedback
    
    def _evaluate_goal(self, review: Dict) -> bool:
        """Evaluate if the goal has been met"""
        score = review.get("score", 0)
        checks = review.get("checks", {})
        
        # Goal is met if:
        # 1. Score is above 85
        # 2. All critical checks pass
        # 3. Goal alignment is good
        
        critical_checks = ["structure", "functionality"]
        critical_passed = all(
            checks.get(check, {}).get("status") == "pass"
            for check in critical_checks
        )
        
        goal_aligned = checks.get("goal_alignment", {}).get("status") == "pass"
        
        return score >= 85 and critical_passed and goal_aligned
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_improvement_suggestions(self) -> List[str]:
        """Get specific improvement suggestions"""
        if not self.review_history:
            return ["Run a review first"]
        
        latest_review = self.review_history[-1]
        suggestions = []
        
        for check_name, check_result in latest_review["checks"].items():
            issues = check_result.get("issues", [])
            if issues:
                suggestions.append(f"Fix: {issues[0]}")
        
        return suggestions[:5]  # Top 5 suggestions
