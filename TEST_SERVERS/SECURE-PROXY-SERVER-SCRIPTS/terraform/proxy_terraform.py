"""
Terraform MCP -> SecureMCPProxy with bind_to_user (Docker stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("search_providers") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

The default toolset hits only the public Terraform Registry, which needs no
token. Set TFE_TOKEN / TFE_ADDRESS only if you want HCP Terraform or
Terraform Enterprise workspace tools.

Run:
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/terraform/proxy_terraform.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

upstream_env = {"PATH": os.environ["PATH"]}
for k in ("TFE_TOKEN", "TFE_ADDRESS"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

docker_args = ["docker", "run", "--rm", "-i"]
if upstream_env.get("TFE_TOKEN"):
    docker_args += ["-e", "TFE_TOKEN"]
if upstream_env.get("TFE_ADDRESS"):
    docker_args += ["-e", "TFE_ADDRESS"]
docker_args += ["hashicorp/terraform-mcp-server:0.5.2"]

proxy = SecureMCPProxy(
    app_name="terraform-proxy",
    command=docker_args,
    env=upstream_env,
)

# Client identity: registers as securemcp-client-terraform-macaw-gateway.
client = Client("terraform-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# search_providers hits the public registry, no token needed.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("search_providers", {"provider_name": "aws"})
print(f"\nsearch_providers -> {str(result)[:300]}", file=sys.stderr)

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

srv = Server("terraform-macaw-proxy")
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
