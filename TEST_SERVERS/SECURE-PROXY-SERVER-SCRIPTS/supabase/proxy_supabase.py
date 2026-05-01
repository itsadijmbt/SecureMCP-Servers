"""
Supabase MCP -> SecureMCPProxy with bind_to_user (via mcp-remote).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("list_projects") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Supabase MCP is OAuth 2.1-protected with proper DCR — mcp-remote handles
the OAuth dance and exposes the remote upstream over stdio; SecureMCPProxy
wraps that.

Defaults bake in Supabase's security recommendations:
  - read_only=true        (read-only Postgres user, no mutating tools)
  - project_ref optional  (set SUPABASE_PROJECT_REF to scope to one project;
                           when set, list_projects is unavailable — swap the
                           Test 1 smoke call to list_tables, args {})

First run opens a browser for Supabase login. Token cached in ~/.mcp-auth/.

Run:
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/supabase/proxy_supabase.py
"""

import os
import sys
import logging
from urllib.parse import urlencode
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

params = {"read_only": "true"}
if os.environ.get("SUPABASE_PROJECT_REF"):
    params["project_ref"] = os.environ["SUPABASE_PROJECT_REF"]
upstream_url = f"https://mcp.supabase.com/mcp?{urlencode(params)}"

proxy = SecureMCPProxy(
    app_name="supabase-proxy",
    command=["npx", "-y", "mcp-remote", upstream_url],
    env={"PATH": os.environ["PATH"], "HOME": os.environ["HOME"]},
)

# Client identity: registers as securemcp-client-supabase-macaw-gateway.
client = Client("supabase-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# list_projects works in unscoped mode. If SUPABASE_PROJECT_REF is set,
# replace this call with list_tables, args {}.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

smoke_tool = "list_tables" if os.environ.get("SUPABASE_PROJECT_REF") else "list_projects"
result = bound.call_tool(smoke_tool, {})
print(f"\n{smoke_tool} -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("supabase-macaw-proxy")
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
