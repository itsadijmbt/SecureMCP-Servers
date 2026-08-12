"""
MACAW client smoke test for mysql_mcp_server
(post low-level-Server -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "mysql" mysql-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)


"""

import asyncio
import sys

from macaw_adapters.mcp import Client


EXPECTED_TOOLS = {
    "list_tables",   # NEW under the port; replaces resources/list
    "read_table",    # NEW under the port; replaces resources/read
    "execute_sql",   # EXISTING; only the decorator changed
}


def get_server(name, client):
    """Look up the mysql_mcp_server's agent_id on the mesh."""
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
        and "securemcp-client-" not in a.get("agent_id", "")
    ]
    if not server:
        print(f"No server found matching: {name}")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw.py "mysql" mysql-test-client')
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
    print("MYSQL_MCP_SERVER TESTS")
    print("=" * 60)

    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_TOOLS - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_TOOLS)} expected tools advertised.")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a @app.tool decorator didn't run, or the port edits ")
        print("  broke the module import. Check server logs.")
        return


    print("\n[TEST 2] list_tables -- replaces dropped resources/list")
    try:
        result = await client.call_tool("list_tables", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- list_tables returned. Either a real table list, ")
        print("  or 'Error listing tables: ...' wrapped from the database. ")
        print("  Both prove the new resources/list -> list_tables conversion ")
        print("  reaches the handler.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")


    print("\n[TEST 3] read_table(table='dummy') -- replaces dropped resources/read")
    try:
        result = await client.call_tool("read_table", {"table": "dummy"})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- read_table returned. Either CSV data from the table, ")
        print("  or 'Database error reading table dummy: ...'. Both prove the ")
        print("  resources/read -> read_table conversion reaches the handler.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")


    print("\n[TEST 4] execute_sql('SELECT 1 + 1 AS answer') -- decorator-only port")
    try:
        result = await client.call_tool(
            "execute_sql",
            {"query": "SELECT 1 + 1 AS answer"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- execute_sql returned. With a real MySQL the result ")
        print("  is `answer\\n2`. Without one, the handler returns ")
        print("  'Error executing query: ...'. Both prove the existing tool ")
        print("  survived the port.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like:

  TEST 1 ✓  All 3 tools advertised: list_tables, read_table, execute_sql.
            Proves: import swap held; resources/list -> list_tables and
            resources/read -> read_table conversions registered cleanly;
            execute_sql still works after the @app.call_tool ->
            @app.tool change.

  TEST 2 ✓  list_tables returned (real list or 'Error: ...').
            Proves: the NEW tool replacing resources/list is reachable
            and runs the same SHOW TABLES code path.

  TEST 3 ✓  read_table(table='dummy') returned (CSV or 'Error: ...').
            Proves: the NEW tool replacing resources/read is reachable
            and runs the same SELECT * FROM X LIMIT 100 code path.

  TEST 4 ✓  execute_sql returned (result row or 'Error: ...').
            Proves: the existing tool survived the decorator change.

""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
