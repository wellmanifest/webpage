# AGENTS.md

This repository is the **HOME** pack for whole-site webpage standardization
(`wellmanifest/webpage`).

HOME vs ADOPT: `HOME wellmanifest`, `shape domain_pack`. Product sites
(e.g. `subactor/www-sub-actor`) **ADOPT** this pack. They must not invent a
second site-UX SSOT.

This pack **composes** other HOME packs; it does not copy their contracts:

| Concern | HOME pack |
| --- | --- |
| Page kind, landmarks, visual budgets | `wellmanifest/gui` |
| Process / inspect / receipt | `wellmanifest/poa` |
| Inert policy (no secrets in URL, propose-only) | `wellmanifest/policy-dsl` |
| Single-exporter composition | `wellmanifest/modularity` |
| Evidence events | `wellmanifest/logs` |
| Allowed color/font tokens | `wellmanifest/brand` |
| LLM route (kind, budgets, hints) | `subactor/subllm` `platform/site-audit` |

Closed vocabulary: `HOME` wellmanifest|subactor|semcod;
`SHAPE` domain_pack|runtime_service|both; `ADOPT` wellmanifest/webpage.

Propose-only: documents and reports are evidence. They do not grant mutation,
merge, or production apply. `shape=runtime_service` must not use
`home=wellmanifest`.
