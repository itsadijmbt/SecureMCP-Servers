# Migration: alibabacloud-rds-openapi-mcp-server → SecureMCP

This document explains *what* we changed when porting Alibaba's RDS MCP server from FastMCP to MACAW's SecureMCP, and more importantly *why* each change was needed. It is written in plain language; the code itself lives in the diffs.

---

## 1. The big picture

Before the port, this server ran on **FastMCP**. FastMCP is "just an MCP server" — it speaks the MCP protocol over HTTP or stdio and routes incoming tool calls to Python functions. It has no notion of "who is calling," no built-in policy, and no tamper-evident audit log.

After the port, the server runs on **SecureMCP**. SecureMCP is FastMCP's job *plus* MACAW's security layer wrapped around it. Every tool call now arrives with a verifiable identity, runs through MACAW policy, gets cryptographically signed, and ends up in an audit log attributed to the actual caller.

We did **not** modify the SecureMCP SDK to make this server fit. We adapted the server to fit SecureMCP. That's the rule across all ports in this workspace.

---

## 2. The hardest problem: per-caller credentials

Alibaba's tools each need an **Aliyun access key** to talk to the Aliyun cloud. The original code supported two credential sources:

1. **Environment variables** (`ALIBABA_CLOUD_ACCESS_KEY_ID`, `..._SECRET`) — one shared service account for everyone.
2. **Per-caller AK/SK** sent as **HTTP headers** with the request.

Path 2 mattered: it lets *each user* of the MCP server use *their own* Aliyun credentials, instead of everyone sharing one service account. In a multi-tenant setup that is the only sane way to bill, audit, and authorize.

The way the original code shipped this per-caller path was:

> An HTTP middleware (`VerifyHeaderMiddleware`) read the headers off every incoming request and stuffed them into a Python `ContextVar` named `current_request_headers`. Every tool then read its credentials *from that ContextVar* via a helper called `get_aksk()`.

This is fine in a FastMCP world where everything is HTTP. **It does not work under SecureMCP**, because:

- SecureMCP doesn't run an HTTP server. It runs over stdio or over MACAW's own mesh transport. There are no HTTP headers for a middleware to read.
- The `VerifyHeaderMiddleware` was attached to FastMCP's `streamable_http_app()`. We don't build that app any more — there is no "ASGI app" to attach middleware to.

So the *transport* that filled the ContextVar (HTTP headers via middleware) is gone. But the *consumers* (`get_aksk()`, `get_rds_account()`, etc., which read from the ContextVar) are deep inside the tool code and we don't want to rewrite them.

We need a new way to get per-caller values into that same ContextVar — without touching the helpers that read from it.

---

## 3. The fix: `_metadata` + a one-line `with` bridge

MACAW's tool calls already carry a per-call dictionary called `_metadata`. The caller writes it, MACAW transports it, the server hands it to the tool through `ctx._metadata`. It's a normal kwarg; nothing magic.

So the question becomes: how do we get the values from `ctx._metadata` into the `current_request_headers` ContextVar that `get_aksk()` is already reading from? Without rewriting `get_aksk()`?

Answer: a tiny **bridge function**. Plain English version of what it does:

> "When a tool starts running, copy whatever's in `ctx._metadata` into the ContextVar. When the tool finishes (or crashes), undo the copy so the next call starts clean."

Concretely it lives in `utils.py` as `metadata_as_request_headers(ctx)`. It's a `@contextmanager` — a Python pattern for "do this on entry, undo it on exit, no matter what."

Each tool now starts with:

```python
async def some_tool(ctx: Context, region_id: str):
    """..."""
    with metadata_as_request_headers(ctx):
        # the entire original tool body, untouched
```

That is the **only** change to the tool body itself. The `with` block is the bridge: at the top it pours `ctx._metadata` into the ContextVar; at the bottom it pours it back out. Inside the block, the existing helpers (`get_aksk`, `get_rds_account`, etc.) work exactly as they always did.

### Why `with` and not `async with`?

The bridge does two operations: `ContextVar.set(...)` on the way in, `ContextVar.reset(...)` on the way out. Both are pure in-memory operations — no network, no disk, nothing to wait on. So the bridge is a *synchronous* context manager (`@contextmanager`), and you use it with plain `with`. You'd only need `async with` if entering or exiting required `await`-ing something. This doesn't.

You can use a sync `with` inside an `async def` function — that is normal Python and is exactly what we do.

### Why we picked `_metadata` and not the other options

MACAW gives you three places to stash credentials:

| Storage | Lifetime | When to use |
|---|---|---|
| `_metadata` | One single tool call | Different creds per call |
| `_session_objects` | One client session | Live objects (DB connections) reused across calls |
| MACAW vault | Persistent across restarts | Service-wide secrets, rotated rarely |

Alibaba's per-caller AK/SK fits `_metadata` cleanly: each call may come from a different end user with different keys. Vault would force everyone onto one key (defeats the point). `_session_objects` would assume the AK/SK is a *live object* (it's just a string). `_metadata` is the smallest, lightest, per-call answer — and it matches the original "per-request headers" model conceptually one-to-one.

### What's the limitation?

`_metadata` is a kwarg. Something has to *populate* it. Two valid populators:

1. A programmatic caller writes it into the call directly (this is how `client-test-macaw.py` does it).
2. An HTTP-fronting shim reads HTTP headers and rewrites them as `_metadata` before MACAW dispatches.

If neither happens, the bridge sees an empty dict and `get_aksk()` falls through to the env-var path. That's the intended fallback.

---

## 4. What we removed and why

### `VerifyHeaderMiddleware` — removed

Original purpose, two jobs:

1. **API-key check** — compared the incoming `Authorization: Bearer <key>` to a hardcoded env var.
2. **Header-to-ContextVar copy** — stashed the request headers into `current_request_headers`.

Both are obsolete under SecureMCP:

1. SecureMCP validates **every** invocation cryptographically. Each incoming call carries a signature from the caller's MACAW-registered keypair, and the Local Agent checks it before the handler runs. That is a much stronger guarantee than a shared bearer token. We don't need a middleware to compare strings any more.
2. The header-copy job is done by `metadata_as_request_headers(ctx)` instead, called from each tool.

So the middleware has nothing left to do. We commented it out (kept the comment for future readers explaining why) rather than deleted it outright, so anyone tracing the migration can see what *used* to live there.

### HTTP transport branch in `main()` — removed

The original `main()` had a big `if transport in ("sse", "streamable-http"):` branch that built a Starlette/Uvicorn app, mounted middleware, exposed `/health`, and started a web server. Under SecureMCP we don't run our own web server — MACAW provides the transport. So the entire branch is dead and we deleted it. The function now just calls `mcp.run(transport)` and lets SecureMCP handle the rest.

### `health_check` endpoint — removed

`health_check` was a Starlette HTTP handler (`request: Request -> JSONResponse`) used by container orchestrators to probe whether the server was alive. With no HTTP server, there is no URL to probe. The function is unreachable code, so we deleted it. If you later want a health check at the MACAW level, expose a `get_health` *tool* — same idea, different transport.

### Dead imports — cleaned

`uvicorn`, `anyio`, parts of `starlette`, `Request`, `JSONResponse` were only used by the now-gone HTTP code. Left in, they fail at import time on machines that don't have those packages. Removed.

---

## 5. The wrapper class change (`RdsMCP`)

The original `RdsMCP` *inherited* from `FastMCP`. It used `super().add_tool(...)` and `super().add_prompt(...)` to register components.

SecureMCP is **not** a subclass of FastMCP. It's a peer class with a similar but narrower API. So:

- `RdsMCP` no longer inherits from anything; it now **wraps** a `SecureMCP` instance via composition (`self._mcp = SecureMCP(...)`).
- The `super().add_tool(...)` call became `self._mcp.tool(name=..., description=...)(item.func)`. Reason: SecureMCP exposes `.tool()` as a decorator factory, not as an imperative `add_tool`. We use the decorator-as-function form.
- We filter the kwargs at this boundary because SecureMCP's `.tool()` only accepts `(name, description, prompts)`. The original code passed things like `annotations=READ_ONLY_TOOL` — that's a FastMCP feature SecureMCP doesn't have, and we drop those keys at registration time rather than asking every tool author to remove them.
- We added a tiny `run(transport)` method that just forwards to `self._mcp.run(transport)`. This is needed because callers do `mcp.run(...)` and there's no inherited `run` any more.

Tool authors don't need to know any of this — they keep writing `@mcp.tool(...)` exactly as before. The wrapper handles the translation.

---

## 6. The two independent layers of auth

This is worth saying clearly because it's easy to mix up.

| Layer | Question it answers | Mechanism | Where it lives |
|---|---|---|---|
| **Caller auth** | Is this really the caller they claim to be? | MACAW signs every call with the caller's keypair; Local Agent verifies before the handler runs | Handled automatically by MACAW. Zero code in this server. |
| **Upstream auth** | Whose Aliyun account do we use to call Aliyun? | Either env vars (service account) or `_metadata` → bridge → ContextVar → `get_aksk()` (per caller) | The bridge in `utils.py` plus the `with` block in each tool. |

These are independent. A call can pass caller auth (MACAW trusts who you are) and still fail upstream auth (your Aliyun key is wrong). That's exactly what TEST 3 in the smoke test demonstrates.

---

## 7. Verification — what the smoke test actually proved

`client-test-macaw.py` runs four calls and looks at the error shapes:

| Test | What it does | Expected proof |
|---|---|---|
| 1. `get_current_time` | Tool that needs no Aliyun creds | The whole MACAW chain works end-to-end |
| 2. `describe_db_instances` *without* `_metadata` | Falls through to env vars (empty in test env) | Aliyun SDK rejects locally with `InvalidCredentials` — proves env-var path executed |
| 3. `describe_db_instances` *with* fake `_metadata` | Bridge transports fake AK/SK to the SDK | Aliyun's *server* rejects with `InvalidAccessKeyId.NotFound` 404 — proves the bridge actually carried values to a real HTTP request |
| 4. `describe_rc_instances` | A tool from `rds_custom` group | Out of scope for the port; failed because we didn't activate that group |

The crucial result: TEST 2 and TEST 3 produce **different** error messages, from **different** sources (SDK-local vs Aliyun-remote). That difference is the proof that both upstream-auth paths are wired correctly.

---

## 8. Things we deliberately did *not* do

- We did not change `get_aksk` or `get_rds_account`. They still read from `current_request_headers`. The bridge is what makes that work; rewriting them would have rippled through ~36 tool files.
- We did not modify the SecureMCP SDK. Every awkward shape (kwarg filtering, decorator-as-function, etc.) was solved by adapting the server, not the SDK.
- We did not add a new credential storage mechanism. `_metadata` already existed; we just used it.
- We did not implement multi-tenant MAPL policy yet. That is a separate concern: SecureMCP enforces *whatever policy MACAW gives it*. Writing per-tool policies for Alibaba RDS is a follow-up.

---

## 9. Quick reference — files touched

- `src/alibabacloud_rds_openapi_mcp_server/core/mcp.py` — wrapper class moved from inheritance to composition; kwarg filtering added; `run()` forwarder added.
- `src/alibabacloud_rds_openapi_mcp_server/utils.py` — added the `metadata_as_request_headers` bridge.
- `src/alibabacloud_rds_openapi_mcp_server/server.py` — every `@mcp.tool` function got `ctx: Context` as its first parameter and a `with metadata_as_request_headers(ctx):` wrap around its body. HTTP transport branch, `VerifyHeaderMiddleware`, `health_check`, and dead imports were removed.
- `client-test-macaw.py` — new smoke test that proves both auth layers work.

That's the whole port.
