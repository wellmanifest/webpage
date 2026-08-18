# Raport witryny — sub.actor site audit (http://127.0.0.1:8789/)

## Jak czytać

Obserwacja (DOM/tokeny) i **kind/budżety** idą z `wellmanifest/gui` (`infer_kind` + `page_profiles`). LLM (`subllm platform/site-audit`, optional / —) może nadpisać kind/budżety i dodać wskazówki.
Soczewki są niezależne od typu strony. Najpierw kind, potem landmarks, potem budżety.

Źródło URL-i: **sitemap**. sitemap=200 robots=200.

## Findings

- `WEB-LLM-001` [error/ux] LLM judgment skipped (--skip-llm)

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
kind **landing** (intent landing) · fonty 1 · kolory 10 · rozmiary 5
- brak defektów soczewek

## Wskazówki (LLM)


POA `poa://wellmanifest.webpage/process/site-audit/v1` effect=read_data.

