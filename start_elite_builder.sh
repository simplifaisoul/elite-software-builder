#!/bin/bash
# Elite Software Builder Startup Script

set -e

echo "🚀 Starting Elite Software Builder..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "📦 Using Docker..."
    
    # Check if config.json exists
    if [ ! -f "config.json" ]; then
        echo "📝 Creating config.json from example..."
        cp config.json.example config.json
        echo "⚠️  Please edit config.json with your credentials!"
    fi
    
    # Create projects directory
    mkdir -p projects
    
    # Build and run
    docker-compose up -d
    
    echo "✅ Elite Software Builder is running!"
    echo "📊 Check status: docker logs elite-software-builder"
    echo "🛑 Stop: docker-compose down"
else
    echo "🐍 Using Python directly..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "Python version: $python_version"
    
    # Install dependencies
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Check if config.json exists
    if [ ! -f "config.json" ]; then
        echo "📝 Creating config.json from example..."
        cp config.json.example config.json
        echo "⚠️  Please edit config.json with your credentials!"
    fi
    
    # Create projects directory
    mkdir -p projects
    
    # Run
    echo "🚀 Starting MCP server..."
    python3 -m elite_builder.main --mode mcp
fi
