"""
Prisma AIRS MCP Relay -> SecureMCPProxy with bind_to_user (uvx stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("fetch") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Architecture (two security relays in series):

  Gemini -> MACAW SecureMCPProxy -> pan-mcp-relay -> downstream MCP servers
                                    (Prisma AIRS scans
                                     descriptions, params,
                                     responses)

The downstream servers are configured in mcp-relay.yaml in this folder. The
default config bundles `mcp-server-fetch` so the relay has at least one
tool to register and scan against.

Run:
    export PRISMA_AIRS_API_KEY="..."
    export PRISMA_AIRS_AI_PROFILE="your-profile-name-or-id"
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/pan-mcp-relay/proxy_pan_mcp_relay.py
"""

import os
import sys
import logging
from pathlib import Path
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("PRISMA_AIRS_API_KEY")
ai_profile = os.environ.get("PRISMA_AIRS_AI_PROFILE")
if not api_key or not ai_profile:
    raise ValueError("Set PRISMA_AIRS_API_KEY and PRISMA_AIRS_AI_PROFILE")

config_file = str(Path(__file__).parent / "mcp-relay.yaml")

proxy = SecureMCPProxy(
    app_name="pan-mcp-relay-proxy",
    command=["uvx", "pan-mcp-relay@latest", "--config-file", config_file],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "PRISMA_AIRS_API_KEY": api_key,
        "PRISMA_AIRS_AI_PROFILE": ai_profile,
    },
)

# Client identity: registers as securemcp-client-pan-mcp-relay-macaw-gateway.
client = Client("pan-mcp-relay-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# Relay registers downstream tools (here: `fetch`). Calling `fetch` exercises
# the full chain: MACAW -> AIRS scan (descriptions+params) -> mcp-server-fetch
# -> example.com response -> AIRS scan (response) -> back to MACAW.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("fetch", {"url": "https://example.com"})
print(f"\nfetch -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("pan-mcp-relay-macaw-proxy")
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
