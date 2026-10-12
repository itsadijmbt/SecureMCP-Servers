# Alibaba Cloud RDS MCP — SecureMCPProxy

Wraps `uvx --with "mcp<2" alibabacloud-rds-openapi-mcp-server@latest` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`). `mcp` is pinned below 2: version 4.0.1 of the upstream does not start with mcp 2.x.
- An Alibaba Cloud AccessKey.

Environment variables:

- `ALIBABA_CLOUD_ACCESS_KEY_ID`  — required.
- `ALIBABA_CLOUD_ACCESS_KEY_SECRET`  — required.
- `ALIBABA_CLOUD_SECURITY_TOKEN`
- `MCP_TOOLSETS`

The upstream starts without the two keys, but every cloud call then fails with `InvalidCredentials`. Set `ALIBABA_CLOUD_SECURITY_TOKEN` only with an STS token. `MCP_TOOLSETS` picks the tool groups: `rds` (default, 36 tools), `rds_custom_read`, `rds_custom_all`. Example: `MCP_TOOLSETS=rds,rds_custom_all` (56 tools).

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

With the default toolset (36 tools) the proxy starts in about 27 seconds, just inside the roughly 30 seconds Claude Code waits by default. With `MCP_TOOLSETS=rds,rds_custom_all` (56 tools) it does not make it: run `export MCP_TIMEOUT=120000` in the shell that starts Claude Code.

## Policy

`Policy/server_policy_v0.1.0.json` is for the app `alibaba-rds-proxy`, the same name as `app_name` in `proxy_alibaba_rds.py`. Tools are named `tool:alibaba-rds-proxy/<tool>`.

- Allowed: 33 tools. All read tools except the ones below, plus two small write tools: `add_tags_to_db_instance` and `modify_db_instance_description`.
- Denied: 23 tools. Instance actions (create, restart, stop, start, resize, modify), network and allow-list changes, account creation, billing (`describe_bills`) and raw SQL (`query_sql`, `explain_sql`, `show_create_table`).
- Limits: `page_size` on 4 tools and `topK` on 2 tools.
- The policy covers all 56 tools of `MCP_TOOLSETS=rds,rds_custom_all`. The allow list is explicit, so a tool added by a later upstream release is blocked until it is added to the policy.

## Checked

- With `alibabacloud-rds-openapi-mcp-server` 4.0.1: 36 tools by default, 56 with `MCP_TOOLSETS=rds,rds_custom_all`, the same names, descriptions and input schemas as the upstream serves on its own.
- Without an Alibaba Cloud account. `get_current_time` returned the time. Cloud calls reached the upstream and came back with its `InvalidCredentials` error.
