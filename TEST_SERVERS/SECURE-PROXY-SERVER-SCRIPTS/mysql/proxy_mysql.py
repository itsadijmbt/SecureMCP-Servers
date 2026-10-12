"""
mysql-proxy -> SecureMCPProxy, served natively.

Prereq:
    export MYSQL_HOST="..."
    export MYSQL_PORT="..."
    export MYSQL_USER="..."
    export MYSQL_PASSWORD="..."
    export MYSQL_DATABASE="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_mysql.py

Claude Code:
    claude mcp add mysql-macaw python /path/to/proxy_mysql.py \
      -e MYSQL_HOST=... \
      -e MYSQL_PORT=... \
      -e MYSQL_USER=... \
      -e MYSQL_PASSWORD=... \
      -e MYSQL_DATABASE=... \
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
for k in ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]
if "MYSQL_USER" not in upstream_env or "MYSQL_PASSWORD" not in upstream_env:
    raise ValueError("Set MYSQL_USER and MYSQL_PASSWORD")

proxy = SecureMCPProxy(
    app_name="mysql-proxy",
    command=["uvx", "mysql_mcp_server"],
    env=upstream_env,
)
logging.info("mysql-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
