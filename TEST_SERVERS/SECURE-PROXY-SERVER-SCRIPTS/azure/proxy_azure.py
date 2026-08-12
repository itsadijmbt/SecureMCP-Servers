"""
azure-proxy -> SecureMCPProxy, served natively.

Prereq:
    export AZURE_CLIENT_ID="..."
    export AZURE_CLIENT_SECRET="..."
    export AZURE_SUBSCRIPTION_ID="..."
    export AZURE_TENANT_ID="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_azure.py
    python proxy_azure.py http 8080

Claude Code:
    claude mcp add azure-macaw python /path/to/proxy_azure.py \
      -e AZURE_CLIENT_ID=... \
      -e AZURE_CLIENT_SECRET=... \
      -e AZURE_SUBSCRIPTION_ID=... \
      -e AZURE_TENANT_ID=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],
}
for k in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET",
          "AZURE_SUBSCRIPTION_ID"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="azure-proxy",
    command=["npx", "-y", "@azure/mcp@latest", "server", "start"],
    env=upstream_env,
)
logging.info("azure-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("azure-macaw-gateway")
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
