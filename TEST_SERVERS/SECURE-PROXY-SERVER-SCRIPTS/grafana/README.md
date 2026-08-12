# Grafana MCP — SecureMCPProxy

Wraps `mcp/grafana` in Docker over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Docker daemon running.
- Image pulled: `docker pull mcp/grafana`.

Environment variables:

- `GRAFANA_URL`
- `GRAFANA_SERVICE_ACCOUNT_TOKEN`

## Setup

```bash
export GRAFANA_URL="..."
export GRAFANA_SERVICE_ACCOUNT_TOKEN="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_grafana.py            # stdio
python proxy_grafana.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add grafana-macaw python /path/to/proxy_grafana.py \
  -e GRAFANA_URL=... \
  -e GRAFANA_SERVICE_ACCOUNT_TOKEN=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
