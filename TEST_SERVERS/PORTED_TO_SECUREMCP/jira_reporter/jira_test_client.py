from macaw_adapters.mcp import Client
import sys
import asyncio
import os

SCHEMAS={}

def get_server(client,name):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id","")
        and "/tool." not in a.get("agent_id","")
    ]

    if not server:
        print(f"No server found matching: {name}")
        print("Start it first: python3.11 server.py")
        return None
    return server[0].get("agent_id")   

async def main():
   
    if len(sys.argv) < 3:
        print("Usage: python3.11 client.py <server_filter_name> <client_name>")
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2] 
    client = Client(client_type)
    server_id = get_server(client,name)

    if not server_id:
        return 
    client.set_default_server(server_id)
    print("Fetching tools from MACAW network...")
    tools = await client.list_tools(server_name=name)  

    seen = set()
    unique_tools =[]

    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            unique_tools.append(t)
            print(f" - {t['name']}")
    

    
    print("\n" + "=" * 60)
    print("TEST 1: generate_jira_report (raw, no LLM)")
    print("=" * 60)
 
    # RECOMMENDED: asyncio.to_thread — truly non-blocking
    # invoke_tool is synchronous and blocks the event loop.
    # to_thread runs it in a background thread so event loop stays free.

    try:
        result = await client.call_tool(
            "generate_jira_report",
            {"max_results": 5, "summarize": False},
            # target_server can be skipped as we set default server while using call_tool
            # target_server =server_id
            )
        
        
        output = result.get("result", result)
        print(output)

        result2 = await asyncio.to_thread(
            client.macaw_client.invoke_tool,
            "find_delayed_issues",
            {"max_results": 5, "explain_delay": False},
             target_agent=server_id,
        )
        output2= result2.get("result", result2)
        print(output2)

    except Exception as e:
                    result = f"Error: {str(e)}"
                    print(f"[Tool failed: {result}]")

    history = await client.get_resource("jira://history")
    for val in history.get("history",[]) or []:
            print(f"     - {val}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)