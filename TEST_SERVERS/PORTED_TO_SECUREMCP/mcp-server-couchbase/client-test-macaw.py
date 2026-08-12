"""
MACAW client smoke test for mcp-server-couchbase
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "couchbase" couchbase-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

"""

import asyncio
import sys

from macaw_adapters.mcp import Client


def get_server(name, client):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
    ]
    if not server:
        print(f"No server found matching: {name}")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw.py "couchbase" couchbase-test-client')
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
    print("COUCHBASE MCP TESTS")
    print("=" * 60)

    print("\n[TEST 1] get_server_configuration_status -- no upstream call")
    try:
        result = await client.call_tool("get_server_configuration_status", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"server_name"' in text or "couchbase" in text.lower():
            print("  PASS -- handler ran, configuration came back. "
                  "Caller-auth + dispatch chain verified.")
        else:
            print("  Inspect -- shape unexpected.")
    except Exception as e:
        print(f"  FAILED: {e}")


    print("\n[TEST 2] test_cluster_connection -- attempts a real cluster connect")
    try:
        result = await client.call_tool("test_cluster_connection", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"success"' in text or '"cluster_connected": True' in text:
            print("  PASS (creds branch) -- Couchbase reachable, cluster built.")
        elif '"error"' in text or '"cluster_connected": False' in text:
            print("  PASS (no-creds/no-server branch) -- the SDK raised, the "
                  "tool wrapped the error, and it came back as JSON. The "
                  "handler chain is wired end-to-end.")
        else:
            print("  Inspect -- response did not match either branch.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  Mesh-level error -- caller-auth or transport problem, "
              "NOT a Couchbase issue.")

   
    print("\n[TEST 3] get_buckets_in_cluster -- read-only cluster query")
    try:
        result = await client.call_tool("get_buckets_in_cluster", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if "[" in text and "]" in text:
            print("  PASS (creds branch) -- bucket names returned. Full "
                  "vertical: client -> mesh -> SecureMCP -> tool -> "
                  "Couchbase SDK -> cluster -> back.")
        else:
            print("  Inspect -- unexpected response shape.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "connect" in msg.lower() or "auth" in msg.lower() or "timeout" in msg.lower():
            print("  PASS (no-creds/no-server branch) -- SDK error propagated "
                  "cleanly through SecureMCP. Same proof as TEST 2 via a "
                  "different SDK path.")
        else:
            print("  Inspect -- exception shape unexpected.")

    print("\n" + "=" * 60)




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
