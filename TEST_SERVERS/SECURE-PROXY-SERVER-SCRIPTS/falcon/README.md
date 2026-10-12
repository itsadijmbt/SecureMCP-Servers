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

`FALCON_BASE_URL` is the API URL of your CrowdStrike region, for example `https://api.us-2.crowdstrike.com`. Without it the upstream uses `https://api.crowdstrike.com` (US-1). `FALCON_MCP_MODULES` is a comma separated list of modules to load, for example `hosts,detections`. Without it every module is loaded.

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

`MCP_TIMEOUT` is needed. With all 169 tools the proxy takes about 100 seconds to start (start-up grows by about half a second per tool). Claude Code waits about 30 seconds by default and then shows the server as failed. Set it in the shell that starts Claude Code. The other way is to load fewer modules with `FALCON_MCP_MODULES` (`hosts` alone is 6 tools).

## Policy

`Policy/server_policy_v0.1.0.json` is for the app `falcon-proxy`, the same name as `app_name` in `proxy_falcon.py`. Tools are named `tool:falcon-proxy/<tool>`.

- Allowed: 124 tools. These are the tools the upstream itself marks as read-only.
- Denied: 45 tools. These are the tools the upstream marks as not read-only: create, update and delete tools, RTR sessions and commands, workflow runs, agent invocations.
- Limits: 114 number parameters on 88 tools, set to the upstream's own minimum and maximum. Example: `limit` on `falcon_search_hosts` must be 1 to 5000.
- The allow list is explicit. A tool added by a later upstream release is blocked until it is added to the policy.

## Checked

- With `falcon-mcp` 0.19.0: 169 tools, the same names, descriptions and input schemas as the upstream serves on its own.
- Against a local stand-in for the Falcon API, not a real Falcon tenant. No Falcon keys were available.
- The upstream logs in to the Falcon API when it starts. With wrong keys it stops, and the proxy does not start.
