"""
alibaba-rds-proxy -> SecureMCPProxy, served natively.

Prereq:
    export ALIBABA_CLOUD_ACCESS_KEY_ID="..."
    export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_alibaba_rds.py

Claude Code:
    claude mcp add alibaba-rds-macaw python /path/to/proxy_alibaba_rds.py \
      -e ALIBABA_CLOUD_ACCESS_KEY_ID=... \
      -e ALIBABA_CLOUD_ACCESS_KEY_SECRET=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    With an STS token also set ALIBABA_CLOUD_SECURITY_TOKEN.
    MCP_TOOLSETS picks the tool groups: rds (default), rds_custom_read, rds_custom_all. Example: MCP_TOOLSETS=rds,rds_custom_all
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
    "ALIBABA_CLOUD_ACCESS_KEY_ID",
    "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
    "ALIBABA_CLOUD_SECURITY_TOKEN",
    "MCP_TOOLSETS",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]
if "ALIBABA_CLOUD_ACCESS_KEY_ID" not in upstream_env or "ALIBABA_CLOUD_ACCESS_KEY_SECRET" not in upstream_env:
    raise ValueError("Set ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET")

proxy = SecureMCPProxy(
    app_name="alibaba-rds-proxy",
    # mcp pinned below 2: version 4.0.1 imports mcp.server.fastmcp, which mcp 2.x no longer has,
    # and the package itself only asks for mcp>=1.26.0.
    command=["uvx", "--with", "mcp<2", "alibabacloud-rds-openapi-mcp-server@latest"],
    env=upstream_env,
)
logging.info("alibaba-rds-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
