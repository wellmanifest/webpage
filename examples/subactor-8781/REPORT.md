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

- SEO-TITLE-002: Page title 'Subactor — platforma autonomizacji procesów biznesowych' is brand-generic while H1 'Wybierz pakiet dla swojej organizacji' is package-specific. Align title to reflect pricing intent.
- UX-STRUCTURE-001: Contact page renders full home page content (integrations, panel preview, full access sections) alongside the form. The form is not the primary focus. Isolate the contact form on its own page template.
- MODULARITY-001: Contact form is injected into home page via ?action=contact query param rather than having a dedicated route/template. This couples form rendering to landing content and prevents independent maintenance.
- UX-STRUCTURE-001: Contact form is embedded within full home page content, reducing form focus and creating cognitive overload.
- MODULARITY-001: Contact route uses query param ?action=contact on home URL instead of a dedicated /contact path. This couples form and landing templates.

POA `poa://wellmanifest.webpage/process/site-audit/v1` effect=read_data.

