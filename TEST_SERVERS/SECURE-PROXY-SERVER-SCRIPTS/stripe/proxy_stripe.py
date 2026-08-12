"""
stripe-proxy -> SecureMCPProxy, served natively.

Prereq:
    export STRIPE_SECRET_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_stripe.py
    python proxy_stripe.py http 8080

Claude Code:
    claude mcp add stripe-macaw python /path/to/proxy_stripe.py \
      -e STRIPE_SECRET_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("STRIPE_SECRET_KEY")
if not api_key:
    raise ValueError("STRIPE_SECRET_KEY is not set (use a Restricted API Key: rk_test_... or rk_live_...)")


proxy = SecureMCPProxy(
    app_name="stripe-proxy",
    command=["npx", "-y", "@stripe/mcp", f"--api-key={api_key}"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
    },
)
logging.info("stripe-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("stripe-macaw-gateway")
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
