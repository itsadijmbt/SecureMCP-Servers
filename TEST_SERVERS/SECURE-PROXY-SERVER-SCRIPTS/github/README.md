# GitHub MCP — SecureMCPProxy

Wraps `https://api.githubcopilot.com/mcp/` over HTTPS with a bearer PAT. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.

Environment variables:

- `GITHUB_PERSONAL_ACCESS_TOKEN`  — required.

## Setup

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_github.py            # stdio
python proxy_github.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add github-macaw python /path/to/proxy_github.py \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
