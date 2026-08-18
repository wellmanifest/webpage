# How a human reads the webpage DSL

The site audit is JSON, but you do not need to read it as a programmer.

## Three columns

| Field | Meaning |
| --- | --- |
| `page.kind` | What the page **is** (landing, marketplace, article, form, auth, panel) |
| `intentKind` | What the URL **promised** |
| `defects[].code` | What is broken, same code on every page type |

If `intentKind` ≠ `kind`, stop. Do not argue about fonts. The user opened the
wrong surface. Kind and intent come from `wellmanifest/gui` `infer_kind`
(URL + DOM + headings). SubLLM (`platform/site-audit`) may override them
only when it emits a valid kind enum. Invented finding ids become hints. Hints that contradict measured titles,
headings, or GUI budgets are dropped. After `WEB-UX-001` is closed
(advertised contact href has a form), unofficial isolate-contact /
dedicated-`/contact` hints are dropped too. Official UX does not require
a standalone `/contact`. Leftover unofficial hints are not tickets. This
pack does not hardcode product paths.

## Severity

- **error** — user cannot finish the job, or crawlers have no index.
- **warn** — site is usable but inconsistent or hard to scan.
- **info** — align later; do not treat as a product outage.

## Order of work

1. Sitemap + robots (`WEB-SITEMAP-001`, `WEB-ROBOTS-001`).
2. Kind / contact path (`WEB-UX-001`, `WEB-UX-002`) — footer/nav advertises
   contact, and the followed page still has no form, or a form page reuses
   another page's H1. Sitemap may omit that URL; the auditor still opens
   the advertised href.
3. One shared footer (`WEB-NAV-001`) and one shared header nav (`WEB-NAV-002`).
   Header signals do not include footer `<nav>` links. A long `article`
   (eight or more H2s) without in-page anchors is `WEB-NAV-003`.
4. Visual budgets (`GUI-VIS-*`) — still not a second brand kit.
5. Cross-page color/font/lang drift (`WEB-CONS-*`).
6. Missing `rel=canonical` (`WEB-SEO-001`).

## Generated report

`REPORT.md` is the same DSL flattened into Polish sentences. If the markdown
and the JSON disagree, the JSON is the source.
