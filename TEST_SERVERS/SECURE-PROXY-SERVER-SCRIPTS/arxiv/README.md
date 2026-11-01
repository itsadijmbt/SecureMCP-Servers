# arXiv MCP — SecureMCPProxy

Wraps `uvx arxiv-mcp-server` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- The MACAW client installed in a Python virtual environment, plus `pip install "macaw-adapters[mcp-proxy]"`, and `MACAW_HOME` set to the MACAW client folder.
- `uvx` on `PATH` (from `uv`).

Environment variables:

None. arXiv is a public service, so no API key or token is needed. Papers are stored in `~/.arxiv-mcp-server/papers`.

## Setup

```bash
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_arxiv.py
```

Register with Claude Code:

```bash
claude mcp add arxiv-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  python /path/to/proxy_arxiv.py'
```
