#!/usr/bin/env python3
"""
Configuration Manager - Handles API keys, database credentials, etc.
"""

import os
import json
from typing import Dict, Optional

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            base_dir = os.path.dirname(__file__)
            config_path = os.path.join(base_dir, "..", "config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or environment"""
        config = {
            "project_name": "elite-built-app",
            "database_type": None,
            "database_url": None,
            "database_ssl": False,
            "api_keys": {},
            "services": {}
        }
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables
        config["database_url"] = os.getenv("DATABASE_URL", config.get("database_url"))
        config["database_type"] = os.getenv("DATABASE_TYPE", config.get("database_type"))
        
        # API keys from environment
        api_keys = config.get("api_keys", {})
        api_keys["openai"] = os.getenv("OPENAI_API_KEY", api_keys.get("openai"))
        api_keys["stripe"] = os.getenv("STRIPE_API_KEY", api_keys.get("stripe"))
        api_keys["github"] = os.getenv("GITHUB_TOKEN", api_keys.get("github"))
        config["api_keys"] = api_keys
        
        return config
    
    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, updates: Dict):
        """Update configuration"""
        self.config.update(updates)
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def request_credentials(self, services: list) -> Dict:
        """Request credentials for required services"""
        missing = []
        available = []
        
        for service in services:
            if service == "database":
                if not self.config.get("database_url"):
                    missing.append("database")
                else:
                    available.append("database")
            elif service in ["openai", "stripe", "github"]:
                if not self.config.get("api_keys", {}).get(service):
                    missing.append(service)
                else:
                    available.append(service)
            else:
                # Check if service is in config
                if service not in self.config.get("services", {}):
                    missing.append(service)
                else:
                    available.append(service)
        
        return {
            "available": available,
            "missing": missing,
            "message": f"Missing credentials for: {', '.join(missing)}" if missing else "All credentials available"
        }
    
    def set_credential(self, service: str, value: str, credential_type: str = "api_key"):
        """Set a credential"""
        if credential_type == "api_key":
            if "api_keys" not in self.config:
                self.config["api_keys"] = {}
            self.config["api_keys"][service] = value
        elif credential_type == "database":
            if service == "url":
                self.config["database_url"] = value
            elif service == "type":
                self.config["database_type"] = value
        else:
            if "services" not in self.config:
                self.config["services"] = {}
            self.config["services"][service] = value
        
        self._save_config()
    
    def get_credential(self, service: str, credential_type: str = "api_key") -> Optional[str]:
        """Get a credential"""
        if credential_type == "api_key":
            return self.config.get("api_keys", {}).get(service)
        elif credential_type == "database":
            if service == "url":
                return self.config.get("database_url")
            elif service == "type":
                return self.config.get("database_type")
        else:
            return self.config.get("services", {}).get(service)
        
        return None
