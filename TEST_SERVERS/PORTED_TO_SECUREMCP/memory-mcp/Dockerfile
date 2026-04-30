# Use the official Python lightweight image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml requirements.txt ./

# Install dependencies
RUN uv sync

# Copy application source code
COPY src/ ./src/
COPY services/ ./services/
COPY tools/ ./tools/
COPY utils/ ./utils/

# Create logs directory
RUN mkdir -p logs

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN uv sync

EXPOSE 8080

# Run the FastMCP server
CMD ["uv", "run", "src/server.py"]
