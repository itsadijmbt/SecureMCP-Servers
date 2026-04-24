from macaw_adapters.mcp import Client
import asyncio
import sys
from google import genai
from google.genai import types

SCHEMAS = {
    "search_arxiv": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for finding papers on ArXiv"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return"
            }
        },
        "required": ["query"]
    },
    "summarize_paper": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL of the ArXiv paper to summarize"
            }
        },
        "required": ["url"]
    }
}

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
        print("Usage: python3.11 client.py <server_filter_name> <client_name>")
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

    # Deduplicate stale registrations
    seen = set()
    unique_tools = []
    for t in tools:
        if t['name'] not in seen:
            seen.add(t['name'])
            unique_tools.append(t)
            print(f" - {t['name']}")

    gemini_func_decl = [
        {
            "name": t["name"],
            "description": t.get("description", ""),
            "parameters": SCHEMAS.get(t["name"], {"type": "object", "properties": {}})
        } for t in unique_tools
    ]

    gemini_tools = [{"function_declarations": gemini_func_decl}]

    ai_client = genai.Client()
    chat = ai_client.chats.create(
       model='gemini-2.0-flash',
        config=types.GenerateContentConfig(tools=gemini_tools)
    )

    print("\nGEMINI AGENT POWERED CLIENT (type 'exit' to quit)")

    while True:
        user = input("\n> ")
        if user.lower() == 'exit':
            break

        resp = chat.send_message(user)

        if resp.function_calls:
            for tool_call in resp.function_calls:
                print(f"\n[Gemini requested: {tool_call.name}({tool_call.args})]")
                try:
                    res = await asyncio.to_thread(
                        client.macaw_client.invoke_tool,
                        tool_call.name,
                        tool_call.args,
                        target_agent=server_id
                    )
                    result = res.get('result', res)
                    print(f"[Tool executed successfully]")
                except Exception as e:
                    result = f"Error: {str(e)}"
                    print(f"[Tool failed: {result}]")

                response = chat.send_message(
                    types.Part.from_function_response(
                        name=tool_call.name,
                        response={"result": result}
                    )
                )
                print(f"\nGemini: {response.text}")
        else:
            print(f"\nGemini: {resp.text}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)