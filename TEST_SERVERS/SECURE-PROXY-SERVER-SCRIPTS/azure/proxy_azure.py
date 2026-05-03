"""
Azure MCP -> SecureMCPProxy with bind_to_user (npx stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("subscription_list") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Auth: Azure MCP uses the official Azure Identity SDK. Two paths:

  A. Azure CLI session — run `az login` once, then this script picks up
     the cached creds from ~/.azure/. Default for human dev boxes.

  B. Service principal — set AZURE_TENANT_ID + AZURE_CLIENT_ID +
     AZURE_CLIENT_SECRET in env. Default for CI / headless agents.

The script forwards both: HOME so az-login creds work, and the SP env
vars when present. Whichever the SDK finds first wins.

If `subscription_list` isn't in the tool list that prints, swap the
smoke target on line 50 for one of the names you see (Azure MCP tool
names sometimes carry an `azmcp_` prefix depending on version).

Run:
    az login                                           # one-time
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/azure/proxy_azure.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],   # for az-login creds at ~/.azure/
}
for k in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET",
          "AZURE_SUBSCRIPTION_ID"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="azure-proxy",
    command=["npx", "-y", "@azure/mcp@latest", "server", "start"],
    env=upstream_env,
)

# Client identity: registers as securemcp-client-azure-macaw-gateway.
client = Client("azure-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# subscription_list / azmcp_subscription_list returns the user's accessible
# Azure subscriptions. No args, read-only. Swap the name if it's not in the
# printed tools list — Azure MCP changes tool names between versions.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("subscription_list", {})
print(f"\nsubscription_list -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("azure-macaw-proxy")
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
