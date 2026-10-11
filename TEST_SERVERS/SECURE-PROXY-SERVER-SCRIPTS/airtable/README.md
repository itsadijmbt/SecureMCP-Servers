# Airtable MCP — SecureMCPProxy

Wraps `npx -y airtable-mcp-server` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `AIRTABLE_API_KEY`  — required.

## Setup

```bash
export AIRTABLE_API_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_airtable.py
```

Register with Claude Code:

```bash
claude mcp add airtable-macaw python /path/to/proxy_airtable.py \
  -e AIRTABLE_API_KEY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
