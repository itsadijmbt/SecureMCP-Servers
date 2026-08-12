"""
snyk-proxy -> SecureMCPProxy, served natively.

Prereq:
    export SNYK_CFG_ORG="..."
    export SNYK_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_snyk.py
    python proxy_snyk.py http 8080

Claude Code:
    claude mcp add snyk-macaw python /path/to/proxy_snyk.py \
      -e SNYK_CFG_ORG=... \
      -e SNYK_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("SNYK_TOKEN")
if not token:
    raise ValueError(
        "SNYK_TOKEN is not set. Get one at https://app.snyk.io/account "
        "(Account Settings -> API Token)."
    )

upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],
    "SNYK_TOKEN": token,
}
if os.environ.get("SNYK_CFG_ORG"):
    upstream_env["SNYK_CFG_ORG"] = os.environ["SNYK_CFG_ORG"]

proxy = SecureMCPProxy(
    app_name="snyk-proxy",
    command=["npx", "-y", "snyk@latest", "mcp", "-t", "stdio"],
    env=upstream_env,
)
logging.info("snyk-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("snyk-macaw-gateway")
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
