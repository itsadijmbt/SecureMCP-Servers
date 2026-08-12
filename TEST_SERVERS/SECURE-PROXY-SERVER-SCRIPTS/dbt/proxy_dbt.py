"""
dbt-proxy -> SecureMCPProxy, served natively.

Prereq:
    export DBT_ACCOUNT_ID="..."
    export DBT_DEV_ENV_ID="..."
    export DBT_HOST="..."
    export DBT_PATH="..."
    export DBT_PROD_ENV_ID="..."
    export DBT_PROJECT_DIR="..."
    export DBT_TOKEN="..."
    export DBT_USER_ID="..."
    export MULTICELL_ACCOUNT_PREFIX="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_dbt.py
    python proxy_dbt.py http 8080

Claude Code:
    claude mcp add dbt-macaw python /path/to/proxy_dbt.py \
      -e DBT_ACCOUNT_ID=... \
      -e DBT_DEV_ENV_ID=... \
      -e DBT_HOST=... \
      -e DBT_PATH=... \
      -e DBT_PROD_ENV_ID=... \
      -e DBT_PROJECT_DIR=... \
      -e DBT_TOKEN=... \
      -e DBT_USER_ID=... \
      -e MULTICELL_ACCOUNT_PREFIX=... \
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
for k in (
    "DBT_HOST",
    "DBT_TOKEN",
    "DBT_PROD_ENV_ID",
    "DBT_DEV_ENV_ID",
    "DBT_USER_ID",
    "DBT_ACCOUNT_ID",
    "DBT_PROJECT_DIR",
    "DBT_PATH",
    "MULTICELL_ACCOUNT_PREFIX",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="dbt-proxy",
    command=["uvx", "dbt-mcp"],
    env=upstream_env,
)
logging.info("dbt-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("dbt-macaw-gateway")
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
