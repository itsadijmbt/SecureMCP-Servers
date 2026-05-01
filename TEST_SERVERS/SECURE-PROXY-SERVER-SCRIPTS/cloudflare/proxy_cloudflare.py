"""
Cloudflare remote MCP -> SecureMCPProxy with bind_to_user.

Wraps Cloudflare's Documentation MCP server (https://docs.mcp.cloudflare.com/mcp)
via direct HTTPS + Bearer API token auth (skipping mcp-remote/OAuth).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("search_cloudflare_documentation") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

To wrap a different Cloudflare server (workers-bindings, observability, radar,
browser, etc.), change CF_MCP_URL below — same auth, same pattern.

Run:
    export CLOUDFLARE_API_TOKEN="..."
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/cloudflare/proxy_cloudflare.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("CLOUDFLARE_API_TOKEN")
if not token:
    raise ValueError("CLOUDFLARE_API_TOKEN is not set")

# Documentation server — read-only doc search. Swap URL for other CF servers:
#   https://bindings.mcp.cloudflare.com/mcp        (Workers Bindings)
#   https://observability.mcp.cloudflare.com/mcp   (Observability)
#   https://radar.mcp.cloudflare.com/mcp           (Radar / Internet traffic)
#   https://browser.mcp.cloudflare.com/mcp         (Browser Rendering)
#   ...etc (14 total, see README).
CF_MCP_URL = "https://docs.mcp.cloudflare.com/mcp"

proxy = SecureMCPProxy(
    app_name="cloudflare-docs-proxy",
    upstream_url=CF_MCP_URL,
    upstream_auth={"type": "bearer", "token": token},
)

# Client identity: registers as securemcp-client-cloudflare-macaw-gateway.
client = Client("cloudflare-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# bound.call_tool routes via the client identity, so MACAW shows: client -> proxy.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("search_cloudflare_documentation", {"query": "workers"})
print(f"\nsearch_cloudflare_documentation -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("cloudflare-macaw-proxy")
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
