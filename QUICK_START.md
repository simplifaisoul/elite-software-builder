# 🚀 Quick Start Guide - Elite Software Builder

## Prerequisites

- **Linux** (or WSL on Windows)
- **Docker** (recommended) OR **Python 3.11+** and **Node.js 18+**
- **Git** (for GitHub export)

## Option 1: Docker (Easiest)

```bash
# 1. Make startup script executable
chmod +x start_elite_builder.sh

# 2. Run the startup script
./start_elite_builder.sh

# The script will:
# - Create config.json from example
# - Build and start the Docker container
# - Run the MCP server
```

## Option 2: Python Direct

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create config.json
cp config.json.example config.json
# Edit config.json with your credentials

# 4. Run MCP server
python -m elite_builder.main --mode mcp

# Or run standalone
python -m elite_builder.main \
  --mode standalone \
  --project-spec "Build a modern website" \
  --goal "Fully functional website with responsive design"
```

## Using MCP Calls

Once the server is running, you can interact with it via MCP:

### Example: Start a Build

```python
import json
import sys

# MCP request to start build
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "start_build",
        "arguments": {
            "project_spec": "Build an e-commerce website with Stripe integration",
            "goal": "Fully functional e-commerce site with product catalog, cart, checkout, and Stripe payment processing",
            "max_iterations": 50
        }
    }
}

print(json.dumps(request))
```

### Example: Check Status

```python
request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "get_build_status",
        "arguments": {}
    }
}
```

### Example: Export to GitHub

```python
request = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "export_to_github",
        "arguments": {
            "repo_name": "my-elite-built-app",
            "github_token": "ghp_your_token_here",
            "organization": "your-org"  # Optional
        }
    }
}
```

## Configuration

Edit `config.json`:

```json
{
  "project_name": "my-app",
  "database_type": "postgresql",
  "database_url": "postgresql://user:pass@host/db",
  "api_keys": {
    "openai": "sk-...",
    "stripe": "sk_live_...",
    "github": "ghp_..."
  }
}
```

## What Happens Next?

1. **Builder** creates the project structure (React + Vite + TypeScript)
2. **Reviewer** analyzes and scores the project
3. **Builder** implements improvements based on feedback
4. Process repeats until goal is met
5. Project is ready in `projects/current/`
6. Export to GitHub when ready!

## Troubleshooting

### Docker Issues
```bash
# Check logs
docker logs elite-software-builder

# Restart
docker-compose restart
```

### Python Issues
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Node.js Issues
```bash
# Check Node version
node --version  # Should be 18+

# Install Node if missing
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Next Steps

- Read `README.md` for full documentation
- Check `projects/current/` for your built project
- View `projects/current/build_history.json` for iteration history

---

**Happy Building! 🎉**
