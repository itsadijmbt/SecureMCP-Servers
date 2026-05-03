# Chrome DevTools MCP — SecureMCPProxy (npx stdio)

Wraps `chrome-devtools-mcp` (Google's official Chrome DevTools Protocol
MCP server) with MACAW. One Python file, two tests.

The interesting bit: this is a **no-credential** wrap — no API key, no
token, no OAuth. Auth is implicit in "you control the Chrome process".
The proxy spawns Chrome via npx, drives it through the DevTools Protocol,
and exposes browser tools (navigate, screenshot, evaluate JS, click, fill
forms, list tabs, etc.) over MCP.

## Prereqs

- MACAW LocalAgent running.
- Node + npm (`node -v && npx --version`).
- **Chrome installed** — the package launches the system Chrome, it does
  not bundle one. On this box: `/usr/bin/google-chrome` ✓.

## Defaults baked into the wrap

`proxy_chrome_devtools.py` spawns chrome-devtools-mcp with:

- **`--headless`** — no GUI window. Safer when Gemini spawns the script
  in a non-desktop context. Drop this flag if you want a visible browser
  for debugging.
- **`--isolated`** — ephemeral profile per session, auto-cleaned. Keeps
  tests deterministic and avoids cookie / session pollution between
  runs. Drop this flag if you need persistent state (logged-in sites,
  saved tabs).

Other flags worth knowing (see upstream README for full list):
`--channel=stable|canary|dev|beta`, `--executable-path=/path/to/chrome`,
`--slim`, `--wsEndpoint=ws://...` (connect to an already-running Chrome
instead of spawning a new one).

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/chrome-devtools/proxy_chrome_devtools.py
```

Expected on stderr:

- `tools: 20+` — full Chrome control surface (navigate, click, fill, screenshot, evaluate, network, console, etc.).
- `list_pages -> {...}` — likely `[]` or a single about:blank entry on a
  fresh isolated profile. Either is a passing smoke test — we're proving
  the chain works, not testing browser behavior.

First run: 30s+ for `npx -y` to download `chrome-devtools-mcp` and for
Chrome to spawn cold. Subsequent runs are faster but not instant
(Chrome boot is ~2-3 s even cached).

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_chrome_devtools.py`. Uncomment the **Test 2** block at the
   bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "chrome-devtools-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/chrome-devtools/proxy_chrome_devtools.py"]
    }
  }
}
```

No env vars — there are no credentials.

**Claude Code CLI:**

```bash
claude mcp add chrome-devtools-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/chrome-devtools/proxy_chrome_devtools.py
```

Then prompt: *"Use the chrome-devtools-macaw MCP server. Navigate to
https://example.com, take a screenshot, and report the page title."*
MACAW console shows two edges (one navigate, one screenshot, one
evaluate-or-similar) per request.

## What this proves architecturally

Every browser action — navigation, JS evaluation, form submission, file
download — passes through MACAW first. That's a meaningful observation
for the registry: **MACAW can mediate full browser-automation surfaces**,
not just data-API calls. Worth a callout when you write the demo.

## Notes on what could go wrong

- **`Failed to launch Chrome`** — Chrome binary missing or wrong path.
  Verify `/usr/bin/google-chrome` exists, or pass
  `--executable-path=/path/to/your/chrome` in the `command` array.
- **`Display server not found` even with `--headless`** — modern Chrome
  uses headless by default; some older builds still need `DISPLAY` set.
  Try `DISPLAY=:0 python3.11 proxy_chrome_devtools.py`. (Likely unneeded
  on this box.)
- **`list_pages` returns empty** — expected on a fresh isolated profile
  with no navigation calls yet. Run `navigate_page` first to populate.
- **Profile lock on second simultaneous run** — Chrome enforces one
  process per profile dir. `--isolated` avoids this; without it, two
  runs collide on `~/.cache/chrome-devtools-mcp/chrome-profile-stable`.
- **`SUID sandbox` error in some Linux containers** — usually means
  Chrome can't set up its sandbox. Add `--no-sandbox` to the chrome
  spawn args (security trade-off; only do this in trusted environments).
