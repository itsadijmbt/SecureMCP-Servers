# Salesforce Agentforce MCP — SecureMCPProxy

Wraps the Agentforce MCP server's own `server.py`, run from a local clone. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- The Agentforce MCP server cloned, with its `.venv` built (`pip install -r requirements.txt`).

Environment variables:

- `SALESFORCE_SCRT_URL`  — required.
- `SALESFORCE_ORG_ID`  — required.
- `SALESFORCE_ES_DEVELOPER_NAME`  — required.
- `SALESFORCE_CAPABILITIES_VERSION`
- `SALESFORCE_CLIENT_ID`
- `SALESFORCE_CLIENT_SECRET`
- `JWT_SECRET`  — required.
- `ACCESS_TOKEN_EXPIRATION_HOURS`
- `SERVER_URL`
- `AGENTFORCE_REPO`  — required.
- `AGENTFORCE_PY`

## Setup

```bash
export SALESFORCE_SCRT_URL="..."
export SALESFORCE_ORG_ID="..."
export SALESFORCE_ES_DEVELOPER_NAME="..."
export SALESFORCE_CAPABILITIES_VERSION="..."
export SALESFORCE_CLIENT_ID="..."
export SALESFORCE_CLIENT_SECRET="..."
export JWT_SECRET="..."
export ACCESS_TOKEN_EXPIRATION_HOURS="..."
export SERVER_URL="..."
export AGENTFORCE_REPO="..."
export AGENTFORCE_PY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_salesforce.py            # stdio
python proxy_salesforce.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add salesforce-agentforce-macaw python /path/to/proxy_salesforce.py \
  -e SALESFORCE_SCRT_URL=... \
  -e SALESFORCE_ORG_ID=... \
  -e SALESFORCE_ES_DEVELOPER_NAME=... \
  -e SALESFORCE_CAPABILITIES_VERSION=... \
  -e SALESFORCE_CLIENT_ID=... \
  -e SALESFORCE_CLIENT_SECRET=... \
  -e JWT_SECRET=... \
  -e ACCESS_TOKEN_EXPIRATION_HOURS=... \
  -e SERVER_URL=... \
  -e AGENTFORCE_REPO=... \
  -e AGENTFORCE_PY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
