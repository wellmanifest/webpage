#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
fail() { echo "WEBPAGE-VALIDATE-001: $*" >&2; exit 1; }
[[ -f VERSION ]] || fail "VERSION missing"
[[ -f standard/webpage.standard.v1.json ]] || fail "standard missing"
[[ -f schemas/webpage-site-audit.schema.json ]] || fail "schema missing"
python3 - <<'PY'
import json
from pathlib import Path
root = Path(".")
version = (root / "VERSION").read_text().strip()
standard = json.loads((root / "standard/webpage.standard.v1.json").read_text())
schema = json.loads((root / "schemas/webpage-site-audit.schema.json").read_text())
assert version == "0.2.4"
assert standard["subllm"] == {"application": "platform", "function": "site-audit", "home": "subactor/subllm"}
assert "requiredPublicPaths" not in standard
audit_src = (root / "scripts/audit_site.py").read_text()
assert "INTENT_BY_PATH" not in audit_src
assert "subllm_judge" in audit_src
assert "/home/tom/" not in audit_src
assert 'page["page"]["kind"] = "unknown"' not in audit_src
assert "WEB-SITEMAP-001" in audit_src
assert "WEB-SEO-001" in audit_src
assert "WEB-UX-001" in audit_src
assert "observation_findings" in audit_src
assert "advertised_contact_targets" in audit_src
assert "mkdtemp" in audit_src
assert 'WEB-LLM-001", "warn"' in audit_src
assert "/home/tom/" not in (root / "scripts/subllm_judge.py").read_text()
assert "infer_kind" in (root / "scripts/audit_site.py").read_text() or "defects_for_page" in audit_src
assert standard["placement"]["home"] == "wellmanifest"
assert standard["placement"]["shape"] == "domain_pack"
assert standard["authority"] == "propose-only"
assert "wellmanifest/gui" in standard["adopt"]
assert "wellmanifest/poa" in standard["adopt"]
assert "wellmanifest/policy-dsl" in standard["adopt"]
assert "wellmanifest/modularity" in standard["adopt"]
assert "wellmanifest/logs" in standard["adopt"]
assert {lens["id"] for lens in standard["lenses"]} >= {
    "kind", "visual", "structure", "navigation", "a11y", "seo", "consistency", "ux", "policy", "modularity"
}
assert schema["$id"] == "https://wellmanifest.com/schemas/webpage/site-audit/v1"
print("ok: wellmanifest/webpage validate")
PY
echo "validated $(cat VERSION)"
