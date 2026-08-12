"""
MACAW client smoke test for esp-rainmaker-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3.11 client-test-macaw.py "ESP-RainMaker" rainmaker-test-client

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
        print('Example: python3 client-test-macaw.py "ESP-RainMaker" rainmaker-test')
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
    print("ESP RAINMAKER MCP TESTS")
    print("=" * 60)

  
    print("\n[TEST 1] no upstream creds needed")
    try:
        result = await client.call_tool("login_instructions", {})

        text = str(result)
        if "esp-rainmaker-cli login" in text:
            print(f"  Result snippet: {text[:120]}...")
            print("  PASS — full dispatch chain works (caller-auth implicit)")
        else:
            print(f"  Got unexpected result shape: {text[:200]}")
            print("  Inspect the response — handler ran but content is unexpected.")
    except Exception as e:
        print(f"  FAILED: {e}")


    print("\n[TEST 2]  exercises the SDK auth path")
    try:
        result = await client.call_tool("check_login_status", {})
        text = str(result)
        print(f"  Result: {text[:200]}")
        if "Login required" in text:
            print("  PASS (no-creds branch) — tool body ran, SDK rejected with "
                  "InvalidUserError/InvalidConfigError, error string was "
                  "translated and returned. Port wiring verified.")
        elif "Login session is active" in text:
            print("  PASS (creds branch) — SDK reads local config, session is "
                  "live, user identity confirmed. Port wiring verified.")
        else:
            print("  Inspect server logs — handler ran but message shape is new.")
    except Exception as e:
        print(f"  Got error: {e}")



  
    print("\n[TEST 3] get_nodes ")
    try:
        result = await client.call_tool("get_nodes", {})
        text = str(result)
        print(f"  Result: {text[:200]}")
        if "Login required" in text:
            print("  PASS (no-creds branch) — same proof as TEST 2 plus "
                  "confirms get_nodes' code path reached ensure_login_session.")
        elif text.startswith("[") or "No nodes found" in text:
            print("  PASS (creds branch) — node list returned from upstream "
                  "API. Full vertical proof: caller-auth -> mesh -> SecureMCP "
                  "-> tool -> SDK -> network -> RainMaker -> back.")
        else:
            print("  Inspect — unexpected response shape.")
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
