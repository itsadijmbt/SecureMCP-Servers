# CrowdStrike Falcon MCP — SecureMCPProxy

Wraps `uvx falcon-mcp` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`).
- A CrowdStrike Falcon API client (client ID and secret).

Environment variables:

- `FALCON_CLIENT_ID`  — required.
- `FALCON_CLIENT_SECRET`  — required.
- `FALCON_BASE_URL`
- `FALCON_MEMBER_CID`
- `FALCON_MCP_MODULES`

`FALCON_BASE_URL` is the API URL of your CrowdStrike region, for example `https://api.us-2.crowdstrike.com`. The default is `https://api.crowdstrike.com` (US-1). `FALCON_MCP_MODULES` is a comma separated list of modules to load, for example `hosts,detections`. The default is every module.

## Setup

```bash
export FALCON_CLIENT_ID="..."
export FALCON_CLIENT_SECRET="..."
export FALCON_BASE_URL="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_falcon.py
```

Register with Claude Code:

```bash
export MCP_TIMEOUT=120000
claude mcp add falcon-macaw python /path/to/proxy_falcon.py \
  -e FALCON_CLIENT_ID=... \
  -e FALCON_CLIENT_SECRET=... \
  -e FALCON_BASE_URL=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```

Startup takes about 100 seconds with all 169 tools, longer than Claude Code's 30s default, so set `MCP_TIMEOUT` before starting Claude Code. `FALCON_MCP_MODULES` loads fewer tools and starts faster.
