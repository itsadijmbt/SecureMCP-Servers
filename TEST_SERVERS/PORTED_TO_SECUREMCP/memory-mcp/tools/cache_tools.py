from typing import Any, Dict, Optional
import httpx
# PORT: FastMCP -> SecureMCP (type hint only; decorator API matches).
# from fastmcp import FastMCP
from macaw_adapters.mcp import SecureMCP
from src.core import config
from src.core.logger import logger
from utils.validators import validate_user_id

def register_cache_tools(mcp: SecureMCP):
    """Register cache-related tools."""
    
    @mcp.tool(
        name="semantic_cache_response", description="Cache AI response for similar queries"
    )
    async def semantic_cache_response(
        user_id: str, query: str, response: str, timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cache an AI response for future similar queries."""
        
        user_id = validate_user_id(user_id)

        payload = {
            "user_id": user_id,
            "query": query,
            "response": response,
        }

        if timestamp:
            payload["timestamp"] = timestamp

        client = httpx.AsyncClient(timeout=300.0)
        try:
            response = await client.post(
                f"{config.SEMANTIC_CACHE_SERVICE_URL}/save_to_cache", json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error: {e.response.status_code} - {e.response.text}")
            return {"error": str(e)}

    @mcp.tool(
        name="check_semantic_cache", description="Get cached response for similar query"
    )
    async def check_semantic_cache(user_id: str, query: str) -> Dict[str, Any]:
        """Retrieve a cached response for a semantically similar query."""
        
        user_id = validate_user_id(user_id)

        payload = {
            "user_id": user_id,
            "query": query,
        }

        client = httpx.AsyncClient(timeout=300.0)
        try:
            response = await client.post(
                f"{config.SEMANTIC_CACHE_SERVICE_URL}/read_cache", json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error: {e.response.status_code} - {e.response.text}")
            return {"error": str(e)}
