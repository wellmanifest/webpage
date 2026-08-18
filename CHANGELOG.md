# Changelog

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
