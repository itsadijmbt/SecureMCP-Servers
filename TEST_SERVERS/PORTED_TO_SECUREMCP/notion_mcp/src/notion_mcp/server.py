"""Notion todo MCP server (ported from low-level mcp.server.Server to SecureMCP).

Port shape:
  - Original used the official MCP SDK's low-level `Server` with a single
    `@server.list_tools()` and a single `@server.call_tool()` if/elif
    dispatcher (the "old format" per skills file Step 0).
  - Per Step 0: schemas were hand-written and 1:1 with the dispatcher
    branches, so the verdict was PORT-by-collapse -- each elif branch
    became its own `@mcp.tool()` decorated async function.
  - The 3 Notion API helper functions (fetch_todos, create_todo,
    mark_todo_complete_in_notion) are UNCHANGED. Helper formerly named
    `complete_todo` was renamed to mark_todo_complete_in_notion because
    `complete_todo` is also a public tool name -- module-level collision
    after collapse. Public tool name kept byte-identical via
    `@mcp.tool(name="complete_todo")`.
"""

# was: from mcp.server import Server
from macaw_adapters.mcp import SecureMCP
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    EmbeddedResource
)
from pydantic import AnyUrl
import os
import json
from datetime import datetime
import httpx
from typing import Any, Sequence
from dotenv import load_dotenv
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('notion_mcp')

# Find and load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
if not env_path.exists():
    raise FileNotFoundError(f"No .env file found at {env_path}")
load_dotenv(env_path)

# Initialize server
# Port Step 1b: low-level Server -> SecureMCP. Name "notion-todo" is
# already kebab-case (matters because SecureMCP server names become part
# of the agent_id routing key; spaces hang call_tool RPC -- verified on
# the excalidraw port).
# was: server = Server("notion-todo")
mcp = SecureMCP("notion-todo")

# Configuration with validation
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_API_KEY:
    raise ValueError("NOTION_API_KEY not found in .env file")
if not DATABASE_ID:
    raise ValueError("NOTION_DATABASE_ID not found in .env file")

NOTION_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

# Notion API headers
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

# ---------------------------------------------------------------------------
# Notion API helpers (UNCHANGED -- Hard Rule 9)
# ---------------------------------------------------------------------------

async def fetch_todos() -> dict:
    """Fetch todos from Notion database"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NOTION_BASE_URL}/databases/{DATABASE_ID}/query",
            headers=headers,
            json={
                "sorts": [
                    {
                        "timestamp": "created_time",
                        "direction": "descending"
                    }
                ]
            }
        )
        response.raise_for_status()
        return response.json()

async def create_todo(task: str, when: str) -> dict:
    """Create a new todo in Notion"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NOTION_BASE_URL}/pages",
            headers=headers,
            json={
                "parent": {"database_id": DATABASE_ID},
                "properties": {
                    "Task": {
                        "type": "title",
                        "title": [{"type": "text", "text": {"content": task}}]
                    },
                    "When": {
                        "type": "select",
                        "select": {"name": when}
                    },
                    "Checkbox": {
                        "type": "checkbox",
                        "checkbox": False
                    }
                }
            }
        )
        response.raise_for_status()
        return response.json()

# Port collision fix: helper renamed from `complete_todo` to
# `mark_todo_complete_in_notion` because `complete_todo` is also a public
# tool name (advertised by the original list_tools); after collapse the
# tool function would shadow the helper at module scope. The public tool
# name is preserved via @mcp.tool(name="complete_todo") below.
# was: async def complete_todo(page_id: str) -> dict:
async def mark_todo_complete_in_notion(page_id: str) -> dict:
    """Mark a todo as complete in Notion"""
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{NOTION_BASE_URL}/pages/{page_id}",
            headers=headers,
            json={
                "properties": {
                    "Checkbox": {
                        "type": "checkbox",
                        "checkbox": True
                    }
                }
            }
        )
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Tools (PORTED from @server.list_tools + @server.call_tool dispatcher).
#
# Original was one Tool(...) list and one if/elif call_tool() dispatcher.
# Per skills file Step 0 "PORT -- collapse into modern @mcp.tool()
# decorators". Schemas were hand-written and 1:1 with the dispatcher
# branches; the collapse preserves the schema's required fields as
# function parameters, the description as the @mcp.tool description,
# and the elif branch body as the function body.
#
# Original blocks preserved at the bottom of this file as a comment.
# ---------------------------------------------------------------------------


@mcp.tool(description="Add a new todo item")
async def add_todo(task: str, when: str) -> str:
    """Add a new todo to Notion.

    Args:
        task: The todo task description.
        when: When the task should be done. Must be 'today' or 'later'.
    """
    if when not in ["today", "later"]:
        raise ValueError("When must be 'today' or 'later'")
    if not task:
        raise ValueError("Task is required")
    try:
        result = await create_todo(task, when)
        return f"Added todo: {task} (scheduled for {when})"
    except httpx.HTTPError as e:
        logger.error(f"Notion API error: {str(e)}")
        return (
            f"Error adding todo: {str(e)}\n"
            "Please make sure your Notion integration is properly set up "
            "and has access to the database."
        )


@mcp.tool(description="Show all todo items from Notion")
async def show_all_todos() -> str:
    """List every todo currently in the configured Notion database."""
    try:
        todos = await fetch_todos()
        formatted_todos = []
        for todo in todos.get("results", []):
            props = todo["properties"]
            formatted_todo = {
                "id": todo["id"],
                "task": props["Task"]["title"][0]["text"]["content"] if props["Task"]["title"] else "",
                "completed": props["Checkbox"]["checkbox"],
                "when": props["When"]["select"]["name"] if props["When"]["select"] else "unknown",
                "created": todo["created_time"]
            }
            formatted_todos.append(formatted_todo)
        return json.dumps(formatted_todos, indent=2)
    except httpx.HTTPError as e:
        logger.error(f"Notion API error: {str(e)}")
        return (
            f"Error fetching todos: {str(e)}\n"
            "Please make sure your Notion integration is properly set up "
            "and has access to the database."
        )


@mcp.tool(description="Show today's todo items from Notion")
async def show_today_todos() -> str:
    """List todos whose 'when' is 'today' in the configured Notion database."""
    try:
        todos = await fetch_todos()
        formatted_todos = []
        for todo in todos.get("results", []):
            props = todo["properties"]
            formatted_todo = {
                "id": todo["id"],
                "task": props["Task"]["title"][0]["text"]["content"] if props["Task"]["title"] else "",
                "completed": props["Checkbox"]["checkbox"],
                "when": props["When"]["select"]["name"] if props["When"]["select"] else "unknown",
                "created": todo["created_time"]
            }
            if formatted_todo["when"].lower() != "today":
                continue
            formatted_todos.append(formatted_todo)
        return json.dumps(formatted_todos, indent=2)
    except httpx.HTTPError as e:
        logger.error(f"Notion API error: {str(e)}")
        return (
            f"Error fetching todos: {str(e)}\n"
            "Please make sure your Notion integration is properly set up "
            "and has access to the database."
        )


# Public tool name preserved as "complete_todo" via the explicit name=
# kwarg (the Python function is renamed to avoid module-level collision
# with the helper `mark_todo_complete_in_notion`).
@mcp.tool(name="complete_todo", description="Mark a todo item as complete")
async def complete_todo_tool(task_id: str) -> str:
    """Mark a todo as complete in Notion.

    Args:
        task_id: The ID of the todo task (Notion page id) to complete.
    """
    if not task_id:
        raise ValueError("Task ID is required")
    try:
        result = await mark_todo_complete_in_notion(task_id)
        return f"Marked todo as complete (ID: {task_id})"
    except httpx.HTTPError as e:
        logger.error(f"Notion API error: {str(e)}")
        return (
            f"Error completing todo: {str(e)}\n"
            "Please make sure your Notion integration is properly set up "
            "and has access to the database."
        )


# ---------------------------------------------------------------------------
# Entry point (Port Step 1d: drop stdio main loop; mesh replaces stdio).
# ---------------------------------------------------------------------------

def main():
    """Run the Notion todo server on the MACAW mesh.

    Port note: the original `async def main()` opened `stdio_server()`
    and called `server.run(read_stream, write_stream, ...)`. Under
    SecureMCP the same compute is reached via `mcp.run()`, which
    registers with the MACAW Local Agent and serves over the mesh.
    See bottom-of-file comment for the dropped stdio block.
    """
    if not NOTION_API_KEY or not DATABASE_ID:
        raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID environment variables are required")
    mcp.run()


if __name__ == "__main__":
    main()


# ===========================================================================
# DROPPED CODE (preserved per "ALWAYS KEEP THE OLD CODE COMMENTED.")
# ===========================================================================
#
# 1) Original @server.list_tools() block (replaced by 4 @mcp.tool() above):
#
# @server.list_tools()
# async def list_tools() -> list[Tool]:
#     """List available todo tools"""
#     return [
#         Tool(
#             name="add_todo",
#             description="Add a new todo item",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "task": {
#                         "type": "string",
#                         "description": "The todo task description"
#                     },
#                     "when": {
#                         "type": "string",
#                         "description": "When the task should be done (today or later)",
#                         "enum": ["today", "later"]
#                     }
#                 },
#                 "required": ["task", "when"]
#             }
#         ),
#         Tool(
#             name="show_all_todos",
#             description="Show all todo items from Notion",
#             inputSchema={"type":"object","properties":{},"required":[]}
#         ),
#         Tool(
#             name="show_today_todos",
#             description="Show today's todo items from Notion",
#             inputSchema={"type":"object","properties":{},"required":[]}
#         ),
#         Tool(
#             name="complete_todo",
#             description="Mark a todo item as complete",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "task_id": {
#                         "type": "string",
#                         "description": "The ID of the todo task to mark as complete"
#                     }
#                 },
#                 "required": ["task_id"]
#             }
#         )
#     ]
#
# Note on `when` enum: the original list_tools schema declared
# enum: ["today","later"]. After collapse the SecureMCP type_map
# (mcp.py:837) only knows base str/int/float/bool/dict/list, so `when`
# is advertised as a plain string. The runtime validation (`if when
# not in ["today","later"]: raise ValueError`) is preserved at the top
# of add_todo, so the behavioural contract is the same -- only the
# advertised schema fidelity is lower. Documented in MIGRATION.txt.
#
# 2) Original @server.call_tool() dispatcher (replaced by per-tool bodies):
#
# @server.call_tool()
# async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | EmbeddedResource]:
#     """Handle tool calls for todo management"""
#     if name == "add_todo":
#         # ... (body now lives in add_todo above)
#     elif name in ["show_all_todos", "show_today_todos"]:
#         # ... (body split into show_all_todos / show_today_todos above)
#     elif name == "complete_todo":
#         # ... (body now lives in complete_todo_tool above)
#     raise ValueError(f"Unknown tool: {name}")
#
# 3) Original stdio main (replaced by sync `def main(): mcp.run()`):
#
# async def main():
#     """Main entry point for the server"""
#     from mcp.server.stdio import stdio_server
#     if not NOTION_API_KEY or not DATABASE_ID:
#         raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID environment variables are required")
#     async with stdio_server() as (read_stream, write_stream):
#         await server.run(
#             read_stream,
#             write_stream,
#             server.create_initialization_options()
#         )
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
#
# 4) Return-type change (per branch):
#    Original returned `[TextContent(type="text", text=<msg>)]` from each
#    branch. New tools return the bare `<msg>` string. SecureMCP wraps
#    non-dict returns as `{"result": <str>}` at mcp.py:811-812. The
#    string content is byte-identical to the original TextContent.text.
