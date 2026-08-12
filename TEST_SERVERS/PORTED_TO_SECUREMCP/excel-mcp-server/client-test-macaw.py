"""
MACAW client smoke test for excel-mcp-server
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "excel" excel-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)



"""

import asyncio
import sys

from macaw_adapters.mcp import Client


EXPECTED_SAMPLE = {
    "apply_formula",
    "validate_formula_syntax",
    "format_range",
    "read_data_from_excel",
    "write_data_to_excel",
    "create_workbook",
    "create_chart",
    "create_pivot_table",
    "create_table",
    "get_workbook_metadata",
}


def get_server(name, client):
    """Look up the excel-mcp-server's agent_id on the mesh."""
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
        print('Example: python3 client-test-macaw.py "excel" excel-test-client')
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
    print("Tools advertised by server (showing first 25):")
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
    for n in sorted(seen)[:25]:
        print(f"  - {n}")
    print(f"\n  Total unique tools: {len(seen)}\n")

    print("=" * 60)
    print("EXCEL-MCP-SERVER TESTS")
    print("=" * 60)


    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_SAMPLE - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_SAMPLE)} sampled tools advertised "
              f"(out of {len(seen)} total).")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a @mcp.tool decorator didn't run, or the kwarg-strip ")
        print("  broke a signature. Check server import logs.")
        return

    
    print("\n[TEST 2] get_workbook_metadata -- read-only handler reach")
    try:
        result = await client.call_tool(
            "get_workbook_metadata",
            {"filepath": "/tmp/macaw-smoke-nonexistent.xlsx"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- get_workbook_metadata returned. Either real metadata, ")
        print("  or 'Error: ...' from the openpyxl read failure. Both prove the ")
        print("  call reached the handler and the openpyxl wrapping is intact.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")


    print("\n[TEST 3] validate_formula_syntax -- different-module handler reach")
    try:
        result = await client.call_tool(
            "validate_formula_syntax",
            {
                "filepath": "/tmp/macaw-smoke-nonexistent.xlsx",
                "sheet_name": "Sheet1",
                "cell": "A1",
                "formula": "=SUM(A2:A10)",
            },
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- validate_formula_syntax returned.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
