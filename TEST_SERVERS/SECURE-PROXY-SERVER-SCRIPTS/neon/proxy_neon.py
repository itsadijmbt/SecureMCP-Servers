"""
Neon MCP -> SecureMCPProxy with bind_to_user (remote HTTP upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("list_projects") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Neon's remote MCP at https://mcp.neon.tech/mcp accepts API key auth via
bearer header — same shape as the GitHub remote proxy. No mcp-remote and
no OAuth dance.

Run:
    export NEON_API_KEY="napi_..."
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/neon/proxy_neon.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("NEON_API_KEY")
if not api_key:
    raise ValueError("NEON_API_KEY is not set (create at https://console.neon.tech/app/settings/api-keys)")

# Append ?readonly=true to the URL if you want to restrict to read-only tools
# (no project create/delete, no migrations, no run_sql writes). Useful for
# locking the proxy down to safe ops without touching MAPL policy.
proxy = SecureMCPProxy(
    app_name="neon-proxy",
    upstream_url="https://mcp.neon.tech/mcp",
    upstream_auth={"type": "bearer", "token": api_key},
)

# Client identity: registers as securemcp-client-neon-macaw-gateway.
client = Client("neon-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# list_projects is read-only and proves auth + dispatch end-to-end.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("list_projects", {})
print(f"\nlist_projects -> {str(result)[:300]}", file=sys.stderr)

# ============================================================================
# Test 2 — stdio MCP gateway (uncomment block below to enable).
# Re-publishes upstream tools as a stdio MCP server. Each tools/call from
# Gemini/Claude CLI is forwarded via bound -> same 2-node graph as Test 1.
# ============================================================================
# import asyncio
# import json
# from mcp.server import Server
# from mcp.server.stdio import stdio_server
# import mcp.types as types
#
# srv = Server("neon-macaw-proxy")
# tool_objs = [
#     types.Tool(
#         name=t["name"],
#         description=t.get("description", ""),
#         inputSchema=t.get("schema") or {"type": "object"},
#     )
#     for t in proxy.list_tools()
# ]
#
# @srv.list_tools()
# async def _list():
#     return tool_objs
#
# @srv.call_tool()
# async def _call(name, args):
#     r = bound.call_tool(name, args or {})
#     return [types.TextContent(type="text", text=json.dumps(r, default=str))]
#
# async def _main():
#     async with stdio_server() as (rd, wr):
#         await srv.run(rd, wr, srv.create_initialization_options())
#
# asyncio.run(_main())
