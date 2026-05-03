"""
Atlassian Rovo MCP -> SecureMCPProxy with bind_to_user (via mcp-remote).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("getAccessibleAtlassianResources") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Atlassian Rovo MCP is OAuth 2.1 with proper DCR. mcp-remote handles the
OAuth dance and exposes the remote server over stdio; SecureMCPProxy
wraps that. No manual app registration, no API token needed.

First run opens a browser for Atlassian login. Token cached in
~/.mcp-auth/. If `getAccessibleAtlassianResources` isn't in the tool list
that prints, swap it for one of the names you see (e.g. `getCurrentUser`)
in line 50.

Run:
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/atlassian/proxy_atlassian.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

ATLASSIAN_MCP_URL = "https://mcp.atlassian.com/v1/mcp/authv2"

proxy = SecureMCPProxy(
    app_name="atlassian-proxy",
    command=["npx", "-y", "mcp-remote", ATLASSIAN_MCP_URL],
    env={"PATH": os.environ["PATH"], "HOME": os.environ["HOME"]},
)

# Client identity: registers as securemcp-client-atlassian-macaw-gateway.
client = Client("atlassian-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# getAccessibleAtlassianResources lists the Cloud sites the user can see.
# No args, no rate-limit cost beyond the per-call quota.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("getAccessibleAtlassianResources", {})
print(f"\ngetAccessibleAtlassianResources -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("atlassian-macaw-proxy")
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
