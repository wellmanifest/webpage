# Raport witryny — sub.actor site audit (http://127.0.0.1:8781/)

## Jak czytać

Obserwacja (DOM/tokeny) jest mierzona. **Kind, budżety i wskazówki pochodzą z LLM**
przez `subllm platform/site-audit`
(unresolved / —).
Soczewki są niezależne od typu strony. Najpierw kind, potem landmarks, potem budżety.

Źródło URL-i: **homepage-links**. sitemap=404 robots=404.

## Findings

- `WEB-LLM-001` [error/ux] WEB-LLM-001: all SubLLM candidates failed: cursor: cursor-sdk not installed | cursor: cursor-sdk not installed | zai/glm-5.2: The read operation timed out | openrouter/glm-5.2: LLM output is not wellmanifest.webpage/llm-judgment/v1 | openrouter/grok-4.5: LLM output is not wellmanifest.webpage/llm-judgment/v1 | openrouter/gemini-3.6-flash: LLM output is not wellmanifest.webpage/llm-judgment/v1

## Strony

### http://127.0.0.1:8781/
kind **unknown** (intent unknown) · fonty 2 · kolory 16 · rozmiary 3
- brak defektów soczewek

### http://127.0.0.1:8781/?action=landing
kind **unknown** (intent unknown) · fonty 2 · kolory 16 · rozmiary 3
- brak defektów soczewek

### http://127.0.0.1:8781/compare?lang=en
kind **unknown** (intent unknown) · fonty 2 · kolory 6 · rozmiary 5
- brak defektów soczewek

### http://127.0.0.1:8781/registry?lang=en
kind **unknown** (intent unknown) · fonty 2 · kolory 5 · rozmiary 6
- brak defektów soczewek

### http://127.0.0.1:8781/legal?lang=en
kind **unknown** (intent unknown) · fonty 1 · kolory 6 · rozmiary 5
- brak defektów soczewek

### http://127.0.0.1:8781/marketplace?lang=en
kind **unknown** (intent unknown) · fonty 2 · kolory 5 · rozmiary 6
- brak defektów soczewek

### http://127.0.0.1:8781/?action=contact
kind **unknown** (intent unknown) · fonty 2 · kolory 17 · rozmiary 3
- brak defektów soczewek

## Wskazówki (LLM)


POA `poa://wellmanifest.webpage/process/site-audit/v1` effect=read_data.

