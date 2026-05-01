"""
dbt MCP -> SecureMCPProxy with bind_to_user (uvx stdio upstream).

Wraps the official `dbt-mcp` Python package (run via uvx) with MACAW. The
upstream exposes ~50 tools across SQL, Semantic Layer, Discovery, dbt CLI,
Admin API, Codegen, LSP, Product Docs, and Server Metadata categories.
Tool groups that lack their required env config are auto-disabled by the
upstream — Server Metadata + Product Docs work with no config.

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("get_mcp_server_version") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Run:
    # Optional — only set what you actually have, leave the rest unset:
    # export DBT_HOST="cloud.getdbt.com"
    # export DBT_TOKEN="dbtu_..."
    # export DBT_PROD_ENV_ID="123456"
    # export DBT_DEV_ENV_ID="123457"
    # export DBT_USER_ID="..."
    # export DBT_PROJECT_DIR="/path/to/your/dbt/project"
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/dbt/proxy_dbt.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# Forward whichever dbt configs the user has set; the upstream disables any
# tool group whose config is absent. Smoke target works without any of these.
upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],
}
for k in (
    "DBT_HOST",
    "DBT_TOKEN",
    "DBT_PROD_ENV_ID",
    "DBT_DEV_ENV_ID",
    "DBT_USER_ID",
    "DBT_ACCOUNT_ID",
    "DBT_PROJECT_DIR",
    "DBT_PATH",
    "MULTICELL_ACCOUNT_PREFIX",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="dbt-proxy",
    command=["uvx", "dbt-mcp"],
    env=upstream_env,
)

# Client identity: registers as securemcp-client-dbt-macaw-gateway.
client = Client("dbt-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# get_mcp_server_version needs no upstream config — proves wrap, dispatch,
# and MACAW gating without depending on dbt Cloud / a local project.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("get_mcp_server_version", {})
print(f"\nget_mcp_server_version -> {str(result)[:300]}", file=sys.stderr)

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
# srv = Server("dbt-macaw-proxy")
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
