
# Fork Claude Session to Dispatch Agent

You are helping the user fork the current Claude Code conversation into a Dispatch agent running in a container. This creates a remote copy of you (Claude) that can run commands inside the container network, access services the local machine can't reach, and continue the conversation from a different vantage point.

## Quick Navigation

Use this to skip steps you've already completed:

- **If you can already see `dispatch-operator` MCP tools** (e.g. `create_agent`, `deploy_agent`, `invoke_function`): Skip to [Step 3: Create the Fork Agent](#step-3-create-the-fork-agent)
- **If the Dispatch CLI is installed** (`dispatch version` works): Skip to [Step 2: Register the MCP Operator](#step-2-register-the-mcp-operator)
- **If neither the CLI nor MCP tools are available**: Start at [Step 1: Install the Dispatch CLI](#step-1-install-the-dispatch-cli)
- **If the fork agent already exists** (from a previous session): Skip to [Step 5: Sync Your Brain](#step-5-sync-your-brain)

---

## Step 1: Install the Dispatch CLI

> Full docs: https://dispatchagents.ai/docs/mcp-quickstart.md

```bash
uv tool install git+ssh://git@github.com/datadog-labs/dispatch_agents_cli.git --upgrade
```

Verify with `dispatch version`. If the user isn't authenticated, run `dispatch login` to complete the browser-based Auth0 flow.

## Step 2: Register the MCP Operator

```bash
# Claude Desktop or Claude Code
dispatch mcp serve operator --register claude

# Cursor
dispatch mcp serve operator --register cursor

# Codex CLI
dispatch mcp serve operator --register codex
```

**IMPORTANT**: After running this, tell the user to reload MCP servers:

- **Claude Code**: Run `/mcp` to reload. You should see `dispatch-operator` appear.
- **Cursor**: Open Settings > MCP and click the refresh icon.
- **Codex**: Start a new session (MCP servers load on startup).

Once you can see tools like `create_agent`, `deploy_agent`, `invoke_function`, proceed to Step 3.

## Step 3: Create the Fork Agent

Use `list_namespaces` to discover available namespaces, then scaffold the agent:

```
Tool: create_agent
Parameters:
  parent_directory: <user's project directory or a subdirectory>
  agent_name: fork-claude-<username>
  description: "Fork of Claude Code session with shell access and persistent storage."
  namespace: <user's namespace>
```

### Configure dispatch.yaml

Replace the generated `dispatch.yaml` with:

```yaml
namespace: <namespace>
entrypoint: agent.py
base_image: python:3.13-slim
agent_name: fork-claude-<username>
system_packages: []
secrets:
  - name: ANTHROPIC_API_KEY
    secret_id: /shared/anthropic-api-key
volumes:
  - name: brain
    mountPath: /data
    mode: read_write_many
```

The `ANTHROPIC_API_KEY` secret powers Claude Code CLI inside the container. The `/data` volume persists conversation history across restarts and redeploys.

### Write agent.py

Replace the scaffolded `agent.py` with this implementation:

```python
"""Fork Claude agent — runs Claude Code inside a Dispatch container."""

import asyncio
import os

from dispatch_agents import BasePayload, fn, init

AGENT_NAME = os.environ.get("DISPATCH_AGENT_NAME", "fork-claude")
CONTEXT_DIR = "/app/context"
PERSISTENT_DIR = "/data/sessions"
NODE_BIN = "/tmp/nodeenv/bin"


@init
async def install_claude_code():
    """Install Node.js and Claude Code CLI at container startup."""
    proc = await asyncio.create_subprocess_exec(
        "pip", "install", "nodeenv",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    proc = await asyncio.create_subprocess_exec(
        "python", "-m", "nodeenv", "--node=22.14.0", "/tmp/nodeenv",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    env = {**os.environ, "PATH": f"{NODE_BIN}:{os.environ.get('PATH', '')}"}
    proc = await asyncio.create_subprocess_exec(
        f"{NODE_BIN}/npm", "install", "-g", "@anthropic-ai/claude-code",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    await proc.communicate()

    os.makedirs(PERSISTENT_DIR, exist_ok=True)
    os.makedirs(CONTEXT_DIR, exist_ok=True)

    proc = await asyncio.create_subprocess_exec(
        f"{NODE_BIN}/claude", "--version",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    stdout, _ = await proc.communicate()
    print(f"[INIT] Claude Code {stdout.decode().strip()} installed")


class SyncBrainRequest(BasePayload):
    """Send conversation history to the agent."""
    session_jsonl: str
    session_name: str = "current"


class SyncBrainResult(BasePayload):
    success: bool
    message: str
    bytes_written: int = 0


@fn()
async def sync_brain(payload: SyncBrainRequest) -> SyncBrainResult:
    """Upload a conversation transcript (JSONL) to the agent.

    Stores in persistent /data volume and sets up Claude Code session directory.
    """
    filename = f"{payload.session_name}.jsonl"
    bytes_written = 0

    for target_dir in [CONTEXT_DIR, PERSISTENT_DIR]:
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, filename)
        with open(path, "w") as f:
            f.write(payload.session_jsonl)
        bytes_written = len(payload.session_jsonl.encode())

    home = os.environ.get("HOME", "/tmp")
    claude_dir = f"{home}/.claude/projects/-app"
    os.makedirs(claude_dir, exist_ok=True)
    with open(f"{claude_dir}/{payload.session_name}.jsonl", "w") as f:
        f.write(payload.session_jsonl)

    return SyncBrainResult(
        success=True,
        message=f"Synced {bytes_written} bytes as '{filename}'",
        bytes_written=bytes_written,
    )


class RunClaudeRequest(BasePayload):
    """Run Claude Code with a prompt, optionally resuming a conversation."""
    prompt: str
    session_name: str | None = None
    model: str = "opus"
    max_budget_usd: float = 10.0


class RunClaudeResult(BasePayload):
    success: bool
    output: str
    error: str | None = None


@fn()
async def run_claude(payload: RunClaudeRequest) -> RunClaudeResult:
    """Spawn Claude Code CLI inside the container.

    If session_name is provided and a matching JSONL exists, resumes that conversation.
    """
    env = {
        **os.environ,
        "PATH": f"{NODE_BIN}:{os.environ.get('PATH', '')}",
        "HOME": os.environ.get("HOME", "/tmp"),
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    }

    cmd = [
        f"{NODE_BIN}/claude", "-p",
        "--dangerously-skip-permissions",
        "--model", payload.model,
        "--max-budget-usd", str(payload.max_budget_usd),
    ]

    if payload.session_name:
        cmd.extend(["--resume", payload.session_name])

    cmd.append(payload.prompt)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd="/app",
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
        return RunClaudeResult(
            success=proc.returncode == 0,
            output=stdout.decode(),
            error=stderr.decode() if proc.returncode != 0 else None,
        )
    except asyncio.TimeoutError:
        return RunClaudeResult(
            success=False, output="", error="Timed out after 5 minutes",
        )
    except Exception as e:
        return RunClaudeResult(success=False, output="", error=str(e))


class RunCommandRequest(BasePayload):
    """Run a shell command inside the container."""
    command: str
    timeout_seconds: int = 60


class RunCommandResult(BasePayload):
    stdout: str
    stderr: str
    returncode: int


@fn()
async def run_command(payload: RunCommandRequest) -> RunCommandResult:
    """Execute an arbitrary shell command inside the container."""
    try:
        proc = await asyncio.create_subprocess_shell(
            payload.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=payload.timeout_seconds,
        )
        return RunCommandResult(
            stdout=stdout.decode(), stderr=stderr.decode(),
            returncode=proc.returncode or 0,
        )
    except asyncio.TimeoutError:
        return RunCommandResult(
            stdout="", stderr=f"Timed out after {payload.timeout_seconds}s",
            returncode=-1,
        )


class ListConversationsResult(BasePayload):
    conversations: list[str]
    persistent: bool


@fn()
async def list_conversations(payload: BasePayload) -> ListConversationsResult:
    """List all conversation threads stored on persistent storage."""
    sessions = []
    persistent = os.path.exists(PERSISTENT_DIR)
    if persistent:
        sessions = [
            f.removesuffix(".jsonl")
            for f in os.listdir(PERSISTENT_DIR)
            if f.endswith(".jsonl")
        ]
    return ListConversationsResult(conversations=sorted(sessions), persistent=persistent)
```

## Step 4: Deploy the Agent

```
Tool: deploy_agent
Parameters:
  agent_directory: <path to fork-claude-<username> directory>
```

Wait for deployment (3-5 min). The `@init` function automatically installs Node.js and Claude Code CLI when the container starts.

Verify with:
```
Tool: list_agents
Parameters:
  namespace: <namespace>
```

## Step 5: Sync Your Brain

Read the current conversation transcript and send it to the agent. Session files live at:

```
~/.claude/projects/<project-path-hash>/<session-id>.jsonl
```

Find the current session (most recently modified `.jsonl` file):

```bash
ls -lt ~/.claude/projects/*/  | head -10
```

Send it to the agent:

```
Tool: invoke_function
Parameters:
  agent_name: fork-claude-<username>
  function_name: sync_brain
  namespace: <namespace>
  payload:
    session_jsonl: <contents of the JSONL file>
    session_name: <session-id>
```

**Note**: If the JSONL is too large for the invoke payload, pass a text summary via `run_claude` prompt instead.

## Step 6: Talk to Your Fork

The forked Claude has full shell access, network access to container services, your conversation history, and persistent storage at `/data`.

### Resume the conversation:

```
Tool: invoke_function
Parameters:
  agent_name: fork-claude-<username>
  function_name: run_claude
  namespace: <namespace>
  payload:
    prompt: "You've been forked into a container. <instructions>"
    session_name: <session-id>
    model: opus
```

### Run a quick command:

```
Tool: invoke_function
Parameters:
  agent_name: fork-claude-<username>
  function_name: run_command
  namespace: <namespace>
  payload:
    command: "python -c \"import httpx; print(httpx.get('http://host.docker.internal:8000/health').text)\""
```

### Update the fork with new context:

Re-invoke `sync_brain` with the latest JSONL anytime. Use `list_conversations` to see all synced threads.

## Tips

- **Model choice**: `opus` for deep reasoning, `sonnet` for quick commands
- **Budget**: `max_budget_usd` caps API spend per invocation
- **Multiple threads**: Different `session_name` values = parallel conversation branches
- **Pentesting**: Ideal for security testing from inside the container network
- **Chaining**: 5-minute timeout per invocation — chain multiple `run_claude` calls for longer work
