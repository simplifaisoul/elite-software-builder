FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY elite_builder/ ./elite_builder/
COPY config.json.example ./config.json.example

# Create necessary directories
RUN mkdir -p /app/projects /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Expose MCP server port (if needed)
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "mcp" ]; then\n\
    exec python -m elite_builder.main --mode mcp\n\
elif [ "$1" = "standalone" ]; then\n\
    exec python -m elite_builder.main --mode standalone --project-spec "$2" --goal "$3" --max-iterations "${4:-50}"\n\
else\n\
    exec python -m elite_builder.main "$@"\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Default to MCP mode
CMD ["mcp"]
