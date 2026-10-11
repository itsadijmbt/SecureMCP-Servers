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
from macaw_adapters.mcp import SecureMCPProxy


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

proxy.run()
