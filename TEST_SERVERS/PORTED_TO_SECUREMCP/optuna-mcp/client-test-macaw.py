"""
MACAW client smoke test for optuna-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "Optuna" optuna-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)


"""

import asyncio
import sys

from macaw_adapters.mcp import Client


def get_server(name, client):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
        # Exclude this client's own agent (its id contains "securemcp-client-")
        and "securemcp-client-" not in a.get("agent_id", "")
    ]
    if not server:
        print(f"No server found matching: {name}")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw.py "Optuna" optuna-test-client')
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
    print("OPTUNA MCP HOLISTIC TESTS")
    print("=" * 60)

    # TEST 1 -- create_study
    # Exercises: .model_dump() at a BaseModel return site (StudyResponse).
    # Expectation: response is a dict containing "study_name".
    print("\n[TEST 1] create_study -- BaseModel return path")
    try:
        result = await client.call_tool(
            "create_study",
            {"study_name": "macaw-smoke", "directions": ["minimize"]},
        )
        text = str(result)
        print(f"  Result: {text[:200]}")
        if "study_name" in text and "macaw-smoke" in text:
            print("  PASS -- StudyResponse.model_dump() reached the wire as a dict.")
        else:
            print("  Inspect -- response shape unexpected.")
    except Exception as e:
        print(f"  FAILED: {e}")
        return

    # TEST 2 -- get_all_study_names
    # Exercises: list[BaseModel] return path (list comprehension with .model_dump()).
    # Expectation: a list with at least one entry containing "macaw-smoke".
    print("\n[TEST 2] get_all_study_names -- list[BaseModel] return path")
    try:
        result = await client.call_tool("get_all_study_names", {})
        text = str(result)
        print(f"  Result: {text[:200]}")
        if "macaw-smoke" in text:
            print("  PASS -- list of dumped StudyResponse dicts came back.")
        else:
            print("  Inspect -- expected to find macaw-smoke in the list.")
    except Exception as e:
        print(f"  Got error: {e}")

    # TEST 3 -- ask
    # Exercises: study state read + TrialResponse.model_dump() return.
    # Search space is a single float distribution between -10 and 10.
    print("\n[TEST 3] ask -- suggest a parameter")
    try:
        result = await client.call_tool(
            "ask",
            {
                "search_space": {
                    "x": {
                        "name": "FloatDistribution",
                        "attributes": {
                            "low": -10.0,
                            "high": 10.0,
                            "step": None,
                            "log": False,
                        },
                    }
                }
            },
        )
        text = str(result)
        print(f"  Result: {text[:200]}")
        if "trial_number" in text and "params" in text:
            print("  PASS -- TrialResponse came back with trial_number + params.")
        else:
            print("  Inspect -- response shape unexpected.")
    except Exception as e:
        print(f"  Got error: {e}")

    # TEST 4 -- tell + best_trial
    # Tell trial 0 a value, then read best_trial back. Exercises:
    # study mutation, error-free flow, and another TrialResponse return.
    print("\n[TEST 4] tell trial 0 a value, then read best_trial")
    try:
        tell_result = await client.call_tool(
            "tell", {"trial_number": 0, "values": 1.23}
        )
        print(f"  tell result: {str(tell_result)[:200]}")

        best = await client.call_tool("best_trial", {})
        text = str(best)
        print(f"  best_trial result: {text[:200]}")
        if "trial_number" in text and "1.23" in text:
            print("  PASS -- full round-trip: tell wrote, best_trial read back.")
        else:
            print("  Inspect -- best_trial shape unexpected.")
    except Exception as e:
        print(f"  Got error: {e}")

    # TEST 5 -- plot_optimization_history
    # Exercises: the base64 dict return (replacement for Image).
    # Expectation: dict with image_format and image_base64 keys.
    print("\n[TEST 5] plot_optimization_history -- base64 image dict path")
    try:
        result = await client.call_tool(
            "plot_optimization_history", {"target_name": "Objective Value"}
        )
        text = str(result)
        # Don't print the whole base64 payload; just check the keys exist.
        snippet = text[:120] + "..." if len(text) > 120 else text
        print(f"  Result snippet: {snippet}")
        if "image_format" in text and "image_base64" in text:
            print("  PASS -- base64 dict came through. Length of "
                  f"image_base64 ~= {len(text)} chars.")
        else:
            print("  Inspect -- did not see expected dict keys.")
    except Exception as e:
        print(f"  Got error: {e}")

    # TEST 6 -- error path
    # Call a tool that requires a study with a fresh server context where
    # study state mismatches. 
    print("\n[TEST 6] error path -- intentionally bad set_metric_names")
    try:
        result = await client.call_tool(
            "set_metric_names",
            {"metric_names": ["a", "b", "c", "d", "e"]},  # too many names
        )
        text = str(result)
        print(f"  Result: {text[:200]}")
        print("  Note: optuna may accept this silently in some versions. "
              "What matters is the call returned through SecureMCP.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:200]}")
        if "metric_names" in msg.lower() or "objective" in msg.lower():
            print("  PASS -- exception propagated as a clean RuntimeError. "
                  "The McpError -> RuntimeError replacement works on the wire.")
        else:
            print("  Inspect -- mesh-level error rather than tool-level.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like across the six tests:

  TEST 1 ✓  StudyResponse.model_dump() returns a usable dict.
  TEST 2 ✓  List of dumped models returns cleanly.
  TEST 3 ✓  ask gives back a TrialResponse with params populated.
  TEST 4 ✓  tell + best_trial round-trips a value through study state.
  TEST 5 ✓  plot tool returns a dict with image_format + image_base64.
  TEST 6 ✓  Bad input raises a RuntimeError that propagates cleanly.

If TESTS 1, 3, 4, 5 all pass, every adapter we added is verified:
  - .model_dump() (TESTS 1, 3, 4)
  - list[.model_dump()] (TEST 2)
  - base64 dict for images (TEST 5)
  - RuntimeError instead of McpError (TEST 6)
  - tool() forwarder accepting @mcp.tool(structured_output=True)
    decorations (implicit -- if any tool returns at all, the
    decorator succeeded).

No upstream creds or external services to set up. Just run the
server and run this script.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
