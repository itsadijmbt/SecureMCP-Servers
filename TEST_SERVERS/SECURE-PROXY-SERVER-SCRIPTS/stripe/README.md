# Stripe MCP — SecureMCPProxy

Wraps the official `@stripe/mcp` npm package (local stdio, Restricted API
Key auth) with MACAW. One Python file, two tests.

We use the **local server with a Restricted API Key** because:
- Tool availability is gated by the RAK's permissions — clean fit for
  MACAW's principle of least privilege.
- Avoids the OAuth dance the remote server (`https://mcp.stripe.com`)
  needs.

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node 18+`, `node -v && npx --version`).
- A Stripe account (test mode is fine — no real money flows).

## Credentials

Create a **Restricted API Key** at
https://dashboard.stripe.com/apikeys → "Create restricted key".

Recommended minimum scopes for the smoke test:
- **Customers:** Read

For Test 2 / broader Gemini-driven exploration, add only what you'll
actually use. Never use a full `sk_*` secret key — Stripe MCP takes the
key as a CLI flag, which means it's visible to anyone with `ps` on this
machine. RAK + minimum scopes contains the blast radius.

```bash
export STRIPE_SECRET_KEY="rk_test_..."
```

`rk_test_` for test mode (recommended), `rk_live_` for production.

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/stripe/proxy_stripe.py
```

Expected: tool list on stderr (depends on RAK scopes — narrow RAK = fewer
tools), then `list_customers -> {"data":[...], "has_more": ...}`. MACAW
console shows one entry under `app_name=stripe-proxy`.

First run is slow (10–20s) because `npx -y` downloads the package.

If `list_customers` returns an empty list, that's fine — the smoke proves
auth + dispatch, not that you have customers.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_stripe.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "stripe-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/stripe/proxy_stripe.py"],
      "env": { "STRIPE_SECRET_KEY": "rk_test_..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add stripe-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/stripe/proxy_stripe.py \
  -e STRIPE_SECRET_KEY=rk_test_...
```

Then prompt: *"Use the stripe-macaw tool to list my customers, limit 5,
and show each as: <id> — <email>."* MACAW console shows a second entry
from the LLM client.

## Notes on what could go wrong

- **`list_customers` not in the tool list** — your RAK doesn't have
  `Customers: Read`. Add it in the dashboard, regenerate, retry.
- **`401` / `Invalid API Key provided`** — `STRIPE_SECRET_KEY` is wrong,
  revoked, or you typed `sk_*` somewhere it expected `rk_*`. Stripe MCP
  accepts either, but RAK is the recommended posture.
- **`ps` shows your key** — yes, that's how Stripe MCP works (key is a
  CLI flag, not env). Keep RAK scopes minimal so a leak is recoverable.
- **Test mode vs live** — `rk_test_*` only sees test-mode data;
  `rk_live_*` sees production. Don't mix prompts referencing test data
  while running with a live key.
