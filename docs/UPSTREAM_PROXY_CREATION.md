# UPSTREAM PROXY: Build Your Own Or Use Public Lists

This guide explains two paths to get an upstream proxy with a different public egress IP:
- Run your own upstream proxy on a server you control (recommended).
- Temporarily use public/free proxy lists (risky; for testing only).

Your traffic flow with an upstream:  
Your Client → Local Proxy (this project) → Upstream Proxy → Target Site

---

## 0) Prerequisites

- A server (VPS or cloud instance) with a public IPv4 (e.g., Ubuntu 22.04).
- Ability to open inbound ports (firewall rules).
- SSH access to the server.
- On your client: curl, and optionally Python 3 if you’ll run tests.

---

## 1) Run Your Own Upstream Proxy (Recommended)

You will set up a standard forward proxy on a VPS so your local proxy can egress with the VPS IP.

### 1.1 Choose a Proxy Type

- Squid (HTTP/HTTPS CONNECT) — robust, production-grade, best default.
- TinyProxy (HTTP/HTTPS CONNECT) — lightweight, simple.
- mitmproxy (developer-friendly) — flexible, easy to start.
- Dante (SOCKS5) — use with `socks5h://` in clients.

### 1.2 Provision a Server

- Create a small VPS (1 vCPU, 512MB+ RAM is fine) in a region you want.
- Note its public IP (e.g., `203.0.113.10`).
- Update and secure:
  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y ufw
  sudo ufw allow OpenSSH
  sudo ufw enable
  ```

Open the proxy port later (3128 or 1080).

---

### 1.3 Option A — Squid (HTTP/HTTPS)

Install:
```bash
sudo apt install -y squid apache2-utils
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.bak
```

Minimal config (allow only your client IP):
```bash
sudo bash -c 'cat >/etc/squid/squid.conf' <<'CONF'
http_port 3128

# Allow only this client IP (replace with your home/office public IP)
acl allowed_client src YOUR_PUBLIC_IP/32
http_access allow allowed_client
http_access deny all

# Privacy: remove forwarding headers
forwarded_for delete
via off
request_header_access X-Forwarded-For deny all
request_header_access Via deny all
request_header_access Forwarded deny all
CONF
```

Open port and restart:
```bash
sudo ufw allow 3128/tcp
sudo systemctl restart squid
sudo systemctl enable squid
```

Test from your client:
```bash
curl -s --proxy http://203.0.113.10:3128 https://api.ipify.org?format=json
```

Optional: Add Basic Auth
```bash
sudo htpasswd -c /etc/squid/passwd proxyuser
# Add to /etc/squid/squid.conf:
# auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
# acl auth_users proxy_auth REQUIRED
# http_access allow allowed_client auth_users
sudo systemctl restart squid
# Test:
curl -s --proxy http://proxyuser:YOURPASS@203.0.113.10:3128 https://httpbin.org/ip
```

---

### 1.4 Option B — TinyProxy (Lightweight)

```bash
sudo apt install -y tinyproxy
sudo sed -i 's/^Port .*/Port 3128/' /etc/tinyproxy/tinyproxy.conf
echo "Allow YOUR_PUBLIC_IP" | sudo tee -a /etc/tinyproxy/tinyproxy.conf
sudo ufw allow 3128/tcp
sudo systemctl restart tinyproxy
sudo systemctl enable tinyproxy
```

Test:
```bash
curl -s --proxy http://203.0.113.10:3128 https://api.ipify.org?format=json
```

---

### 1.5 Option C — mitmproxy (General Purpose)

```bash
pip install mitmproxy
mitmproxy --mode regular --listen-host 0.0.0.0 --listen-port 3128
```

Open port:
```bash
sudo ufw allow 3128/tcp
```

Test:
```bash
curl -s --proxy http://203.0.113.10:3128 https://httpbin.org/ip
```

---

### 1.6 Option D — Dante (SOCKS5)

```bash
sudo apt install -y dante-server
sudo bash -c 'cat >/etc/danted.conf' <<'CONF'
logoutput: syslog
internal: 0.0.0.0 port = 1080
external: eth0
method: none

client pass {
  from: YOUR_PUBLIC_IP/32 to: 0.0.0.0/0
}
pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  protocol: tcp udp
}
CONF
sudo ufw allow 1080/tcp
sudo systemctl restart danted
sudo systemctl enable danted
```

Test (SOCKS5):
```bash
curl -s --socks5-hostname 203.0.113.10:1080 https://api.ipify.org?format=json
```

For Python `requests`, use `socks5h://` and install `requests[socks]`.

---

### 1.7 Hardening Checklist

- Restrict access by IP allowlist and/or authentication.
- Keep ports closed except the proxy port and SSH.
- Monitor logs:
  - Squid: `/var/log/squid/access.log`
  - TinyProxy: `/var/log/tinyproxy/tinyproxy.log`
  - Dante: syslog/journal
- Rotate logs and update system regularly.
- Never run an open proxy.

---

### 1.8 Using Your Upstream in This Project

In your `config.json`:
```json
{
  "upstream_proxy": {
    "http": "http://203.0.113.10:3128",
    "https": "http://203.0.113.10:3128"
  }
}
```

For SOCKS5 (Dante):
```json
{
  "upstream_proxy": {
    "http": "socks5h://203.0.113.10:1080",
    "https": "socks5h://203.0.113.10:1080"
  }
}
```

Ensure your proxy forwards via `requests.request(..., proxies=upstream_proxies)`.  
Re-test:
```bash
# Baseline (direct)
curl -s https://api.ipify.org?format=json

# Via your local proxy (forwarding endpoint if CONNECT not implemented)
curl -s "http://127.0.0.1:9000?url=https://api.ipify.org?format=json"

# Or via curl --proxy for HTTP targets (no CONNECT required)
curl -s --proxy http://127.0.0.1:9000 http://httpbin.org/ip
```

---

## 2) Using Public/Free Proxy Lists (Risky; For Testing)

Free proxies are often slow, unstable, and unsafe. Treat them as untrusted. Never send sensitive data.

### 2.1 Sources

- ProxyScrape: https://proxyscrape.com/free-proxy-list
- GitHub aggregators (search “free proxy list”)
- Other APIs (many are mirrors of each other)

Example: Fetch ProxyScrape list (HTTP):
```bash
curl -s "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=all" \
  | head
```

Use as `ip:port` lines.

### 2.2 Validate Proxies Programmatically (Python)

```python
import time, requests

def test_proxy(p, timeout=5):
    proxies = {"http": f"http://{p}", "https": f"http://{p}"}
    t0 = time.time()
    try:
        r = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=timeout)
        r.raise_for_status()
        return True, time.time() - t0, r.json().get("ip")
    except Exception:
        return False, None, None

# Example usage:
# proxies = ["1.2.3.4:8080", "5.6.7.8:3128", ...]
# good = [p for p in proxies if test_proxy(p)[0]]
```

Filter for:
- Success status,
- Latency under your threshold (e.g., < 2s),
- Anonymity (no `X-Forwarded-For` echoes if you check headers on httpbin.org/headers).

### 2.3 Rotate Through Validated Proxies

- Store a pool of working proxies and rotate per request.
- Expect frequent churn; revalidate periodically.
- Respect target services and legal terms.

### 2.4 Wire Into This Project

After you select a working free proxy:
```json
{
  "upstream_proxy": {
    "http": "http://IP:PORT",
    "https": "http://IP:PORT"
  }
}
```

Restart your local proxy and test:
```bash
curl -s "http://127.0.0.1:9000?url=https://api.ipify.org?format=json"
```

---

## 3) Troubleshooting

- Same IP with/without proxy:
  - Your upstream is not configured or not used. Confirm `/proxy/status` shows upstream and your code passes `proxies=...` to `requests`.
- HTTPS failing with curl `--proxy`:
  - Your local proxy likely lacks CONNECT tunneling. Use the forwarding-style endpoint `?url=...` or rely on an upstream that supports CONNECT; curl will CONNECT to the upstream directly.
- 407 Proxy Authentication Required:
  - Add credentials to the upstream URL (e.g., `http://user:pass@ip:port`), or configure auth on server and client.
- Timeouts / Connection refused:
  - Verify the upstream port is open (`ufw`, cloud firewall, `netstat -tulpen`).
- Verify port listening:
  ```bash
  sudo ss -tulpen | grep -E "3128|1080"
  ```
- Windows client checks:
  ```powershell
  Test-NetConnection 203.0.113.10 -Port 3128
  ```

---

## 4) Security Notes

- Never expose an unauthenticated open proxy to the internet.
- Prefer IP allowlists plus authentication.
- Do not proxy sensitive credentials via unknown/free proxies.
- Keep software up-to-date and monitor access logs.

---

## 5) Quick Command Reference

- Direct IP:
  ```bash
  curl -s https://api.ipify.org?format=json
  ```
- Through upstream directly:
  ```bash
  curl -s --proxy http://203.0.113.10:3128 https://httpbin.org/ip
  ```
- Through local proxy forwarding:
  ```bash
  curl -s "http://127.0.0.1:9000?url=https://api.ipify.org?format=json"
  ```
- Through local proxy as HTTP proxy (HTTP targets only if no CONNECT):
  ```bash
  curl -s --proxy http://127.0.0.1:9000 http://httpbin.org/ip
  ```

---

## 6) Integrating With `proxy_server.py` (Reminder)

Ensure outbound requests actually use the upstream:
```python
proxies = self.config.get("upstream_proxy") or None
resp = requests.request(
    method=request.method,
    url=target_url,
    headers=out_headers,
    data=request.get_data(),
    params=request.args,
    stream=True,
    timeout=self._timeout,
    verify=self.config.get("verify_ssl", True),
    proxies=proxies,  # critical
)
```

Check `/proxy/status` to confirm upstream settings are detected.