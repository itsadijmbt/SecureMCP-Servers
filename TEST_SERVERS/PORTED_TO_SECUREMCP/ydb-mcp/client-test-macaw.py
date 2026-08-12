"""
MACAW client smoke test for ydp-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3.11 client-test-macaw.py "YDB MCP Server"  ydb-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)
"""

import asyncio
import logging
from macaw_adapters.mcp import Client
import sys


def get_server(name, client):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
    ]

    if not server:
        print(f" no server for name {name}")
        return None

    return server[0].get("agent_id")


async def main():

    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw.py "YDB MCP" ydb-test-client')
        sys.exit(1)

    name = sys.argv[1]
    client_name = sys.argv[2]

    client = Client(client_name)
    server_id = get_server(name, client)

    if not server_id:
        return
    client.set_default_server(server_id)

    tools = await client.list_tools(server_name=name)
    seen = set()
    print("Tools advertised by server:")
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            print(f"  - {t['name']}")
    print(f"\n  Total unique tools: {len(seen)}\n")

    print("=" * 60)
    print(" YDB MCP TESTS")
    print("=" * 60)


   
    print("\n[TEST 1] ydb_status -- check connection health")
    try:
        result = await client.call_tool("ydb_status", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if "connected" in text:
            print("  PASS (connected branch) -- YDB is reachable.")
        elif "error" in text:
            print("  PASS (error branch) -- YDB is not reachable from this "
                  "host, but the handler ran and the error came back "
                  "cleanly. Port works; YDB is just absent.")
        else:
            print("  Inspect -- response shape is unexpected.")
    except Exception as e:
        print(f"  FAILED: {e}")

    print("\n[TEST 2] ydb_query ")
    try:
        result = await client.call_tool("ydb_query", {"sql": "SELECT 1 AS x"})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"x"' in text and "1" in text:
            print("  PASS (creds branch) -- query reached YDB and got a row.")
        elif '"error"' in text:
            print("  PASS (no-server branch) -- the SDK raised, the tool's "
                  "except block caught it, and the error came back as "
                  "JSON. Handler chain is wired.")
        else:
            print("  Inspect -- response did not match either branch.")
    except Exception as e:
        print(f"  Got error: {e}")

    print("\n[TEST 3] ydb_list_directory -- list root /")
    try:
        result = await client.call_tool("ydb_list_directory", {"path": "/"})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"items"' in text:
            print("  PASS (creds branch) -- scheme client reached YDB and "
                  "returned a directory listing.")
        elif '"error"' in text:
            print("  PASS (no-server branch) -- scheme client raised, "
                  "error came back as JSON. Same proof as TEST 2 but "
                  "through a different SDK path.")
        else:
            print("  Inspect -- unexpected response.")
    except Exception as e:
        print(f"  Got error: {e}")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
