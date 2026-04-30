
# Getting Started with Dispatch Agents

You are helping the user build their first Dispatch Agent. Walk them through the process step by step, adapting to what they want to build.

## Step 0: Check Prerequisites

Before building an agent, ensure the Dispatch CLI is installed and authenticated.

### Check CLI Installation

Run `dispatch version` to check if the CLI is installed. If it fails or is not found:

```bash
uv tool install git+ssh://git@github.com/datadog-labs/dispatch_agents_cli.git --upgrade
```

### Authenticate

Run `dispatch login` to authenticate in the browser with Auth0. This is the normal path for human CLI usage and matches the web app login experience.

If the user is intentionally running the CLI in a machine or CI context, `DISPATCH_API_KEY` still works as an explicit override.

### Set Up LLM Providers for Local Dev

If the agent will use LLM features (`llm.chat()` or Claude Agent SDK), run the interactive setup wizard:

```bash
dispatch llm setup
```

This walks through configuring API keys for local development. Keys are stored in the macOS Keychain and used by the local router's LLM gateway.

Once the CLI is installed and authenticated, proceed to Step 1.

## Step 1: Scaffold the Agent

Use the MCP `create_agent` tool to scaffold a new agent directory:

```
Tool: create_agent
Parameters:
  parent_directory: <current working directory>
  agent_name: <name the user wants, kebab-case>
  description: <what the agent does>
```

This creates a directory with:
- `agent.py` — the main entrypoint with handler functions
- `dispatch.yaml` — deployment configuration
- `pyproject.toml` — Python dependencies

## Step 2: Write Handler Functions

Dispatch agents expose functionality through decorated async functions. There are two patterns:

### Pattern A: Direct Functions (`@fn`)

Use `@fn()` for functions that other agents (or the platform) call directly by name. This is the most common pattern for service-style agents.

```python
from dispatch_agents import BasePayload, fn

class MyRequest(BasePayload):
    query: str

class MyResponse(BasePayload):
    answer: str

@fn()
async def my_function(payload: MyRequest) -> MyResponse:
    """Process the request and return a response."""
    return MyResponse(answer=f"Processed: {payload.query}")
```

Calling from another agent:

```python
from dispatch_agents import invoke

# Returns a dict by default
result = await invoke("agent-name", "my_function", {"query": "hello"})

# Or with typed response
result = await invoke("agent-name", "my_function", {"query": "hello"}, response_model=MyResponse)
```

### Pattern B: Topic Subscribers (`@on`)

Use `@on(topic="...")` for event-driven handlers that react to messages on a topic. Multiple agents can subscribe to the same topic.

```python
from dispatch_agents import BasePayload, on

class OrderPayload(BasePayload):
    order_id: str
    amount: float

class OrderConfirmation(BasePayload):
    order_id: str
    status: str

@on(topic="orders.created")
async def handle_new_order(payload: OrderPayload) -> OrderConfirmation:
    """React to new order events."""
    return OrderConfirmation(order_id=payload.order_id, status="confirmed")
```

Publishing events from another agent:

```python
from dispatch_agents import emit_event

await emit_event("orders.created", {"order_id": "123", "amount": 99.99})
```

### Pattern C: GitHub Event Handlers

Subscribe to GitHub webhook events:

```python
from dispatch_agents import on
from dispatch_agents.integrations.github import PullRequestReviewCommentCreated

@on(github_event=PullRequestReviewCommentCreated)
async def on_pr_review_comment(event: PullRequestReviewCommentCreated) -> None:
    print(f"Comment from {event.comment.user.login}: {event.comment.body}")
```

### Key Rules for Handlers

1. **All payloads must inherit from `BasePayload`** (which extends Pydantic's `BaseModel` with strict validation).
2. **All handlers must be `async`** functions.
3. **The first parameter must be typed** with a `BasePayload` subclass.
4. **Return type** must be a `BasePayload` subclass or `None`.
5. **Handler names must be unique** across the agent.
6. **`ValueError`** = non-retryable error. **`OSError`** = retryable error.

## Step 3: Using LLMs in Your Agent

You can use any LLM framework you like — the Dispatch LLM Gateway proxies requests so your agent doesn't need to manage API keys directly. The gateway sets standard environment variables (`OPENAI_BASE_URL`, `ANTHROPIC_BASE_URL`) that most SDKs pick up automatically.

If you don't have a preference, here are two good defaults:

### Simple LLM calls: `dispatch_agents.llm`

For straightforward prompt-in, text-out patterns (chat completion, summarization, classification):

```python
from dispatch_agents import llm

response = await llm.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": payload.query},
    ],
)
reply = response.choices[0].message.content
```

### Agentic workflows: Claude Agent SDK

For agents that need tool calling, MCP server connections, web browsing, file creation, or multi-step reasoning:

```python
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

options = ClaudeAgentOptions(
    model="claude-sonnet-4-20250514",
    system_prompt="You are a research analyst.",
    tools=["WebSearch", "WebFetch"],
)

result: ResultMessage = await query(
    prompt=payload.query,
    options=options,
)
```

Install as a dependency:

```bash
cd <agent-directory>
uv add claude-agent-sdk
```

## Step 4: Add Dependencies

### Python packages

Add Python dependencies using `uv`:

```bash
cd <agent-directory>
uv add httpx  # or any pip-installable package
```

### System packages

For OS-level packages (e.g., `ffmpeg`, `git`), add them in `dispatch.yaml`:

```yaml
system_packages:
  - ffmpeg
  - git
```

### Secrets

For secrets your agent needs at runtime (database URLs, third-party API keys, etc.):

1. **Add to `dispatch.yaml`** so Dispatch knows about them:

```yaml
secrets:
  - name: MY_API_KEY
    secret_id: /my-agent/api-key
```

2. **Create a `.env` file** in the agent directory for local development:

```
MY_API_KEY=sk-...
```

The `.env` file is automatically loaded by `dispatch agent dev`. Access secrets as environment variables in your code:

```python
import os
api_key = os.environ["MY_API_KEY"]
```

3. **Upload to production** before deploying — run this from the agent directory:

```bash
dispatch secret manage --upload
```

This reads values from `.env`, checks what's already uploaded, and prompts before overwriting.

**Important:** Do NOT add LLM provider API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY) as agent secrets. These are handled automatically by the LLM Gateway — configure them with `dispatch llm local` for local dev, or `dispatch llm configure` for production.

## Step 5: Use Memory APIs (Optional)

Dispatch provides three types of persistent memory. Import the singleton client:

```python
from dispatch_agents import memory
```

### Long-term Memory (Key-Value Store)

```python
# Store a value (agent_name auto-detected from DISPATCH_AGENT_NAME env var)
# Returns MemoryWriteResponse with .message field
await memory.long_term.add(mem_key="user_prefs", mem_val='{"theme": "dark"}')

# Retrieve a value — returns KVGetResponse with .value (str | None)
result = await memory.long_term.get(mem_key="user_prefs")
if result.value is not None:
    prefs = json.loads(result.value)

# Delete a value — returns MemoryWriteResponse
await memory.long_term.delete(mem_key="user_prefs")

# Read another agent's data by overriding agent_name
result = await memory.long_term.get(mem_key="config", agent_name="other-agent")
```

### Short-term Memory (Session Store)

```python
# Store session data — returns MemoryWriteResponse
await memory.short_term.add(session_id="sess-123", session_data={"step": 1, "context": "..."})

# Retrieve session — returns SessionGetResponse with .session_data (dict)
result = await memory.short_term.get(session_id="sess-123")
session = result.session_data  # dict[str, Any]

# Delete session — returns MemoryWriteResponse
await memory.short_term.delete(session_id="sess-123")
```

**Note:** Memory APIs require the backend to be running. In local dev mode, use persistent storage (`volumes`) for file-based persistence instead.

## Step 6: Use Persistent Storage (Optional)

For file-based persistence, configure a volume in `dispatch.yaml`:

```yaml
volumes:
  - name: data
    mountPath: /data
    mode: read_write_many
```

Then use `get_data_dir()` in your agent code:

```python
from dispatch_agents import get_data_dir

DATA_DIR = get_data_dir()
my_file = DATA_DIR / "state.json"
my_file.write_text('{"count": 0}')
```

`get_data_dir()` returns `/data` in production (EFS mount) and a local mock directory during `dispatch agent dev`.

## Step 7: Test Locally

Use the MCP `start_local_agent_dev` tool to start the agent in dev mode:

```
Tool: start_local_agent_dev
Parameters:
  agent_directory: <path to agent directory>
```

This automatically starts the local router if it isn't already running.

### Invoke a `@fn()` function locally

Use the MCP `invoke_local_function` tool:

```
Tool: invoke_local_function
Parameters:
  agent_directory: <path to agent directory>
  function_name: "my_function"
  payload: {"query": "hello"}
```

### Send a test event to a `@on()` handler locally

Use the MCP `send_local_test_event` tool:

```
Tool: send_local_test_event
Parameters:
  topic: "orders.created"
  payload: {"order_id": "123", "amount": 99.99}
  agent_directory: <path to agent directory>
```

### Read local agent logs

Use the MCP `read_local_agent_logs` tool:

```
Tool: read_local_agent_logs
Parameters:
  agent_directory: <path to agent directory>
```

### Stop local dev

When done testing, stop the local router:

```
Tool: stop_local_router
```

## Step 8: Deploy

If the agent uses secrets, make sure they're uploaded first (from the agent directory):

```bash
dispatch secret manage --upload
```

Then deploy using the MCP `deploy_agent` tool:

```
Tool: deploy_agent
Parameters:
  agent_directory: <path to agent directory>
```

After deployment, invoke the agent remotely:

```
Tool: invoke_function
Parameters:
  agent_name: "my-agent"
  function_name: "my_function"
  payload: {"query": "hello"}
```

## Common Issues

### "No handler registered for topic: X"

The topic string in `@on(topic="X")` must exactly match the topic used in `emit_event("X", ...)`. Check for typos and case sensitivity.

### Payload validation errors

All payload fields must match the `BasePayload` subclass definition exactly. `BasePayload` uses strict validation — extra fields are rejected, missing required fields raise errors. Check field names, types, and required vs optional.

### Import errors on deploy

Make sure all Python dependencies are in `pyproject.toml` (use `uv add <package>`). System packages go in `dispatch.yaml` under `system_packages`.

### Handler not found on invoke

- For `@fn()`: the function name in `invoke("agent", "function_name", ...)` must match the Python function name (or the `name=` parameter if specified).
- For `@on()`: handlers are invoked via their topic. Use `emit_event(topic, payload)` not `invoke()`.

### Local dev not receiving events

Make sure the local router is running (`start_local_agent_dev` or `dispatch agent dev` will start it automatically). Check agent logs with `read_local_agent_logs` for errors, or run `dispatch router logs` for router-level issues.

### LLM calls failing locally

Make sure you've configured LLM provider API keys for local dev:

```bash
dispatch llm setup
```

Then restart the router (`dispatch router stop && dispatch router start`).

## Complete Example

Here is a minimal working agent using `llm.chat()`:

```python
"""My first Dispatch agent."""

from dispatch_agents import BasePayload, fn, llm

class AskRequest(BasePayload):
    question: str

class AskResponse(BasePayload):
    answer: str

@fn()
async def ask(payload: AskRequest) -> AskResponse:
    """Answer a question using an LLM."""
    response = await llm.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Be concise."},
            {"role": "user", "content": payload.question},
        ],
    )
    return AskResponse(answer=response.choices[0].message.content)
```

With `dispatch.yaml`:

```yaml
namespace: my-namespace
entrypoint: agent.py
base_image: python:3.13-slim
agent_name: my-agent
```
