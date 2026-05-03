"""
Grafana MCP -> SecureMCPProxy with bind_to_user (Docker stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("list_datasources") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Run:
    export GRAFANA_URL="https://yourorg.grafana.net"   # or http://localhost:3000
    export GRAFANA_SERVICE_ACCOUNT_TOKEN="glsa_..."
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/grafana/proxy_grafana.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

grafana_url = os.environ.get("GRAFANA_URL")
token = os.environ.get("GRAFANA_SERVICE_ACCOUNT_TOKEN")
if not grafana_url or not token:
    raise ValueError(
        "Set GRAFANA_URL (e.g. http://localhost:3000) and "
        "GRAFANA_SERVICE_ACCOUNT_TOKEN (glsa_...)"
    )

# The Docker image defaults to SSE mode; -t stdio is required for MCP-over-stdio.
# --network=host lets the container reach a localhost Grafana on the host.
proxy = SecureMCPProxy(
    app_name="grafana-proxy",
    command=[
        "docker", "run", "--rm", "-i", "--network=host",
        "-e", "GRAFANA_URL",
        "-e", "GRAFANA_SERVICE_ACCOUNT_TOKEN",
        "grafana/mcp-grafana", "-t", "stdio",
    ],
    env={
        "PATH": os.environ["PATH"],
        "GRAFANA_URL": grafana_url,
        "GRAFANA_SERVICE_ACCOUNT_TOKEN": token,
    },
)

# Client identity: registers as securemcp-client-grafana-macaw-gateway.
client = Client("grafana-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# list_datasources is read-only and proves auth + dispatch end-to-end.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("list_datasources", {})
print(f"\nlist_datasources -> {str(result)[:300]}", file=sys.stderr)

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
# srv = Server("grafana-macaw-proxy")
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
