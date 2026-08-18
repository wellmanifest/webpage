"""Call subactor/subllm platform/site-audit. Fail closed. No local model IDs."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

def _subllm_src() -> Path | None:
    env = os.environ.get("SUBLLM_SRC")
    if env:
        return Path(env)
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "subactor" / "subllm" / "src"
        if (candidate / "subllm").is_dir():
            return candidate
    return None


_SUBLLM = _subllm_src()
if _SUBLLM is not None:
    sys.path.insert(0, str(_SUBLLM))

APPLICATION = "platform"
FUNCTION = "site-audit"
JUDGMENT_SCHEMA = "wellmanifest.webpage/llm-judgment/v1"
KIND_ENUM = {"landing", "marketplace", "article", "form", "auth", "panel", "unknown"}
FAMILY_ENUM = {"marketing", "commerce", "workspace", "content", "account"}
SEVERITY_ENUM = {"info", "warn", "error"}
KIND_ALIASES = {
    "comparison": "article",
    "legal": "article",
    "listing": "marketplace",
    "pricing": "landing",
    "contact": "form",
    "registry": "marketplace",
}
SEVERITY_ALIASES = {
    "high": "error",
    "medium": "warn",
    "low": "info",
    "warning": "warn",
    "fatal": "error",
}


def _pack_root() -> Path:
    return Path(__file__).resolve().parents[1]


def standard_finding_codes() -> set[str]:
    standard = json.loads((_pack_root() / "standard/webpage.standard.v1.json").read_text())
    codes = {"WEB-LLM-001"}
    for lens in standard.get("lenses") or []:
        codes.update(str(code) for code in (lens.get("codes") or []))
    return codes


def _import_subllm():
    try:
        from subllm import MissingCredentialError, available_routes, resolve
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "subllm is not importable; set PYTHONPATH to subactor/subllm/src"
        ) from exc
    return MissingCredentialError, available_routes, resolve


def _extract_json_object(text: str) -> dict[str, Any]:
    blob = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", blob, re.S)
    if fenced:
        blob = fenced.group(1)
    else:
        start, end = blob.find("{"), blob.rfind("}")
        if start >= 0 and end > start:
            blob = blob[start : end + 1]
    data = json.loads(blob)
    if not isinstance(data, dict):
        raise ValueError("LLM output is not a JSON object")
    return data


def normalize_kind(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "unknown"
    if raw in KIND_ENUM:
        return raw
    prefix = raw.split(".", 1)[0]
    if prefix in KIND_ENUM:
        return prefix
    return KIND_ALIASES.get(raw) or KIND_ALIASES.get(prefix) or "unknown"


def normalize_severity(value: Any) -> str:
    raw = str(value or "").strip().lower()
    mapped = SEVERITY_ALIASES.get(raw, raw)
    return mapped if mapped in SEVERITY_ENUM else "info"


def _hint_text(item: Any) -> str:
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        text = str(item.get("hint") or item.get("message") or "").strip()
        target = str(item.get("target") or "").strip()
        if text and target:
            return f"{target}: {text}"[:400]
        return text[:400]
    return ""


def _normalize_finding(raw: Any, known: set[str]) -> tuple[dict[str, Any] | None, str]:
    if not isinstance(raw, dict):
        return None, ""
    code = str(raw.get("code") or raw.get("id") or "").strip()
    message = str(raw.get("message") or "").strip()
    if not code or not message:
        return None, ""
    if code not in known:
        return None, f"{code}: {message}"[:400]
    item: dict[str, Any] = {
        "code": code,
        "severity": normalize_severity(raw.get("severity")),
        "lens": str(raw.get("lens") or "ux"),
        "message": message[:400],
    }
    if raw.get("url"):
        item["url"] = str(raw["url"])
    return item, ""


def _normalize_budgets(raw: Any) -> dict[str, int] | None:
    if not isinstance(raw, dict):
        return None
    try:
        budgets = {
            "fontFamilies": int(raw["fontFamilies"]),
            "colors": int(raw["colors"]),
            "fontSizes": int(raw["fontSizes"]),
        }
    except (KeyError, TypeError, ValueError):
        return None
    if not (1 <= budgets["fontFamilies"] <= 16):
        return None
    if not (1 <= budgets["colors"] <= 64):
        return None
    if not (1 <= budgets["fontSizes"] <= 32):
        return None
    return budgets


def normalize_judgment(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data.get("pages"), list):
        raise ValueError("llm-judgment.pages must be an array")
    known = standard_finding_codes()
    hints: list[str] = []
    for item in list(data.get("hints") or []) + list(data.get("poaHints") or []):
        text = _hint_text(item)
        if text and text not in hints:
            hints.append(text)
    pages: list[dict[str, Any]] = []
    for raw in data.get("pages") or []:
        if not isinstance(raw, dict):
            continue
        nested = raw.get("page") if isinstance(raw.get("page"), dict) else {}
        findings: list[dict[str, Any]] = []
        for defect in raw.get("findings") or []:
            item, hint = _normalize_finding(defect, known)
            if item:
                findings.append(item)
            elif hint and hint not in hints:
                hints.append(hint)
        page: dict[str, Any] = {
            "url": str(raw.get("url") or ""),
            "kind": normalize_kind(raw.get("kind") or nested.get("kind")),
            "intentKind": normalize_kind(raw.get("intentKind") or nested.get("intentKind")),
            "findings": findings,
        }
        budgets = _normalize_budgets(raw.get("budgets") or raw.get("visualBudget"))
        if budgets:
            page["budgets"] = budgets
        family = str(raw.get("family") or nested.get("family") or "")
        if family in FAMILY_ENUM:
            page["family"] = family
        summary = raw.get("summary")
        if isinstance(summary, str) and summary.strip():
            page["summary"] = summary.strip()[:400]
        pages.append(page)
    site_findings: list[dict[str, Any]] = []
    for defect in list(data.get("siteFindings") or []) + list(data.get("findings") or []):
        item, hint = _normalize_finding(defect, known)
        if item:
            site_findings.append(item)
        elif hint and hint not in hints:
            hints.append(hint)
    out: dict[str, Any] = {
        "schema": JUDGMENT_SCHEMA,
        "pages": pages,
        "siteFindings": site_findings,
        "hints": hints,
    }
    paths = data.get("proposedSitemapPaths")
    if isinstance(paths, list):
        out["proposedSitemapPaths"] = [str(path) for path in paths if str(path).strip()]
    return out


def parse_judgment(text: str) -> dict[str, Any]:
    data = _extract_json_object(text)
    if data.get("schema") != JUDGMENT_SCHEMA and isinstance(data.get("judgment"), dict):
        data = data["judgment"]
    if not isinstance(data, dict) or data.get("schema") != JUDGMENT_SCHEMA:
        raise ValueError("LLM output is not wellmanifest.webpage/llm-judgment/v1")
    return normalize_judgment(data)


def parse_judgment_file(path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    raw = path.read_text()
    meta: dict[str, str] = {}
    try:
        wrapper = json.loads(raw)
    except json.JSONDecodeError:
        wrapper = {}
    if isinstance(wrapper, dict) and isinstance(wrapper.get("meta"), dict):
        meta = {
            key: str(wrapper["meta"][key])
            for key in ("application", "function", "provider", "model")
            if wrapper["meta"].get(key)
        }
    return parse_judgment(raw), meta


def _complete_openai(route: Any, prompt: str, timeout: int = 120) -> str:
    body: dict[str, Any] = {
        "model": route.wire_model,
        **route.provider_request_fields(),
        "messages": [
            {
                "role": "system",
                "content": "Return only JSON matching wellmanifest.webpage/llm-judgment/v1.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    extra = getattr(route, "provider_request_fields", None)
    if extra and route.provider == "zai":
        body.update(route.provider_request_fields())
    payload = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {route.api_key}",
        "Content-Type": "application/json",
        **dict(route.extra_headers),
    }
    req = urllib.request.Request(
        f"{route.api_base.rstrip('/')}/chat/completions",
        data=payload,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def _complete_cursor(route: Any, prompt: str) -> str:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

    sdk = route.cursor_sdk_kwargs()
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=sdk["api_key"],
            model=sdk["model"],
            local=LocalAgentOptions(cwd=str(Path.cwd())),
        ),
    )
    output = getattr(result, "result", None)
    if output is None:
        raise RuntimeError("cursor_sdk_empty_result")
    return str(output)


def complete(prompt: str, *, timeout: int = 120) -> tuple[dict[str, Any], dict[str, str]]:
    MissingCredentialError, available_routes, _resolve = _import_subllm()
    try:
        candidates = list(available_routes(APPLICATION, FUNCTION))
    except MissingCredentialError as exc:
        raise RuntimeError(f"WEB-LLM-001: no SubLLM credential for {APPLICATION}/{FUNCTION}: {exc}") from exc
    if not candidates:
        raise RuntimeError(f"WEB-LLM-001: no available route for {APPLICATION}/{FUNCTION}")

    errors: list[str] = []
    for route in candidates:
        try:
            if route.transport == "cursor-sdk":
                try:
                    import cursor_sdk  # noqa: F401
                except ImportError:
                    errors.append(f"{route.provider}: cursor-sdk not installed")
                    continue
                text = _complete_cursor(route, prompt)
            else:
                route_timeout = min(timeout, 20) if route.provider == "zai" else timeout
                text = _complete_openai(route, prompt, route_timeout)
            judgment = parse_judgment(text)
            return judgment, {
                "application": APPLICATION,
                "function": FUNCTION,
                "provider": route.provider,
                "model": route.model,
            }
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{route.provider}/{route.model}: {exc}")
            continue
    raise RuntimeError("WEB-LLM-001: all SubLLM candidates failed: " + " | ".join(errors))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Judge an observation via subllm platform/site-audit")
    parser.add_argument("prompt_file", nargs="?", default="-")
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    prompt = sys.stdin.read() if args.prompt_file == "-" else Path(args.prompt_file).read_text()
    judgment, meta = complete(prompt)
    blob = json.dumps({"meta": meta, "judgment": judgment}, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(blob + "\n")
    else:
        print(blob)
