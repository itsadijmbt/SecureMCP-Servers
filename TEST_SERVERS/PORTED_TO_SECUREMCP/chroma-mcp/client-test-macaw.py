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
        print("Start it first: python3.11 server.py")
        return None
    return server[0].get("agent_id")


async def main():

    if len(sys.argv) < 3:
        print("Usage: python3.11 client-test-macaw.py <server_filter_name> <client_name>")
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]
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

    # ============================================================
    # TEST 1: chroma_create_collection — create a new collection
    # ============================================================
    print("\n" + "=" * 60)
    print("TEST 1: chroma_create_collection")
    print("=" * 60)
    r1 = await client.call_tool(
        "chroma_create_collection",
        {
            "collection_name": "physics_notes",
            "embedding_function_name": "default",
            "metadata": {"owner": "test-client", "topic": "physics"},
        },
    )
    print("create result:", r1)

    # ============================================================
    # TEST 2: chroma_add_documents — insert documents
    # ============================================================
    print("\n" + "=" * 60)
    print("TEST 2: chroma_add_documents")
    print("=" * 60)
    r2 = await client.call_tool(
        "chroma_add_documents",
        {
            "collection_name": "physics_notes",
            "documents": [
                "The sky is blue because of Rayleigh scattering.",
                "Qdrant is a vector database written in Rust.",
            ],
            "ids": ["doc-1", "doc-2"],
            "metadatas": [{"tag": "physics"}, {"tag": "database"}],
        },
    )
    print("add result:", r2)

    # ============================================================
    # TEST 3: chroma_query_documents — semantic search
    # ============================================================
    print("\n" + "=" * 60)
    print("TEST 3: chroma_query_documents (semantic match for physics)")
    print("=" * 60)
    r3 = await client.call_tool(
        "chroma_query_documents",
        {
            "collection_name": "physics_notes",
            "query_texts": ["why is the sky blue"],
            "n_results": 2,
        },
    )
    print("query result:", r3)
    assert r3 and any("Rayleigh" in str(x) for x in (r3 if isinstance(r3, list) else [r3])), \
        "FAIL: stored entry not retrievable by semantic query"
    print("PASS: semantic roundtrip works")

    # ============================================================
    # TEST 4: chroma_list_collections — verify collection is listed
    # ============================================================
    print("\n" + "=" * 60)
    print("TEST 4: chroma_list_collections")
    print("=" * 60)
    r4 = await client.call_tool(
        "chroma_list_collections",
        {},
    )
    print("list result:", r4)

    # ============================================================
    # TEST 5: chroma_delete_collection — cleanup
    # ============================================================
    print("\n" + "=" * 60)
    print("TEST 5: chroma_delete_collection")
    print("=" * 60)
    r5 = await client.call_tool(
        "chroma_delete_collection",
        {"collection_name": "physics_notes"},
    )
    print("delete result:", r5)


if __name__ == "__main__":
    asyncio.run(main())
