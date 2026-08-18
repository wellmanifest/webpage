# wellmanifest/webpage

Whole-site UX standard. One document describes **every public page**, not
only the signed-in panel.

HOME `wellmanifest`, shape `domain_pack`, propose-only. Product runtimes
ADOPT this pack. This pack ADOPTs `gui`, `poa`, `policy-dsl`, `modularity`,
`logs`, and `brand` — it does not copy their contracts.

## What it adds

- Closed **lenses** (kind, visual, structure, navigation, a11y, seo,
  consistency, ux, policy, modularity) that apply to any page type.
- `wellmanifest.webpage/site-audit/v1` — sitemap-driven report.
- Human markdown + LLM prompt generated from the same DSL.
- Evidence JSONL for `wellmanifest/logs`.

## Quick start

Needs `subactor/subllm` on `PYTHONPATH` (or `pip install -e` that repo) and a
workspace credential in `subllm/.env`. Route: `platform/site-audit`.

```bash
./project.sh check
PYTHONPATH="${SUBLLM_SRC:-../subllm/src}" \
  python3 scripts/audit_site.py --base http://127.0.0.1:8781/ \
  --out-dir examples/subactor-8781
```

Read `examples/subactor-8781/REPORT.md` (human) and `LLM_PROMPT.md` (LLM).

## Sitemap

`:8781` currently has **no** `/sitemap.xml` or `/robots.txt`. The audit
records `WEB-SITEMAP-001` and writes a proposed sitemap. Runtime apply lives
in `subactor/www-sub-actor` (not here) — see `examples/adopt/`.
