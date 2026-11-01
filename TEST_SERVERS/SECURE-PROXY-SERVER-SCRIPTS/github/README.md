# GitHub MCP — SecureMCPProxy

Wraps `https://api.githubcopilot.com/mcp/` over HTTPS with a bearer PAT. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- The MACAW client installed in a Python virtual environment, plus `pip install "macaw-adapters[mcp-proxy]"`, and `MACAW_HOME` set to the MACAW client folder.

Environment variables:

- `GITHUB_PERSONAL_ACCESS_TOKEN`  — required.

## Setup

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_github.py
```

Register with Claude Code:

```bash
claude mcp add github-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export GITHUB_PERSONAL_ACCESS_TOKEN="..." && \
  python /path/to/proxy_github.py'
```
