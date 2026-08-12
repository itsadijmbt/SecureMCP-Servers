"""
salesforce-agentforce-proxy -> SecureMCPProxy, served natively.

Prereq:
    export ACCESS_TOKEN_EXPIRATION_HOURS="..."
    export AGENTFORCE_PY="..."
    export AGENTFORCE_REPO="..."
    export JWT_SECRET="..."
    export SALESFORCE_CAPABILITIES_VERSION="..."
    export SALESFORCE_CLIENT_ID="..."
    export SALESFORCE_CLIENT_SECRET="..."
    export SALESFORCE_ES_DEVELOPER_NAME="..."
    export SALESFORCE_ORG_ID="..."
    export SALESFORCE_SCRT_URL="..."
    export SERVER_URL="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_salesforce.py
    python proxy_salesforce.py http 8080

Claude Code:
    claude mcp add salesforce-agentforce-macaw python /path/to/proxy_salesforce.py \
      -e ACCESS_TOKEN_EXPIRATION_HOURS=... \
      -e AGENTFORCE_PY=... \
      -e AGENTFORCE_REPO=... \
      -e JWT_SECRET=... \
      -e SALESFORCE_CAPABILITIES_VERSION=... \
      -e SALESFORCE_CLIENT_ID=... \
      -e SALESFORCE_CLIENT_SECRET=... \
      -e SALESFORCE_ES_DEVELOPER_NAME=... \
      -e SALESFORCE_ORG_ID=... \
      -e SALESFORCE_SCRT_URL=... \
      -e SERVER_URL=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    AGENTFORCE_REPO must be cloned and its .venv built:
    python -m venv .venv && .venv/bin/pip install -r requirements.txt
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

AGENTFORCE_REPO = os.environ.get("AGENTFORCE_REPO")
if not AGENTFORCE_REPO:
    raise ValueError("AGENTFORCE_REPO is not set")
AGENTFORCE_PY = os.environ.get("AGENTFORCE_PY", f"{AGENTFORCE_REPO}/.venv/bin/python")

upstream_env = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"]}
for k in ("SALESFORCE_SCRT_URL", "SALESFORCE_ORG_ID",
          "SALESFORCE_ES_DEVELOPER_NAME", "SALESFORCE_CAPABILITIES_VERSION",
          "SALESFORCE_CLIENT_ID", "SALESFORCE_CLIENT_SECRET",
          "JWT_SECRET", "ACCESS_TOKEN_EXPIRATION_HOURS", "SERVER_URL"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

for required in ("SALESFORCE_SCRT_URL", "SALESFORCE_ORG_ID",
                 "SALESFORCE_ES_DEVELOPER_NAME", "JWT_SECRET"):
    if required not in upstream_env:
        raise ValueError(f"{required} is not set")

proxy = SecureMCPProxy(
    app_name="salesforce-agentforce-proxy",
    command=[AGENTFORCE_PY, f"{AGENTFORCE_REPO}/server.py"],
    env=upstream_env,
)
logging.info("salesforce-agentforce-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("salesforce-agentforce-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

import macaw_adapters.mcp._endpoint as _endpoint

_StubClient = _endpoint.Client


def _bound_stub_client(name):
    stub = _StubClient(name)
    stub.macaw_client = bound.user_client
    return stub


_endpoint.Client = _bound_stub_client

transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
proxy.run(transport=transport, port=port)
