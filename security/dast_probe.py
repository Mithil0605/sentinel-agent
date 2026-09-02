#!/usr/bin/env python3
"""Automated DAST/VAPT probe against the running Sentinel Agent.

Checks common web vulnerabilities: headers, CORS, path traversal, sensitive
file exposure, SQLi/XSS in inputs, method tampering, and DoS payloads.
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
import time

BASE = "http://127.0.0.1:8000"
results: list[dict] = []


def req(path, method="GET", data=None, headers=None, timeout=6):
    url = BASE + path
    body = json.dumps(data).encode() if data is not None else None
    h = dict(headers or {})
    if body is not None:
        h.setdefault("Content-Type", "application/json")
    r = urllib.request.Request(url, data=body, method=method, headers=h)
    start = time.time()
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        code = resp.status
        resp_headers = dict(resp.headers.items())
        content = resp.read().decode("utf-8", "replace")
        return code, resp_headers, content, time.time() - start
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers.items()), e.read().decode("utf-8", "replace"), time.time() - start
    except Exception as e:
        return None, {}, str(e), time.time() - start


def add(status, title, detail, severity):
    results.append({"status": status, "title": title, "detail": detail, "severity": severity})


def check_headers(path="/"):
    code, h, _, _ = req(path)
    if h is None or isinstance(h, dict) and not h:
        add("WARN", "Could not read response headers", f"no headers parsed for {path}", "low")
        return code
    hl = {k.lower(): v for k, v in (h or {}).items()}
    required = {
        "content-security-policy": "CSP",
        "x-content-type-options": "nosniff",
        "x-frame-options": "frame defense",
        "referrer-policy": "referrer control",
    }
    for head, name in required.items():
        if head in hl:
            add("PASS", f"Header present: {name}", f"{head} set on {path}", "info")
        else:
            add("FAIL", f"Missing header: {name}", f"{head} absent on {path}", "low")
    csp = hl.get("content-security-policy", "")
    if "unsafe-inline" in csp and "script-src" in csp:
        add("WARN", "CSP allows unsafe-inline", "script-src permits unsafe-inline", "medium")
    return code


def check_cors():
    code, h, _, _ = req("/api/chat", method="OPTIONS", headers={
        "Origin": "https://evil.example.com",
        "Access-Control-Request-Method": "POST",
    })
    acao = h.get("Access-Control-Allow-Origin")
    if acao and acao != "*" and "evil.example" in acao:
        add("FAIL", "CORS reflects arbitrary origin", f"ACAO={acao}", "medium")
    elif acao == "*":
        add("WARN", "CORS wildcard", "ACAO=*", "low")
    else:
        add("PASS", "CORS not reflecting evil origin", f"ACAO={acao}", "info")


def check_path_traversal():
    targets = [
        "/static/../../../../etc/passwd",
        "/static/..%2f..%2f..%2fetc/passwd",
        "/static/%2e%2e/%2e%2e/etc/passwd",
        "/api/../../etc/passwd",
    ]
    for t in targets:
        code, _, content, _ = req(t)
        if code == 200 and "root:" in content:
            add("FAIL", "Path traversal", f"Read /etc/passwd via {t}", "high")
        else:
            add("INFO", f"Path traversal blocked: {t}", f"got {code}", "info")


def check_sensitive_files():
    targets = ["/.env", "/.env.example", "/backend/app/main.py", "/proc/self/environ",
               "/server-status", "/actuator", "/static/../.env", "/sentinel.db"]
    for t in targets:
        code, _, content, _ = req(t)
        if code == 200 and any(k in content for k in ["SECRET_KEY", "DATABASE_URL", "root:", "manifest"]):
            add("FAIL", "Sensitive file exposed", f"URL {t} returned {code}", "high")
        else:
            add("INFO", f"Sensitive probe blocked: {t}", f"got {code}", "info")


def check_method_tampering():
    for method in ["TRACE", "PUT", "DELETE"]:
        code, h, content, _ = req("/api/chat", method=method)
        if code == 200 and "TRACE" in content:
            add("FAIL", "TRACE enabled", "TRACE returned 200", "medium")
        else:
            add("INFO", f"Method {method} handled", f"got {code}", "info")
    code, h, content, _ = req("/", method="POST")
    if code == 405:
        add("PASS", "POST to root returns 405", "", "info")
    else:
        add("INFO", f"POST to root returns {code}", "", "info")


def check_open_redirect():
    for u in ["/?next=https://evil.com", "/api/health?redirect=https://evil.com"]:
        code, h, _, _ = req(u)
        loc = h.get("Location", "")
        if loc.startswith("http") and "evil.com" in loc:
            add("FAIL", "Open redirect", f"Location={loc}", "medium")
        else:
            add("INFO", "No open redirect", f"{u} -> {code}", "info")


def check_sqli_xss_inputs():
    payloads = [
        ("' OR '1'='1", "sqli"),
        ("<script>alert(1)</script>", "xss"),
        ("1; DROP TABLE users--", "sqli"),
    ]
    for payload, kind in payloads:
        code, _, content, _ = req("/api/chat", method="POST",
                                  data={"message": payload, "session_id": "sec"})
        if kind == "xss" and content and "<script>alert(1)</script>" in content:
            add("FAIL", "Stored/reflected XSS in response", "script payload reflected raw", "high")
        elif content and "internal server error" in content.lower():
            add("WARN", f"Possible {kind} causing 500", f"payload caused error", "medium")
        else:
            add("INFO", f"{kind} payload handled", f"got {code}", "info")


def check_dos_payload():
    big = "x" * 9000
    code, _, content, dt = req("/api/chat", method="POST",
                               data={"message": big, "session_id": "sec"})
    if code == 422:
        add("PASS", "Oversized payload rejected", f"422 in {dt:.2f}s", "info")
    else:
        add("WARN", f"Oversized payload returned {code}", f"in {dt:.2f}s", "medium")


def main():
    check_headers()
    check_cors()
    check_path_traversal()
    check_sensitive_files()
    check_method_tampering()
    check_open_redirect()
    check_sqli_xss_inputs()
    check_dos_payload()

    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    passes = [r for r in results if r["status"] == "PASS"]
    print(f"\n===== DAST/VAPT SUMMARY =====")
    print(f"PASS: {len(passes)}  WARN: {len(warns)}  FAIL: {len(fails)}  INFO: {len(results)-len(passes)-len(warns)-len(fails)}")
    for r in results:
        icon = {"PASS": "✔", "FAIL": "✖", "WARN": "⚑", "INFO": "•"}[r["status"]]
        print(f"  {icon} [{r['severity']}] {r['title']} — {r['detail']}")
    json.dump(results, open("/tmp/dast_results.json", "w"), indent=2)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
