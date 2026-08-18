# LLM prompts from the webpage DSL

Do not paste raw HTML into a model. Paste `site-audit/v1` (or the generated
`LLM_PROMPT.md`).

## System rules (always)

```
ADOPT wellmanifest/webpage + wellmanifest/gui + wellmanifest/poa
     + wellmanifest/policy-dsl + wellmanifest/modularity + wellmanifest/logs.
Resolve LLM via subactor/subllm application=platform function=site-audit.
HOME of the product runtime is subactor, shape runtime_service.
Return only wellmanifest.webpage/llm-judgment/v1 JSON.
Do not invent brand tokens. Colors/fonts HOME: wellmanifest/brand.
One finding code → one ticket. Do not merge lenses.
```

## Task prompts

**Repair plan**

```
Z findings[] zrób listę ticketów: title, lens, allowedPaths, nonGoals.
Najpierw error, potem warn. Pomiń WEB-MOD-001 (to przypomnienie SSOT).
```

**Copy / UX**

```
Dla każdej strony z kind=landing|marketplace napisz jedną poprawkę H1
i jeden next-step CTA. Nie zmieniaj panel DSL (gui/dsl/v1).
```

**Consistency**

```
Porównaj visual.counts między stronami tej samej family.
Zaproponuj wspólny budżet, nie nową paletę.
```

Generated file: `examples/subactor-8781/LLM_PROMPT.md`.
