from typing import List
from tavily import TavilyClient
from src.core.config import TAVILY_API_KEY

async def search_web(query: str) -> List[str]:
    """Performs a web search using Tavily API."""
    tavily_client = (
        TavilyClient(api_key=TAVILY_API_KEY)
        if TAVILY_API_KEY
        else None
    )

    documents = tavily_client.search(query)
    return [doc["content"] for doc in documents.get("results", [])]
