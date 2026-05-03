"""
Snyk MCP -> SecureMCPProxy with bind_to_user (npx stdio upstream).

Two tests, one file. Calls go: client identity -> server identity -> upstream,
so MACAW renders a two-node graph (client ──> server) for both tests.

  Test 1 (active by default):  one bound.call_tool("snyk_version") then exit.
  Test 2 (uncomment block):    stdio MCP gateway for Gemini/Claude CLI.

Snyk's MCP is part of the official Snyk CLI (v1.1298.0+), invoked as
`snyk mcp -t stdio`. Same wrap shape as airtable / notion / postman:
npx stdio with PATH + HOME forwarded, plus SNYK_TOKEN for auth.

Tools exposed (read-mostly, scanning surface):
  - snyk_sca_scan        (open source dependency vulnerabilities)
  - snyk_code_scan       (proprietary code SAST)
  - snyk_iac_scan        (Infrastructure as Code)
  - snyk_container_scan  (container images)
  - snyk_sbom_scan       (existing SBOM analysis)
  - snyk_aibom           (AI Bill of Materials)
  - snyk_trust           (trust a folder before scanning)
  - snyk_auth            (login — usually automatic)
  - snyk_logout          (terminate session)
  - snyk_version         (zero-arg smoke target)

Run:
    export SNYK_TOKEN="..."
    /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \\
        TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/snyk/proxy_snyk.py
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("SNYK_TOKEN")
if not token:
    raise ValueError(
        "SNYK_TOKEN is not set. Get one at https://app.snyk.io/account "
        "(Account Settings -> API Token)."
    )

upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],
    "SNYK_TOKEN": token,
}
# Optional — multi-org Snyk accounts need this to scope correctly.
if os.environ.get("SNYK_CFG_ORG"):
    upstream_env["SNYK_CFG_ORG"] = os.environ["SNYK_CFG_ORG"]

proxy = SecureMCPProxy(
    app_name="snyk-proxy",
    command=["npx", "-y", "snyk@latest", "mcp", "-t", "stdio"],
    env=upstream_env,
)

# Client identity: registers as securemcp-client-snyk-macaw-gateway.
client = Client("snyk-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 — smoke check (default).
# snyk_version is zero-arg, no scope-gated, no scan side effects. Proves
# auth handshake + dispatch end-to-end without burning Snyk scan quota.
# ============================================================================
tools = proxy.list_tools()
print(f"tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

result = bound.call_tool("snyk_version", {})
print(f"\nsnyk_version -> {str(result)[:300]}", file=sys.stderr)

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
# srv = Server("snyk-macaw-proxy")
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
