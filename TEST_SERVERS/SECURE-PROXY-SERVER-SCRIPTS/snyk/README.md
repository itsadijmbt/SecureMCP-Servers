# Snyk MCP — SecureMCPProxy

Wraps `npx -y snyk@latest mcp -t stdio`. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `SNYK_TOKEN`
- `SNYK_CFG_ORG`

## Setup

```bash
export SNYK_TOKEN="..."
export SNYK_CFG_ORG="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_snyk.py            # stdio
python proxy_snyk.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add snyk-macaw python /path/to/proxy_snyk.py \
  -e SNYK_TOKEN=... \
  -e SNYK_CFG_ORG=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
