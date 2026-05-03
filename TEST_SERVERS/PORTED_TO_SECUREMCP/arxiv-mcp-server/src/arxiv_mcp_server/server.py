"""
Arxiv MCP Server (SecureMCP port).

WHAT THIS FILE USED TO DO
=========================
The original was a low-level MCP server. It had:
  - one big @server.list_tools() that returned 10 Tool objects
  - one big @server.call_tool() with `if name == "search_papers": ...`
    branching to 10 handler functions
  - prompts handlers (@server.list_prompts / @server.get_prompt)
  - transport machinery to expose the server over stdio OR streamable
    HTTP (uvicorn + Starlette + StreamableHTTPSessionManager + DNS
    rebinding protection)

WHAT THIS FILE DOES NOW
=======================
Same 10 tools, but each is a normal @app.tool() function instead of
a branch in a giant if/elif. Each new function is a thin wrapper:

  - it takes the same parameters the old `inputSchema` advertised
  - it builds the `arguments` dict the old handler expected
  - it awaits the SAME handle_*() function (untouched in tools/<name>.py)
  - it pulls the text out of the returned TextContent and returns it
    as a plain string

The prompt subsystem and the HTTP/SSE/Streamable transport machinery
are dropped. Those served the MCP protocol layer; under MACAW the
mesh carries traffic, so the original transport code has no purpose.
The original code is preserved as comment blocks below for review.

See MIGRATION.txt for the full port plan and BROKEN ON PURPOSE list.
"""

import json
import logging
from typing import Any, Dict, List, Optional

# import mcp.types as types                                                  # PORT: dropped, no Tool/TextContent return-construction here anymore
# import uvicorn                                                             # PORT: dropped, HTTP transport gone
# from mcp.server import NotificationOptions, Server                         # PORT: dropped
# from mcp.server.models import InitializationOptions                        # PORT: dropped, MCP-protocol-layer init
# from mcp.server.stdio import stdio_server                                  # PORT: dropped, no stdio transport under SecureMCP
# from mcp.server.streamable_http_manager import StreamableHTTPSessionManager  # PORT: dropped, no streamable HTTP
# from mcp.server.transport_security import TransportSecuritySettings       # PORT: dropped, no HTTP transport to secure
# from starlette.applications import Starlette                              # PORT: dropped
# from starlette.routing import Mount                                       # PORT: dropped
from macaw_adapters.mcp import SecureMCP

from .config import Settings

# We still import the handlers; their bodies are unchanged. The Tool()
# objects (search_tool, download_tool, etc.) are NOT imported here
# anymore -- they were used by the old @server.list_tools() to advertise
# tools. SecureMCP derives the schema from the @app.tool() function
# signature instead.
from .tools import (
    handle_search,
    handle_download,
    handle_list_papers,
    handle_read_paper,
    handle_get_abstract,
)
# from .tools import search_tool, download_tool, list_tool, read_tool, abstract_tool   # PORT: Tool() objects no longer wired
from .tools import (
    handle_semantic_search,
    handle_reindex,
    # semantic_search_tool, reindex_tool,                                   # PORT
    handle_citation_graph,
    # citation_graph_tool,                                                   # PORT
    handle_watch_topic,
    # watch_topic_tool,                                                      # PORT
    handle_check_alerts,
    # check_alerts_tool,                                                     # PORT
)
# from .prompts.handlers import list_prompts as handler_list_prompts         # PORT: prompts subsystem dropped
# from .prompts.handlers import get_prompt as handler_get_prompt             # PORT

settings = Settings()
logger = logging.getLogger("arxiv-mcp-server")
logger.setLevel(logging.INFO)
# server = Server(settings.APP_NAME)    # PORT: was the low-level Server
app = SecureMCP(settings.APP_NAME)


# ======================================================================
# PORT NOTE -- prompts subsystem dropped
# ----------------------------------------------------------------------
# The original delegated @server.list_prompts and @server.get_prompt
# to prompts/handlers.py, which exposed 4 prompts (paper analysis,
# summarize paper, compare papers, literature review) with session-
# aware argument handling.
#
# SecureMCP's @app.prompt() decorator registers a static prompt
# handler -- it doesn't have the dynamic argument-driven get_prompt
# flow the original used. The prompt subsystem is dropped under this
# port. The 4 prompt files remain on disk untouched; they are simply
# no longer registered with SecureMCP.
#
# See MIGRATION.txt -> BROKEN ON PURPOSE (a) for restoration notes.
# ======================================================================
# @server.list_prompts()
# async def list_prompts() -> List[types.Prompt]:
#     """List available prompts."""
#     return await handler_list_prompts()
#
#
# @server.get_prompt()
# async def get_prompt(
#     name: str, arguments: Dict[str, str] | None = None
# ) -> types.GetPromptResult:
#     """Get a specific prompt with arguments."""
#     return await handler_get_prompt(name, arguments)


# ======================================================================
# PORT NOTE -- the @server.list_tools / @server.call_tool dispatcher
# is replaced by 10 @app.tool() wrappers below. Each wrapper:
#   1. Takes the same parameters the old inputSchema advertised
#      (typed Python kwargs, not a generic `arguments: dict`).
#   2. Rebuilds the dict the original handle_*() expects, skipping
#      kwargs that are None so optional fields stay omitted.
#   3. Awaits the handle_*() function unchanged (its body lives in
#      tools/<name>.py and is byte-for-byte the same).
#   4. Pulls the text out of the returned [TextContent(...)] list
#      and returns it as a plain string. SecureMCP wraps non-dict
#      returns as {"result": <str>} -- mesh consumers see the same
#      content under a result key.
# The _tool_error_message helper is KEPT (active) so the wrappers can
# preserve the original "raise on error payload" behaviour.
# ======================================================================

# @server.list_tools()
# async def list_tools() -> List[types.Tool]:
#     """List available arXiv research tools."""
#     return [
#         search_tool, download_tool, list_tool, read_tool, abstract_tool,
#         semantic_search_tool, reindex_tool, citation_graph_tool,
#         watch_topic_tool, check_alerts_tool,
#     ]


def _tool_error_message(result: List[Any]) -> Optional[str]:
    """Return the error text if a tool result is an error payload.

    Original docstring: 'Return the error text if a tool result is an
    error payload.'  Kept verbatim so wrapper functions can mirror the
    original call_tool's error-raising behaviour.
    """
    if len(result) != 1 or getattr(result[0], "type", None) != "text":
        return None

    text = getattr(result[0], "text", "")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text if text.startswith("Error:") else None

    if isinstance(payload, dict) and payload.get("status") == "error":
        return text
    return None


def _extract_text(result: List[Any]) -> str:
    """Pull the .text out of the first TextContent in a handler result.

    Handlers return a list with (typically) one TextContent. We extract
    the text and return it as a plain string so SecureMCP's mesh wrap
    is `{"result": <str>}` rather than `{"result": [TextContent(...)]}`.
    """
    if not result:
        return ""
    first = result[0]
    return getattr(first, "text", str(first))


# @server.call_tool()
# async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
#     """Handle tool calls for arXiv research functionality."""
#     logger.debug(f"Calling tool {name} with arguments {arguments}")
#     try:
#         if name == "search_papers":
#             result = await handle_search(arguments)
#         elif name == "download_paper":
#             result = await handle_download(arguments)
#         elif name == "list_papers":
#             result = await handle_list_papers(arguments)
#         elif name == "read_paper":
#             result = await handle_read_paper(arguments)
#         elif name == "get_abstract":
#             result = await handle_get_abstract(arguments)
#         elif name == "semantic_search":
#             result = await handle_semantic_search(arguments)
#         elif name == "reindex":
#             result = await handle_reindex(arguments)
#         elif name == "citation_graph":
#             result = await handle_citation_graph(arguments)
#         elif name == "watch_topic":
#             result = await handle_watch_topic(arguments)
#         elif name == "check_alerts":
#             result = await handle_check_alerts(arguments)
#         else:
#             result = [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]
#         if error_message := _tool_error_message(result):
#             raise RuntimeError(error_message)
#         return result
#     except Exception as e:
#         logger.error(f"Tool error: {str(e)}")
#         raise


# ----------------------------------------------------------------------
# Wrapper 1: search_papers
# ----------------------------------------------------------------------
@app.tool()
async def search_papers(
    query: str,
    max_results: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    categories: Optional[List[str]] = None,
    sort_by: Optional[str] = None,
) -> str:
    """Search for papers on arXiv with advanced filtering.

    Args:
        query: Search query. Use quoted phrases for exact matches
               (e.g. '"machine learning"'). Field specifiers
               (ti:, au:, abs:, cat:) and boolean ops (AND, OR,
               ANDNOT) are supported.
        max_results: Maximum number of results to return (default 10,
                     max 50).
        date_from: Start date YYYY-MM-DD.
        date_to: End date YYYY-MM-DD.
        categories: arXiv categories to filter (e.g. ["cs.AI", "cs.LG"]).
        sort_by: "relevance" (default) or "date".
    """
    args: Dict[str, Any] = {"query": query}
    if max_results is not None:
        args["max_results"] = max_results
    if date_from is not None:
        args["date_from"] = date_from
    if date_to is not None:
        args["date_to"] = date_to
    if categories is not None:
        args["categories"] = categories
    if sort_by is not None:
        args["sort_by"] = sort_by
    result = await handle_search(args)
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 2: download_paper
# ----------------------------------------------------------------------
@app.tool()
async def download_paper(paper_id: str) -> str:
    """Download a paper from arXiv and return its full text content.

    Tries the HTML version first; falls back to PDF conversion.

    Args:
        paper_id: The arXiv ID of the paper to download (e.g. '2103.12345').
    """
    result = await handle_download({"paper_id": paper_id})
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 3: list_papers
# ----------------------------------------------------------------------
@app.tool()
async def list_papers() -> str:
    """List all papers that have been downloaded and stored locally.

    Returns arXiv IDs only -- use read_paper to access content. Returns
    an empty list if no papers have been downloaded yet.
    """
    result = await handle_list_papers({})
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 4: read_paper
# ----------------------------------------------------------------------
@app.tool()
async def read_paper(paper_id: str) -> str:
    """Read the full text content of a paper previously downloaded.

    Will fail with a clear error if the paper has not been downloaded
    yet -- call download_paper first.

    Args:
        paper_id: The arXiv ID of the paper to read.
    """
    result = await handle_read_paper({"paper_id": paper_id})
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 5: get_abstract
# ----------------------------------------------------------------------
@app.tool()
async def get_abstract(paper_id: str) -> str:
    """Fetch the abstract and metadata of an arXiv paper without
    downloading the full paper.

    Use this before download_paper to assess relevance. Returns:
    title, authors, abstract, categories, published date, PDF URL.

    Args:
        paper_id: The arXiv paper ID (e.g. '2401.12345').
    """
    result = await handle_get_abstract({"paper_id": paper_id})
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 6: semantic_search
# ----------------------------------------------------------------------
@app.tool()
async def semantic_search(
    query: Optional[str] = None,
    paper_id: Optional[str] = None,
    max_results: int = 10,
) -> str:
    """Semantic similarity search over locally downloaded papers.

    Supports free-text queries or finding papers semantically similar
    to a given paper_id. Only searches your local downloaded
    collection -- empty results if no papers have been downloaded.
    Requires pro dependencies.

    Args:
        query: Free-text semantic query.
        paper_id: Find papers similar to this arXiv paper ID.
        max_results: Maximum number of results to return (default 10).
    """
    args: Dict[str, Any] = {"max_results": max_results}
    if query is not None:
        args["query"] = query
    if paper_id is not None:
        args["paper_id"] = paper_id
    result = await handle_semantic_search(args)
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 7: reindex
# ----------------------------------------------------------------------
@app.tool()
async def reindex(clear_existing: bool = True) -> str:
    """Rebuild the local semantic index for downloaded papers.

    Args:
        clear_existing: If true, clear the existing index before
                        rebuilding (default True).
    """
    result = await handle_reindex({"clear_existing": clear_existing})
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 8: citation_graph
# ----------------------------------------------------------------------
@app.tool()
async def citation_graph(paper_id: str) -> str:
    """Return papers citing an arXiv paper and papers that it
    references using Semantic Scholar's citation graph.

    Args:
        paper_id: arXiv ID (e.g. '2401.12345').
    """
    result = await handle_citation_graph({"paper_id": paper_id})
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 9: watch_topic
# ----------------------------------------------------------------------
@app.tool()
async def watch_topic(
    topic: str,
    categories: Optional[List[str]] = None,
    max_results: int = 10,
) -> str:
    """Save or update a persistent research topic watch.

    When checked via check_alerts, returns only papers published since
    the last check. Calling watch_topic with the same topic string
    updates the existing watch.

    Args:
        topic: Query string to monitor (uses arXiv search syntax).
        categories: Optional arXiv category filter (e.g. ['cs.LG']).
        max_results: Maximum papers per alert check (default 10).
    """
    args: Dict[str, Any] = {"topic": topic, "max_results": max_results}
    if categories is not None:
        args["categories"] = categories
    result = await handle_watch_topic(args)
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ----------------------------------------------------------------------
# Wrapper 10: check_alerts
# ----------------------------------------------------------------------
@app.tool()
async def check_alerts(topic: Optional[str] = None) -> str:
    """Check all saved topic watches for newly published papers.

    Omitting the topic parameter runs ALL saved watches. Passing a
    topic string checks only that specific watch.

    Args:
        topic: Optional. Check only this specific watched topic
               (must match exactly the topic string used in
               watch_topic). Omit to check all saved watches.
    """
    args: Dict[str, Any] = {}
    if topic is not None:
        args["topic"] = topic
    result = await handle_check_alerts(args)
    err = _tool_error_message(result)
    if err:
        raise RuntimeError(err)
    return _extract_text(result)


# ======================================================================
# PORT NOTE -- transport machinery dropped
# ----------------------------------------------------------------------
# The original had:
#   - _initialization_options(): built MCP-protocol InitializationOptions
#   - _csv_settings(): parsed CSV env settings
#   - _transport_security_settings(): DNS rebinding protection for HTTP
#   - _run_stdio(): served the server over stdio
#   - _run_streamable_http(): served the server over uvicorn + Starlette
#                             with StreamableHTTPSessionManager
#   - main(): picked stdio vs streamable_http based on settings.TRANSPORT
#
# Under SecureMCP all of that goes away. The mesh carries traffic;
# there is no MCP-stdio listener and no HTTP listener to secure.
# `app.run()` is sync, creates its own asyncio.run() internally
# (mcp.py:628-635), and registers the server as a mesh agent.
#
# Original code preserved as a comment block below.
# ======================================================================
# def _initialization_options() -> InitializationOptions:
#     """Build shared MCP initialization options for every transport."""
#     return InitializationOptions(
#         server_name=settings.APP_NAME,
#         server_version=settings.APP_VERSION,
#         capabilities=server.get_capabilities(
#             notification_options=NotificationOptions(resources_changed=True),
#             experimental_capabilities={},
#         ),
#     )
#
#
# def _csv_settings(value: str) -> list[str]:
#     """Parse a comma-separated environment setting into non-empty strings."""
#     return [item.strip() for item in value.split(",") if item.strip()]
#
#
# def _transport_security_settings() -> TransportSecuritySettings:
#     """Build explicit DNS rebinding protection for Streamable HTTP."""
#     host = settings.HOST
#     port = settings.PORT
#     loopback_hosts = {"127.0.0.1", "localhost", "[::1]"}
#     allowed_hosts = {
#         host,
#         f"{host}:{port}",
#         *(f"{h}:{port}" for h in loopback_hosts),
#         *loopback_hosts,
#     }
#     allowed_hosts.update(_csv_settings(settings.ALLOWED_HOSTS))
#
#     origin_hosts = {host, *loopback_hosts}
#     allowed_origins = {
#         f"http://{origin_host}:{port}" for origin_host in origin_hosts
#     } | {f"https://{origin_host}:{port}" for origin_host in origin_hosts}
#     allowed_origins.update(_csv_settings(settings.ALLOWED_ORIGINS))
#
#     return TransportSecuritySettings(
#         enable_dns_rebinding_protection=True,
#         allowed_hosts=sorted(allowed_hosts),
#         allowed_origins=sorted(allowed_origins),
#     )
#
#
# async def _run_stdio() -> None:
#     """Run the MCP server over stdio."""
#     async with stdio_server() as streams:
#         await server.run(streams[0], streams[1], _initialization_options())
#
#
# async def _run_streamable_http() -> None:
#     """Run the MCP server over Streamable HTTP."""
#     session_manager = StreamableHTTPSessionManager(
#         app=server, event_store=None, json_response=False,
#         security_settings=_transport_security_settings(),
#     )
#     starlette_app = Starlette(routes=[Mount("/mcp", app=session_manager.handle_request)])
#     config = uvicorn.Config(
#         starlette_app, host=settings.HOST, port=settings.PORT, log_level="info",
#     )
#     uvicorn_server = uvicorn.Server(config)
#     logger.info("Starting streamable HTTP transport on %s:%s", settings.HOST, settings.PORT)
#     async with session_manager.run():
#         await uvicorn_server.serve()
#
#
# async def main():
#     """Run the server async context."""
#     transport = settings.TRANSPORT.lower().replace("-", "_")
#     if transport in {"stdio", ""}:
#         await _run_stdio()
#     elif transport in {"http", "streamable_http"}:
#         await _run_streamable_http()
#     else:
#         raise ValueError(
#             f"Unsupported transport {settings.TRANSPORT!r}; expected 'stdio' or 'http'"
#         )


def main():
    """Run the SecureMCP server (sync; SecureMCP owns its asyncio.run())."""
    logger.info("Starting %s on the MACAW mesh", settings.APP_NAME)
    app.run()
