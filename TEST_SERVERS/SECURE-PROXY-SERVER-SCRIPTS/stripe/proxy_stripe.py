"""
Stripe MCP -> SecureMCPProxy with bind_to_user (npx stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("list_customers") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Run:
    export STRIPE_SECRET_KEY="rk_test_..."   # use a Restricted API Key
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/stripe/proxy_stripe.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("STRIPE_SECRET_KEY")
if not api_key:
    raise ValueError("STRIPE_SECRET_KEY is not set (use a Restricted API Key: rk_test_... or rk_live_...)")

# Stripe MCP takes the key as a CLI flag, not an env var. This means the key
# is visible to anyone with `ps` on this box — use a Restricted API Key with
# minimal scopes, never your full sk_*.
proxy = SecureMCPProxy(
    app_name="stripe-proxy",
    command=["npx", "-y", "@stripe/mcp", f"--api-key={api_key}"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
    },
)

# Client identity: registers as securemcp-client-stripe-macaw-gateway.
client = Client("stripe-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# list_customers with limit=1 is read-only and proves auth + dispatch.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("list_customers", {"limit": 1})
print(f"\nlist_customers -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("stripe-macaw-proxy")
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
