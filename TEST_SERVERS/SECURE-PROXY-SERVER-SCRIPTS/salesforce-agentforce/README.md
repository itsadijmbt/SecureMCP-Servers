# Salesforce Agentforce MCP — SecureMCPProxy (HTTP upstream)

Wraps a self-hosted FastMCP-based Salesforce Agentforce MCP server with
MACAW. One Python file, two tests.

## Why this is different from the others

Every other server in `SECURE-PROXY-SERVER-SCRIPTS/` ships as a packaged
artifact (`docker pull ...`, `npx -y ...`). **This one doesn't.** It's
someone's Python project that you clone and run yourself — `python
server.py` on `localhost:8000`. The proxy then points at
`http://localhost:8000/mcp`.

So there are **two processes** to run:

```
Terminal A: the Agentforce MCP server (their repo)
   python server.py
   ↓ listens on http://localhost:8000/mcp

Terminal B: our wrap (this script)
   python3.11 proxy_salesforce.py
   ↓ connects to http://localhost:8000/mcp
   ↓ exposes MACAW-bound tools to Gemini/Claude
```

## Prereqs

- MACAW LocalAgent running.
- The Agentforce MCP server cloned and runnable. From its README:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env       # then edit .env
  ./run_server.sh            # or: python server.py
  ```
- A Salesforce org with Agentforce enabled (for the upstream to actually do
  anything). Required env vars in *its* `.env`:
  - `SALESFORCE_SCRT_URL`
  - `SALESFORCE_ORG_ID`
  - `SALESFORCE_ES_DEVELOPER_NAME`
  - `SALESFORCE_CAPABILITIES_VERSION` (default `258`)

## Credentials (for our proxy)

The upstream `/mcp` endpoint is **permissive** — anonymous calls pass
through. So no token is strictly required. If you want to drive it as an
authenticated user (and exercise the OAuth path), set:

```bash
export AGENTFORCE_JWT="ey..."   # JWT obtained via the server's /oauth/token flow
```

The upstream URL defaults to `http://localhost:8000/mcp`. Override:

```bash
export AGENTFORCE_MCP_URL="https://your-heroku-app.herokuapp.com/mcp"
```

## Test 1 — proxy works (1 dot)

In one terminal, start the upstream:

```bash
# In the agentforce-mcp repo:
./run_server.sh
```

In another terminal:

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/salesforce-agentforce/proxy_salesforce.py
```

Expected: tool list on stderr (likely just `agentforce_chat`), then either:

- ✓ `agentforce_chat -> {...response from Salesforce...}` — full chain working.
- ✗ `agentforce_chat -> {error: "..."}` — wrap is fine but the upstream
  isn't configured (Salesforce env vars missing in *its* `.env`). Still a
  PROXY ✓ from our side; the upstream owner needs to fix their config.

MACAW console shows one entry under `app_name=salesforce-agentforce-proxy`.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_salesforce.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI:

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "salesforce-agentforce-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/salesforce-agentforce/proxy_salesforce.py"],
      "env": {
        "AGENTFORCE_MCP_URL": "http://localhost:8000/mcp"
      }
    }
  }
}
```

The Agentforce server **must already be running** before you launch
Gemini, otherwise the spawn fails at the `SecureMCPProxy(...)` connect step
and Gemini will show `Disconnected`.

**Claude Code CLI:**

```bash
claude mcp add salesforce-agentforce-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/salesforce-agentforce/proxy_salesforce.py \
  -e AGENTFORCE_MCP_URL=http://localhost:8000/mcp
```

Then prompt: *"Use the salesforce-agentforce-macaw tool, call
agentforce_chat with message 'What can you do?'"*

## Notes on what could go wrong

- **`Connection refused` at proxy startup** — the upstream Agentforce
  server isn't running. Start it first.
- **`agentforce_chat` returns a Salesforce error** — that's the upstream's
  Salesforce config, not our wrap. Check `SALESFORCE_SCRT_URL`,
  `SALESFORCE_ORG_ID`, etc. in *their* `.env`.
- **`x-openai-session` mismatch in Gemini** — the upstream uses
  `x-openai-session` for ChatGPT-style session continuity. Gemini doesn't
  send this header; each call gets a fresh Agentforce session. Functional
  but loses conversation context — same limitation Claude/Gemini hit
  natively.
- **HTTP transport edge cases** — `SecureMCPProxy` handles MCP session IDs
  for Streamable HTTP. If you see `Mcp-Session-Id missing` errors, set
  `MCP_SESSION_MODE=stateless` in the upstream's `.env`.
- **OAuth complexity is invisible to us** — the upstream's whole DCR /
  PKCE / dual-leg OAuth flow is for browser clients (ChatGPT). We bypass
  it entirely by sending `Authorization: Bearer <pre-obtained-JWT>` (or
  nothing, since `/mcp` is permissive). If you want full OAuth, wrap with
  `mcp-remote` instead — same pattern as Figma but it should work since
  this server *does* support DCR.
