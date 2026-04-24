from macaw_adapters.mcp import Client
import asyncio
import sys

def get_server(client, name):
    agents = client.macaw_client.list_agents(agent_type="app")  
    server = [
        a for a in agents
        if name in a.get("agent_id","")
        if "/tool." not in a.get("agent_id","")
    ]

    if not server:
        print(f"no server")
        return None
    return server[0].get("agent_id")

async def main():
    if len(sys.argv) < 3:
        print("Usage: python3 client.py <server_filter_name> <client_name>")
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]

    client = Client(client_type)
    server_id = get_server(client, name)
    
    if not server_id:
        return

    # CRITICAL: Set the target server before calling tools!
    client.set_default_server(server_id)

    tools = await client.list_tools(server_name=name)
    seen = set()
    unique_tools = []
    for t in tools:
        if t['name'] not in seen:
            seen.add(t['name'])
            unique_tools.append(t)
            print(f" - {t['name']}")

    print("\n" + "="*50)
    print("STARTING POSTGRESQL TOOL TESTS")
    print("="*50)

    # ---------------------------------------------------------
    # Example 1: Call 'list_tables' (No arguments needed)
    # ---------------------------------------------------------
    print("\n[TEST 1] Executing 'list_tables'...")
    try:
        result = await client.call_tool("list_tables", {})
        
        # Safely extract the output
        output = result.get("result", result) if isinstance(result, dict) else getattr(result, "text", result)
        print("Result:\n", output)
    except Exception as e:
        print(f"[Tool failed: {e}]")

    # ---------------------------------------------------------
    # Example 2: Call 'get_table_schema' (Requires an argument)
    # ---------------------------------------------------------
    print("\n[TEST 2] Executing 'get_table_schema' for table 'users'...")
    try:
    
        result = await client.call_tool("get_table_schema", {"table_name": "users"})
        
        output = result.get("result", result) if isinstance(result, dict) else getattr(result, "text", result)
        print("Result:\n", output)
    except Exception as e:
        print(f"[Tool failed: {e}]")

    # ---------------------------------------------------------
    # Example 3: Call 'execute_query' (Requires an argument)
    # ---------------------------------------------------------
    print("\n[TEST 3] Executing 'execute_query' (SELECT LIMIT 2)...")
    try:

        query = "SELECT * FROM users LIMIT 2;"
        result = await client.call_tool("execute_query", {"query": query})
        
        output = result.get("result", result) if isinstance(result, dict) else getattr(result, "text", result)
        print("Result:\n", output)
    except Exception as e:
        print(f"[Tool failed: {e}]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")