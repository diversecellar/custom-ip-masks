# Custom IP Masks Proxy Server - Functionality Improvements Overview

## Introduction

Custom IP Masks is a Flask-based HTTP forwarder that fetches a target URL on behalf of the client. It masks the client IP by stripping forwarding headers and optionally using an upstream proxy. Additionally, it adds simple request logging and status/health endpoints.

## Request Flow

Requesting is when the client sends a request to the web server, which then forwards it to the target URL - thus the server is able to see the request as coming from the client IP (or the upstream proxy, if configured). The request flow occurs as follows (step-by-step):

Flask routes all methods to `_handle_request`.
   - `_get_target_url` resolves the destination from:
     - query param ?url=..., or
     - header X-Target-URL, or
     - the path itself (prepends http:// if missing).
   - `_prepare_headers`:
     - copies incoming headers, removes Host/Content-Length and known IP-leaking headers,
     - adds configured headers and optional randomized User-Agent.
   - `_rate_limit_exceeded` currently always returns False (placeholder).
   - `_make_request` uses requests.Session to call the destination with stream=True and allow_redirects=False.
   - `_create_response` builds a Flask Response, copies upstream headers, removes Content-Encoding/Transfer-Encoding/Connection, and adds X-Proxied-By.

## Configuration highlights

- upstream_proxy: passed to requests.Session.proxies to chain through another proxy.
- auth: sets session.auth (server-side HTTP auth, not proxy-auth).
- timeout: intended request timeout, but not actually applied (see “Notable gaps”).
- logging: adds both console and file handlers with the provided format.
- rate_limit: enabled flag and RPM value exist, but logic is not implemented.

## Notable gaps and risks

We could possibly improve on the following areas:

- **Timeout not applied:** requests doesn’t use `session.timeout`; pass `timeout=...` to `session.request` or per-call.
- **Streaming mismatch:** `stream=True` is set, but .content reads the entire body into memory; either stream to the client or drop stream=True.
- **Redirects:** `allow_redirects=False` with no manual 3xx handling may confuse clients; consider forwarding Location transparently or following redirects.
- **Security:** `verify=False` disables TLS verification; risky for production.
- **SSRF risk:** accepts arbitrary URLs from clients; consider allow/block lists and URL validation.
- **Rate limiting:** placeholder always returns False; no per-IP accounting.
- **Max content length:** config exists but is not enforced for requests or responses.
- **Proxy authentication:** `auth` sets server auth; proxy authentication (e.g., HTTP Proxy-Authorization) is not implemented.
- **Header handling:** removing Content-Encoding while returning raw upstream content can cause mismatches; recompress or avoid stripping unless decoding first.
- **Logger duplication:** creating multiple instances can add multiple handlers to the same logger name.

## Quick improvement checklist

- [x] Pass `timeout=self.config['timeout']` to `session.request`.
- [ ] If you want streaming, iterate `upstream_response.raw` and stream to Flask Response; otherwise remove `stream=True`.
- [ ] Decide on redirect behavior; either follow or forward `Location`.
- [ ] Re-enable TLS verification and add CA options; optionally allow opt-out only for trusted cases (Important).
- [ ] Implement per-IP rate limiting (e.g., in-memory sliding window or Redis).
- [ ] Enforce `max_content_length` on request bodies and cap response size.
- [ ] Validate target URLs against allowlists or at least disallow private address ranges.
- [ ] Guard logger setup to avoid duplicate handlers (check if handlers already attached).

---

**Author**: Paul Namalomba<br>
**Created**: September, 2025<br>
**Version**: Rolling (v0.1.3 as of Nov 2025)