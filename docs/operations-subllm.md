# SubLLM integration

HOME of the route catalog is `subactor/subllm`. This pack only consumes it.

```text
application = platform
function    = site-audit
```

```python
from subllm import available_routes
routes = available_routes("platform", "site-audit")
```

The auditor sends measured observation JSON and expects
`wellmanifest.webpage/llm-judgment/v1`. Cursor SDK candidates are skipped
when `cursor-sdk` is not installed; Z.AI calls use a 20s timeout so a later
OpenRouter candidate can still run. SubLLM itself does not retry.

Live models sometimes wrap the document (`{meta, judgment}`) or emit aliases
(`page.kind`, `visualBudget`, `id`, `findings`, `poaHints`). The pack
normalizes those onto the schema. Finding codes that are not in
`webpage.standard.v1` become hints — the auditor does not invent new WEB-*
codes from the model.
