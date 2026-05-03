# Azure MCP — SecureMCPProxy (npx stdio)

Wraps the official `@azure/mcp` npm package (Microsoft's Azure MCP server,
all Azure tools in one stdio server) with MACAW. One Python file, two
tests.

The wrap pattern is the same as Postman / Airtable / Notion — local stdio
via `npx -y` — but the auth model is **Azure Identity SDK**, not a static
token. That means either an `az login` session or service principal env
vars.

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node -v && npx --version`).
- An Azure subscription. Free tier ($200 / 30-day credit for new accounts)
  is enough for read-only smoke testing.
- **One of**:
  - **Azure CLI** installed and logged in: `az login` (recommended for dev).
  - **Service principal** credentials in env (recommended for CI).

## Auth — pick one

### A. Azure CLI session (recommended for dev)

```bash
# Install Azure CLI if missing (Linux):
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Sign in interactively:
az login
```

This drops creds in `~/.azure/`. The script forwards `HOME` to the upstream
subprocess so `@azure/mcp` picks them up automatically. No env vars to set.

### B. Service principal (headless)

Create one once:

```bash
az ad sp create-for-rbac --name macaw-azure-mcp --role Reader \
   --scopes /subscriptions/<subId>
```

That prints a JSON with `appId`, `password`, `tenant`. Map them:

```bash
export AZURE_TENANT_ID="<tenant>"
export AZURE_CLIENT_ID="<appId>"
export AZURE_CLIENT_SECRET="<password>"
export AZURE_SUBSCRIPTION_ID="<subId>"
```

The script forwards all four when set.

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/azure/proxy_azure.py
```

Expected: tool list on stderr (~50–80 tools depending on Azure MCP
version — Azure exposes a lot), then `subscription_list -> [...]` listing
your subscriptions.

If `subscription_list` errors with "tool not found", read the printed
tools list and swap the name on line 50 of `proxy_azure.py`. Common
alternatives: `azmcp_subscription_list`, `subscription_account_list`.
Microsoft renames these between versions; the printed list is the source
of truth.

First run: 30s+ for `npx -y` to fetch `@azure/mcp` (large package).
Subsequent runs are fast.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_azure.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "azure-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/azure/proxy_azure.py"],
      "env": {
        "AZURE_TENANT_ID": "...",
        "AZURE_CLIENT_ID": "...",
        "AZURE_CLIENT_SECRET": "..."
      }
    }
  }
}
```

(Or omit the `env` block and rely on `az login` — but only if the user
running Gemini is the same OS user that ran `az login`, otherwise the
spawned subprocess won't see `~/.azure/`.)

**Claude Code CLI:**

```bash
claude mcp add azure-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/azure/proxy_azure.py \
  -e AZURE_TENANT_ID=... -e AZURE_CLIENT_ID=... -e AZURE_CLIENT_SECRET=...
```

Then prompt: *"Use the azure-macaw tool to list my Azure subscriptions."*
MACAW console shows a second entry from the LLM client.

## Notes on what could go wrong

- **`az NOT INSTALLED`** — install Azure CLI (see Prereqs).
- **First run hangs ~30s** — `npx` is downloading `@azure/mcp`. It's a big
  package; be patient.
- **`DefaultAzureCredential failed`** — neither `az login` nor SP env vars
  worked. Run `az account show` to verify CLI auth, or print the env vars
  to verify they're populated.
- **`Tool not found: subscription_list`** — Azure MCP renamed it. Read the
  printed tools list and swap on line 50.
- **`AuthorizationFailed: Caller does not have permission`** — your
  identity / SP doesn't have `Reader` on the target resource. For smoke
  testing, `Reader` at subscription scope is enough.
- **No subscriptions returned** — the identity is authenticated but has
  no subscriptions associated. Free Azure tier accounts get one free
  subscription on signup; corporate accounts may need an admin to assign
  one.

## Sister server: Microsoft Fabric MCP

Same `microsoft/mcp` repo, separate server:
`@microsoft/fabric-mcp-server` (or similar — check the repo). Same wrap
shape; same Azure-Identity-style auth. Wrap it as `proxy_fabric.py` if /
when you need it. Not in scope for this folder.
