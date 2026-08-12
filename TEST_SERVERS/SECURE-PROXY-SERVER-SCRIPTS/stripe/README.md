# Stripe MCP — SecureMCPProxy

Wraps `npx -y @stripe/mcp` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `STRIPE_SECRET_KEY`

## Setup

```bash
export STRIPE_SECRET_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_stripe.py            # stdio
python proxy_stripe.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add stripe-macaw python /path/to/proxy_stripe.py \
  -e STRIPE_SECRET_KEY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
