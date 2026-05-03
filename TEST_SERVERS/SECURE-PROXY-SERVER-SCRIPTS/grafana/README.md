# Grafana MCP — SecureMCPProxy (Docker stdio)

Wraps the official `grafana/mcp-grafana` Docker image with MACAW. One Python
file, two tests. Same shape as `proxy_mongodb.py` (Docker stdio upstream).

## Why Docker, not `uvx`

Both work. `uvx mcp-grafana` is one less moving part if you already have
`uv` installed; the Docker image is more universal — same toolchain we
already use for MongoDB. Pick one and stick with it; we default to Docker
here. To swap to `uvx`, replace `command` with
`["uvx", "mcp-grafana"]` and drop the `-i`/`-e` Docker flags.

## Prereqs

- MACAW LocalAgent running.
- Docker daemon up. Pull once:
  ```bash
  docker pull grafana/mcp-grafana
  ```
- A reachable Grafana instance:
  - **Local:** `docker run -d --name grafana-test -p 3000:3000 grafana/grafana`
  - **Cloud:** any Grafana Cloud stack URL (`https://<org>.grafana.net`).

## Credentials

Grafana → **Administration → Users and access → Service accounts** →
*Add service account*. Give it the **Editor** role (simplest) or finer
RBAC if you want least privilege. Then *Add service account token* →
copy the `glsa_...` value (only shown once).

```bash
export GRAFANA_URL="http://localhost:3000"          # or https://<org>.grafana.net
export GRAFANA_SERVICE_ACCOUNT_TOKEN="glsa_..."
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/grafana/proxy_grafana.py
```

Expected: tool list on stderr (~40+ tools depending on enabled categories),
then `list_datasources -> [{...}]` listing your configured datasources
(may be empty `[]` on a fresh Grafana — that's fine, proves auth + dispatch).
MACAW console shows one entry under `app_name=grafana-proxy`.

First run is slow (10–20s) because Docker is pulling the image. Subsequent
runs are fast.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_grafana.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "grafana-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/grafana/proxy_grafana.py"],
      "env": {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_SERVICE_ACCOUNT_TOKEN": "glsa_..."
      }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add grafana-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/grafana/proxy_grafana.py \
  -e GRAFANA_URL=http://localhost:3000 \
  -e GRAFANA_SERVICE_ACCOUNT_TOKEN=glsa_...
```

Then prompt: *"Use the grafana-macaw tool to list my datasources by name
and type."*

## Restricting the toolset

Grafana MCP exposes ~40 tools by default and another ~10 disabled (admin,
clickhouse, cloudwatch, elasticsearch, examples, graphite, runpanelquery).
For least privilege:

- Add `--disable-write` to the Docker command to make the proxy strictly
  read-only (no dashboard edits, no incident writes, no annotation writes).
- Add `--disable-<category>` flags for whole categories you don't use.

Example: read-only, only datasource + Prometheus tools:

```python
command=[
    "docker", "run", "--rm", "-i", "--network=host",
    "-e", "GRAFANA_URL",
    "-e", "GRAFANA_SERVICE_ACCOUNT_TOKEN",
    "grafana/mcp-grafana", "-t", "stdio",
    "--disable-write",
    "--disable-dashboard", "--disable-incident", "--disable-alerting",
    "--disable-oncall", "--disable-sift", "--disable-asserts",
    "--disable-navigation", "--disable-rendering", "--disable-pyroscope",
    "--disable-loki",
],
```

## Notes on what could go wrong

- **`401 Unauthorized`** — token is wrong, expired, or doesn't match
  `GRAFANA_URL`'s org. Service account tokens are org-scoped.
- **`list_datasources` returns empty** — Grafana has no datasources
  configured. Add one in **Connections → Data sources** before testing
  any datasource-specific tool (`query_prometheus`, `query_loki_logs`).
- **`get datasource by uid : ... 400 id is invalid`** — Grafana < 9.0.
  The `/datasources/uid/{uid}` endpoint was added in 9.0. Upgrade.
- **Container can't reach localhost Grafana** — `--network=host` covers
  the typical case. On Docker Desktop (macOS/Windows), use
  `host.docker.internal` instead and set
  `GRAFANA_URL=http://host.docker.internal:3000`.
- **Grafana Cloud rate limits** — read-heavy LLM workloads can trip rate
  limits on Free tier. Pin reads to specific dashboards/datasources via
  RBAC scopes if you hit this.
