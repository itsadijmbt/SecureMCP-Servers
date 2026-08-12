"""
MACAW client smoke test for alibabacloud-rds-openapi-mcp-server
(post FastMCP -> SecureMCP port).

Usage:
    python3.11 client-test-macaw.py "Alibaba Cloud RDS OPENAPI" rds-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

"""

from macaw_adapters.mcp import Client
import asyncio
import sys


def get_server(client, name):
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
        print('Example: python3 client-test-macaw.py "Alibaba Cloud RDS OPENAPI" rds-test')
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]

    client = Client(client_type)
    server_id = get_server(client, name)
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
    print("RDS-MCP TESTS")
    print("=" * 60)

    print("\n[TEST 1] get_current_time — no credentials needed")
    try:
        result = await client.call_tool("get_current_time", {})
        print(f"  Result: {result}")
        print("  PASS — full dispatch chain works (caller-auth implicit)")
    except Exception as e:
        print(f"  FAILED: {e}")


    print("\n[TEST 2] describe_db_instances — env-var fallback path (no _metadata)")
    try:
        result = await client.call_tool(
            "describe_db_instances",
            {"region_id": "cn-hangzhou"},
        )
        print(f"  Result: {result}")
        print("  Note: success here means env vars ARE set. Both paths are reachable.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:200]}")
        if "credential" in msg.lower() or "access" in msg.lower() or "aksk" in msg.lower():
            print("  PASS — error came from Aliyun SDK (env-var path executed; creds rejected)")
        else:
            print("  Inspect server logs to confirm error origin (handler ran but failed).")

 
    print("\n[TEST 3] describe_db_instances — per-caller path (_metadata with fake AK/SK)")
    try:
        result = await client.call_tool(
            "describe_db_instances",
            {
                "region_id": "cn-hangzhou",
                "_metadata": {
                    "ak": "fake-access-key-from-test",
                    "sk": "fake-secret-from-test",
                },
            },
        )
        print(f"  Result: {result}")
        print("  Note: success would be unexpected with fake creds. Check log.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:200]}")
        if "InvalidAccessKey" in msg or "Forbidden" in msg or "access" in msg.lower():
            print("  PASS — Aliyun rejected the fake creds (bridge transported values OK)")
        else:
            print("  Compare error against TEST 2 — different message means both paths work.")

    
    print("\n[TEST 4] describe_rc_instances — service-account-only tool (env vars only)")
    try:
        result = await client.call_tool(
            "describe_rc_instances",
            {"region_id": "cn-hangzhou"},
        )
        print(f"  Result: {result}")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:200]}")
        print("  Note: This tool ignores _metadata by design. Always uses env vars.")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
