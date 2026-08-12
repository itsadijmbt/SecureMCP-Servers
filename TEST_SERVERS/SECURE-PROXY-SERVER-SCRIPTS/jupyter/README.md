# Jupyter MCP — SecureMCPProxy

Wraps `jupyter-mcp-server start` over stdio, against a Jupyter server you run. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `jupyter-mcp-server` installed and on `PATH`, and a running Jupyter server.

Environment variables:

- `JUPYTER_URL`
- `JUPYTER_TOKEN`
- `DOCUMENT_ID`

## Setup

```bash
export JUPYTER_URL="..."
export JUPYTER_TOKEN="..."
export DOCUMENT_ID="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_jupyter.py            # stdio
python proxy_jupyter.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add jupyter-macaw python /path/to/proxy_jupyter.py \
  -e JUPYTER_URL=... \
  -e JUPYTER_TOKEN=... \
  -e DOCUMENT_ID=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
