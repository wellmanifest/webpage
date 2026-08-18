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
when `cursor-sdk` is not installed; the caller then uses the next
OpenAI-compatible candidate (Z.AI / OpenRouter). SubLLM itself does not retry.
