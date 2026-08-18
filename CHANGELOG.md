# Changelog

## [0.2.2] - 2026-08-18
### Added
- Deterministic `WEB-SEO-001` (canonical), `WEB-UX-001` (contact without a form),
  `WEB-CONS-003` (html lang drift), and `WEB-A11Y-*` from observed signals.
  These do not wait for SubLLM and do not hardcode product paths.

## [0.2.1] - 2026-08-18
### Fixed
- Keep `wellmanifest/gui` `infer_kind` and profile budgets when SubLLM fails.
- Emit `WEB-SITEMAP-001` / `WEB-ROBOTS-001` from HTTP status, not from the LLM.
- Resolve `gui/scripts` as a sibling path (no machine-local `/home/tom/...`).

## [0.2.0] - 2026-08-18
### Changed
- Kind, visual budgets, site findings and hints come from SubLLM
  `platform/site-audit`. The auditor only observes DOM/tokens and fail-closed
  policy (secrets in URL).
- URL discovery uses sitemap or homepage links. No product path allowlist.

## [0.1.0] - 2026-08-18
### Added
- Whole-site `wellmanifest.webpage/site-audit/v1` with ten type-independent lenses.
- ADOPT composition of gui, poa, policy-dsl, modularity, logs, brand.
- Sitemap-driven auditor, human `REPORT.md`, LLM prompt, logs JSONL.
- Proposed sitemap/robots for sub.actor (`:8781` currently 404s both).
