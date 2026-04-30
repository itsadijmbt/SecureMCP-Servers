import asyncio
from fastmcp import Client
from datetime import datetime, timezone
import json
import time
import os


async def extract_tool_response(result):
    """Extract text content from tool response and parse as JSON if possible."""
    response_data = {}
    for content in result.content:
        if hasattr(content, "text"):
            response_data = content.text
            break
    
    # Try to parse as JSON if it's a string
    if isinstance(response_data, str):
        try:
            response_data = json.loads(response_data)
        except json.JSONDecodeError:
            pass  # Keep as string if not valid JSON
    
    return response_data

async def test_server():
    """Test the MCP server using streamable-http transport."""
    
    print("🚀 Starting MCP Server Test Suite")
    print("=" * 60)
    
    # Test data
    test_user_id = "test.user@example.com"
    test_conversation_id = "test_conversation_001"
    test_query = "F1 Street Circuit Driving Experience at Marina Bay Sands"
    test_mongodb_config = {
        "connection_string": os.getenv("MONGODB_URI"),
        "database_name": "maap_data_loader", 
        "collection_name": "documents",
        "fulltext_search_field": "text",
        "vector_search_index_name": "documents_vector_search_index",
        "vector_search_field": "embedding",
        "user_id": test_user_id,
        "weight": 0.5,
        "limit": 5
    }
    
    async with Client("http://localhost:8080/mcp/") as client:
        try:
            # ============================================================
            # 1. List Available Tools
            # ============================================================
            health = await client.read_resource("health://status")
            print("MCP Server Health: ",health)

            conversation_prompt = await client.get_prompt("conversation_prompt")
            print("\nConversation Prompt: \n", conversation_prompt)

            print("\n1️⃣  LISTING AVAILABLE TOOLS")
            print("-" * 30)
            tools = await client.list_tools()
            print(f"Found {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                print(f"   {i}. {tool.name}")
            
            # ============================================================
            # 2. Test Memory Tools - Store Memory
            # ============================================================
            print("\n2️⃣  TESTING MEMORY TOOLS - STORE")
            print("-" * 35)
            # Store a human message
            print("📝 Storing human message...")
            store_result = await client.call_tool("store_memory", {
                "conversation_id": test_conversation_id,
                "text": "I'm interested in the F1 racing experience at Marina Bay Sands. Can you tell me more about it?",
                "message_type": "human",
                "user_id": test_user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            store_response = await extract_tool_response(store_result)
            print(f"   Result: {store_response}")
            
            # Store an AI response
            print("🤖 Storing AI response...")
            ai_response = "The F1 Street Circuit at Marina Bay Sands offers an incredible racing experience through the heart of Singapore. It's a night race with stunning city views and challenging turns."
            store_ai_result = await client.call_tool("store_memory", {
                "conversation_id": test_conversation_id,
                "text": ai_response,
                "message_type": "ai", 
                "user_id": test_user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            store_ai_response = await extract_tool_response(store_ai_result)
            print(f"   Result: {store_ai_response}")
            
            # ============================================================
            # 3. Test Memory Tools - Retrieve Memory
            # ============================================================
            print("\n3️⃣  TESTING MEMORY TOOLS - RETRIEVE")
            print("-" * 37)
            print("🔍 Retrieving relevant memories...")
            memory_result = await client.call_tool("retrieve_memory", {
                "user_id": test_user_id,
                "text": "Tell me about F1 racing experiences"
            })
            
            memory_response = await extract_tool_response(memory_result)
            print(f"   Related Conversation: {memory_response.get('related_conversation', 'None')}")
            print(f"   Conversation Summary: {memory_response.get('conversation_summary', 'None')}")
            print(f"   Similar Memories: {memory_response.get('similar_memories', 'None')}")
            
            # ============================================================
            # 4. Test Semantic Cache - Store Cache
            # ============================================================
            print("\n4️⃣  TESTING SEMANTIC CACHE - STORE")
            print("-" * 36)
            print("💾 Caching AI response...")
            cache_store_result = await client.call_tool("semantic_cache_response", {
                "user_id": test_user_id,
                "query": test_query,
                "response": ai_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            cache_store_response = await extract_tool_response(cache_store_result)
            print(f"   Result: {cache_store_response}")
            
            # ============================================================
            # 5. Test Semantic Cache - Check Cache
            # ============================================================
            print("\n5️⃣  TESTING SEMANTIC CACHE - CHECK")
            print("-" * 35)
            print("🔎 Checking semantic cache...")
            cache_check_result = await client.call_tool("check_semantic_cache", {
                "user_id": test_user_id,
                "query": "F1 Street Driving Experience at Marina Bay"  # Similar but different query
            })
            cache_check_response = await extract_tool_response(cache_check_result)
            print(f"   Cached Response: {cache_check_response}")
            
            # ============================================================
            # 6. Test Hybrid Search
            # ============================================================
            print("\n6️⃣  TESTING HYBRID SEARCH")
            print("-" * 26)
            print("🔍 Performing hybrid search on MongoDB...")
            hybrid_result = await client.call_tool("hybrid_search", {
                **test_mongodb_config,
                "query": test_query
            })
            
            hybrid_response = await extract_tool_response(hybrid_result)
            if "results" in hybrid_response:
                results = hybrid_response["results"]
                print(f"   Found {len(results)} results:")
                for i, result in enumerate(results[:3], 1):  # Show first 3 results
                    print(f"   {i}. Score: {result.get('score', 'N/A'):.4f}")
                    text_preview = (result.get('text', '')[:100] + '...') if len(result.get('text', '')) > 100 else result.get('text', '')
                    print(f"      Text: {text_preview}")
            else:
                print(f"   No results or error: {hybrid_response}")
            
            # Test with different weight settings
            print("🔍 Testing with keyword-focused search (weight=0.2)...")
            keyword_result = await client.call_tool("hybrid_search", {
                **test_mongodb_config,
                "query": test_query,
                "weight": 0.2  # More focus on keyword matching
            })
            keyword_response = await extract_tool_response(keyword_result)
            keyword_count = len(keyword_response.get("results", []))
            print(f"   Found {keyword_count} results with keyword focus")
            
            print("🔍 Testing with semantic-focused search (weight=0.8)...")
            semantic_result = await client.call_tool("hybrid_search", {
                **test_mongodb_config,
                "query": test_query,
                "weight": 0.8  # More focus on semantic similarity
            })
            semantic_response = await extract_tool_response(semantic_result)
            semantic_count = len(semantic_response.get("results", []))
            print(f"   Found {semantic_count} results with semantic focus")
            
            # ============================================================
            # 7. Test Web Search
            # ============================================================
            print("\n7️⃣  TESTING WEB SEARCH")
            print("-" * 22)
            print("🌐 Performing web search...")
            web_result = await client.call_tool("search_web", {
                "query": test_query
            })
            
            web_response = await extract_tool_response(web_result)
            if isinstance(web_response, list):
                print(f"   Found {len(web_response)} web results:")
                for i, content in enumerate(web_response[:2], 1):  # Show first 2 results
                    preview = (content[:150] + '...') if len(content) > 150 else content
                    print(f"   {i}. {preview}")
            elif isinstance(web_response, dict) and "results" in web_response:
                results = web_response["results"]
                print(f"   Found {len(results)} web results:")
                for i, result in enumerate(results[:2], 1):
                    title = result.get('title', 'No title')[:80]
                    snippet = result.get('snippet', 'No snippet')[:100]
                    print(f"   {i}. {title}")
                    print(f"      {snippet}...")
            else:
                print(f"   Web search result: {web_response}")
            
            # ============================================================
            # 8. Test Error Handling
            # ============================================================
            print("\n8️⃣  TESTING ERROR HANDLING")
            print("-" * 27)
            
            # Test with invalid user_id
            print("❌ Testing invalid user_id...")
            try:
                error_result = await client.call_tool("store_memory", {
                    "conversation_id": test_conversation_id,
                    "text": "This should fail",
                    "message_type": "human",
                    "user_id": None  # Invalid user_id
                })
                error_response = await extract_tool_response(error_result)
                print(f"   Unexpected success: {error_response}")
            except Exception as e:
                print(f"   Expected error caught: {type(e).__name__}")
            
            # Test with invalid message_type
            print("❌ Testing invalid message_type...")
            try:
                error_result = await client.call_tool("store_memory", {
                    "conversation_id": test_conversation_id,
                    "text": "This should fail",
                    "message_type": "invalid_type",  # Invalid message type
                    "user_id": test_user_id
                })
                error_response = await extract_tool_response(error_result)
                print(f"   Unexpected success: {error_response}")
            except Exception as e:
                print(f"   Expected error caught: {type(e).__name__}")
            
            # ============================================================
            # 9. Performance Test
            # ============================================================
            print("\n9️⃣  PERFORMANCE TEST")
            print("-" * 20)
            
            start_time = time.time()
            
            # Concurrent tool calls
            tasks = [
                client.call_tool("retrieve_memory", {
                    "user_id": test_user_id,
                    "text": "F1 racing"
                }),
                client.call_tool("check_semantic_cache", {
                    "user_id": test_user_id,
                    "query": "Racing experience"
                }),
                client.call_tool("hybrid_search", {
                    **test_mongodb_config,
                    "query": "Marina Bay",
                    "limit": 3
                })
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start_time
            
            print(f"   Concurrent execution of 3 tools: {elapsed:.2f} seconds")
            successful = sum(1 for r in results if not isinstance(r, Exception))
            print(f"   Successful calls: {successful}/3")
            
            # Show results of performance test
            for i, result in enumerate(results, 1):
                if not isinstance(result, Exception):
                    response = await extract_tool_response(result)
                    result_type = type(response).__name__
                    print(f"   Task {i} result type: {result_type}")
                else:
                    print(f"   Task {i} failed: {result}")
            
        except Exception as e:
            print(f"\n❌ ERROR during testing: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            print("\n" + "=" * 60)
            print("🏁 MCP Server Test Suite Complete!")
            print("=" * 60)

async def test_individual_tool(tool_name: str):
    """Test a specific tool individually."""
    print(f"\n🔧 Testing individual tool: {tool_name}")
    
    async with Client("http://localhost:8080/mcp") as client:
        try:
            if tool_name == "hybrid_search":
                result = await client.call_tool("hybrid_search", {
                    "connection_string": os.getenv("MONGODB_URI"),
                    "database_name": "maap_data_loader",
                    "collection_name": "documents",
                    "fulltext_search_field": "text",
                    "vector_search_index_name": "documents_vector_search_index",
                    "vector_search_field": "embedding",
                    "query": "Singapore attractions",
                    "user_id": "test.user@example.com",
                    "weight": 0.5,
                    "limit": 5
                })
                
            elif tool_name == "search_web":
                result = await client.call_tool("search_web", {
                    "query": "Singapore Marina Bay attractions"
                })
                
            elif tool_name == "retrieve_memory":
                result = await client.call_tool("retrieve_memory", {
                    "user_id": "test.user@example.com",
                    "text": "Singapore attractions"
                })
                
            elif tool_name == "check_semantic_cache":
                result = await client.call_tool("check_semantic_cache", {
                    "user_id": "test.user@example.com",
                    "query": "F1 Street Driving Experience at Marina Bay"
                })
                
            else:
                print(f"Tool {tool_name} test not implemented")
                return
            
            response = await extract_tool_response(result)
            print(f"Result: {json.dumps(response, indent=2) if isinstance(response, dict) else response}")
            
        except Exception as e:
            print(f"Error testing {tool_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    # Check if specific tool test is requested
    if len(sys.argv) > 1:
        tool_name = sys.argv[1]
        asyncio.run(test_individual_tool(tool_name))
    else:
        # Run full test suite
        asyncio.run(test_server())