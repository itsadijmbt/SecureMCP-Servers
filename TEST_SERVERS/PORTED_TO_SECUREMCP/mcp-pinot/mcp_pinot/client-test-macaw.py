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
          print("Usage: python3 client.py <server_filter_name> <client_name>")
          sys.exit(1)

      name = sys.argv[1]
      client_type = sys.argv[2]

      client = Client(client_type)
      server_id = get_server(client, name)
                                                                                                                                                                                              
      if not server_id:
          return                                                                                                                                                                              
                  
      client.set_default_server(server_id)

      # List all tools
      tools = await client.list_tools(server_name=name)
      seen = set()                                                                                                                                                                            
      for t in tools:
          if t["name"] not in seen:                                                                                                                                                           
              seen.add(t["name"])
              print(f" - {t['name']}")

      print("\n" + "=" * 50)
      print("PINOT-MCP TOOL TESTS")
      print("=" * 50)

      # Test 1: Verify Pinot connectivity
      print("\n[TEST 1] test_connection")
      try:
          result = await client.call_tool("test_connection", {})
          print(f"  Result: {result}")
      except Exception as e:
          print(f"  Failed: {e}")

      # Test 2: List tables in the Pinot cluster
      print("\n[TEST 2] list_tables")
      try:
          result = await client.call_tool("list_tables", {})
          print(f"  Result: {result}")
      except Exception as e:
          print(f"  Failed: {e}")

      # Test 3: Fetch details for a specific table
      # NOTE: replace "airlineStats" with a table that exists in your cluster
      print("\n[TEST 3] table_details")
      try:
          result = await client.call_tool("table_details", {"tableName": "airlineStats"})
          preview = str(result)[:200].replace("\n", " ")
          print(f"  Result: {preview}...")
      except Exception as e:
          print(f"  Failed: {e}")                                                                                                                                                             
                                                                                                                                                                                              
   
if __name__ == "__main__":                                                                                                                                                                  
      try:        
          asyncio.run(main())
      except KeyboardInterrupt:
          print("\nExiting...")
      except Exception as e:
          print(f"\nError: {e}")                                                                                                                                                              
          sys.exit(1)