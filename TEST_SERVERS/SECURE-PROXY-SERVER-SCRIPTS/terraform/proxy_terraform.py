"""
terraform-proxy -> SecureMCPProxy, served natively.

Prereq:
    export TFE_ADDRESS="..."
    export TFE_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_terraform.py
    python proxy_terraform.py http 8080

Claude Code:
    claude mcp add terraform-macaw python /path/to/proxy_terraform.py \
      -e TFE_ADDRESS=... \
      -e TFE_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

upstream_env = {"PATH": os.environ["PATH"]}
for k in ("TFE_TOKEN", "TFE_ADDRESS"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

docker_args = ["docker", "run", "--rm", "-i"]
if upstream_env.get("TFE_TOKEN"):
    docker_args += ["-e", "TFE_TOKEN"]
if upstream_env.get("TFE_ADDRESS"):
    docker_args += ["-e", "TFE_ADDRESS"]
docker_args += ["hashicorp/terraform-mcp-server:0.5.2"]

proxy = SecureMCPProxy(
    app_name="terraform-proxy",
    command=docker_args,
    env=upstream_env,
)
logging.info("terraform-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("terraform-macaw-gateway")
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
