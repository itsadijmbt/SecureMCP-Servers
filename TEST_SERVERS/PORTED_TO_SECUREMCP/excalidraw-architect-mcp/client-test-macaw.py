"""MACAW client smoke test for excalidraw-architect-mcp (FastMCP -> SecureMCP).

Three tests:
  TEST 1  list_tools             -- mesh advertises 4 tools
  TEST 2  mermaid_to_excalidraw  -- write a small diagram to /tmp
  TEST 3  get_diagram_info       -- read it back, assert nodes are seen

Tests 2 and 3 form a write/read-back pair: the simplest end-to-end
behaviour check that touches both the layout/render path and the
state parser.

Usage:
    python client-test-macaw.py "Excalidraw Architect" <client_name>
"""

import asyncio
import os
import sys

from macaw_adapters.mcp import Client


SMOKE_FILE = "/tmp/excal_port_smoke.excalidraw"

# Tiny mermaid sample -- 3 nodes, 2 edges, all upstream parser-supported.
SMOKE_MERMAID = """flowchart LR
    A[Frontend] --> B[API]
    B --> C[(Postgres)]
"""


def get_server(client, name):
    """Locate the excalidraw SecureMCP server on the MACAW mesh."""
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
        and "securemcp-client-" not in a.get("agent_id", "")
    ]
    if not server:
        print(f"No SecureMCP server matching '{name}' found.")
        print("Start it first: python -m excalidraw_mcp")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python client-test-macaw.py "Excalidraw Architect" <client_name>')
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]
    client = Client(client_type)
    server_id = get_server(client, name)
    if not server_id:
        return 1
    client.set_default_server(server_id)
    print(f"Connected to: {server_id}")

    # Clean any leftover from a previous run so TEST 2 assertions are honest.
    if os.path.exists(SMOKE_FILE):
        os.remove(SMOKE_FILE)

    # TEST 1 -- mesh-native tool discovery
    print("\n" + "=" * 60)
    print("TEST 1: list_tools  (mesh advertises 4 excalidraw tools)")
    print("=" * 60)
    tools = await client.list_tools(server_name=name)
    seen = set()
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            print(f"  - {t['name']}")
    print(f"  -> {len(seen)} unique tools advertised")
    expected = {"create_diagram", "mermaid_to_excalidraw",
                "modify_diagram", "get_diagram_info"}
    missing = expected - seen
    assert not missing, f"FAIL: missing tools {missing}"
    print("  PASS -- all 4 expected tools present")

    # TEST 2 -- mermaid_to_excalidraw writes a real .excalidraw file
    print("\n" + "=" * 60)
    print("TEST 2: mermaid_to_excalidraw  (writes /tmp file)")
    print("=" * 60)
    r2 = await client.call_tool(
        "mermaid_to_excalidraw",
        {"mermaid_syntax": SMOKE_MERMAID, "output_path": SMOKE_FILE},
    )
    output2 = r2.get("result", r2) if isinstance(r2, dict) else r2
    print(f"  result: {str(output2)[:240]}")
    assert os.path.exists(SMOKE_FILE), f"FAIL: {SMOKE_FILE} not created"
    size = os.path.getsize(SMOKE_FILE)
    assert size > 0, f"FAIL: {SMOKE_FILE} is empty"
    print(f"  PASS -- {SMOKE_FILE} written ({size} bytes)")

    # TEST 3 -- get_diagram_info reads back what TEST 2 wrote
    print("\n" + "=" * 60)
    print("TEST 3: get_diagram_info  (read back, assert nodes survive)")
    print("=" * 60)
    r3 = await client.call_tool("get_diagram_info", {"file_path": SMOKE_FILE})
    output3 = r3.get("result", r3) if isinstance(r3, dict) else r3
    summary = str(output3)
    print(f"  summary head: {summary[:240]}")
    # We don't pin exact labels because upstream component-detection may
    # rewrite "Postgres" styling; we check the labels we provided exist
    # somewhere in the printed summary.
    for label in ("Frontend", "API", "Postgres"):
        assert label in summary, f"FAIL: label '{label}' missing from summary"
    print("  PASS -- all 3 mermaid labels round-tripped through "
          "parse -> layout -> render -> read")

    # Cleanup so reruns are honest.
    if os.path.exists(SMOKE_FILE):
        os.remove(SMOKE_FILE)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
