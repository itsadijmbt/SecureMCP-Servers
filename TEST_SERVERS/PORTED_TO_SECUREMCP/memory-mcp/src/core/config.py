# config.py
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application settings
APP_NAME = "memory-mcp"
APP_VERSION = "1.0"
APP_DESCRIPTION = (
    "MongoDB Memory Model Context Protocol(MCP) Server for AI applications"
)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOGGER_SERVICE_URL = os.getenv("LOGGER_SERVICE_URL", "http://event-logger:8181")
AI_MEMORY_SERVICE_URL = os.getenv("AI_MEMORY_SERVICE_URL", "http://ai-memory:8182")
SEMANTIC_CACHE_SERVICE_URL = os.getenv(
    "SEMANTIC_CACHE_SERVICE_URL", "http://semantic-cache:8183"
)
DATA_LOADER_SERVICE_URL = os.getenv("DATA_LOADER_SERVICE_URL", "http://data-loader:8184")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v1")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
EMBEDDING_MODEL_INPUT_TOKEN_LIMIT = int(
    os.getenv("EMBEDDING_MODEL_INPUT_TOKEN_LIMIT", "8192")
)
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "1536"))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
