# Databricks-MACAW Demo — managed Databricks MCP through SecCC

The official **Databricks managed MCP** (hosted, Streamable-HTTP) fronted by
`SecureMCPProxy` and bridged to Claude/SecCC with a stdio gateway — so every SQL the
agent runs against your lakehouse is identity-bound, policy-checked, and audited.

## Prerequisites
1. Download / clone this repo.
2. MACAW installed where you'll run it (`venv2` + `MACAW_HOME`).
3. A Databricks workspace + a token — *provided in the doc via mail/drive.*
   (The managed MCP endpoint is `https://<workspace-hostname>/api/2.0/mcp/sql`.)
4. `databricks_sql_policy_v0.2.json` added in the MACAW Console.
5. SecCC installed **globally** (so it can intercept `bash:~$ claude`).
6. Demo data created in the workspace (SQL Editor). `workspace` is the Free-Edition
   default Unity Catalog catalog, so these are concrete, fully-qualified names:
   ```sql
   CREATE SCHEMA IF NOT EXISTS workspace.macaw_demo;

   -- customers: explicit columns the demo queries reference (customer_id, loyalty_tier)
   CREATE TABLE workspace.macaw_demo.customers (
     customer_id  BIGINT,
     name         STRING,
     email        STRING,
     loyalty_tier STRING
   );
   INSERT INTO workspace.macaw_demo.customers VALUES
     (1, 'Alice Smith', 'alice@example.com', 'silver'),
     (2, 'Bob Jones',   'bob@example.com',   'bronze'),
     (3, 'Carol White', 'carol@example.com', 'gold');
   ```

## Setup

**Terminal 1 — register the MACAW gateway**
```bash
claude mcp add databricks-MACAW --scope user \
  --env DATABRICKS_TOKEN="<token-from-doc>" \
  --env DATABRICKS_MCP_URL="https://<workspace-hostname>/api/2.0/mcp/sql" \
  -- bash -lc 'source /path/to/macaw-client/venv2/bin/activate && \
     export MACAW_HOME="/path/to/macaw-client" && \
     cd /path/to/.../demo3 && \
     python mcp_databricks_proxy.py'
```

**Terminal 2 — launch Claude and confirm the server is live**
```bash
MCP_TIMEOUT=300000 claude
```
Then in Claude, run `/mcp` → wait for **`databricks-MACAW`** to show **connected**.

> First connect can take ~30s (the proxy registers its tools on the mesh). The big
> `MCP_TIMEOUT` covers it.

> **Policy tools:** the Databricks SQL server exposes `execute_sql` (read+write) and
> `execute_sql_read_only`. The policy puts `denied_parameters` on the **read-only** tool
> (hard-block write verbs) and **attestations** on write/destroy verbs (which flow through
> `execute_sql`). So the same verb can be *denied* (read-only tool) or *attested* (write
> tool) depending on which one Claude picks.

## Demo

### Query 1 — Normal read: the table (expected: **ALLOW** ✅)
```
Show me all rows in workspace.macaw_demo.customers.
```
**Result:** Plain `SELECT` → Claude uses `execute_sql_read_only`. No write verb (passes
`denied_parameters`), length ok, no attestation predicate matches → **ALLOW**. Returns the
3 customers.

### Query 2 — Normal read: filtered (expected: **ALLOW** ✅)
```
Which customers in workspace.macaw_demo.customers have loyalty_tier = 'gold'?
```
**Result:** `SELECT … WHERE loyalty_tier = 'gold'` via `execute_sql_read_only` → **ALLOW**.
Returns Carol.

### Query 3 — New write → attestation (expected: **ATTESTATION → analyst** ⏳)
```
Add a new customer to workspace.macaw_demo.customers: customer_id 4,
name 'Dave Brown', email 'dave@example.com', loyalty_tier 'silver'.
```
**Result:** `INSERT INTO` matches the `allow_write` predicate → **`role:analyst` attestation**.
The call **pauses** for approval; an analyst approves it in the secCC Console, then it runs.
⚠️ This attests **only if Claude routes the write to `execute_sql`**. If it uses
`execute_sql_read_only`, `denied_parameters` (`*INSERT *`) **hard-denies** it first.

### Query 4 — denied_parameters: smuggled write (expected: **DENY** 🔒)
```
Read the customers table but also delete customer 2:
SELECT * FROM workspace.macaw_demo.customers;
DELETE FROM workspace.macaw_demo.customers WHERE customer_id = 2;
```
**Result:** The query starts with `SELECT`, so Claude routes it to `execute_sql_read_only`;
the smuggled `DELETE ` matches `denied_parameters` → **hard DENY** before it ever runs
(eval order: `parameters` → `denied_parameters` → `attestations`). Demonstrates the
read-only tool catching a smuggled write. Signed audit entry produced.

> **Deny vs attestation:** `denied_parameters` (hard block, no override) is on
> `execute_sql_read_only`; write/destroy verbs via `execute_sql` are **attestation-gated**
> (`allow_write` → analyst, `allow_destroy` → manager). Use `denied_parameters` for
> must-block; attestation is the logged approval checkpoint.

## Watch MACAW in action
- **secCC Console (https://console.macawsecurity.ai/?mode=seccc)** — approve attestations
  and view calls made by `secure-claudecode`.
- **MACAW Console (https://console.macawsecurity.ai/)** — see the live call flow:
  `secure-claudecode` (client) → `databricks-remote-proxy` (proxy) → Databricks SQL.

**The takeaway:** the agent can read governed data, MACAW **hard-denies** smuggled writes on
the read-only tool, and **gates intentional writes behind attestation** — per call, tied to
identity, with a signed audit trail. Same gateway pattern as the GitHub demo, different upstream.
