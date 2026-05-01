"""
MongoDB MCP -> SecureMCPProxy with bind_to_user (Docker stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("list-databases") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Run:
    export MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017"
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/mongodb/proxy_mongodb.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)


class TolerantSecureMCPProxy(SecureMCPProxy):
    # MongoDB MCP server emits notifications/resources/updated for debug://mongodb
    # right after tools/list, racing stdio_client cleanup -> BrokenResourceError.
    # If tools were already discovered, the connection is functional.
    def _connect_and_discover(self):
        try:
            super()._connect_and_discover()
        except ConnectionError:
            if not self.tool_schemas:
                raise
            self._connected = True
            logging.getLogger(__name__).warning(
                "Discovered %d tools despite cleanup race", len(self.tool_schemas))


upstream_env = {"PATH": os.environ["PATH"]}
for k in ("MDB_MCP_CONNECTION_STRING", "MDB_MCP_API_CLIENT_ID", "MDB_MCP_API_CLIENT_SECRET"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]
if "MDB_MCP_CONNECTION_STRING" not in upstream_env and "MDB_MCP_API_CLIENT_ID" not in upstream_env:
    raise ValueError("Set MDB_MCP_CONNECTION_STRING or MDB_MCP_API_CLIENT_ID+MDB_MCP_API_CLIENT_SECRET")

proxy = TolerantSecureMCPProxy(
    app_name="mongodb-proxy",
    command=[
        "docker", "run", "--rm", "-i", "--network=host",
        "-e", "MDB_MCP_CONNECTION_STRING",
        "-e", "MDB_MCP_API_CLIENT_ID",
        "-e", "MDB_MCP_API_CLIENT_SECRET",
        "-e", "MDB_MCP_READ_ONLY=true",
        "-e", "MDB_MCP_LOGGERS=stderr",
        "mongodb/mongodb-mcp-server:latest",
    ],
    env=upstream_env,
)

# Client identity: registers as securemcp-client-mongodb-macaw-gateway.
client = Client("mongodb-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# bound.call_tool routes via the client identity, so MACAW shows: client -> proxy.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("list-databases", {})
print(f"\nlist-databases -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("mongodb-macaw-proxy")
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
