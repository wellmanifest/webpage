#!/usr/bin/env python3
"""Observe a site, then judge with subactor/subllm platform/site-audit."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

PACK_ROOT = Path(__file__).resolve().parents[1]


def gui_scripts_dir() -> Path:
    env = os.environ.get("WELLMANIFEST_GUI_SCRIPTS")
    if env:
        return Path(env)
    sibling = PACK_ROOT.parent / "gui" / "scripts"
    if (sibling / "gui_page.py").is_file():
        return sibling
    raise RuntimeError("wellmanifest/gui scripts not found; set WELLMANIFEST_GUI_SCRIPTS")


GUI_SCRIPTS = gui_scripts_dir()
sys.path.insert(0, str(GUI_SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gui_page import build_page, defects_for_page  # noqa: E402
from subllm_judge import complete as subllm_complete  # noqa: E402

STANDARD = json.loads((PACK_ROOT / "standard/webpage.standard.v1.json").read_text())
PACK_VERSION = (PACK_ROOT / "VERSION").read_text().strip()
SECRET_RE = re.compile(r"(token|secret|password|api[_-]?key)=", re.I)

LENS_JS = r"""
() => {
  const qs = (s) => document.querySelector(s);
  const hrefs = Array.from(document.querySelectorAll("a[href]"))
    .map((a) => a.getAttribute("href") || "")
    .filter((h) => h && !h.startsWith("javascript:"));
  return {
    lang: document.documentElement.lang || "",
    title: document.title || "",
    viewport: Boolean(qs("meta[name=viewport]")),
    canonical: (qs("link[rel=canonical]") || {}).href || "",
    linkCount: hrefs.length,
    footerLinks: Array.from(document.querySelectorAll("footer a[href], .footer a[href]"))
      .map((a) => a.getAttribute("href") || ""),
    navLinks: Array.from(document.querySelectorAll("header a[href], nav a[href], .nav a[href]"))
      .map((a) => a.getAttribute("href") || ""),
    pageLinks: hrefs,
    buttonCount: document.querySelectorAll("button, [role=button], input[type=submit]").length,
    formCount: document.querySelectorAll("form").length,
  };
}
"""


def finding(code: str, severity: str, lens: str, message: str, url: str = "") -> dict[str, Any]:
    item = {"code": code, "severity": severity, "lens": lens, "message": message}
    if url:
        item["url"] = url
    return item


def fetch_status(url: str) -> int:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except Exception:  # noqa: BLE001
        return 0


def sitemap_urls(sitemap_url: str) -> list[str]:
    with urllib.request.urlopen(sitemap_url, timeout=8) as resp:
        tree = ET.fromstring(resp.read())
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text.strip() for loc in tree.findall(".//sm:loc", ns) if loc.text]


def same_origin_page(base: str, href: str) -> str | None:
    absolute = urllib.parse.urljoin(base, href)
    parsed = urllib.parse.urlparse(absolute)
    base_parsed = urllib.parse.urlparse(base)
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc != base_parsed.netloc:
        return None
    path = parsed.path or "/"
    skip = STANDARD.get("observation", {}).get("skipPathPrefixes") or []
    if any(path.startswith(prefix) for prefix in skip):
        return None
    if Path(path).suffix in {".svg", ".ico", ".png", ".jpg", ".css", ".js", ".xml", ".txt"}:
        return None
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", parsed.query, ""))


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def wait_json(url: str, timeout: float = 15.0, method: str = "GET") -> dict:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=2) as resp:
                return json.loads(resp.read().decode())
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.2)
    raise RuntimeError(f"CDP not ready: {last}")


async def cdp_eval(ws_url: str, page_url: str, expression: str) -> dict:
    import websockets

    async with websockets.connect(ws_url, max_size=8_000_000) as ws:
        msg_id = 0

        async def send(method: str, params: dict | None = None) -> dict:
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                raw = json.loads(await ws.recv())
                if raw.get("id") == msg_id:
                    if "error" in raw:
                        raise RuntimeError(raw["error"])
                    return raw.get("result") or {}

        await send("Page.enable")
        await send("Runtime.enable")
        await send("Page.navigate", {"url": page_url})
        deadline = time.time() + 12
        while time.time() < deadline:
            try:
                raw = json.loads(await asyncio.wait_for(ws.recv(), timeout=1.0))
            except TimeoutError:
                continue
            if raw.get("method") in {"Page.loadEventFired", "Page.domContentEventFired"}:
                break
        await asyncio.sleep(1.2)
        result = await send(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
        )
        value = (result.get("result") or {}).get("value")
        if not isinstance(value, dict):
            raise RuntimeError(f"evaluate returned {result!r}")
        return value


def path_of(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.query:
        return f"{parsed.path or '/'}?{parsed.query}"
    return parsed.path or "/"


def observation_page(url: str, raw: dict[str, Any], signals: dict[str, Any]) -> dict[str, Any]:
    page = build_page(
        url=url,
        title=raw.get("title") or signals.get("title") or "",
        structure=raw.get("structure") or {},
        tokens=raw.get("tokens") or {},
        source="observed",
        page_id=f"observed/{path_of(url).strip('/').replace('?', '-') or 'home'}",
    )
    page["defects"] = defects_for_page(page)
    kind = (page.get("page") or {}).get("kind") or "unknown"
    if raw.get("url"):
        page["page"]["url"] = raw["url"]
    lenses = {lens["id"]: [] for lens in STANDARD["lenses"]}
    for defect in page["defects"]:
        code = str(defect.get("code") or "")
        if code.startswith("GUI-PAGE-KIND"):
            lenses["kind"].append(defect)
        elif code.startswith("GUI-PAGE-CHROME") or code.startswith("GUI-VIS-STRUCT"):
            lenses["structure"].append(defect)
        else:
            lenses["visual"].append(defect)
    return {
        "url": url,
        "intentKind": kind,
        "httpStatus": 200,
        "page": page,
        "signals": signals,
        "lenses": lenses,
    }


def policy_findings(url: str) -> list[dict[str, Any]]:
    if SECRET_RE.search(url):
        return [finding(
            "WEB-POLICY-001", "error", "policy",
            "URL looks like it carries a secret/token (policy-dsl: fail closed)", url,
        )]
    return []


CONTACT_HREF_RE = re.compile(
    r"(?:^|[?&])action=contact(?:&|$)|(?:^|/)contact(?:/|\?|$)",
    re.I,
)


def looks_like_contact_href(href: str) -> bool:
    return bool(CONTACT_HREF_RE.search(href or ""))


def observation_findings(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic lenses from observed signals. No product path table."""
    out: list[dict[str, Any]] = []
    langs: set[str] = set()
    contact_hrefs: set[str] = set()
    for item in pages:
        url = str(item.get("url") or "")
        sig = item.get("signals") or {}
        lenses = item.setdefault("lenses", {})
        lang = str(sig.get("lang") or "").strip()
        if lang:
            langs.add(lang)
        if not sig.get("canonical"):
            row = finding("WEB-SEO-001", "warn", "seo", "Missing rel=canonical", url)
            lenses.setdefault("seo", []).append(row)
            out.append(row)
        if not lang:
            row = finding("WEB-A11Y-001", "warn", "a11y", "html lang is empty", url)
            lenses.setdefault("a11y", []).append(row)
            out.append(row)
        if sig.get("viewport") is False:
            row = finding("WEB-A11Y-002", "warn", "a11y", "viewport meta missing", url)
            lenses.setdefault("a11y", []).append(row)
            out.append(row)
        for href in list(sig.get("footerLinks") or []) + list(sig.get("navLinks") or []):
            if looks_like_contact_href(str(href)):
                contact_hrefs.add(str(href))

    if len(langs) > 1:
        out.append(finding(
            "WEB-CONS-003",
            "warn",
            "consistency",
            "html lang differs across pages: " + ", ".join(sorted(langs)),
        ))

    for href in sorted(contact_hrefs):
        target = urllib.parse.urljoin(str(pages[0].get("url") or "/"), href) if pages else href
        matched = next(
            (
                item
                for item in pages
                if urllib.parse.urldefrag(str(item.get("url") or ""))[0].rstrip("/")
                == urllib.parse.urldefrag(target)[0].rstrip("/")
                or href in str(item.get("url") or "")
            ),
            None,
        )
        form_count = int((matched.get("signals") or {}).get("formCount") or 0) if matched else 0
        if matched is not None and form_count > 0:
            continue
        row = finding(
            "WEB-UX-001",
            "error",
            "ux",
            f"Contact path {href} has no form (advertised in nav/footer)",
            href,
        )
        out.append(row)
        if matched is not None:
            matched.setdefault("lenses", {}).setdefault("ux", []).append(row)
    return out


def apply_judgment(pages: list[dict[str, Any]], judgment: dict[str, Any]) -> None:
    by_url = {item["url"]: item for item in pages}
    for judged in judgment.get("pages") or []:
        item = by_url.get(judged.get("url") or "")
        if item is None:
            continue
        item["intentKind"] = judged.get("intentKind") or "unknown"
        meta = item["page"].setdefault("page", {})
        meta["kind"] = judged.get("kind") or "unknown"
        if judged.get("family"):
            meta["family"] = judged["family"]
        meta["intentKind"] = item["intentKind"]
        if judged.get("budgets"):
            item["page"]["visual"]["budgets"] = judged["budgets"]
        buckets = item["lenses"]
        for defect in judged.get("findings") or []:
            lens = defect.get("lens") or "ux"
            buckets.setdefault(lens, []).append(defect)


def judgment_prompt(site: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    payload = {
        "task": "Judge this observation into wellmanifest.webpage/llm-judgment/v1",
        "rules": [
            "Do not invent brand tokens. Colors/fonts HOME is wellmanifest/brand.",
            "Do not hardcode product paths; use only URLs present in observation.",
            "Assign page.kind and intentKind from URL+DOM+headings, not from a built-in map.",
            "Choose visual budgets per kind after seeing counts. Emit GUI-VIS-* only when counts exceed your budget.",
            "Emit WEB-SITEMAP-001 / WEB-ROBOTS-001 only when site.sitemapStatus/robotsStatus is not 200.",
            "POA effect is read_data. Propose hints, do not apply.",
        ],
        "lenses": [lens["id"] for lens in STANDARD["lenses"]],
        "site": site,
        "pages": [
            {
                "url": item["url"],
                "title": item["page"].get("title"),
                "structure": item["page"].get("structure"),
                "counts": item["page"].get("visual", {}).get("counts"),
                "tokens": item["page"].get("visual", {}).get("tokens"),
                "signals": {
                    "lang": (item.get("signals") or {}).get("lang"),
                    "viewport": (item.get("signals") or {}).get("viewport"),
                    "formCount": (item.get("signals") or {}).get("formCount"),
                    "footerLinks": (item.get("signals") or {}).get("footerLinks"),
                    "navLinks": (item.get("signals") or {}).get("navLinks"),
                },
            }
            for item in pages
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def human_report(audit: dict[str, Any]) -> str:
    route = audit.get("subllm") or {}
    lines = [
        f"# Raport witryny — {audit.get('title')}",
        "",
        "## Jak czytać",
        "",
        "Obserwacja (DOM/tokeny) i **kind/budżety** idą z `wellmanifest/gui` "
        "(`infer_kind` + `page_profiles`). LLM (`subllm "
        f"{route.get('application', 'platform')}/{route.get('function', 'site-audit')}`"
        f", {route.get('provider') or 'optional'} / {route.get('model') or '—'}) "
        "może nadpisać kind/budżety i dodać wskazówki.",
        "Soczewki są niezależne od typu strony. Najpierw kind, potem landmarks, potem budżety.",
        "",
        f"Źródło URL-i: **{audit['site']['source']}**. sitemap={audit['site']['sitemapStatus']} robots={audit['site']['robotsStatus']}.",
        "",
        "## Findings",
        "",
    ]
    for item in audit.get("findings") or []:
        lines.append(f"- `{item['code']}` [{item['severity']}/{item['lens']}] {item['message']}")
    lines += ["", "## Strony", ""]
    for page in audit.get("pages") or []:
        meta = (page.get("page") or {}).get("page") or {}
        counts = (page.get("page") or {}).get("visual", {}).get("counts") or {}
        lines.append(f"### {page.get('url')}")
        lines.append(
            f"kind **{meta.get('kind')}** (intent {page.get('intentKind')}) · "
            f"fonty {counts.get('fontFamilies')} · kolory {counts.get('colors')} · rozmiary {counts.get('fontSizes')}"
        )
        defects = [f for lens in (page.get("lenses") or {}).values() for f in lens]
        if not defects:
            lines.append("- brak defektów soczewek")
        for defect in defects:
            lines.append(f"- `{defect.get('code')}` {defect.get('message')}")
        lines.append("")
    lines += ["## Wskazówki (LLM)", ""]
    for hint in audit.get("hints") or []:
        lines.append(f"- {hint}")
    lines += ["", f"POA `{audit.get('poa', {}).get('processRef')}` effect=read_data.", ""]
    return "\n".join(lines) + "\n"


def llm_followup_prompt(audit: dict[str, Any]) -> str:
    return (
        "Kontynuuj z tym werdyktem. Z findings zrób listę ticketów "
        "(jeden lens = jeden ticket). Nie wymyślaj palety.\n\n"
        f"```json\n{json.dumps({'schema': audit.get('schema'), 'findings': audit.get('findings'), 'hints': audit.get('hints'), 'subllm': audit.get('subllm')}, ensure_ascii=False, indent=2)}\n```\n"
    )


def write_logs(path: Path, audit: dict[str, Any]) -> None:
    failed = any(f.get("severity") == "error" for f in audit.get("findings") or [])
    events = [
        {"schema": "wellmanifest.logs/event/v1", "eventType": "validation_started", "outcome": "OBSERVED", "ref": audit.get("id")},
        {
            "schema": "wellmanifest.logs/event/v1",
            "eventType": "validation_failed" if failed else "validation_passed",
            "outcome": "REJECTED" if failed else "ACCEPTED",
            "ref": audit.get("id"),
            "findingCount": len(audit.get("findings") or []),
        },
    ]
    path.write_text("".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events))


def proposed_sitemap(base: str, paths: list[str]) -> str:
    rows = []
    for path in paths:
        loc = urllib.parse.urljoin(base, path.lstrip("/")) if path not in {"/", ""} else base
        rows.append(f"  <url><loc>{loc}</loc><changefreq>weekly</changefreq></url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )


def probe_urls(urls: list[str], page_js: str, chrome_bin: str) -> list[dict[str, Any]]:
    port = free_port()
    user_dir = Path(tempfile.mkdtemp(prefix="webpage-audit-chrome-"))
    chrome = subprocess.Popen(
        [
            chrome_bin, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--remote-allow-origins=*", f"--remote-debugging-port={port}",
            f"--user-data-dir={user_dir}", "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pages: list[dict[str, Any]] = []
    try:
        wait_json(f"http://127.0.0.1:{port}/json/version")
        for url in urls:
            tab = wait_json(
                f"http://127.0.0.1:{port}/json/new?{urllib.parse.quote(url, safe='')}",
                method="PUT",
            )
            combined = (
                "(() => { const page = (" + page_js + ")(); "
                "const signals = (" + LENS_JS + ")(); "
                "return { page, signals }; })()"
            )
            bundle = asyncio.run(cdp_eval(tab["webSocketDebuggerUrl"], url, combined))
            pages.append(observation_page(url, bundle.get("page") or {}, bundle.get("signals") or {}))
    finally:
        chrome.terminate()
        try:
            chrome.wait(timeout=5)
        except subprocess.TimeoutExpired:
            chrome.kill()
        shutil.rmtree(user_dir, ignore_errors=True)
    return pages


def discover_urls(base: str, home: dict[str, Any], *, max_pages: int) -> list[str]:
    found = [base]
    signals = home.get("signals") or {}
    for href in (signals.get("footerLinks") or []) + (signals.get("navLinks") or []):
        absolute = same_origin_page(base, href)
        if absolute and absolute not in found:
            found.append(absolute)
        if len(found) >= max_pages:
            break
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8781/")
    parser.add_argument("--out-dir", default=str(PACK_ROOT / "examples/subactor-8781"))
    parser.add_argument("--chrome", default="google-chrome")
    parser.add_argument("--max-pages", type=int, default=int((STANDARD.get("observation") or {}).get("maxPages") or 12))
    parser.add_argument("--judgment", default="", help="Reuse a saved llm-judgment JSON instead of calling SubLLM")
    parser.add_argument("--skip-llm", action="store_true")
    args = parser.parse_args()
    base = args.base if args.base.endswith("/") else args.base + "/"

    sitemap_url = urllib.parse.urljoin(base, "sitemap.xml")
    robots_url = urllib.parse.urljoin(base, "robots.txt")
    sitemap_status = fetch_status(sitemap_url)
    robots_status = fetch_status(robots_url)
    source = "homepage-links"
    seed = [base]
    if sitemap_status == 200:
        try:
            seed = sitemap_urls(sitemap_url) or seed
            source = "sitemap"
        except Exception:  # noqa: BLE001
            source = "homepage-links"

    gui_extract = (GUI_SCRIPTS / "probe-visual.py").read_text()
    match = re.search(r'EXTRACT_JS = r"""(.*?)"""', gui_extract, re.S)
    if not match:
        raise SystemExit("gui EXTRACT_JS missing")
    page_js = match.group(1)

    first = probe_urls(seed[:1], page_js, args.chrome)
    urls = seed if source == "sitemap" else discover_urls(base, first[0], max_pages=args.max_pages)
    rest = [url for url in urls if url != first[0]["url"]]
    pages = first + (probe_urls(rest, page_js, args.chrome) if rest else [])

    site = {
        "baseUrl": base,
        "sitemapUrl": sitemap_url,
        "sitemapStatus": sitemap_status,
        "robotsStatus": robots_status,
        "source": source,
    }

    findings: list[dict[str, Any]] = []
    if sitemap_status != 200:
        findings.append(finding(
            "WEB-SITEMAP-001", "error", "seo",
            f"sitemap.xml returned {sitemap_status}", sitemap_url,
        ))
    if robots_status != 200:
        findings.append(finding(
            "WEB-ROBOTS-001", "error", "seo",
            f"robots.txt returned {robots_status}", robots_url,
        ))
    for item in pages:
        findings.extend(policy_findings(item["url"]))
    findings.extend(observation_findings(pages))

    subllm_meta = {"application": "platform", "function": "site-audit", "provider": "", "model": ""}
    hints: list[str] = []
    judgment: dict[str, Any] = {}
    if args.judgment:
        judgment = json.loads(Path(args.judgment).read_text())
        subllm_meta["provider"] = "fixture"
        subllm_meta["model"] = Path(args.judgment).name
    elif not args.skip_llm:
        try:
            judgment, subllm_meta = subllm_complete(judgment_prompt(site, pages))
        except Exception as exc:  # noqa: BLE001
            findings.append(finding("WEB-LLM-001", "error", "ux", str(exc)))
    else:
        findings.append(finding("WEB-LLM-001", "error", "ux", "LLM judgment skipped (--skip-llm)"))

    if judgment:
        apply_judgment(pages, judgment)
        findings.extend(judgment.get("siteFindings") or [])
        hints = list(judgment.get("hints") or [])
    for item in pages:
        for lens_id, lens_findings in (item.get("lenses") or {}).items():
            for defect in lens_findings:
                row = dict(defect)
                row.setdefault("lens", lens_id)
                row.setdefault("url", item.get("url") or "")
                findings.append(row)

    audit = {
        "schema": "wellmanifest.webpage/site-audit/v1",
        "$schema": "https://wellmanifest.com/schemas/webpage/site-audit/v1",
        "id": "subactor.www/site-audit",
        "version": PACK_VERSION,
        "title": f"sub.actor site audit ({base})",
        "placement": {
            "home": "subactor",
            "shape": "runtime_service",
            "adopt": "wellmanifest/webpage",
            "runtimeOwner": "subactor",
        },
        "adopt": STANDARD["adopt"] + ["subactor/subllm"],
        "poa": {"processRef": STANDARD["poa"]["processRef"], "effect": "read_data"},
        "subllm": subllm_meta,
        "site": site,
        "pages": pages,
        "findings": findings,
        "hints": hints,
    }

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "site-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    (out / "REPORT.md").write_text(human_report(audit))
    (out / "LLM_PROMPT.md").write_text(llm_followup_prompt(audit))
    if judgment:
        (out / "llm-judgment.json").write_text(json.dumps(judgment, ensure_ascii=False, indent=2) + "\n")
    write_logs(out / "audit.events.jsonl", audit)
    paths = list(judgment.get("proposedSitemapPaths") or [])
    if not paths:
        paths = sorted({urllib.parse.urlparse(item["url"]).path or "/" for item in pages})
    (out / "proposed-sitemap.xml").write_text(proposed_sitemap(base, paths))
    (out / "proposed-robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n"
    )
    print(
        f"wrote {out} pages={len(pages)} findings={len(findings)} "
        f"source={source} subllm={subllm_meta.get('provider')}/{subllm_meta.get('model')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
