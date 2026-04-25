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
        print("Usage: python3 client-test-macaw.py <server_filter_name> <client_name>")
        print("Example: python3 client-test-macaw.py Iceberg iceberg-test-client")
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]

    client = Client(client_type)
    server_id = get_server(client, name)

    if not server_id:
        return

    client.set_default_server(server_id)

    # List all tools registered on the server
    tools = await client.list_tools(server_name=name)
    seen = set()
    print("Tools advertised by server:")
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            print(f" - {t['name']}")

    print("\n" + "=" * 50)
    print("ICEBERG-MCP TOOL TESTS")
    print("=" * 50)

    # ----------------------------------------------------------------
    # TEST 1 — get_schema (no args)
    # Easiest possible test. Calls `SHOW TABLES` against Impala.
    # If Impala is reachable, returns a JSON list of table names.
    # If not, returns "Error: ..." but the call still completes
    # (handler runs, exception caught inside impala_tools.get_schema).
    # ----------------------------------------------------------------
    print("\n[TEST 1] get_schema — list tables in current Impala database")
    try:
        result = await client.call_tool("get_schema", {})
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Failed: {e}")

    # ----------------------------------------------------------------
    # TEST 2 — execute_query with `SHOW TABLES`
    # Verifies the SQL path works for read-only commands.
    # `SHOW` is in the readonly_prefixes allowlist (impala_tools.py:47).
    # ----------------------------------------------------------------
    print("\n[TEST 2] execute_query — SHOW TABLES")
    try:
        result = await client.call_tool("execute_query", {"query": "SHOW TABLES"})
        preview = str(result)[:300].replace("\n", " ")
        print(f"  Result: {preview}...")
    except Exception as e:
        print(f"  Failed: {e}")

    # ----------------------------------------------------------------
    # TEST 3 — execute_query with a SELECT
    # Simplest valid SELECT. Doesn't depend on any specific table
    # existing in the cluster.
    # ----------------------------------------------------------------
    print("\n[TEST 3] execute_query — SELECT 1")
    try:
        result = await client.call_tool("execute_query", {"query": "SELECT 1"})
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Failed: {e}")

    # ----------------------------------------------------------------
    # TEST 4 — Read-only enforcement
    # Sending a write query should return the readonly rejection
    # message ("Only read-only queries are allowed.") because
    # impala_tools.execute_query checks the first word against an
    # allowlist (select / show / describe / with).
    # This proves the upstream's safety check still runs under SecureMCP.
    # ----------------------------------------------------------------
    print("\n[TEST 4] execute_query — write attempt (should be rejected)")
    try:
        result = await client.call_tool(
            "execute_query",
            {"query": "INSERT INTO foo VALUES (1)"},
        )
        print(f"  Result: {result}")
        # Expected: {"result": "Only read-only queries are allowed."}
        if "read-only" in str(result).lower():
            print("  PASS: read-only filter is intact")
        else:
            print("  WARN: write query was not rejected — check impala_tools filter")
    except Exception as e:
        print(f"  Failed: {e}")

    print("\nAll tests done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
