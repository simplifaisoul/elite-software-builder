#!/usr/bin/env python3
"""
Orchestrator - Manages the loop between Builder and Reviewer agents
"""

import os
import json
import asyncio
import time
from typing import Dict, Optional
from datetime import datetime

from elite_builder.builder_agent import BuilderAgent
from elite_builder.reviewer_agent import ReviewerAgent
from elite_builder.config_manager import ConfigManager

class Orchestrator:
    def __init__(self, project_spec: str, goal: str, max_iterations: int = 50):
        self.project_spec = project_spec
        self.goal = goal
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.is_running = False
        self.is_stopped = False
        
        # Setup paths
        self.base_path = os.path.join(os.path.dirname(__file__), "..", "projects")
        self.current_project_path = os.path.join(self.base_path, "current")
        os.makedirs(self.current_project_path, exist_ok=True)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        
        # Initialize agents
        self.builder = BuilderAgent(self.current_project_path, self.config)
        self.reviewer = ReviewerAgent(self.current_project_path, self.goal)
        
        # History
        self.history = []
        self.start_time = None
    
    async def run(self):
        """Run the builder-reviewer loop"""
        self.is_running = True
        self.is_stopped = False
        self.start_time = datetime.now()
        
        print(f"[Orchestrator] Starting Elite Software Builder")
        print(f"[Orchestrator] Goal: {self.goal}")
        print(f"[Orchestrator] Max iterations: {self.max_iterations}")
        
        # Initial project creation
        if self.current_iteration == 0:
            print(f"[Orchestrator] Creating initial project structure...")
            result = self.builder.create_project_structure()
            if not result.get("success"):
                print(f"[Orchestrator] Error creating project: {result.get('error')}")
                self.is_running = False
                return
        
        # Main loop
        while self.current_iteration < self.max_iterations and not self.is_stopped:
            self.current_iteration += 1
            print(f"\n[Orchestrator] === Iteration {self.current_iteration} ===")
            
            # Step 1: Reviewer reviews the project
            print(f"[Orchestrator] Reviewer analyzing project...")
            review = self.reviewer.review_project(self.current_iteration)
            
            review_summary = {
                "iteration": self.current_iteration,
                "score": review.get("score", 0),
                "meets_goal": review.get("meets_goal", False),
                "feedback_count": len(review.get("feedback", []))
            }
            
            print(f"[Orchestrator] Review Score: {review_summary['score']:.1f}/100")
            print(f"[Orchestrator] Meets Goal: {review_summary['meets_goal']}")
            
            # Check if goal is met
            if review.get("meets_goal", False):
                print(f"[Orchestrator] ✓ Goal achieved! Stopping loop.")
                self.history.append({
                    "iteration": self.current_iteration,
                    "action": "goal_achieved",
                    "review": review_summary
                })
                break
            
            # Step 2: Builder implements improvements based on feedback
            print(f"[Orchestrator] Builder implementing improvements...")
            feedback = review.get("feedback", [])
            suggestions = self.reviewer.get_improvement_suggestions()
            
            # Extract features to implement from feedback and project spec
            features_to_implement = self._extract_features_from_feedback(feedback, suggestions)
            
            if features_to_implement:
                build_result = self.builder.implement_features(features_to_implement, "\n".join(feedback))
                print(f"[Orchestrator] Builder result: {build_result.get('message', 'Completed')}")
            else:
                print(f"[Orchestrator] No specific features to implement, continuing...")
            
            # Step 3: Install dependencies if needed
            if self.current_iteration == 1:
                print(f"[Orchestrator] Installing dependencies...")
                install_result = self.builder.install_dependencies()
                if install_result.get("success"):
                    print(f"[Orchestrator] Dependencies installed")
                else:
                    print(f"[Orchestrator] Dependency installation issue: {install_result.get('error')}")
            
            # Step 4: Build project to check for errors
            if self.current_iteration % 3 == 0:  # Build every 3 iterations
                print(f"[Orchestrator] Building project...")
                build_result = self.builder.build_project()
                if build_result.get("success"):
                    print(f"[Orchestrator] Build successful")
                else:
                    print(f"[Orchestrator] Build errors: {build_result.get('error', 'Unknown')[:200]}")
            
            # Save iteration history
            self.history.append({
                "iteration": self.current_iteration,
                "review": review_summary,
                "features_implemented": features_to_implement,
                "timestamp": datetime.now().isoformat()
            })
            
            # Small delay between iterations
            await asyncio.sleep(2)
        
        # Final review
        if not self.is_stopped:
            print(f"\n[Orchestrator] === Final Review ===")
            final_review = self.reviewer.review_project(self.current_iteration + 1)
            print(f"[Orchestrator] Final Score: {final_review.get('score', 0):.1f}/100")
            print(f"[Orchestrator] Goal Met: {final_review.get('meets_goal', False)}")
            
            self.history.append({
                "iteration": self.current_iteration + 1,
                "action": "final_review",
                "review": {
                    "score": final_review.get("score", 0),
                    "meets_goal": final_review.get("meets_goal", False)
                }
            })
        
        # Save history
        self._save_history()
        
        self.is_running = False
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        print(f"\n[Orchestrator] Build process completed in {elapsed:.1f} seconds")
        print(f"[Orchestrator] Total iterations: {self.current_iteration}")
    
    def _extract_features_from_feedback(self, feedback: list, suggestions: list) -> list:
        """Extract features to implement from feedback"""
        features = []
        
        # Combine feedback and suggestions
        all_feedback = feedback + suggestions
        
        # Extract feature requests
        feature_keywords = {
            "navigation": ["navigation", "navbar", "menu"],
            "hero": ["hero", "banner", "landing"],
            "authentication": ["auth", "login", "signup", "authentication"],
            "api": ["api", "backend", "service"],
            "database": ["database", "db", "data"],
            "responsive": ["responsive", "mobile", "responsive design"],
            "styling": ["styling", "css", "design", "ui"],
            "components": ["component", "module"]
        }
        
        for item in all_feedback:
            item_lower = item.lower()
            for feature, keywords in feature_keywords.items():
                if any(keyword in item_lower for keyword in keywords):
                    if feature not in features:
                        features.append(feature)
        
        # If no specific features found, add generic improvements
        if not features:
            features = ["improve_code_quality", "add_missing_components"]
        
        return features[:5]  # Limit to 5 features per iteration
    
    def _save_history(self):
        """Save build history"""
        history_path = os.path.join(self.current_project_path, "build_history.json")
        with open(history_path, 'w') as f:
            json.dump({
                "project_spec": self.project_spec,
                "goal": self.goal,
                "total_iterations": self.current_iteration,
                "history": self.history,
                "completed_at": datetime.now().isoformat()
            }, f, indent=2)
    
    def get_status(self) -> Dict:
        """Get current status"""
        return {
            "is_running": self.is_running,
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "goal": self.goal,
            "goal_met": any(
                h.get("review", {}).get("meets_goal", False)
                for h in self.history
            ) if self.history else False,
            "latest_score": self.history[-1].get("review", {}).get("score", 0) if self.history else 0,
            "elapsed_time": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def stop(self):
        """Stop the build process"""
        self.is_stopped = True
        self.is_running = False
        print(f"[Orchestrator] Build process stopped by user")
