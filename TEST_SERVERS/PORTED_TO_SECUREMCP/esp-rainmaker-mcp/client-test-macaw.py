"""
MACAW client smoke test for esp-rainmaker-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3.11 client-test-macaw.py "ESP-RainMaker" rainmaker-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

This script tests TWO independent auth layers:


    CALLER AUTH (handled by MACAW automatically)                    
    Question: "Is this really me calling?"                          
    Mechanism: MACAWClient signs every invoke_tool call with this   
               caller's private key. Server-side MACAW Local Agent  
               validates the signature before the handler runs.     
    Tested by: simply being able to invoke any tool. If caller-auth
               fails, you'd never see a response 

    UPSTREAM AUTH (handled by the rmaker_lib SDK reading a local    
    config file written by `esp-rainmaker-cli login`)               
    Question: "Whose ESP RainMaker account do we use?"              
    Mechanism: the SDK reads `~/.espressif/...` style config that   
               contains a refreshable token.  It is single- 
               user by upstream design the cred file represents   
               one account; every MACAW caller hitting this server  
               ends up acting as that account.    

    Tested by: the difference between "no creds on host" (predict-  
               able SDK error string) and "creds on host" (real     
               user/node data). See bottom of file for both flows.  
  
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
        print("  This is a BLOCKER — the port itself isn't working.")

    # ----------------------------------------------------------------
    # TEST 2 — check_login_status
    # This tool calls ensure_login_session() which constructs
    # rmaker_lib.session.Session(). The Session ctor reads a local
    # config file written by `esp-rainmaker-cli login`.
    #
    # Two valid outcomes — BOTH prove the port works:
    #   A) NO creds on host  -> tool returns the SDK-translated string
    #      "Login required. Please run the 'login_instructions' tool
    #      ..." (this comes from the ValueError raised in
    #      ensure_login_session when InvalidUserError/InvalidConfigError
    #      bubbles up). That string can ONLY appear if the tool body
    #      ran, which means MACAW + SecureMCP wiring is correct.
    #   B) CREDS on host     -> tool returns
    #      "Login session is active for user: <username>"
    #      which proves SDK auth flowed through the same wired path.
    #
    # ----------------------------------------------------------------
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
        print("  Mesh-level error — caller-auth or transport problem, NOT an "
              "ESP-creds issue.")


  
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
        print("  Mesh-level or SDK-level exception leaking through. "
              "Compare to TEST 2's behavior.")


    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""

  Without ESP creds on this host:
    TEST 1   static markdown returned )
    TEST 2   "Login required..."
    TEST 3   same "Login required..."
    => Port is correct; ESP creds are absent (expected on a fresh host).

  With ESP creds on this host (after `esp-rainmaker-cli login`):
    TEST 1   static markdown
    TEST 2   "Login session is active for user: <name>"
    TEST 3   ["nodeid1", "nodeid2", ...] 

How to flip from "no creds" to "with creds":
  1. pip install esp-rainmaker-cli  
                                       
  2. esp-rainmaker-cli login         (opens browser; writes local config)
  3. Verify file at the path printed by check_login_status (typically
     under ~/.espressif/...).
  4. Restart this MCP server so the SecureMCP process picks up the new
     config (the SDK caches Session state in-process).
  5. Re-run this script. TEST 2 and TEST 3 should flip to the "creds
     branch" messages above.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
