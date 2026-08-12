"""
mongodb-proxy -> SecureMCPProxy, served natively.

Prereq:
    export MDB_MCP_API_CLIENT_ID="..."
    export MDB_MCP_API_CLIENT_SECRET="..."
    export MDB_MCP_CONNECTION_STRING="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_mongodb.py
    python proxy_mongodb.py http 8080

Claude Code:
    claude mcp add mongodb-macaw python /path/to/proxy_mongodb.py \
      -e MDB_MCP_API_CLIENT_ID=... \
      -e MDB_MCP_API_CLIENT_SECRET=... \
      -e MDB_MCP_CONNECTION_STRING=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    Needs a running Docker daemon and the image pulled:
    docker pull mongodb/mongodb-mcp-server:latest
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)


upstream_env = {"PATH": os.environ["PATH"]}
for k in ("MDB_MCP_CONNECTION_STRING", "MDB_MCP_API_CLIENT_ID", "MDB_MCP_API_CLIENT_SECRET"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]
if "MDB_MCP_CONNECTION_STRING" not in upstream_env and "MDB_MCP_API_CLIENT_ID" not in upstream_env:
    raise ValueError("Set MDB_MCP_CONNECTION_STRING or MDB_MCP_API_CLIENT_ID+MDB_MCP_API_CLIENT_SECRET")

proxy = SecureMCPProxy(
    app_name="mongodb-proxy",
    command=[
        "docker", "run", "--rm", "-i", "--network=host",
        "-e", "MDB_MCP_CONNECTION_STRING",
        "-e", "MDB_MCP_API_CLIENT_ID",
        "-e", "MDB_MCP_API_CLIENT_SECRET",
        "-e", "MDB_MCP_READ_ONLY=true",
        "-e", "MDB_MCP_LOGGERS=stderr",
        "mongodb/mongodb-mcp-server:latest",
    ],
    env=upstream_env,
)
logging.info("mongodb-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("mongodb-macaw-gateway")
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
