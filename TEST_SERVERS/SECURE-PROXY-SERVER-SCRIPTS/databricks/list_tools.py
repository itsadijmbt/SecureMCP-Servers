"""
List the tools (names + param schemas) a Databricks managed MCP endpoint exposes.

Raw MCP client -- NO MACAW, no mesh -- just to harvest the exact tool surface for
red-team policy drafting (denied_parameters / allowed_values need real param names).

Run:
    export DATABRICKS_TOKEN="dapi..."
    export DATABRICKS_MCP_URL="https://<workspace>/api/2.0/mcp/sql"
    python list_tools.py
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    url = os.environ.get("DATABRICKS_MCP_URL")
    token = os.environ.get("TOKEN")
    if not url or not token:
        sys.exit("set DATABRICKS_MCP_URL and DATABRICKS_TOKEN")

    async with streamablehttp_client(url, headers={"Authorization": f"Bearer {token}"}) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            resp = await s.list_tools()
            tools = resp.tools
            print(f"\n=== {len(tools)} tools at {url} ===\n")
            for t in tools:
                print(f"### {t.name}")
                if t.description:
                    print(f"  {t.description.strip()[:200]}")
                schema = t.inputSchema or {}
                props = schema.get("properties", {}) or {}
                required = set(schema.get("required", []) or [])
                if props:
                    print("  params:")
                    for name, d in props.items():
                        req = "  [required]" if name in required else ""
                        typ = d.get("type", d.get("anyOf", "?"))
                        desc = (d.get("description", "") or "")[:70]
                        print(f"    - {name}: {typ}{req}  {desc}")
                else:
                    print("  params: (none / free-form)")
                print()

            # Machine-readable dump for the red team (exact schemas).
            dump = [{"name": t.name, "description": t.description,
                     "inputSchema": t.inputSchema} for t in tools]
            with open("databricks_tools_sql.json", "w") as f:
                json.dump(dump, f, indent=2)
            print(">>> full schemas written to databricks_tools.json")


if __name__ == "__main__":
    asyncio.run(main())
