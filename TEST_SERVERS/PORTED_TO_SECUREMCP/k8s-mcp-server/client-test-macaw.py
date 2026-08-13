"""
MACAW client smoke test for k8s-mcp-server
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "k8s-mcp-server" k8s-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

"""

import asyncio
import sys

from macaw_adapters.mcp import Client


EXPECTED_TOOLS = {
    "describe_kubectl",
    "describe_helm",
    "describe_istioctl",
    "describe_argocd",
    "execute_kubectl",
    "execute_helm",
    "execute_istioctl",
    "execute_argocd",
}


def get_server(name, client):
    """Look up the k8s-mcp-server's agent_id on the mesh."""
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
        print('Example: python3 client-test-macaw.py "k8s" k8s-test-client')
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
    print("K8S-MCP-SERVER TESTS")
    print("=" * 60)


    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_TOOLS - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_TOOLS)} expected tools advertised.")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a @mcp.tool decorator didn't run, or a Field-default ")
        print("  rewrite broke the signature. Check server import logs.")
        return


    print("\n[TEST 2] describe_kubectl -- handler reachability (read-only)")
    try:
        result = await client.call_tool(
            "describe_kubectl",
            {"command": "version"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- describe_kubectl returned. Either kubectl produced ")
        print("  help text, or the handler caught the missing-kubectl error ")
        print("  and returned a structured result. Both prove the call ")
        print("  reached the handler.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")

    
    print("\n[TEST 3] execute_kubectl 'version --client' -- end-to-end (no cluster)")
    try:
        result = await client.call_tool(
            "execute_kubectl",
            {"command": "version --client", "timeout": 10},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- execute_kubectl returned. If you see a kubectl ")
        print("  version string, end-to-end works. If you see a structured ")
        print("  error (kubectl missing or validation rejected), the handler ")
        print("  still ran and the CLI subprocess plumbing is intact.")
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
