# Raport witryny — sub.actor site audit (http://127.0.0.1:8789/)

## Jak czytać

Obserwacja (DOM/tokeny) i **kind/budżety** idą z `wellmanifest/gui` (`infer_kind` + `page_profiles`). LLM (`subllm platform/site-audit`, openrouter / glm-5.2) dodaje wskazówki; kind nadpisuje tylko przy poprawnym enum.
Soczewki są niezależne od typu strony. Najpierw kind, potem landmarks, potem budżety.

Źródło URL-i: **sitemap**. sitemap=200 robots=200.

## Findings


## Strony

### http://127.0.0.1:8789/
kind **landing** (intent landing) · fonty 1 · kolory 10 · rozmiary 5
- brak defektów soczewek

### http://127.0.0.1:8789/compare
kind **article** (intent article) · fonty 1 · kolory 6 · rozmiary 3
- brak defektów soczewek

### http://127.0.0.1:8789/registry
kind **marketplace** (intent marketplace) · fonty 1 · kolory 5 · rozmiary 3
- brak defektów soczewek

### http://127.0.0.1:8789/marketplace
kind **marketplace** (intent marketplace) · fonty 1 · kolory 5 · rozmiary 3
- brak defektów soczewek

### http://127.0.0.1:8789/legal
kind **article** (intent article) · fonty 1 · kolory 6 · rozmiary 3
- brak defektów soczewek

### http://127.0.0.1:8789/?action=contact
kind **form** (intent form) · fonty 1 · kolory 10 · rozmiary 5
- brak defektów soczewek

## Wskazówki (LLM)

- site.brand.colors: Extract 6 core brand colors from HOME page and register as design tokens. Map rgba variants to opacity-modified token aliases.
- site.brand.typeScale: Consolidate 5 font sizes to 4 by merging 25.5px into nearest step. Register as type-scale tokens.
- pages[/?action=contact].title: Set contact page title to 'Kontakt — wdrożenie On-Premise | Subactor' to reflect form intent and differentiate from home.
- pages[/?action=contact].structure: Remove duplicate H2 matching H1 text. Isolate contact form from home page sections (integrations, panel preview, full access).
- pages[/legal].structure: Add in-page table of contents with anchor links to each of the 12 H2 sections for improved navigation.
- GUI-VIS-001: Color count 10 exceeds budget 6. Consolidate rgba opacity variants (e.g. rgba(183,247,92,0.15), rgba(34,211,197,0.15), rgba(202,214,224,0.18)) into tokenized surface/accent tokens with opacity modifiers.
- GUI-VIS-002: Font-size count 5 exceeds budget 4. Consider merging 25.5px and 19.125px into a single intermediate step or mapping both to the same token.
- SEO-TITLE-002: Page title 'Subactor — platforma autonomizacji procesów biznesowych' is brand-generic while H1 'Wybierz pakiet dla swojej organizacji' is package-specific. Align title to reflect pricing intent.
- GUI-VIS-001: Color count 6 slightly exceeds budget 5. One rgba variant (rgba(202,214,224,0.18)) could be tokenized as a surface-overlay token.
- GUI-VIS-001: Color count 6 slightly exceeds budget 5. rgba(34,211,197,0.08) is a one-off variant — tokenize as accent-secondary-faint.
- UX-NAV-001: 12 H2 sections with no in-page table of contents or anchor navigation. Add a sticky TOC or section anchors for findability in long legal content.
- GUI-VIS-001: Color count 10 exceeds budget 6. Same excess as home page — inherited from shared template. Consolidate rgba opacity variants into tokens.
- GUI-VIS-002: Font-size count 5 exceeds budget 4. Inherited from home template.
- A11Y-HEADING-001: H1 'Zapytanie o wdrożenie On-Premise' and H2 'Zapytanie o wdrożenie On-Premise' are identical. Remove the duplicate H2 or change it to a contextual subheading.
- SEO-TITLE-001: Page title 'Subactor — platforma autonomizacji procesów biznesowych' is identical to home page and does not reflect contact intent. Set a descriptive title like 'Kontakt — wdrożenie On-Premise | Subactor'.
- UX-STRUCTURE-001: Contact page renders full home page content (integrations, panel preview, full access sections) alongside the form. The form is not the primary focus. Isolate the contact form on its own page template.
- MODULARITY-001: Contact form is injected into home page via ?action=contact query param rather than having a dedicated route/template. This couples form rendering to landing content and prevents independent maintenance.
- GUI-VIS-001: Multiple pages exceed color budget due to rgba opacity variants of brand colors. Define opacity-modified tokens (e.g. accent-primary--faint, surface--overlay) instead of inline rgba values.
- GUI-VIS-002: Home and contact pages use 5 font sizes vs budget 4. Consolidate 25.5px into either 19.125px or 38.25px step.
- SEO-TITLE-001: Contact page title is identical to home page. Each page should have a unique, intent-reflective title.
- A11Y-HEADING-001: Duplicate H1/H2 heading text on contact page reduces heading distinctiveness for screen reader navigation.
- UX-STRUCTURE-001: Contact form is embedded within full home page content, reducing form focus and creating cognitive overload.
- MODULARITY-001: Contact route uses query param ?action=contact on home URL instead of a dedicated /contact path. This couples form and landing templates.
- UX-NAV-001: Legal page has 12 H2 sections with no in-page navigation. Add a table of contents or section anchors.

POA `poa://wellmanifest.webpage/process/site-audit/v1` effect=read_data.

