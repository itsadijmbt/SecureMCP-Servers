from typing import Any, Dict, Optional
import httpx
# PORT: FastMCP -> SecureMCP (type hint only; decorator API matches).
# from fastmcp import FastMCP
from macaw_adapters.mcp import SecureMCP
from src.core import config
from src.core.logger import logger
from utils.validators import validate_user_id, validate_message_type

def register_memory_tools(mcp: SecureMCP):
    """Register memory-related tools."""
    
    @mcp.tool(name="store_memory", description="Store a message in AI memory")
    async def store_memory(
        conversation_id: str,
        text: str,
        message_type: str,
        user_id: str,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a message to conversation history."""
        
        user_id = validate_user_id(user_id)
        message_type = validate_message_type(message_type)

        payload = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "type": message_type,
            "text": text,
        }

        if timestamp:
            payload["timestamp"] = timestamp

        client = httpx.AsyncClient(timeout=300.0)
        try:
            response = await client.post(
                f"{config.AI_MEMORY_SERVICE_URL}/conversation/", json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(
                f"Error adding message to memory: {e.response.status_code} - {e.response.text}"
            )
            return {"error": str(e)}

    @mcp.tool(
        name="retrieve_memory",
        description="Get relevant AI memory with context and summary",
    )
    async def retrieve_memory(user_id: str, text: str) -> Dict[str, Any]:
        """Comprehensive memory retrieval: finds relevant memories, context, and generates a summary."""

        try:
            user_id = validate_user_id(user_id)
            params = {"user_id": user_id, "text": text}

            client = httpx.AsyncClient(timeout=1000.0)
            response = await client.get(
                f"{config.AI_MEMORY_SERVICE_URL}/retrieve_memory/", params=params
            )
            response.raise_for_status()
            return {
                "related_conversation": response.json().get("related_conversation", ""),
                "conversation_summary": response.json().get("conversation_summary", ""),
                "similar_memories": response.json().get("similar_memories", ""),
            }

        except httpx.HTTPError as e:
            logger.error(
                f"Error retrieving memory: {e.response.status_code} - {e.response.text}"
            )
            return {
                "related_conversation": f"Error retrieving memory: {e.response.status_code} - {e.response.text}",
                "conversation_summary": "",
                "similar_memories": "",
            }
