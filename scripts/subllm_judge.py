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


def _import_subllm():
    try:
        from subllm import MissingCredentialError, available_routes, resolve
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "subllm is not importable; set PYTHONPATH to subactor/subllm/src"
        ) from exc
    return MissingCredentialError, available_routes, resolve


def parse_judgment(text: str) -> dict[str, Any]:
    blob = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", blob, re.S)
    if fenced:
        blob = fenced.group(1)
    else:
        start, end = blob.find("{"), blob.rfind("}")
        if start >= 0 and end > start:
            blob = blob[start : end + 1]
    data = json.loads(blob)
    if not isinstance(data, dict) or data.get("schema") != JUDGMENT_SCHEMA:
        raise ValueError("LLM output is not wellmanifest.webpage/llm-judgment/v1")
    if not isinstance(data.get("pages"), list):
        raise ValueError("llm-judgment.pages must be an array")
    return data


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
                text = _complete_openai(route, prompt, timeout)
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
