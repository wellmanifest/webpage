# Webpage standardization (normative)

Authority: **propose-only**. Adopters implement in their runtime HOME.

Pack version **0.2.0** (standard document version 1).

## Objects

| Object | Role |
| --- | --- |
| Site audit | `wellmanifest.webpage/site-audit/v1` — sitemap + pages + findings |
| Page document | Reused `wellmanifest.gui/page/v1` per URL |
| Lenses | Type-independent checks (kind, visual, nav, a11y, seo, …) |
| POA process | `poa://wellmanifest.webpage/process/site-audit/v1` (`read_data`) |
| Logs projection | JSONL `validation_*` events |

## Invariants

1. Missing `/sitemap.xml` or `/robots.txt` is `WEB-SITEMAP-001` /
   `WEB-ROBOTS-001` from the HTTP status, not from the LLM.
2. Kind, budgets and hints are **not** hardcoded. SubLLM `platform/site-audit`
   returns `wellmanifest.webpage/llm-judgment/v1`. Observation is measured.
3. URL lists come from the sitemap or homepage links, never a product allowlist.
4. Brand tokens are not redefined here (`wellmanifest/brand`).
5. Reports never grant apply (POA + policy-dsl). Secrets in a URL stay
   fail-closed without the model.
6. Modules stay single-exporter (`wellmanifest/modularity`).

## Adopting

1. `placement.adopt: wellmanifest/webpage` on the runtime ticket.
2. Pin this pack revision. Implement sitemap/robots in the product repo.
3. Run `python3 scripts/audit_site.py --base <origin>`.
4. Open tickets from `findings[]`, one lens at a time.
