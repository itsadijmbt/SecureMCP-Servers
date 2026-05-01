"""
Salesforce Agentforce MCP -> SecureMCPProxy with bind_to_user (stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("agentforce_chat") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

The agentforce-mcp-server in TEST_SERVERS/OFFICIAL_PY_INTE_SECUREMCP/ runs as
a FastMCP stdio server. Our proxy spawns it directly and pipes stdio.

Required env (passed through to the upstream subprocess):
  SALESFORCE_SCRT_URL, SALESFORCE_ORG_ID, SALESFORCE_ES_DEVELOPER_NAME,
  JWT_SECRET (and optionally SALESFORCE_CAPABILITIES_VERSION, etc.)

Run:
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/salesforce-agentforce/proxy_salesforce.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

AGENTFORCE_REPO = os.environ.get(
    "AGENTFORCE_REPO",
    "/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/OFFICIAL_PY_INTE_SECUREMCP/agentforce-mcp-server",
)
AGENTFORCE_PY = os.environ.get(
    "AGENTFORCE_PY",
    f"{AGENTFORCE_REPO}/.venv/bin/python",
)

upstream_env = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"]}
for k in ("SALESFORCE_SCRT_URL", "SALESFORCE_ORG_ID",
          "SALESFORCE_ES_DEVELOPER_NAME", "SALESFORCE_CAPABILITIES_VERSION",
          "SALESFORCE_CLIENT_ID", "SALESFORCE_CLIENT_SECRET",
          "JWT_SECRET", "ACCESS_TOKEN_EXPIRATION_HOURS", "SERVER_URL"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

for required in ("SALESFORCE_SCRT_URL", "SALESFORCE_ORG_ID",
                 "SALESFORCE_ES_DEVELOPER_NAME", "JWT_SECRET"):
    if required not in upstream_env:
        raise ValueError(f"{required} is not set")

proxy = SecureMCPProxy(
    app_name="salesforce-agentforce-proxy",
    command=[AGENTFORCE_PY, f"{AGENTFORCE_REPO}/server.py"],
    env=upstream_env,
)

# Client identity: registers as securemcp-client-salesforce-agentforce-macaw-gateway.
client = Client("salesforce-agentforce-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# `agentforce_chat` is the primary tool; "Hello" round-trips through the
# Salesforce Agentforce session if the upstream server is configured. If the
# upstream lacks Salesforce env vars, the call returns an error from the
# upstream — that still proves the wrap chain works (it just shows that the
# upstream server itself isn't configured, which is a separate problem).
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("agentforce_chat", {"message": "Hello"})
print(f"\nagentforce_chat -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("salesforce-agentforce-macaw-proxy")
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
