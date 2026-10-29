# Supabase MCP — SecureMCPProxy

Wraps `npx -y mcp-remote https://mcp.supabase.com/mcp` — OAuth in the browser on first run. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js 20+ on `PATH` (`mcp-remote` needs it).

Environment variables:

- `SUPABASE_PROJECT_REF`

## Setup

```bash
export SUPABASE_PROJECT_REF="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_supabase.py
```

Register with Claude Code:

```bash
claude mcp add supabase-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export SUPABASE_PROJECT_REF="..." && \
  python /path/to/proxy_supabase.py'
```
