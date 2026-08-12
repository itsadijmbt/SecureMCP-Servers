"""
supabase-proxy -> SecureMCPProxy, served natively.

Prereq:
    export SUPABASE_PROJECT_REF="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_supabase.py
    python proxy_supabase.py http 8080

Claude Code:
    claude mcp add supabase-macaw python /path/to/proxy_supabase.py \
      -e SUPABASE_PROJECT_REF=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    PATH must point at Node 20+: mcp-remote needs undici, which fails on Node 18
    with "ReferenceError: File is not defined".
"""

import os
import sys
import logging
from urllib.parse import urlencode
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

params = {"read_only": "true"}
if os.environ.get("SUPABASE_PROJECT_REF"):
    params["project_ref"] = os.environ["SUPABASE_PROJECT_REF"]
upstream_url = f"https://mcp.supabase.com/mcp?{urlencode(params)}"

proxy = SecureMCPProxy(
    app_name="supabase-proxy",
    command=["npx", "-y", "mcp-remote", upstream_url],
    env={"PATH": os.environ["PATH"], "HOME": os.environ["HOME"]},
)
logging.info("supabase-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("supabase-macaw-gateway")
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
