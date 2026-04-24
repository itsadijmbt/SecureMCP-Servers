from macaw_adapters.mcp import Client
import sys
import asyncio

def get_server(client, name):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
    ]

    if not server:
        print(f"No server found matching: {name}")
        print("Start it first: python3 server.py")
        return None
    return server[0].get("agent_id")   

async def main():
    if len(sys.argv) < 3:
        print("Usage: python3 client.py <server_filter_name> <client_name>")
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2] 
    
    # Initialize MACAW Client
    client = Client(client_type)
    server_id = get_server(client, name)

    if not server_id:
        return 
        
    client.set_default_server(server_id)
    
    print("Fetching tools from MACAW network...")
    tools = await client.list_tools(server_name=name)  

    seen = set()
    unique_tools = []

    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            unique_tools.append(t)
            print(f" - {t['name']}")
    
    # ==========================================
    # TEST 1: Get Server Info
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 1: 'info' (Checking Redis DB Stats)")
    print("=" * 60)
    try:
        result = await client.call_tool("info", {})
        output = result.get("result", result) if isinstance(result, dict) else getattr(result, "text", result)
        print(output)
    except Exception as e:
        print(f"[Tool failed: {e}]")

    # ==========================================
    # TEST 2: Set a String Value
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 2: 'set' (Writing data to Redis)")
    print("=" * 60)
    try:
        # Pushing a key-value pair into Redis
        result2 = await client.call_tool(
            "set",
            {"key": "macaw_test_key", "value": "SecureMCP Redis Integration Successful!"}
        )
        output2 = result2.get("result", result2) if isinstance(result2, dict) else getattr(result2, "text", result2)
        print(output2)
    except Exception as e:
        print(f"[Tool failed: {e}]")

    # ==========================================
    # TEST 3: Get the String Value Back
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST 3: 'get' (Reading data from Redis via background thread)")
    print("=" * 60)
    try:
        # Using the asyncio.to_thread pattern from your template for variety
        result3 = await asyncio.to_thread(
            client.macaw_client.invoke_tool,
            "get",
            {"key": "macaw_test_key"},
            target_agent=server_id,
        )
        output3 = result3.get("result", result3) if isinstance(result3, dict) else getattr(result3, "text", result3)
        print(output3)
    except Exception as e:
        print(f"[Tool failed: {e}]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)