# Grafana MCP — SecureMCPProxy

Wraps `grafana/mcp-grafana` in Docker over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Docker daemon running.
- Image pulled: `docker pull grafana/mcp-grafana`.

Environment variables:

- `GRAFANA_URL`  — required.
- `GRAFANA_SERVICE_ACCOUNT_TOKEN`  — required.

## Setup

```bash
export GRAFANA_URL="..."
export GRAFANA_SERVICE_ACCOUNT_TOKEN="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_grafana.py
```

Register with Claude Code:

```bash
claude mcp add grafana-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export GRAFANA_URL="..." && \
  export GRAFANA_SERVICE_ACCOUNT_TOKEN="..." && \
  python /path/to/proxy_grafana.py'
```
