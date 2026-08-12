# Terraform MCP — SecureMCPProxy

Wraps `hashicorp/terraform-mcp-server:0.5.2` in Docker over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Image pulled: `docker pull hashicorp/terraform-mcp-server:0.5.2`.

Environment variables:

- `TFE_TOKEN`
- `TFE_ADDRESS`

## Setup

```bash
export TFE_TOKEN="..."
export TFE_ADDRESS="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_terraform.py            # stdio
python proxy_terraform.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add terraform-macaw python /path/to/proxy_terraform.py \
  -e TFE_TOKEN=... \
  -e TFE_ADDRESS=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
