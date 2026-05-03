# Snyk MCP — SecureMCPProxy (npx stdio)

Wraps Snyk's official MCP server (built into the Snyk CLI v1.1298.0+) with
MACAW. One Python file, two tests.

The Snyk CLI is a security-scanning toolkit for SCA (open source
dependencies), SAST (proprietary code), IaC, and container images — all
exposed as MCP tools when run as `snyk mcp -t stdio`. Same wrap shape as
airtable / notion / postman: npx stdio + static API token.

> Note on the upstream repo: `github.com/snyk/snyk-ls` is the **Snyk
> Language Server**, not a standalone MCP server. The MCP is shipped in
> the main `snyk` CLI binary; the LS just registers a notification so an
> LSP client knows the CLI's MCP endpoint exists. We wrap the CLI
> directly via `npx -y snyk@latest mcp -t stdio`.

## Prereqs

- MACAW LocalAgent running.
- Node + npm (`node -v && npx --version`).
- A Snyk account (free tier works for individual use).

## Credentials

1. https://app.snyk.io/account → **General Account Settings → Auth
   Token** → copy.
2. ```bash
   export SNYK_TOKEN="..."
   ```
3. (Multi-org accounts only) ```bash
   export SNYK_CFG_ORG="<your-org-id>"
   ```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/snyk/proxy_snyk.py
```

Expected: tool list on stderr (~10 tools — `snyk_sca_scan`,
`snyk_code_scan`, `snyk_iac_scan`, `snyk_container_scan`,
`snyk_sbom_scan`, `snyk_aibom`, `snyk_trust`, `snyk_auth`,
`snyk_logout`, `snyk_version`), then `snyk_version -> {...}` reporting
the CLI version.

`snyk_version` is the smoke target because it's zero-arg, no scope check,
no scan side effects, no quota cost. A 200-shape response proves the
auth handshake worked and tool dispatch round-trips correctly without
spending any of your scan budget.

First run: 30s+ — `npx -y` downloads `snyk@latest` (the full CLI is a
significant package). Subsequent runs are fast.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_snyk.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "snyk-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/snyk/proxy_snyk.py"],
      "env": { "SNYK_TOKEN": "..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add snyk-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/snyk/proxy_snyk.py \
  -e SNYK_TOKEN=...
```

Then prompt: *"Use the snyk-macaw tool to call snyk_version and report
the CLI version. Do not call any other tool."* MACAW console shows a
second entry from the LLM client.

To exercise a real scan:

> "Use snyk-macaw. Call snyk_trust on `/home/itsadijmbt/MACAW-MCP-STORE`,
> then snyk_sca_scan on the same path. Report only the **count** of
> vulnerabilities by severity (critical/high/medium/low). Do not list
> every CVE."

That'll burn one scan from your quota but proves the full chain works
on a real workload.

## Why this one matters for the registry

This is the **first security-scanning MCP server** in your scan list.
Worth a callout: MACAW is now mediating a tool whose entire purpose is
to find *other* security issues. If you turn that on for a real codebase
through the LLM, every scan request and every finding flows through
MACAW — useful "security-on-security" data point.

## Notes on what could go wrong

- **`npx: command not found`** — install Node.js.
- **First call hangs ~30s** — `npx -y` downloading. Be patient.
- **`Authentication failed`** — `SNYK_TOKEN` invalid, expired, or scoped
  to a different region. Verify with `npx snyk@latest auth $SNYK_TOKEN`
  in a separate shell.
- **`Tool not found: snyk_version`** — Snyk CLI < v1.1298.0 (MCP wasn't
  yet added). `npx -y snyk@latest` should always pull the latest, so
  this should never fire; if it does, your npm cache is stuck — clear
  with `npm cache clean --force`.
- **`Scan exceeded plan limits`** on actual scan tools — Snyk free tier
  has monthly limits. `snyk_version` doesn't count. Real scans do.
- **Multi-org Snyk: scan goes to wrong org** — set `SNYK_CFG_ORG` to
  the org ID (find at https://app.snyk.io/org/<slug>/manage/settings).
