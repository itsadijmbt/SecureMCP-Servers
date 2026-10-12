# Alibaba Cloud RDS MCP — SecureMCPProxy

Wraps `uvx --with "mcp<2" alibabacloud-rds-openapi-mcp-server@latest` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`).
- An Alibaba Cloud AccessKey.

Environment variables:

- `ALIBABA_CLOUD_ACCESS_KEY_ID`  — required.
- `ALIBABA_CLOUD_ACCESS_KEY_SECRET`  — required.
- `ALIBABA_CLOUD_SECURITY_TOKEN`
- `MCP_TOOLSETS`

Set `ALIBABA_CLOUD_SECURITY_TOKEN` only with an STS token. `MCP_TOOLSETS` picks the tool groups: `rds` (default, 36 tools), `rds_custom_read`, `rds_custom_all`. Example: `MCP_TOOLSETS=rds,rds_custom_all` (56 tools).

## Setup

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="..."
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_alibaba_rds.py
```

Register with Claude Code:

```bash
claude mcp add alibaba-rds-macaw python /path/to/proxy_alibaba_rds.py \
  -e ALIBABA_CLOUD_ACCESS_KEY_ID=... \
  -e ALIBABA_CLOUD_ACCESS_KEY_SECRET=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```

With `MCP_TOOLSETS=rds,rds_custom_all`, startup can exceed Claude Code's 30s default. Run `export MCP_TIMEOUT=120000` before starting Claude Code.
