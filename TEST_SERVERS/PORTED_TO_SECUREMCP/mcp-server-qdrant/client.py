
from macaw_adapters.mcp import Client
import sys
import asyncio

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
 
      # ============================================================         
      # TEST 1: qdrant-store — write an entry                                                                                                                                                 
      # ============================================================                                                                                                                          
      print("\n" + "=" * 60)                                                                                                                                                                  
      print("TEST 1: qdrant-store")                                                                                                                                                           
      print("=" * 60)                                                                                                                                                                         
      r1 = await client.call_tool(
          "qdrant-store",
          {
              "information": "The sky is blue because of Rayleigh scattering.",
              "metadata": {"tag": "physics", "source": "test-client"},                                                                                                                        
          },                                                                                                                                                                                  
      )                                                                                                                                                                                       
      print("store result:", r1)                                                                                                                                                              
                  
      # ============================================================
      # TEST 2: qdrant-store — second entry, different topic
      # ============================================================                                                                                                                          
      print("\n" + "=" * 60)
      print("TEST 2: qdrant-store (second entry)")                                                                                                                                            
      print("=" * 60)
      r2 = await client.call_tool(                                                                                                                                                            
          "qdrant-store",
          {
              "information": "Qdrant is a vector database written in Rust.",
              "metadata": {"tag": "database"},
          },
      )
      print("store result:", r2)

      # ============================================================
      # TEST 3: qdrant-find — semantic search should return entry 1
      # ============================================================
      print("\n" + "=" * 60)
      print("TEST 3: qdrant-find (semantic match for physics)")
      print("=" * 60)
      r3 = await client.call_tool(
          "qdrant-find",
          {"query": "why is the sky blue"},
      )
      print("find result:", r3)
      assert r3 and any("Rayleigh" in str(x) for x in r3), \
          "FAIL: stored entry not retrievable by semantic query"
      print("PASS: semantic roundtrip works")

      # ============================================================
      # TEST 4: qdrant-find — different query, should return entry 2
      # ============================================================
      print("\n" + "=" * 60)
      print("TEST 4: qdrant-find (semantic match for database)")
      print("=" * 60)
      r4 = await client.call_tool(
          "qdrant-find",
          {"query": "vector search engine"},
      )                                                                                                                                                                                       
      print("find result:", r4)
                                                                                                                                                                                              
      # ============================================================
      # TEST 5: qdrant-find — query unrelated to anything stored
      # ============================================================
      print("\n" + "=" * 60)
      print("TEST 5: qdrant-find (no match expected)")
      print("=" * 60)                                                                                                                                                                         
      r5 = await client.call_tool(
          "qdrant-find",                                                                                                                                                                      
          {"query": "medieval siege weapons"},
      )                                                                                                                                                                                       
      print("find result:", r5, "(may be None or low-relevance hits)")
                                                                                                                                                                                              
                  
if __name__ == "__main__":
      asyncio.run(main())
