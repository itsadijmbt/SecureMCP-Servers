"""
mcp-obsidian server (SecureMCP port).

WHAT THIS FILE USED TO DO
=========================
The original was a low-level MCP server. It had:
  - A dict `tool_handlers` mapping tool names to ToolHandler instances.
  - One @app.list_tools() that asked each handler for its
    Tool() description and returned them all.
  - One @app.call_tool() that looked up the handler by name and
    called its run_tool(args) method.
  - 13 ToolHandler subclasses defined in tools.py, each carrying its
    own name + Tool() description + run_tool body.

WHAT THIS FILE DOES NOW
=======================
Same 13 tools, but each is a normal @app.tool() function. The 13
ToolHandler subclasses in tools.py are NOT changed -- the port
keeps a single instance of each at module level and the wrapper
functions delegate to handler.run_tool(args).

Each wrapper:
  - takes typed kwargs matching the original inputSchema
  - builds the dict the handler's run_tool expects, skipping kwargs
    that are None so optional fields stay omitted
  - calls handler.run_tool(args) (sync method -- returns a list of
    TextContent)
  - extracts the .text from the TextContent and returns it as a
    plain string

The tool names are preserved exactly via @app.tool(name=...) so
existing callers see the same advertised names.

See MIGRATION.txt for the full port plan.
"""

import json
import logging
from collections.abc import Sequence
from typing import Any, Dict, List, Optional

import os
from dotenv import load_dotenv
# from mcp.server import Server                                              # PORT
# from mcp.types import (                                                    # PORT: TextContent etc no longer used here directly
#     Tool,
#     TextContent,
#     ImageContent,
#     EmbeddedResource,
# )
from macaw_adapters.mcp import SecureMCP

load_dotenv()

from . import tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

api_key = os.getenv("OBSIDIAN_API_KEY")
if not api_key:
    raise ValueError(f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}")

# PORT: was `app = Server("mcp-obsidian")`. We keep the variable name
# `app` (the original used it too) so every decorator below stays
# `@app.tool(...)`.
app = SecureMCP("mcp-obsidian")


# ======================================================================
# PORT NOTE -- the ToolHandler registry pattern is gone
# ----------------------------------------------------------------------
# Original had a `tool_handlers` dict, an `add_tool_handler()` helper,
# and a `get_tool_handler()` lookup. SecureMCP routes tool calls by
# name through @app.tool() decoration, so the manual registry is
# redundant. We instantiate each handler ONCE at module level (same
# semantic as the original add_tool_handler calls) and wrap each one
# with a @app.tool() function below.
#
# The 13 ToolHandler subclasses in tools.py are NOT changed. They
# carry their own inputSchema (documentation reference) and run_tool
# bodies (active code -- called by every wrapper).
# ======================================================================
# tool_handlers = {}
# def add_tool_handler(tool_class: tools.ToolHandler):
#     global tool_handlers
#     tool_handlers[tool_class.name] = tool_class
#
# def get_tool_handler(name: str) -> tools.ToolHandler | None:
#     if name not in tool_handlers:
#         return None
#     return tool_handlers[name]


# ----------------------------------------------------------------------
# Single instance of each ToolHandler (created once at module load,
# matching the original add_tool_handler() calls).
# ----------------------------------------------------------------------
_LIST_VAULT = tools.ListFilesInVaultToolHandler()
_LIST_DIR = tools.ListFilesInDirToolHandler()
_GET_FILE = tools.GetFileContentsToolHandler()
_SIMPLE_SEARCH = tools.SearchToolHandler()
_APPEND = tools.AppendContentToolHandler()
_PATCH = tools.PatchContentToolHandler()
_PUT = tools.PutContentToolHandler()
_DELETE = tools.DeleteFileToolHandler()
_COMPLEX_SEARCH = tools.ComplexSearchToolHandler()
_BATCH_GET = tools.BatchGetFileContentsToolHandler()
_PERIODIC = tools.PeriodicNotesToolHandler()
_RECENT_PERIODIC = tools.RecentPeriodicNotesToolHandler()
_RECENT_CHANGES = tools.RecentChangesToolHandler()


def _extract_text(result: Sequence[Any]) -> str:
    """Pull the .text out of the first TextContent in a handler result.

    Handlers return a list with (typically) one TextContent. We extract
    the text and return it as a plain string so SecureMCP's mesh wrap
    is `{"result": <str>}` rather than `{"result": [TextContent(...)]}`.
    """
    if not result:
        return ""
    first = result[0]
    return getattr(first, "text", str(first))


# ======================================================================
# PORT NOTE -- the @app.list_tools / @app.call_tool dispatcher is
# replaced by 13 @app.tool() wrappers below. Each wrapper:
#   - has typed Python kwargs matching the original inputSchema
#   - builds the dict the handler's run_tool() expects
#   - calls handler.run_tool(args)
#   - returns the text content as a plain string
# Tool names are preserved via @app.tool(name=...) so existing callers
# see the same advertised names (obsidian_*).
# Original code preserved as comments below.
# ======================================================================
# @app.list_tools()
# async def list_tools() -> list[Tool]:
#     """List available tools."""
#     return [th.get_tool_description() for th in tool_handlers.values()]
#
#
# @app.call_tool()
# async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
#     """Handle tool calls for command line run."""
#     if not isinstance(arguments, dict):
#         raise RuntimeError("arguments must be dictionary")
#     tool_handler = get_tool_handler(name)
#     if not tool_handler:
#         raise ValueError(f"Unknown tool: {name}")
#     try:
#         return tool_handler.run_tool(arguments)
#     except Exception as e:
#         logger.error(str(e))
#         raise RuntimeError(f"Caught Exception. Error: {str(e)}")


# ----------------------------------------------------------------------
# Wrapper 1: obsidian_list_files_in_vault (no parameters)
# ----------------------------------------------------------------------
@app.tool(name=tools.TOOL_LIST_FILES_IN_VAULT)
def obsidian_list_files_in_vault() -> str:
    """List all files and directories in the root directory of your Obsidian vault."""
    return _extract_text(_LIST_VAULT.run_tool({}))


# ----------------------------------------------------------------------
# Wrapper 2: obsidian_list_files_in_dir (dirpath required)
# ----------------------------------------------------------------------
@app.tool(name=tools.TOOL_LIST_FILES_IN_DIR)
def obsidian_list_files_in_dir(dirpath: str) -> str:
    """List all files and directories in a specific Obsidian directory.

    Args:
        dirpath: Path to list files from (relative to your vault root).
                 Empty directories will not be returned.
    """
    return _extract_text(_LIST_DIR.run_tool({"dirpath": dirpath}))


# ----------------------------------------------------------------------
# Wrapper 3: obsidian_get_file_contents (filepath required)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_get_file_contents")
def obsidian_get_file_contents(filepath: str) -> str:
    """Return the content of a single file in your vault.

    Args:
        filepath: Path to the relevant file (relative to your vault root).
    """
    return _extract_text(_GET_FILE.run_tool({"filepath": filepath}))


# ----------------------------------------------------------------------
# Wrapper 4: obsidian_simple_search (query required, context_length optional)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_simple_search")
def obsidian_simple_search(query: str, context_length: int = 100) -> str:
    """Simple text search across all files in the vault.

    Use this for plain-text matching. For structured queries, see
    obsidian_complex_search.

    Args:
        query: Text to search for in the vault.
        context_length: How much context to return around each match
                        (default 100 characters).
    """
    return _extract_text(
        _SIMPLE_SEARCH.run_tool({"query": query, "context_length": context_length})
    )


# ----------------------------------------------------------------------
# Wrapper 5: obsidian_append_content (filepath + content required)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_append_content")
def obsidian_append_content(filepath: str, content: str) -> str:
    """Append content to a new or existing file in the vault.

    Args:
        filepath: Path to the file (relative to vault root).
        content: Content to append to the file.
    """
    return _extract_text(
        _APPEND.run_tool({"filepath": filepath, "content": content})
    )


# ----------------------------------------------------------------------
# Wrapper 6: obsidian_patch_content (5 required fields)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_patch_content")
def obsidian_patch_content(
    filepath: str,
    operation: str,
    target_type: str,
    target: str,
    content: str,
) -> str:
    """Insert content into a note relative to a heading, block, or frontmatter.

    Args:
        filepath: Path to the file (relative to vault root).
        operation: One of "append", "prepend", or "replace".
        target_type: One of "heading", "block", or "frontmatter".
        target: The heading path, block reference, or frontmatter field.
        content: Content to insert.
    """
    return _extract_text(
        _PATCH.run_tool({
            "filepath": filepath,
            "operation": operation,
            "target_type": target_type,
            "target": target,
            "content": content,
        })
    )


# ----------------------------------------------------------------------
# Wrapper 7: obsidian_put_content (filepath + content required)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_put_content")
def obsidian_put_content(filepath: str, content: str) -> str:
    """Create a new file in your vault or fully replace an existing file.

    Args:
        filepath: Path to the file (relative to your vault root).
        content: Full content of the file to write.
    """
    return _extract_text(
        _PUT.run_tool({"filepath": filepath, "content": content})
    )


# ----------------------------------------------------------------------
# Wrapper 8: obsidian_delete_file (filepath required + confirm)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_delete_file")
def obsidian_delete_file(filepath: str, confirm: bool = False) -> str:
    """Delete a file or directory from the vault.

    Args:
        filepath: Path to the file or directory to delete (relative to vault root).
        confirm: Must be set to True to actually delete (safety guard).
    """
    return _extract_text(
        _DELETE.run_tool({"filepath": filepath, "confirm": confirm})
    )


# ----------------------------------------------------------------------
# Wrapper 9: obsidian_complex_search (JsonLogic query required)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_complex_search")
def obsidian_complex_search(query: Dict[str, Any]) -> str:
    """Complex search using a JsonLogic query.

    Supports standard JsonLogic operators plus 'glob' and 'regexp'
    for pattern matching.

    Examples:
      All markdown files:
        {"glob": ["*.md", {"var": "path"}]}
      All markdown files containing '1221':
        {"and": [
          {"glob": ["*.md", {"var": "path"}]},
          {"regexp": [".*1221.*", {"var": "content"}]}
        ]}

    Args:
        query: JsonLogic query object. See examples above.
    """
    return _extract_text(_COMPLEX_SEARCH.run_tool({"query": query}))


# ----------------------------------------------------------------------
# Wrapper 10: obsidian_batch_get_file_contents (filepaths required)
# ----------------------------------------------------------------------
@app.tool(name="obsidian_batch_get_file_contents")
def obsidian_batch_get_file_contents(filepaths: List[str]) -> str:
    """Return the contents of multiple files in your vault.

    Files are returned concatenated with headers identifying each one.

    Args:
        filepaths: List of file paths (relative to your vault root).
    """
    return _extract_text(_BATCH_GET.run_tool({"filepaths": filepaths}))


# ----------------------------------------------------------------------
# Wrapper 11: obsidian_get_periodic_note
# ----------------------------------------------------------------------
# Note: the original kwarg is named `type`, which shadows the Python
# built-in inside the function scope. Harmless and necessary -- if we
# renamed it, the JSON-schema parameter name would change and clients
# that pass {"type": "..."} would break.
@app.tool(name="obsidian_get_periodic_note")
def obsidian_get_periodic_note(period: str, type: str = "content") -> str:
    """Get the current periodic note for a specified period.

    Args:
        period: One of "daily", "weekly", "monthly", "quarterly", "yearly".
        type: "content" (default) or "metadata". Metadata includes
              note metadata (paths, tags, etc.) plus the content.
    """
    return _extract_text(
        _PERIODIC.run_tool({"period": period, "type": type})
    )


# ----------------------------------------------------------------------
# Wrapper 12: obsidian_get_recent_periodic_notes
# ----------------------------------------------------------------------
@app.tool(name="obsidian_get_recent_periodic_notes")
def obsidian_get_recent_periodic_notes(
    period: str,
    limit: int = 5,
    include_content: bool = False,
) -> str:
    """Get the most recent periodic notes for a period type.

    Args:
        period: One of "daily", "weekly", "monthly", "quarterly", "yearly".
        limit: Maximum number of notes to return (default 5; range 1-50).
        include_content: Whether to include note content (default False).
    """
    return _extract_text(
        _RECENT_PERIODIC.run_tool({
            "period": period,
            "limit": limit,
            "include_content": include_content,
        })
    )


# ----------------------------------------------------------------------
# Wrapper 13: obsidian_get_recent_changes
# ----------------------------------------------------------------------
@app.tool(name="obsidian_get_recent_changes")
def obsidian_get_recent_changes(limit: int = 10, days: int = 90) -> str:
    """Get recently modified files in the vault.

    Args:
        limit: Maximum number of files to return (default 10; range 1-100).
        days: Only include files modified within this many days
              (default 90).
    """
    return _extract_text(
        _RECENT_CHANGES.run_tool({"limit": limit, "days": days})
    )


# ======================================================================
# PORT NOTE -- entry point
# ----------------------------------------------------------------------
# Original was async main() with `async with stdio_server()` +
# app.run(read_stream, write_stream, app.create_initialization_options()).
# Under SecureMCP `app.run()` is sync (mcp.py:628-635) and creates its
# own asyncio.run() internally. The mesh carries traffic; no stdio
# pipes needed.
# ======================================================================
# async def main():
#     # Import here to avoid issues with event loops
#     from mcp.server.stdio import stdio_server
#
#     async with stdio_server() as (read_stream, write_stream):
#         await app.run(
#             read_stream,
#             write_stream,
#             app.create_initialization_options()
#         )


def main():
    """Run the SecureMCP server (sync; SecureMCP owns its asyncio.run())."""
    logger.info("Starting mcp-obsidian on the MACAW mesh")
    app.run()
