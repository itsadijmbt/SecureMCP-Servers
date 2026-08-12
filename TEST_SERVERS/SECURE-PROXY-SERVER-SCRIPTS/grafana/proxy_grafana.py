"""
grafana-proxy -> SecureMCPProxy, served natively.

Prereq:
    export GRAFANA_SERVICE_ACCOUNT_TOKEN="..."
    export GRAFANA_URL="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_grafana.py
    python proxy_grafana.py http 8080

Claude Code:
    claude mcp add grafana-macaw python /path/to/proxy_grafana.py \
      -e GRAFANA_SERVICE_ACCOUNT_TOKEN=... \
      -e GRAFANA_URL=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

grafana_url = os.environ.get("GRAFANA_URL")
token = os.environ.get("GRAFANA_SERVICE_ACCOUNT_TOKEN")
if not grafana_url or not token:
    raise ValueError(
        "Set GRAFANA_URL (e.g. http://localhost:3000) and "
        "GRAFANA_SERVICE_ACCOUNT_TOKEN (glsa_...)"
    )


proxy = SecureMCPProxy(
    app_name="grafana-proxy",
    command=[
        "docker", "run", "--rm", "-i", "--network=host",
        "-e", "GRAFANA_URL",
        "-e", "GRAFANA_SERVICE_ACCOUNT_TOKEN",
        "grafana/mcp-grafana", "-t", "stdio",
    ],
    env={
        "PATH": os.environ["PATH"],
        "GRAFANA_URL": grafana_url,
        "GRAFANA_SERVICE_ACCOUNT_TOKEN": token,
    },
)
logging.info("grafana-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("grafana-macaw-gateway")
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
