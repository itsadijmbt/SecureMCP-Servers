# Prisma AIRS MCP Relay MCP — SecureMCPProxy

Wraps `uvx pan-mcp-relay@latest --config-file mcp-relay.yaml` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`).
- `mcp-relay.yaml` in this folder configures the relay's own upstreams.

Environment variables:

- `PRISMA_AIRS_API_KEY`
- `PRISMA_AIRS_AI_PROFILE`

## Setup

```bash
export PRISMA_AIRS_API_KEY="..."
export PRISMA_AIRS_AI_PROFILE="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_pan_mcp_relay.py            # stdio
python proxy_pan_mcp_relay.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add pan-mcp-relay-macaw python /path/to/proxy_pan_mcp_relay.py \
  -e PRISMA_AIRS_API_KEY=... \
  -e PRISMA_AIRS_AI_PROFILE=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
