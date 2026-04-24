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
      print("FALCON-MCP TOOL TESTS")
      print("=" * 50)                                                                                                                                                                         
   
      # Test 1: Check connectivity                                                                                                                                                            
      print("\n[TEST 1] falcon_check_connectivity")
      try:                                                                                                                                                                                    
          result = await client.call_tool("falcon_check_connectivity", {})
          print(f"  Result: {result}")                                                                                                                                                        
      except Exception as e:
          print(f"  Failed: {e}")
                                                                                                                                                                                              
      # Test 2: List enabled modules
      print("\n[TEST 2] falcon_list_enabled_modules")                                                                                                                                         
      try:        
          result = await client.call_tool("falcon_list_enabled_modules", {})
          print(f"  Result: {result}")
      except Exception as e:
          print(f"  Failed: {e}")

      # Test 3: List all available modules
      print("\n[TEST 3] falcon_list_modules")
      try:
          result = await client.call_tool("falcon_list_modules", {})
          print(f"  Result: {result}")
      except Exception as e:
          print(f"  Failed: {e}")
                                                                                                                                                                                              
      # Test 4: Get a resource (FQL guide)
      print("\n[TEST 4] Resource: hosts FQL guide")                                                                                                                                           
      try:        
          result = await client.get_resource("falcon://hosts/search/fql-guide")
          preview = str(result)[:120].replace("\n", " ")
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
