# 🚀 Elite Software Builder

**An autonomous AI-powered system that builds and continuously improves websites through intelligent builder-reviewer loops.**

## 🌟 Overview

The Elite Software Builder is a revolutionary system that uses two AI agents working in a continuous loop:

1. **Builder Agent**: Creates and improves websites using modern technologies (React, Vite, TypeScript, TailwindCSS)
2. **Reviewer Agent**: Reviews the website, provides feedback, and scores the implementation
3. **Orchestrator**: Manages the loop until the exact goal is achieved

The system doesn't stop improving until it meets your exact specifications!

## ✨ Key Features

- 🔄 **Continuous Improvement Loop**: Builder and Reviewer work together non-stop until goal is met
- 🎯 **Goal-Oriented**: Stops only when the exact goal is achieved
- 🔑 **Credential Management**: Asks for API keys, database credentials, and other needed services
- 🚀 **Modern Stack**: React, Vite, TypeScript, TailwindCSS out of the box
- 📦 **Docker Ready**: Run on any Linux box with Docker
- 🔌 **MCP Integration**: Full MCP server support for remote control
- 📤 **GitHub Export**: Automatic export to GitHub using MCP tools
- 🐳 **Containerized**: Docker container for easy deployment

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         MCP Server / Orchestrator        │
└──────────────┬──────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼─────┐    ┌──────▼──────┐
│  Builder  │◄───┤  Reviewer   │
│   Agent   │───►│   Agent     │
└─────┬─────┘    └──────┬──────┘
      │                 │
      └────────┬────────┘
               │
      ┌────────▼────────┐
      │  React + Vite   │
      │    Project      │
      └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone or navigate to the project
cd elite-software-builder

# Build the Docker image
docker build -t elite-builder .

# Run with docker-compose (easiest)
docker-compose up -d

# Or run directly
docker run -d \
  -v $(pwd)/projects:/app/projects \
  -v $(pwd)/config.json:/app/config.json \
  -e GITHUB_TOKEN=your_github_token \
  -e DATABASE_URL=your_db_url \
  -p 8000:8000 \
  elite-builder
```

### Option 2: Direct Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Ensure Node.js 18+ and npm are installed
node --version  # Should be 18+
npm --version   # Should be 9+

# Run as MCP server
python -m elite_builder.main --mode mcp

# Or run standalone
python -m elite_builder.main \
  --mode standalone \
  --project-spec "Build a modern SaaS dashboard with user authentication" \
  --goal "Fully functional dashboard with auth, database integration, and responsive design" \
  --max-iterations 50
```

## 📋 Configuration

### Create `config.json`

```json
{
  "project_name": "my-saas-app",
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

You can also use environment variables:

```bash
export DATABASE_URL="postgresql://..."
export DATABASE_TYPE="postgresql"
export OPENAI_API_KEY="sk-..."
export STRIPE_API_KEY="sk_live_..."
export GITHUB_TOKEN="ghp_..."
```

## 🔌 MCP Integration

The Elite Software Builder runs as an MCP server, allowing you to control it remotely via MCP calls.

### Available MCP Tools

1. **`start_build`**
   - Start building a project
   - Parameters: `project_spec`, `goal`, `max_iterations`

2. **`get_build_status`**
   - Get current build status
   - Returns: iteration count, score, goal status

3. **`stop_build`**
   - Stop the current build process

4. **`export_to_github`**
   - Export the built project to GitHub
   - Parameters: `repo_name`, `github_token`, `organization` (optional)

5. **`request_credentials`**
   - Request API keys and credentials
   - Parameters: `required_services` (array)

### Example MCP Call

```python
# Using MCP client
result = await mcp_client.call_tool(
    "start_build",
    {
        "project_spec": "Build an e-commerce website with Stripe integration",
        "goal": "Fully functional e-commerce site with product catalog, cart, checkout, and Stripe payment processing",
        "max_iterations": 50
    }
)
```

## 🔄 How the Loop Works

1. **Initialization**
   - Builder creates project structure (React + Vite + TypeScript)
   - Sets up package.json, vite.config.ts, tailwind.config.js
   - Creates basic App.tsx and components

2. **Review Phase**
   - Reviewer analyzes the project
   - Checks: structure, code quality, functionality, goal alignment, best practices
   - Calculates score (0-100)
   - Determines if goal is met

3. **Build Phase**
   - Builder receives feedback
   - Implements requested features
   - Adds components, services, configurations
   - Installs dependencies if needed

4. **Iteration**
   - Process repeats
   - Builds project every 3 iterations to check for errors
   - Continues until goal is met or max iterations reached

5. **Completion**
   - Final review
   - Project export ready
   - GitHub export available

## 📁 Project Structure

```
elite-software-builder/
├── elite_builder/
│   ├── __init__.py
│   ├── main.py                 # Main entry point
│   ├── mcp_server.py           # MCP server
│   ├── orchestrator.py         # Loop orchestrator
│   ├── builder_agent.py        # Builder agent
│   ├── reviewer_agent.py       # Reviewer agent
│   ├── config_manager.py       # Config management
│   └── github_integration.py   # GitHub export
├── projects/
│   └── current/                # Current project being built
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config.json.example
└── README.md
```

## 🎯 Example Use Cases

### E-Commerce Website
```bash
python -m elite_builder.main \
  --mode standalone \
  --project-spec "E-commerce website with product catalog, shopping cart, and payment" \
  --goal "Fully functional e-commerce site with Stripe integration, product management, and order processing"
```

### SaaS Dashboard
```bash
python -m elite_builder.main \
  --mode standalone \
  --project-spec "SaaS dashboard with user authentication and analytics" \
  --goal "Complete dashboard with login, user management, data visualization, and API integration"
```

### Portfolio Website
```bash
python -m elite_builder.main \
  --mode standalone \
  --project-spec "Modern portfolio website" \
  --goal "Responsive portfolio site with project showcase, contact form, and smooth animations"
```

## 🔐 Security Notes

- API keys are stored in `config.json` (add to `.gitignore`)
- Use environment variables in production
- GitHub tokens should have minimal required permissions
- Database credentials should use connection strings with proper SSL

## 🐛 Troubleshooting

### Docker Issues
```bash
# Check logs
docker logs elite-software-builder

# Restart container
docker-compose restart
```

### MCP Connection Issues
- Ensure port 8000 is accessible
- Check firewall settings
- Verify MCP client configuration

### Build Errors
- Check Node.js version (18+ required)
- Ensure npm dependencies install correctly
- Review build logs in `projects/current/build_history.json`

## 📝 Requirements

- **Python**: 3.11+
- **Node.js**: 18+
- **npm**: 9+
- **Git**: For GitHub export
- **Docker**: Optional but recommended

## 📚 Documentation

- **[Complete How-To Guide](./docs/ELITE_BUILDER_COMPLETE_GUIDE.md)** - Full usage guide
- **[System Deep Dive](./docs/SYSTEM_DEEP_DIVE.md)** - Architecture and implementation details
- **[Quick Start](./QUICK_START.md)** - Fast setup guide
- **[System Overview](./SYSTEM_OVERVIEW.md)** - High-level overview

## 🤝 Contributing

This is an autonomous builder system. The agents will improve the codebase themselves! 🚀

## 📄 License

MIT License - Build amazing things!

---

**Built with ❤️ by the Elite Software Builder**

*"We don't stop until it's perfect."*
