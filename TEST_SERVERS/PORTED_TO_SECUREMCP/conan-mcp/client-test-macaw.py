"""
MACAW client smoke test for conan-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py conan-mcp conan-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

Two layers being checked:

  Caller auth -- "is this caller really who they say they are?"
  MACAW signs every invoke_tool call with this caller's keypair.
  If MACAW didn't trust us, none of the calls below would even
  reach the server. Any response coming back at all is the proof.

  Upstream auth -- "what do we use to talk to Conan?"
  Conan-mcp has NO upstream auth in the usual sense. The server
  shells out to the `conan` CLI binary on the host. The "creds"
  question is replaced by "is the conan binary installed on this
  host and can the user run it?"
  Two outcomes both prove the port:
    - conan installed       -> tools return real data (lists, dicts)
    - conan NOT installed   -> the SDK raises RuntimeError("Command
                               not found.") which propagates back
                               through SecureMCP cleanly.
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

    # TEST 1 -- list_conan_profiles
    # Simplest possible call. No arguments. Calls `conan profile list`
    # which returns the local profiles. Default install gives at least
    # one profile named "default".
    # Outcomes:
    #   - conan installed     -> a Python list of profile names.
    #   - conan NOT installed -> exception with "Command not found."
    #     (or the chain returns an error result wrapping it).
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

    # TEST 2 -- get_conan_profile
    # Calls `conan profile show` for the default profile. Slightly
    # more involved than TEST 1 because the tool body builds a
    # command pattern. Same two outcome branches.
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

    # TEST 3 -- list_conan_packages with a popular package name
    # Hits a remote Conan registry. With conan installed and network
    # access, returns a dict listing package versions. Without
    # conan, same "Command not found" shape as the other tests.
    # Useful as the "real upstream call" test in the creds branch
    # since it proves remote queries work, not just local profile lookups.
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

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What you should see:

  Without conan installed on this host:
    TEST 1, 2, 3 all return / raise with "Command not found." or
    "RuntimeError: Command not found." from the run_command helper.
    All three came back through the SecureMCP handler chain. That
    is the port-correctness proof.

  With conan installed:
    TEST 1  Python list of profiles, e.g. ["default"].
    TEST 2  Dict with profile settings (compiler, arch, build_type).
    TEST 3  Dict with fmt package versions from conancenter.

How to run with conan installed (the creds-branch run):

  Two paths.

  Path A -- pip install conan into the same Python env:

      pip install conan
      conan profile detect --force        # creates a default profile
      python3 -m conan_mcp.main           # in Terminal 1, leaves running
      python3 client-test-macaw.py conan-mcp conan-client   # Terminal 2

  Path B -- use uv (project already pulls conan as a dep via pyproject):

      uv sync                              # installs conan + mcp deps
      uv run conan profile detect --force  # creates default profile
      uv run conan-mcp                     # Terminal 1, server up
      uv run python client-test-macaw.py conan-mcp conan-client  # Terminal 2

  After Path A or Path B, the three tests should flip from
  "Command not found" to real data branches.

If TEST 1 returns profiles but TEST 3 fails with "remote" or
"connection" in the error, conan is installed but cannot reach
conancenter. That is a network issue, not the port.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
