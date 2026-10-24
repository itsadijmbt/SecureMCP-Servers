# Airtable MCP — SecureMCPProxy

Wraps `npx -y airtable-mcp-server` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `AIRTABLE_API_KEY`  — required.

## Setup

```bash
export AIRTABLE_API_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_airtable.py
```

Register with Claude Code:

```bash
claude mcp add airtable-macaw python /path/to/proxy_airtable.py \
  -e AIRTABLE_API_KEY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```

## Policy

`Policy/server_policy_v0.2.0.json` (`app:airtable-proxy`), written against `airtable-mcp-server` 1.14.0 (16 tools):

- Allowed: `list_bases`, `list_tables`, `describe_table`, `list_records`, `search_records`, `get_record`, `list_comments`, `create_record`, `create_comment`, `update_records`. Any other tool, including one a later upstream release adds, is refused.
- Denied: `delete_records`, `create_table`, `update_table`, `create_field`, `update_field`, `upload_attachment`.
- `update_records` waits for `airtable_edit_approved`, approved by a user with role `admin` (120 s). It can blank fields, so it is treated like a delete.
- `baseId`, `tableId`, `recordId` must be IDs (`app`/`tbl`/`rec` + 14 characters). The upstream puts them into the API URL path unescaped, so without the pattern `tableId: "../meta/bases/<id>/tables"` reaches other Airtable endpoints. Table names are refused for the same reason.
- `maxRecords` (1–1000) is required on `list_records` and `search_records`. Without it the upstream reads every page of the table.

### The `{}` rule in `denied_parameters`

```json
"tool:airtable-proxy/list_records": { "tableId": ["{NOT (params.maxRecords > 0)}"] }
```

In `denied_parameters`, a plain string is a glob matched against that parameter's value. A string wrapped in `{}` is a
condition: it reads the call's actual parameter values and compares them, and the call is denied when it is true
(MAPL guide, "Combining Patterns": *"may reference any parameter of the call"*). Numbers compare as numbers.

A constraint on a parameter the call omits is never checked, so `"maxRecords": {"max": 1000}` alone does not stop a call
that leaves `maxRecords` out. A comparison on an absent parameter is false, so `NOT (params.maxRecords > 0)` is true
exactly when `maxRecords` is missing. The rule is listed under `tableId` because rules under an omitted parameter are skipped,
and every call sends `tableId`.

Verified on MACAW client 0.9.10.1 with the policy loaded in the Console (2026-10-24): `list_records` without `maxRecords`
is refused with `Parameter 'tableId' matches denied pattern: {NOT (params.maxRecords > 0)}`; with `maxRecords: 100` it passes;
a `{params.maxRecords > 9}` control refuses `10` and `100`, which a text comparison would let through.

### Not covered

- MAPL cannot read inside `fields` and `records`: a credential, or an attachment given as `{"url": …}`, can still be written
  through `create_record`.
- `rate_limit: 30` (per caller and tool, per minute) has not been seen to refuse a call: calls through the hosted control plane
  took about 10 s each, so a test never reached 30 a minute.
- Whether a user without role `admin` is refused as the approver has not been tested.
