# Dispatch CLI MCP Server

There are two types of MCP server provided by the dispatch CLI:

## Operator
This MCP server provides tools to manage Dispatch Agents, including creating, deploying, and getting logs.

### Server Instructions

The operator MCP server includes built-in instructions that help AI agents understand how to configure
Dispatch agents. These instructions cover:

- **Agent configuration** (`.dispatch.yaml`) - Required and optional fields
- **Persistent storage** (`persist_storage: true`) - Persistent `/data` directory
- **Secrets** - Injecting secrets as environment variables
- **Agent functions** - Using the `@fn()` decorator from the SDK
- **Workflow** - Create → Configure → Implement → Test → Deploy

AI clients (like Claude) automatically receive these instructions when connecting to the MCP server.

To inspect the MCP server locally, run this command:
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost
```

You can also list tools directly in your terminal, e.g.
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli --method tools/list \
  | jq '.tools[] | {name, description}'
```

You can also invoke tools (e.g. to create an agent):
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli --method tools/call \
  --tool-name create_agent \
  --tool-arg 'request={"parent_directory": "examples", "agent_name": "dispatch-mcp-test", "description": "Agent created using dispatch CLI MCP server", "namespace": "examples"}'
```

Note: Operator tools use Pydantic models for inputs, so arguments must be passed as a nested `request` object.

### Local Development Tools

The operator MCP server includes tools for local development and testing:

#### Stop Local Router
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli --method tools/call \
  --tool-name stop_local_router \
  --tool-arg 'request={}'
```

#### Send Test Event to Local Router
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli --method tools/call \
  --tool-name send_local_test_event \
  --tool-arg 'request={"topic": "test", "payload": {"subject": "world"}, "agent_directory": "examples/hello_world"}'
```

#### Start Agent in Dev Mode
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli --method tools/call \
  --tool-name start_local_agent_dev \
  --tool-arg 'request={"agent_directory": "examples/hello_world"}'
```

#### Read Local Agent Logs
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli --method tools/call \
  --tool-name read_local_agent_logs \
  --tool-arg 'request={"agent_directory": "examples/hello_world", "lines": 50}'
```

### Prompts

The operator MCP server includes helpful prompts for common workflows:

#### Local Agent Dev Workflow
An interactive prompt that guides you through testing an agent locally:
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-operator-localhost \
  --cli --method prompts/get \
  --prompt-name local_agent_dev
```

This prompt:
- Automatically discovers available agent directories (searches for dispatch.yaml files)
- Asks you to select which agent to test
- Guides you through:
  1. Starting the agent in dev mode
  2. Selecting a function/topic to test
  3. Sending a test event with appropriate payload
  4. Checking logs for errors

## Agent
This MCP server provides tools to interact with a deployed agent. It dynamically generates a tool for each of the agent's registered functions.

Inspect:
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-agent-examples-hello-world
```

List tools:
```bash
npx --min-release-age=30 @modelcontextprotocol/inspector \
  --config $(git rev-parse --show-toplevel)/.mcp.json \
  --server dispatch-agent-examples-hello-world \
  --cli --method tools/list \
  | jq '.tools[] | {name, description}'
```
