"""
Notion MCP -> SecureMCPProxy with bind_to_user (npx stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("API-post-search") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Run:
    export NOTION_TOKEN="ntn_..."
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/notion/proxy_notion.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("NOTION_TOKEN")
if not token:
    raise ValueError("NOTION_TOKEN is not set (format: ntn_...)")

proxy = SecureMCPProxy(
    app_name="notion-proxy",
    command=["npx", "-y", "@notionhq/notion-mcp-server"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "NOTION_TOKEN": token,
    },
)

# Client identity: registers as securemcp-client-notion-macaw-gateway.
client = Client("notion-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# Search with empty query returns up to 100 items the integration can see.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("API-post-search", {"query": ""})
print(f"\nAPI-post-search -> {str(result)[:300]}", file=sys.stderr)

# ============================================================================
# Test 2 — stdio MCP gateway (uncomment block below to enable).
# Re-publishes upstream tools as a stdio MCP server. Each tools/call from
# Gemini/Claude CLI is forwarded via bound -> same 2-node graph as Test 1.
# ============================================================================
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

srv = Server("notion-macaw-proxy")
tool_objs = [
    types.Tool(
        name=t["name"],
        description=t.get("description", ""),
        inputSchema=t.get("schema") or {"type": "object"},
    )
    for t in proxy.list_tools()
]

@srv.list_tools()
async def _list():
    return tool_objs

@srv.call_tool()
async def _call(name, args):
    r = bound.call_tool(name, args or {})
    return [types.TextContent(type="text", text=json.dumps(r, default=str))]

async def _main():
    async with stdio_server() as (rd, wr):
        await srv.run(rd, wr, srv.create_initialization_options())

asyncio.run(_main())
