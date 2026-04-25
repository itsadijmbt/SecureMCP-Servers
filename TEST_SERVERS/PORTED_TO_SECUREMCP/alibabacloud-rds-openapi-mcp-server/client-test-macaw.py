"""
MACAW client smoke test for alibabacloud-rds-openapi-mcp-server
(post FastMCP -> SecureMCP port).

Usage:
    python3.11 client-test-macaw.py "Alibaba Cloud RDS OPENAPI" rds-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

This script tests TWO independent auth layers:

  ┌──────────────────────────────────────────────────────────────────┐
  │  CALLER AUTH (handled by MACAW automatically)                    │
  │  Question: "Is this really me calling?"                          │
  │  Mechanism: MACAWClient signs every invoke_tool call with this   │
  │             caller's private key. Server-side MACAW Local Agent  │
  │             validates the signature before the handler runs.     │
  │  Tested by: simply being able to invoke any tool. If caller-auth │
  │             fails, you'd never see a response.                   │
  └──────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────┐
  │  UPSTREAM AUTH (handled by THIS server using _metadata or env)   │
  │  Question: "Whose Aliyun account do we use to call Aliyun?"      │
  │  Two paths:                                                      │
  │    A) env-var service account: caller sends no _metadata, server │
  │       falls back to ALIBABA_CLOUD_ACCESS_KEY_ID env var.         │
  │    B) per-caller via _metadata: caller sends                     │
  │       _metadata={"ak":...,"sk":...,"sts":...} and server uses    │
  │       those for the Aliyun call.                                 │
  │  Tested by: comparing the error shapes from the same tool when   │
  │             called with vs without _metadata. Different error    │
  │             patterns prove both code paths reach the upstream    │
  │             call site differently.                               │
  └──────────────────────────────────────────────────────────────────┘
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

    # ----------------------------------------------------------------
    # CALLER AUTH proof (passive): we just registered as
    # `securemcp-client-<client_type>:<hash>`. Every invoke_tool below
    # carries our cryptographic signature. If MACAW didn't trust us,
    # NONE of the calls below would even reach the server's handlers.
    # We're proving caller-auth simply by getting any successful
    # response (or a server-side error rather than a mesh-rejection).
    # ----------------------------------------------------------------

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

    # ----------------------------------------------------------------
    # TEST 1 — get_current_time
    # A tool that doesn't need Aliyun credentials. Proves the chain
    # MACAW signature → mesh dispatch → bridge wrap → handler → return
    # works end-to-end. 
    # ----------------------------------------------------------------
    print("\n[TEST 1] get_current_time — no credentials needed")
    try:
        result = await client.call_tool("get_current_time", {})
        print(f"  Result: {result}")
        print("  PASS — full dispatch chain works (caller-auth implicit)")
    except Exception as e:
        print(f"  FAILED: {e}")
        print("  This is a BLOCKER — the port itself isn't working.")

    # ----------------------------------------------------------------
    # TEST 2 — describe_db_instances WITHOUT _metadata
    # Tests the SERVICE-ACCOUNT (env-var fallback) upstream path.

    # ----------------------------------------------------------------
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

    # ----------------------------------------------------------------
    # TEST 3 — describe_db_instances WITH fake _metadata
 
    # ----------------------------------------------------------------
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

    # ----------------------------------------------------------------
    # TEST 4 — describe_rc_instances (rds_custom toolset)
    
    # ----------------------------------------------------------------
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

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like across the four tests:

  TEST 1 ✓  Full dispatch chain works (port-correctness proof).
  TEST 2 ✗  Failure from Aliyun SDK (env-var path reached, creds empty/invalid).
  TEST 3 ✗  Different failure from Aliyun SDK (bridge path reached, fake creds rejected).
  TEST 4 ✗  Same shape as TEST 2 (both ignore _metadata; both use env vars).

If TESTS 2 and 3 produce DIFFERENT error messages, the SecureMCP port
is verified end-to-end on both upstream-auth paths.

If you want TEST 2 to succeed cleanly, set real Aliyun creds:
    export ALIBABA_CLOUD_ACCESS_KEY_ID=LTAI...
    export ALIBABA_CLOUD_ACCESS_KEY_SECRET=...

If you want TEST 3 to succeed cleanly, replace the fake AK/SK in this
file with your real Aliyun credentials.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
