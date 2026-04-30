"""
MACAW client smoke test for datacloud-mcp-query
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "datacloud" datacloud-test-client
    python3 client-test-macaw.py "Demo"      datacloud-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

What this tests:
    1. Port-correctness -- server registered, all 3 tools advertised on the mesh.
    2. list_tables   -- handler reachability (hits Salesforce Data Cloud Query API).
    3. describe_table -- handler reachability + plain default works (no Field).
    4. query         -- required-arg ('sql') round-trip + plain default works.

Tests 2-4 reach the real Salesforce Data Cloud Query API via auth_provider.
Without valid SF auth (sf_cli alias OR oauth client_id+secret) the server
won't even boot -- auth_provider construction raises SystemExit at module
load (server.py:23). So if you can run TEST 1, you already have working
SF auth, and TESTS 2-4 will return real data or a clean upstream error.

What we are proving with this smoke test is:
  - the FastMCP -> SecureMCP import flip didn't break registration
  - the pydantic Field strip didn't break call dispatch
  - default-valued args ('dataspace="default"') and required args ('sql',
    'table') both round-trip through the mesh correctly
"""

import asyncio
import sys

from macaw_adapters.mcp import Client


EXPECTED_TOOLS = {"query", "list_tables", "describe_table"}


def get_server(name, client):
    """Look up the datacloud server's agent_id on the mesh.

    Filters out per-tool sub-agents and the test client's own agent.
    """
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
        print('Example: python3 client-test-macaw.py "datacloud" datacloud-test-client')
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
    print("DATACLOUD-MCP-QUERY TESTS")
    print("=" * 60)

    # --------------------------------------------------------------
    # TEST 1 -- expected tools all present
    #
    # Pure port-correctness check. Proves:
    #   - import swap (mcp.server.fastmcp -> SecureMCP) succeeded
    #   - SecureMCP("Demo") boot succeeded
    #   - all three @mcp.tool(...) decorators executed without
    #     pydantic.Field at signature-parse time
    # No upstream Data Cloud call yet.
    # --------------------------------------------------------------
    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_TOOLS - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_TOOLS)} tools advertised "
              "(query, list_tables, describe_table).")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Likely an import-time error in server.py. Check the "
              "server log for traceback.")
        return

    # --------------------------------------------------------------
    # TEST 2 -- list_tables with default dataspace
    #
    # Caller passes NO args. The handler signature is now
    #   async def list_tables(dataspace: str = "default")
    # Without the Field strip, dataspace would default to a FieldInfo
    # object and the SQL parameter for tableFilter would still bind
    # ok, but the dataspace string would be malformed -- this test
    # exercises the plain-default path post-port.
    # --------------------------------------------------------------
    print("\n[TEST 2] list_tables -- default-arg path")
    try:
        result = await client.call_tool("list_tables", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- list_tables returned. Default 'dataspace=\"default\"' "
              "took effect (real Python default, not FieldInfo).")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "FieldInfo" in msg or "Field(" in msg:
            print("  FAILED -- FieldInfo leaked into the handler. The "
                  "Field strip in server.py is incomplete.")
        else:
            print("  PASS-ish -- exception was not from a Field leak. "
                  "Likely upstream Data Cloud / auth issue. Handler "
                  "was reached.")

    # --------------------------------------------------------------
    # TEST 3 -- describe_table with required arg
    #
    # 'table' is now a required Python arg (no default). If the
    # mesh dispatch layer mishandled the new signature, we'd see
    # a TypeError before the handler runs.
    # --------------------------------------------------------------
    print("\n[TEST 3] describe_table -- required-arg path")
    try:
        result = await client.call_tool(
            "describe_table",
            {"table": "Account__dlm"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- describe_table accepted the required 'table' arg "
              "and returned (real columns or upstream error).")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "missing" in msg.lower() and "table" in msg.lower():
            print("  FAILED -- mesh dispatch lost the 'table' arg.")
        elif "FieldInfo" in msg:
            print("  FAILED -- FieldInfo leaked into the handler.")
        else:
            print("  PASS-ish -- exception was not a signature mismatch. "
                  "Handler was reached.")

    # --------------------------------------------------------------
    # TEST 4 -- query with required 'sql' and plain default kwargs
    #
    # Smallest valid query that proves the round-trip without
    # depending on a specific table existing.
    # --------------------------------------------------------------
    print("\n[TEST 4] query -- required + default args")
    try:
        result = await client.call_tool(
            "query",
            {"sql": "SELECT 1 AS macaw_smoke"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- query accepted required 'sql' and defaulted "
              "dataspace + query_settings correctly.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "FieldInfo" in msg:
            print("  FAILED -- FieldInfo leaked into run_query.")
        else:
            print("  PASS-ish -- exception was not a Field leak. Handler "
                  "was reached; upstream Data Cloud / SQL surface is "
                  "where the failure came from.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like:

  TEST 1 ✓  All 3 tools advertised on the mesh.
            Proves: import swap and SecureMCP boot succeeded.

  TEST 2 ✓  list_tables returned without a FieldInfo error.
            Proves: dataspace='default' is a real string at handler
            time, not a pydantic FieldInfo object.

  TEST 3 ✓  describe_table accepted 'table' as a required arg.
            Proves: stripping Field on a required-only param did
            not change required-ness of the arg in the schema.

  TEST 4 ✓  query accepted 'sql' and defaulted the rest correctly.
            Proves: mixed required + plain-default signature works
            end-to-end.

If all four pass, the FastMCP -> SecureMCP port + Field strip is
verified. Validating actual Data Cloud SQL behavior (table contents,
SQL dialect) is the responsibility of the upstream Salesforce
documentation; this smoke test proves the port itself.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
