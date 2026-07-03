"""
DATABRICKS managed MCP  --  stdio MCP front for a SecureMCPProxy (gateway).

WHY THIS EXISTS
    Databricks managed MCP is a HOSTED, Streamable-HTTP server (not self-hostable),
    so the only integration is SecureMCPProxy. But a SecureMCPProxy is a MESH agent --
    a native MCP client (Claude Code / secCC) can't connect to it directly (-32000).



MANAGED-MCP ENDPOINTS (set DATABRICKS_MCP_URL to one; verbatim from Databricks docs):
    SQL                  https://<workspace>/api/2.0/mcp/sql
    Unity Catalog funcs  https://<workspace>/api/2.0/mcp/functions/{catalog}/{schema}/{function}
    Genie                https://<workspace>/api/2.0/mcp/genie                (or /genie/{space_id})
    AI / Vector Search   https://<workspace>/api/2.0/mcp/ai-search/{catalog}/{schema}/{index}
  Auth: a Databricks PAT works as a bearer token. (On-behalf-of OAuth needs the
  per-server scope: sql / unity-catalog / genie / ai-search.)


NOTE: stdout must carry ONLY JSON-RPC. Every diagnostic here goes to stderr. The
stdio front (srv) is NOT optional -- remove it and this becomes a bare mesh server.
Keep the upstream toolset small (managed MCP tool count x ~1.3s registration must
finish inside Claude's 60s initialize window).
"""

import os
import sys
import json
import asyncio
import logging

from macaw_adapters.mcp import SecureMCPProxy, Client

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types


logging.basicConfig(level=logging.INFO, stream=sys.stderr)



token = os.environ.get("DATABRICKS_TOKEN")
if not token:
    raise ValueError("DATABRICKS_TOKEN is not set (workspace PAT)")

DATABRICKS_MCP_URL = os.environ.get("DATABRICKS_MCP_URL")
if not DATABRICKS_MCP_URL:
    raise ValueError(
        "DATABRICKS_MCP_URL is not set -- e.g. https://<workspace>/api/2.0/mcp/sql")

proxy = SecureMCPProxy(
    app_name="databricks-remote-proxy",
    upstream_url=DATABRICKS_MCP_URL,
    upstream_auth={"type": "bearer", "token": token},
)


client = Client("secure-claude-code")
bound = proxy.bind_to_user(client.macaw_client)

_tools = proxy.list_tools()
print(f"[databricks-proxy] proxy live -- {len(_tools)} tools discovered", file=sys.stderr)


srv = Server("databricks-macaw")


@srv.list_tools()
async def _list_tools():
    # proxy tool dicts are {"name","description","schema"} (proxy.py:184-188);
    # MCP wants inputSchema, so map "schema" -> inputSchema.
    return [
        types.Tool(
            name=t["name"],
            description=t.get("description", ""),
            inputSchema=t.get("schema") or {"type": "object"},
        )
        for t in proxy.list_tools()
    ]


@srv.call_tool()
async def _call_tool(name, arguments):
    # Relay into the mesh as the bound identity. A MAPL deny raises here;
    # surface it as text so Claude shows the refusal instead of crashing.
    try:
        result = bound.call_tool(name, arguments or {})
        text = json.dumps(result, default=str) if isinstance(result, (dict, list)) \
            else str(result)
    except Exception as e:
        text = f"MACAW deny / upstream error: {e}"
    return [types.TextContent(type="text", text=text)]


async def _serve():
    print("[databricks-proxy] serving stdio MCP -> relaying to databricks-remote-proxy",
          file=sys.stderr)
    async with stdio_server() as (rd, wr):
        await srv.run(rd, wr, srv.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(_serve())
