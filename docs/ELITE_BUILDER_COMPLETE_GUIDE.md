# Elite Software Builder - Complete How-To Guide

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [MCP Integration](#mcp-integration)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Introduction

The **Elite Software Builder** is an autonomous AI-powered system that continuously builds and improves websites through an intelligent builder-reviewer feedback loop. It doesn't stop until your exact goal is achieved.

### Key Concepts

- **Builder Agent**: Creates and improves websites using modern technologies
- **Reviewer Agent**: Analyzes, scores, and provides feedback
- **Orchestrator**: Manages the continuous improvement loop
- **Goal-Oriented**: Stops only when the specified goal is met

---

## System Overview

### Architecture Flow

```
User Input (Project Spec + Goal)
         ↓
   Orchestrator
         ↓
    ┌────┴────┐
    │         │
Builder    Reviewer
    │         │
    └────┬────┘
         ↓
   Improvement
         ↓
   Goal Met? → Yes → Export to GitHub
         ↓ No
    Continue Loop
```

### Technology Stack

- **Frontend**: React 18.2+
- **Build Tool**: Vite 5.0+
- **Language**: TypeScript 5.2+
- **Styling**: TailwindCSS 3.3+
- **Package Manager**: npm 9+
- **Runtime**: Node.js 18+

---

## Installation & Setup

### Prerequisites

- **Python 3.11+** (for the builder system)
- **Node.js 18+** (for building projects)
- **npm 9+** (package manager)
- **Git** (for GitHub export)
- **Docker** (optional, recommended)

### Option 1: Docker Installation (Recommended)

```bash
# 1. Clone or navigate to the project
cd elite-software-builder

# 2. Build the Docker image
docker build -t elite-builder .

# 3. Create config.json
cp config.json.example config.json
# Edit config.json with your credentials

# 4. Start with docker-compose
docker-compose up -d

# 5. Check logs
docker logs elite-software-builder
```

### Option 2: Direct Python Installation

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Node.js installation
node --version  # Should be 18+
npm --version   # Should be 9+

# 4. Create config.json
cp config.json.example config.json
```

### Verification

```bash
# Test Python installation
python -m elite_builder.main --help

# Test Node.js
node --version
npm --version
```

---

## Configuration

### Configuration File (`config.json`)

Create or edit `config.json` in the project root:

```json
{
  "project_name": "my-elite-app",
  "database_type": "postgresql",
  "database_url": "postgresql://user:password@localhost:5432/mydb",
  "database_ssl": false,
  "api_keys": {
    "openai": "sk-...",
    "stripe": "sk_live_...",
    "github": "ghp_..."
  },
  "services": {
    "email": "sendgrid_api_key_here"
  }
}
```

### Environment Variables

Alternatively, use environment variables:

```bash
export DATABASE_URL="postgresql://user:pass@host/db"
export DATABASE_TYPE="postgresql"
export OPENAI_API_KEY="sk-..."
export STRIPE_API_KEY="sk_live_..."
export GITHUB_TOKEN="ghp_..."
```

### Credential Management

The system will automatically request missing credentials:

1. **Database**: PostgreSQL, MongoDB, or MySQL
2. **API Keys**: OpenAI, Stripe, GitHub, etc.
3. **Services**: Email providers, payment gateways, etc.

---

## Usage Guide

### Method 1: MCP Server Mode (Recommended)

Start the MCP server:

```bash
# Docker
docker-compose up -d

# Or Python
python -m elite_builder.main --mode mcp
```

Then use MCP client to interact:

```python
# Example: Start a build
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "start_build",
    "arguments": {
      "project_spec": "Build an e-commerce website with Stripe integration",
      "goal": "Fully functional e-commerce site with product catalog, shopping cart, checkout, and Stripe payment processing",
      "max_iterations": 50
    }
  }
}
```

### Method 2: Standalone Mode

```bash
python -m elite_builder.main \
  --mode standalone \
  --project-spec "Build a modern SaaS dashboard" \
  --goal "Fully functional dashboard with user authentication, database integration, and responsive design" \
  --max-iterations 50
```

### Available MCP Tools

#### 1. `start_build`

Start building a project.

**Parameters:**
- `project_spec` (string, required): Detailed specification
- `goal` (string, required): Exact goal to achieve
- `max_iterations` (integer, optional): Maximum iterations (default: 50)

**Example:**
```json
{
  "name": "start_build",
  "arguments": {
    "project_spec": "Build a blog platform",
    "goal": "Fully functional blog with posts, comments, and user authentication",
    "max_iterations": 30
  }
}
```

#### 2. `get_build_status`

Get current build status.

**Returns:**
- `is_running`: Whether build is active
- `current_iteration`: Current iteration number
- `goal_met`: Whether goal has been achieved
- `latest_score`: Latest review score (0-100)
- `elapsed_time`: Time elapsed in seconds

#### 3. `stop_build`

Stop the current build process.

#### 4. `export_to_github`

Export the built project to GitHub.

**Parameters:**
- `repo_name` (string, required): Repository name
- `github_token` (string, required): GitHub personal access token
- `organization` (string, optional): GitHub organization

**Example:**
```json
{
  "name": "export_to_github",
  "arguments": {
    "repo_name": "my-elite-built-app",
    "github_token": "ghp_...",
    "organization": "my-org"
  }
}
```

#### 5. `request_credentials`

Request API keys and credentials.

**Parameters:**
- `required_services` (array, required): List of services needing credentials

---

## MCP Integration

### MCP Server Protocol

The Elite Software Builder implements the Model Context Protocol (MCP) using JSON-RPC 2.0 over stdio.

### Connection

The server listens on stdin/stdout for JSON-RPC messages:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### Available Methods

- `tools/list`: List all available tools
- `tools/call`: Call a tool with arguments
- `resources/list`: List available resources
- `resources/read`: Read a resource by URI

### Example MCP Client

```python
import json
import sys

def send_mcp_request(method, params, request_id=1):
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params
    }
    print(json.dumps(request))
    sys.stdout.flush()
    
    # Read response
    response = json.loads(sys.stdin.readline())
    return response

# Start a build
response = send_mcp_request("tools/call", {
    "name": "start_build",
    "arguments": {
        "project_spec": "Build a website",
        "goal": "Fully functional website",
        "max_iterations": 50
    }
})
```

---

## Advanced Features

### Custom Project Templates

The builder supports custom project structures. Modify `builder_agent.py` to add:

```python
def _create_custom_template(self):
    # Your custom template logic
    pass
```

### Custom Review Criteria

Extend the reviewer in `reviewer_agent.py`:

```python
def _check_custom_criteria(self) -> Dict:
    # Your custom review logic
    pass
```

### Integration with CI/CD

Export to GitHub automatically triggers:

1. Repository creation
2. Initial commit
3. GitHub Actions setup (if configured)

### Monitoring Build Progress

Check `projects/current/build_history.json`:

```json
{
  "project_spec": "...",
  "goal": "...",
  "total_iterations": 15,
  "history": [
    {
      "iteration": 1,
      "review": {
        "score": 45.0,
        "meets_goal": false
      },
      "features_implemented": ["navigation", "hero"],
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

#### 1. Docker Container Won't Start

```bash
# Check logs
docker logs elite-software-builder

# Check if port is in use
netstat -tuln | grep 8000

# Restart container
docker-compose restart
```

#### 2. Node.js Not Found

```bash
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
```

#### 3. Build Errors

```bash
# Check project directory
ls -la projects/current/

# Check build history
cat projects/current/build_history.json

# Check npm dependencies
cd projects/current
npm install
npm run build
```

#### 4. MCP Connection Issues

- Verify MCP server is running
- Check stdin/stdout connection
- Verify JSON-RPC message format
- Check firewall settings

#### 5. GitHub Export Fails

```bash
# Verify GitHub token
echo $GITHUB_TOKEN

# Test git connection
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Check repository permissions
```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Best Practices

### 1. Goal Definition

**Good Goals:**
- ✅ "Fully functional e-commerce site with Stripe payment processing, product catalog, shopping cart, and order management"
- ✅ "Responsive portfolio website with project showcase, contact form, and smooth animations"

**Bad Goals:**
- ❌ "Make a website"
- ❌ "Build something cool"

### 2. Project Specifications

Be specific about:
- Required features
- Technology preferences
- Design requirements
- Integration needs

### 3. Iteration Limits

- **Simple projects**: 20-30 iterations
- **Medium projects**: 30-50 iterations
- **Complex projects**: 50-100 iterations

### 4. Credential Security

- Never commit `config.json` to version control
- Use environment variables in production
- Rotate API keys regularly
- Use least-privilege tokens

### 5. Monitoring

- Check build status regularly
- Review iteration history
- Monitor resource usage
- Track goal progress

---

## Next Steps

1. **Start Simple**: Begin with a basic project
2. **Iterate**: Refine your goals based on results
3. **Scale**: Move to more complex projects
4. **Automate**: Integrate with CI/CD pipelines
5. **Extend**: Customize agents for your needs

---

## Support & Resources

- **Documentation**: See `ELITE_BUILDER_README.md`
- **Quick Start**: See `QUICK_START.md`
- **System Overview**: See `SYSTEM_OVERVIEW.md`
- **Code Examples**: Check `projects/current/` after a build

---

**Happy Building! 🚀**
