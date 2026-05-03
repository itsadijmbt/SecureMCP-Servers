"""
Chrome DevTools MCP -> SecureMCPProxy with bind_to_user (npx stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("list_pages") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Chrome DevTools MCP (chrome-devtools-mcp) drives a real Chrome instance
via the Chrome DevTools Protocol. No API key, no token — auth is "you
own the browser process". Same wrap shape as airtable / notion / postman:
npx stdio with PATH + HOME forwarded.

Defaults baked into the spawn:
  --headless   no GUI window (safe when spawned by Gemini in a non-desktop
               context; flip off if you want a visible browser).
  --isolated   ephemeral Chrome profile per session, auto-cleaned. Keeps
               smoke tests deterministic and free of cookie pollution.

Run:
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/chrome-devtools/proxy_chrome_devtools.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

proxy = SecureMCPProxy(
    app_name="chrome-devtools-proxy",
    command=[
        "npx", "-y", "chrome-devtools-mcp@latest",
        "--headless",
        "--isolated",
    ],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],   # for ~/.cache/chrome-devtools-mcp
    },
)

# Client identity: registers as securemcp-client-chrome-devtools-macaw-gateway.
client = Client("chrome-devtools-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# list_pages: zero args, returns currently open tabs. Will be ~empty on a
# fresh isolated headless profile, but a 200-shape response proves the
# whole chain works: MACAW -> chrome-devtools-mcp -> Chrome DevTools
# Protocol -> back.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("list_pages", {})
print(f"\nlist_pages -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("chrome-devtools-macaw-proxy")
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
