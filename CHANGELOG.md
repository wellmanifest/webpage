# Changelog

## [0.2.7] - 2026-08-18
### Added
- Structure lens lists `GUI-VIS-STRUCT-005` (article kind without `<article>`).

## [0.2.6] - 2026-08-18
### Added
- Deterministic `WEB-NAV-002` (header nav link-set drift). `navLinks` ignore
  anchors inside `footer` so a footer `<nav>` is not counted twice.

## [0.2.5] - 2026-08-18
### Added
- Deterministic `WEB-NAV-001` (footer link-set drift) and same-family
  `WEB-CONS-001` / `WEB-CONS-002` (color-count / font-family drift).

## [0.2.4] - 2026-08-18
### Changed
- `--skip-llm` records `WEB-LLM-001` as **warn**, not error. A skipped judge
  is an operator choice; a failed SubLLM call stays error.

## [0.2.3] - 2026-08-18
### Fixed
- Follow contact hrefs advertised in nav/footer even when sitemap omitted them.
  `WEB-UX-001` only fires after that page is observed and still has no form.

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
