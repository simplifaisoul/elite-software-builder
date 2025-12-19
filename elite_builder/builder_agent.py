#!/usr/bin/env python3
"""
Builder Agent - Creates and improves websites
"""

import os
import json
import subprocess
import shutil
from typing import Dict, List, Optional
from pathlib import Path

class BuilderAgent:
    def __init__(self, project_path: str, config: Dict):
        self.project_path = project_path
        self.config = config
        self.tech_stack = {
            "frontend": "react",
            "build_tool": "vite",
            "styling": "tailwindcss",
            "language": "typescript"
        }
    
    def create_project_structure(self) -> Dict[str, any]:
        """Create initial project structure"""
        try:
            # Create project directory
            os.makedirs(self.project_path, exist_ok=True)
            
            # Create standard React + Vite structure
            structure = {
                "src": {
                    "components": {},
                    "sections": {},
                    "utils": {},
                    "hooks": {},
                    "services": {},
                    "types": {}
                },
                "public": {},
                "config": {}
            }
            
            self._create_directory_structure(structure)
            
            # Create package.json
            self._create_package_json()
            
            # Create vite.config.ts
            self._create_vite_config()
            
            # Create tsconfig.json
            self._create_tsconfig()
            
            # Create tailwind.config.js
            self._create_tailwind_config()
            
            # Create index.html
            self._create_index_html()
            
            # Create main.tsx
            self._create_main_tsx()
            
            # Create App.tsx
            self._create_app_tsx()
            
            return {
                "success": True,
                "message": "Project structure created successfully",
                "path": self.project_path
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_directory_structure(self, structure: Dict, base_path: str = ""):
        """Recursively create directory structure"""
        for name, content in structure.items():
            path = os.path.join(self.project_path, base_path, name)
            os.makedirs(path, exist_ok=True)
            
            if isinstance(content, dict):
                self._create_directory_structure(content, os.path.join(base_path, name))
    
    def _create_package_json(self):
        """Create package.json with all dependencies"""
        package_json = {
            "name": self.config.get("project_name", "elite-built-app"),
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "lint": "eslint . --ext ts,tsx"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
                "framer-motion": "^10.16.4",
                "lucide-react": "^0.294.0",
                "axios": "^1.6.0",
                "zustand": "^4.4.7"
            },
            "devDependencies": {
                "@types/react": "^18.2.43",
                "@types/react-dom": "^18.2.17",
                "@typescript-eslint/eslint-plugin": "^6.14.0",
                "@typescript-eslint/parser": "^6.14.0",
                "@vitejs/plugin-react": "^4.2.1",
                "autoprefixer": "^10.4.16",
                "eslint": "^8.55.0",
                "eslint-plugin-react-hooks": "^4.6.0",
                "eslint-plugin-react-refresh": "^0.4.5",
                "postcss": "^8.4.32",
                "tailwindcss": "^3.3.6",
                "typescript": "^5.2.2",
                "vite": "^5.0.8"
            }
        }
        
        # Add database dependencies if needed
        if self.config.get("database_type") == "postgresql":
            package_json["dependencies"]["pg"] = "^8.11.3"
            package_json["dependencies"]["@types/pg"] = "^8.10.9"
        elif self.config.get("database_type") == "mongodb":
            package_json["dependencies"]["mongodb"] = "^6.3.0"
        
        # Add API client dependencies
        if self.config.get("api_keys", {}).get("stripe"):
            package_json["dependencies"]["@stripe/stripe-js"] = "^2.4.0"
        
        with open(os.path.join(self.project_path, "package.json"), 'w') as f:
            json.dump(package_json, f, indent=2)
    
    def _create_vite_config(self):
        """Create vite.config.ts"""
        vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
'''
        with open(os.path.join(self.project_path, "vite.config.ts"), 'w') as f:
            f.write(vite_config)
    
    def _create_tsconfig(self):
        """Create tsconfig.json"""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }
        
        with open(os.path.join(self.project_path, "tsconfig.json"), 'w') as f:
            json.dump(tsconfig, f, indent=2)
        
        # Create tsconfig.node.json
        tsconfig_node = {
            "compilerOptions": {
                "composite": True,
                "skipLibCheck": True,
                "module": "ESNext",
                "moduleResolution": "bundler",
                "allowSyntheticDefaultImports": True
            },
            "include": ["vite.config.ts"]
        }
        
        with open(os.path.join(self.project_path, "tsconfig.node.json"), 'w') as f:
            json.dump(tsconfig_node, f, indent=2)
    
    def _create_tailwind_config(self):
        """Create tailwind.config.js"""
        tailwind_config = '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
      },
    },
  },
  plugins: [],
}
'''
        with open(os.path.join(self.project_path, "tailwind.config.js"), 'w') as f:
            f.write(tailwind_config)
        
        # Create postcss.config.js
        postcss_config = '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
        with open(os.path.join(self.project_path, "postcss.config.js"), 'w') as f:
            f.write(postcss_config)
    
    def _create_index_html(self):
        """Create index.html"""
        index_html = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Elite Built App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''
        with open(os.path.join(self.project_path, "index.html"), 'w') as f:
            f.write(index_html)
    
    def _create_main_tsx(self):
        """Create main.tsx"""
        main_tsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
        with open(os.path.join(self.project_path, "src", "main.tsx"), 'w') as f:
            f.write(main_tsx)
        
        # Create index.css
        index_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
}

body {
  margin: 0;
  min-height: 100vh;
}
'''
        with open(os.path.join(self.project_path, "src", "index.css"), 'w') as f:
            f.write(index_css)
    
    def _create_app_tsx(self):
        """Create basic App.tsx"""
        app_tsx = '''import { useState } from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-center text-gray-900 mb-8">
          Welcome to Your Elite Built App
        </h1>
        <p className="text-center text-gray-600">
          This application is being continuously improved by the Elite Software Builder.
        </p>
      </div>
    </div>
  )
}

export default App
'''
        with open(os.path.join(self.project_path, "src", "App.tsx"), 'w') as f:
            f.write(app_tsx)
    
    def implement_features(self, features: List[str], feedback: Optional[str] = None) -> Dict:
        """Implement requested features based on project spec and feedback"""
        try:
            # This would use AI/LLM to generate code, but for now we'll create structured components
            implemented = []
            
            for feature in features:
                result = self._implement_feature(feature, feedback)
                if result["success"]:
                    implemented.append(feature)
            
            return {
                "success": True,
                "implemented_features": implemented,
                "message": f"Implemented {len(implemented)} features"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _implement_feature(self, feature: str, feedback: Optional[str] = None) -> Dict:
        """Implement a single feature"""
        # This is a placeholder - in a real implementation, this would use an LLM
        # to generate appropriate code based on the feature description
        
        feature_lower = feature.lower()
        
        if "navigation" in feature_lower or "navbar" in feature_lower:
            return self._create_navigation_component()
        elif "hero" in feature_lower:
            return self._create_hero_section()
        elif "api" in feature_lower or "backend" in feature_lower:
            return self._create_api_service()
        elif "database" in feature_lower:
            return self._create_database_config()
        elif "authentication" in feature_lower or "auth" in feature_lower:
            return self._create_auth_system()
        else:
            # Generic component creation
            return self._create_generic_component(feature)
    
    def _create_navigation_component(self) -> Dict:
        """Create navigation component"""
        nav_code = '''import { useState } from 'react'
import { Menu, X } from 'lucide-react'

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="text-2xl font-bold text-primary-600">Your App</div>
          <div className="hidden md:flex space-x-6">
            <a href="#home" className="text-gray-700 hover:text-primary-600">Home</a>
            <a href="#about" className="text-gray-700 hover:text-primary-600">About</a>
            <a href="#services" className="text-gray-700 hover:text-primary-600">Services</a>
            <a href="#contact" className="text-gray-700 hover:text-primary-600">Contact</a>
          </div>
          <button className="md:hidden" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>
    </nav>
  )
}
'''
        nav_path = os.path.join(self.project_path, "src", "components", "Navigation.tsx")
        with open(nav_path, 'w') as f:
            f.write(nav_code)
        
        return {"success": True, "component": "Navigation"}
    
    def _create_hero_section(self) -> Dict:
        """Create hero section"""
        hero_code = '''export default function Hero() {
  return (
    <section className="bg-gradient-to-r from-primary-600 to-indigo-600 text-white py-20">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-5xl font-bold mb-4">Welcome to Excellence</h1>
        <p className="text-xl mb-8">Built with Elite Software Builder</p>
        <button className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">
          Get Started
        </button>
      </div>
    </section>
  )
}
'''
        hero_path = os.path.join(self.project_path, "src", "sections", "Hero.tsx")
        with open(hero_path, 'w') as f:
            f.write(hero_code)
        
        return {"success": True, "component": "Hero"}
    
    def _create_api_service(self) -> Dict:
        """Create API service"""
        api_code = '''import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3001/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api
'''
        api_path = os.path.join(self.project_path, "src", "services", "api.ts")
        with open(api_path, 'w') as f:
            f.write(api_code)
        
        return {"success": True, "service": "api"}
    
    def _create_database_config(self) -> Dict:
        """Create database configuration"""
        db_type = self.config.get("database_type", "postgresql")
        
        if db_type == "postgresql":
            db_code = f'''import pg from 'pg'

const pool = new pg.Pool({{
  connectionString: process.env.DATABASE_URL || '{self.config.get("database_url", "")}',
  ssl: {str(self.config.get("database_ssl", False)).lower()}
}})

export default pool
'''
        else:
            db_code = f'''import {{ MongoClient }} from 'mongodb'

const client = new MongoClient(
  process.env.MONGODB_URI || '{self.config.get("database_url", "")}'
)

export default client
'''
        
        db_path = os.path.join(self.project_path, "src", "services", "database.ts")
        with open(db_path, 'w') as f:
            f.write(db_code)
        
        return {"success": True, "config": "database"}
    
    def _create_auth_system(self) -> Dict:
        """Create authentication system"""
        auth_code = '''import { create } from 'zustand'

interface AuthState {
  user: any | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: () => boolean
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  login: async (email: string, password: string) => {
    // Implement login logic
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await response.json()
    set({ user: data.user, token: data.token })
  },
  logout: () => {
    set({ user: null, token: null })
  },
  isAuthenticated: () => {
    return get().token !== null
  },
}))
'''
        auth_path = os.path.join(self.project_path, "src", "hooks", "useAuth.ts")
        with open(auth_path, 'w') as f:
            f.write(auth_code)
        
        return {"success": True, "system": "authentication"}
    
    def _create_generic_component(self, feature: str) -> Dict:
        """Create a generic component for unspecified features"""
        component_name = feature.replace(" ", "").replace("-", "")
        component_code = f'''export default function {component_name}() {{
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">{feature}</h2>
      <p>This component implements: {feature}</p>
    </div>
  )
}}
'''
        component_path = os.path.join(self.project_path, "src", "components", f"{component_name}.tsx")
        with open(component_path, 'w') as f:
            f.write(component_code)
        
        return {"success": True, "component": component_name}
    
    def install_dependencies(self) -> Dict:
        """Install npm dependencies"""
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Dependencies installed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def build_project(self) -> Dict:
        """Build the project"""
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Project built successfully",
                    "output_path": os.path.join(self.project_path, "dist")
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
