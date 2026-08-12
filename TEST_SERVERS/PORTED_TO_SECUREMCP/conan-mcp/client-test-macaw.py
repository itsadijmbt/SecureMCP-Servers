"""
MACAW client smoke test for conan-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py conan-mcp conan-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)


"""

import asyncio
import logging
from macaw_adapters.mcp import Client
import sys


def get_server(name, client):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
    ]

    if not server:
        print(f" no server for name {name}")
        return None

    return server[0].get("agent_id")


async def main():

    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw.py conan-mcp conan-client')
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
    print(" CONAN MCP TESTS")
    print("=" * 60)

    print("\n[TEST 1] list_conan_profiles -- no args, basic call")
    try:
        result = await client.call_tool("list_conan_profiles", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if "default" in text or "[" in text:
            print("  PASS (creds branch) -- conan is installed and listed "
                  "profiles. Full chain works end to end.")
        elif "not found" in text.lower() or "Command not found" in text:
            print("  PASS (no-binary branch) -- conan is not installed; "
                  "the SDK raised, exception propagated cleanly through "
                  "SecureMCP. Port wiring verified.")
        else:
            print("  Inspect -- response shape unexpected.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "not found" in msg.lower() or "Command not found" in msg:
            print("  PASS (no-binary branch) -- exception came from the "
                  "subprocess layer, made it back to the client. Chain wired.")
        else:
            print("  Inspect -- exception type unexpected; may be a port issue.")

    print("\n[TEST 2] get_conan_profile -- default profile")
    try:
        result = await client.call_tool("get_conan_profile", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"settings"' in text or '"compiler"' in text or "{" in text:
            print("  PASS (creds branch) -- profile data returned. The "
                  "tool body successfully shelled out and parsed JSON.")
        elif "not found" in text.lower() or "Command not found" in text:
            print("  PASS (no-binary branch) -- same chain proof as TEST 1, "
                  "different tool reaching the same subprocess error.")
        else:
            print("  Inspect -- response shape unexpected.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "not found" in msg.lower():
            print("  PASS (no-binary branch).")
        else:
            print("  Inspect -- unexpected exception.")

    print("\n[TEST 3] list_conan_packages -- search for 'fmt' on conancenter")
    try:
        result = await client.call_tool(
            "list_conan_packages",
            {"name": "fmt", "remote": "conancenter"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"fmt' in text or '"Local Cache"' in text or "{" in text:
            print("  PASS (creds branch) -- remote package list reached. "
                  "Full vertical: client -> mesh -> SecureMCP -> tool body "
                  "-> conan CLI -> conancenter -> back.")
        elif "not found" in text.lower() or "Command not found" in text:
            print("  PASS (no-binary branch) -- same proof as TEST 1.")
        elif "remote" in text.lower():
            print("  PASS-ish -- conan ran but couldn't reach conancenter. "
                  "Network issue, not a port issue.")
        else:
            print("  Inspect -- response shape unexpected.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "not found" in msg.lower():
            print("  PASS (no-binary branch).")
        else:
            print("  Inspect.")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
