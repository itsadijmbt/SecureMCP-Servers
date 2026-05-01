# MongoDB MCP — SecureMCPProxy (Docker stdio)

Wraps the official `mongodb/mongodb-mcp-server` Docker image with MACAW.
One Python file, two tests.

## Prereqs

- MACAW LocalAgent running.
- Docker daemon running, image pulled:
  ```bash
  docker pull mongodb/mongodb-mcp-server:latest
  ```
- A reachable MongoDB. Local quick-start:
  ```bash
  docker run -d --name mongo-test -p 27017:27017 mongo:7
  ```

## Credentials

```bash
export MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017"
```

Or, for Atlas:

```bash
export MDB_MCP_API_CLIENT_ID="..."
export MDB_MCP_API_CLIENT_SECRET="..."
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/mongodb/proxy_mongodb.py
```

Expected: tool list on stderr, then `list-databases -> {...}`. MACAW console
shows one entry under `app_name=mongodb-proxy`.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_mongodb.py`. The Test 2 block is already active (uncommented).
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "mongodb-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/mongodb/proxy_mongodb.py"],
      "env": { "MDB_MCP_CONNECTION_STRING": "mongodb://localhost:27017" }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add mongodb-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/mongodb/proxy_mongodb.py \
  -e MDB_MCP_CONNECTION_STRING=mongodb://localhost:27017
```

Then in the CLI, prompt: *"Use the mongodb-macaw tool to call list-databases."*
MACAW console shows a second entry — originated from a real LLM client, not
the smoke test.

## Notes on what could go wrong

- The MongoDB MCP server emits `notifications/resources/updated` for
  `debug://mongodb` right after responding to `tools/list`. That notification
  arrives while the mcp SDK's stdio_client is already exiting its
  ClientSession context, so the consumer channel is closed and the SDK raises
  `BrokenResourceError`. `TolerantSecureMCPProxy` in this file ignores the
  error iff tools were already discovered — the connection is functional.
  Per-server quirk; stays in this file rather than in `SecureMCPProxy`.
- `MDB_MCP_READ_ONLY=true` is passed to the upstream container so create /
  delete / drop / update / insert / rename tools never register. Keep it on
  for testing; flip when you actually want write access.
- The container uses `--network=host` so `mongodb://localhost:27017` reaches
  the local mongo. On a non-host-network setup, replace with
  `host.docker.internal` and adjust `MDB_MCP_CONNECTION_STRING` accordingly.
