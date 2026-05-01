# Terraform MCP — SecureMCPProxy (Docker stdio)

Wraps the official `hashicorp/terraform-mcp-server` Docker image with MACAW.
One Python file, two tests.

## Why this one is auth-free for smoke

The default toolset (`registry`) talks to the public Terraform Registry —
no token, no account. Only the `terraform` (HCP Terraform / Enterprise
workspaces) and `registry-private` toolsets need `TFE_TOKEN`. The smoke
test uses `search_providers`, which is registry-only.

## Prereqs

- MACAW LocalAgent running.
- Docker daemon running. Image pulled (or pulled on first run):
  ```bash
  docker pull hashicorp/terraform-mcp-server:0.5.2
  ```

## Credentials (optional)

For HCP Terraform / Enterprise tools (workspaces, runs, private modules),
set:

```bash
export TFE_TOKEN="..."                          # required for HCP/TFE
export TFE_ADDRESS="https://app.terraform.io"   # default; override for self-hosted TFE
```

For **only** public registry usage (the smoke test), leave both unset.

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/terraform/proxy_terraform.py
```

Expected: tool list on stderr, then `search_providers -> [{...aws...}, ...]`
returning popular AWS providers from the public registry. MACAW console
shows one entry under `app_name=terraform-proxy`.

First run downloads the Docker image (~50 MB). Subsequent runs reuse it.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_terraform.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "terraform-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/terraform/proxy_terraform.py"],
      "env": {}
    }
  }
}
```

(Add `"TFE_TOKEN": "..."` to `env` only if you'll exercise workspace tools.)

**Claude Code CLI:**

```bash
claude mcp add terraform-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/terraform/proxy_terraform.py
```

Then prompt: *"Use the terraform-macaw tool to search for the AWS provider
and show its latest version and download URL."* MACAW console shows a
second entry from the LLM client.

## Notes on what could go wrong

- **`docker: command not found` from the Python script** — `docker` not on
  the venv shell's PATH. Verify with `which docker`. The proxy forwards the
  parent's PATH to the subprocess explicitly, so this should be fine if
  `docker` runs from your shell.
- **First-run pull stalls** — the script's stdio transport doesn't surface
  Docker pull progress. If Test 1 hangs >60s, run `docker pull
  hashicorp/terraform-mcp-server:0.5.2` manually first.
- **`401 Unauthorized` on workspace tools** — `TFE_TOKEN` is missing or
  scoped wrong. Public registry tools (`search_providers`,
  `get_provider_details`, `search_modules`) do not need a token; workspace
  tools (`list_workspaces`, `create_workspace`) do.
- **TLS errors behind a corporate proxy (Zscaler, etc.)** — mount your
  corporate CA into the container. See the upstream README's Troubleshooting
  section; pass `-v /path/ca.pem:/etc/ssl/certs/corporate-ca.pem -e
  SSL_CERT_FILE=/etc/ssl/certs/corporate-ca.pem` in the `docker_args` list
  in `proxy_terraform.py`.
- **Tool filtering** — to expose only a subset (e.g. just registry tools),
  add `"--toolsets=registry"` to the end of `docker_args`. Keeps the LLM's
  context window smaller.
