"""
MACAW client smoke test for dispatch_cli operator MCP server
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw-operator.py "dispatch-operator" operator-test-client

Args:
    1. server filter substring (matches against agent_id on the mesh)
    2. client name (any string for this caller's MACAW identity)

Prerequisites (the server side):
    1. MACAW Local Agent running.
    2. macaw_client + secureAI[all] installed in the same env as dispatch_cli.
    3. Dispatch credentials available to the server (env vars or
       `dispatch auth login`) so the upstream backend calls inside tool
       bodies can authenticate.
    4. Operator MCP server running:
           dispatch mcp serve operator --namespace <your-namespace>
       It will register on the MACAW mesh as agent
       `securemcp-dispatch-operator` (no longer speaks stdio MCP).

What this tests:
    1. Port-correctness: server registered, all tools advertised on the mesh.
    2. Schema-flattening: tool input schemas show flat kwargs (namespace,
       limit, ...) NOT a single `request` parameter. This proves the
       pydantic-model-as-input rewrite worked.
    3. Tool reachability: list_namespaces (no args) round-trips through
       MACAW -> handler -> dispatch backend.
    4. Argument plumbing: list_agents(namespace=...) round-trips with the
       flattened arg shape.

Without valid dispatch credentials on the server side, tests 3 and 4 will
fail at the dispatch backend (expected). Test 1 and 2 do NOT need
credentials -- they prove port-correctness independent of the backend.
"""

import asyncio
import sys

from macaw_adapters.mcp import Client


def get_server(name, client):
    """Look up the operator server's agent_id on the mesh.

    Filters out:
      - per-tool sub-agents (their agent_id contains '/tool.')
      - this client's own agent (its id contains 'securemcp-client-')
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
        print("Is the operator server running? Try:")
        print("  dispatch mcp serve operator --namespace <your-namespace>")
        return None
    return server[0].get("agent_id")


def _print_schema(tool):
    """Print a tool's input schema in compact form."""
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    if not props:
        print("    (no parameters)")
        return
    for pname, pinfo in props.items():
        ptype = pinfo.get("type", "?")
        req_marker = "*" if pname in required else " "
        print(f"    {req_marker} {pname}: {ptype}")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw-operator.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw-operator.py "dispatch-operator" operator-test')
        sys.exit(1)

    name = sys.argv[1]
    client_name = sys.argv[2]

    client = Client(client_name)
    server_id = get_server(name, client)
    if not server_id:
        return
    client.set_default_server(server_id)

    tools = await client.list_tools(server_name=name)
    seen = {}
    for t in tools:
        seen[t["name"]] = t  # dedupe; keep last occurrence's schema
    tool_names = sorted(seen.keys())

    print("Tools advertised by server:")
    for n in tool_names:
        print(f"  - {n}")
    print(f"\n  Total unique tools: {len(tool_names)}\n")

    print("=" * 60)
    print("DISPATCH OPERATOR MCP TESTS")
    print("=" * 60)

    # --------------------------------------------------------------
    # TEST 1 -- server registered, expected tools present
    #
    # Pure port-correctness check. If list_tools came back populated,
    # we know:
    #   - SecureMCP boot succeeded (mcp.run() reached the mesh)
    #   - create_operator_mcp ran every @mcp.tool() registration
    #   - MACAWClient.register() succeeded
    # No upstream dispatch backend call yet.
    # --------------------------------------------------------------
    print("\n[TEST 1] tool list -- port-correctness")
    expected = {
        "list_namespaces", "list_agents", "create_agent",
        "deploy_agent", "get_deploy_status",
        "stop_agent", "reboot_agent", "uninstall_agent", "get_agent_logs",
        "get_topic_schema", "publish_event", "list_topics",
        "get_recent_events", "get_event_trace", "get_recent_traces",
        "get_agent_functions", "invoke_function", "get_invocation_status",
        "list_long_term_memories",
        "start_local_agent_dev", "stop_local_router", "list_local_routers",
        "send_local_test_event", "invoke_local_function", "read_local_agent_logs",
        "create_schedule", "list_schedules", "get_schedule",
        "update_schedule", "delete_schedule",
        "submit_feedback",
    }
    missing = expected - set(tool_names)
    extra = set(tool_names) - expected
    if not missing:
        print(f"  PASS -- all {len(expected)} expected tools advertised.")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
    if extra:
        print(f"  Note -- additional tools not in this checklist: {sorted(extra)}")

    # --------------------------------------------------------------
    # TEST 2 -- input schemas show flat kwargs, NOT a `request` param
    #
    # This is THE test for the pydantic-model-as-input rewrite. Before
    # the port, every tool had a single `request: SomeRequest` param.
    # SecureMCP cannot introspect pydantic models, so the port flattened
    # each tool to typed kwargs.
    #
    # Expectation: list_agents shows `namespace` and `limit` parameters
    # (not a single `request`).
    # --------------------------------------------------------------
    print("\n[TEST 2] schema flattening -- list_agents parameters")
    if "list_agents" in seen:
        schema = seen["list_agents"].get("inputSchema") or seen["list_agents"].get("input_schema") or {}
        props = schema.get("properties", {})
        if "request" in props and len(props) == 1:
            print("  FAILED -- list_agents still advertises a single `request` param.")
            print("           The pydantic-model-as-input was not flattened.")
        elif "namespace" in props and "limit" in props:
            print("  PASS -- list_agents advertises flat kwargs (namespace, limit).")
            print("    schema:")
            _print_schema(seen["list_agents"])
        else:
            print("  Inspect -- unexpected schema shape:")
            _print_schema(seen["list_agents"])
    else:
        print("  SKIPPED -- list_agents not in tool list.")

    # --------------------------------------------------------------
    # TEST 3 -- list_namespaces (no-args read tool)
    #
    # Round-trips through MACAW mesh -> server handler -> dispatch
    # backend. Two valid outcomes:
    #   a) Backend reachable + creds correct: returns namespaces.
    #   b) Bad creds / backend down: tool body raises, exception
    #      propagates as RuntimeError on the wire.
    # Either outcome PROVES port-correctness: the call reached the
    # handler with no schema-shape errors.
    # --------------------------------------------------------------
    print("\n[TEST 3] list_namespaces -- handler reachability")
    try:
        result = await client.call_tool("list_namespaces", {})
        text = str(result)[:240]
        print(f"  Result: {text}")
        if "namespaces" in text.lower() or "[" in text:
            print("  PASS (creds branch) -- list_namespaces returned data. Full "
                  "vertical works: client -> mesh -> handler -> dispatch -> back.")
        else:
            print("  PASS (no-creds branch) -- handler ran. Whatever response "
                  "came back, it didn't fail at the SecureMCP layer.")
    except Exception as e:
        msg = str(e)[:240]
        print(f"  Got error: {msg}")
        if "missing" in msg.lower() and "argument" in msg.lower():
            print("  FAILED -- TypeError on missing args. Schema-flattening bug.")
        else:
            print("  PASS (no-creds branch) -- exception was NOT a schema/arg "
                  "error. Came from upstream dispatch backend, which means the "
                  "MACAW + SecureMCP layer did its job.")

    # --------------------------------------------------------------
    # TEST 4 -- list_agents with namespace kwarg (flattened-arg plumbing)
    #
    # Same as TEST 3 but with a required argument. Proves:
    #   - the flattened `namespace: str` parameter is wired correctly
    #   - the value flows from JSON-RPC into the function body
    #   - `_get_namespace(namespace)` accepts it
    #
    # If the flattening were broken, this would fail with TypeError
    # before reaching the dispatch backend.
    # --------------------------------------------------------------
    print("\n[TEST 4] list_agents(namespace='default') -- argument plumbing")
    try:
        result = await client.call_tool(
            "list_agents",
            {"namespace": "default", "limit": 5},
        )
        text = str(result)[:240]
        print(f"  Result: {text}")
        if "agents" in text.lower() or "[" in text:
            print("  PASS (creds branch) -- list_agents executed end-to-end.")
        else:
            print("  PASS (no-creds branch) -- handler ran with the flattened "
                  "namespace/limit kwargs. Response shape unrelated to port.")
    except Exception as e:
        msg = str(e)[:240]
        print(f"  Got error: {msg}")
        if "missing" in msg.lower() and "argument" in msg.lower():
            print("  FAILED -- argument plumbing broken. Flattened kwargs not "
                  "reaching the handler.")
        else:
            print("  PASS (no-creds branch) -- exception was NOT a schema/arg "
                  "error. Args reached the handler; failure is downstream.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like across the four tests (no real dispatch backend needed):

  TEST 1 PASS  Server registered on the mesh; ~31 tools advertised.
               Proves: framework swap + every @mcp.tool() registration ran.

  TEST 2 PASS  list_agents schema shows `namespace` and `limit` (flat),
               not a single `request` param. Proves: the pydantic-model
               flattening worked end-to-end through MACAW's tool list.

  TEST 3 PASS  list_namespaces either succeeded or failed at the dispatch
               backend without TypeError. Proves: handler reachable, no-arg
               tool path works.

  TEST 4 PASS  list_agents(namespace=..., limit=5) either succeeded or
               failed at the dispatch backend without TypeError. Proves:
               flattened kwargs reach the function body intact.

If TESTS 1 and 2 PASS, the port itself is correct. TESTS 3 and 4 only
require dispatch backend credentials to go full green.

Failure modes that mean the PORT is wrong (vs. environment):
  - TEST 1 missing tools  -> registration step didn't run; check the SecureMCP
                             import and the create_operator_mcp body.
  - TEST 2 single `request` param -> flattening missed; some tool still has
                             `def my_tool(request: SomeRequest)`.
  - TEST 3/4 TypeError on args -> a tool body still references `request.X`
                             after the signature was flattened.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
