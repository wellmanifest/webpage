Kontynuuj z tym werdyktem. Z findings zrób listę ticketów (jeden lens = jeden ticket). Nie wymyślaj palety.

```json
{
  "schema": "wellmanifest.webpage/site-audit/v1",
  "findings": [
    {
      "code": "WEB-LLM-001",
      "severity": "error",
      "lens": "ux",
      "message": "WEB-LLM-001: all SubLLM candidates failed: cursor: cursor-sdk not installed | cursor: cursor-sdk not installed | zai/glm-5.2: The read operation timed out | openrouter/glm-5.2: LLM output is not wellmanifest.webpage/llm-judgment/v1 | openrouter/grok-4.5: LLM output is not wellmanifest.webpage/llm-judgment/v1 | openrouter/gemini-3.6-flash: LLM output is not wellmanifest.webpage/llm-judgment/v1"
    }
  ],
  "hints": [],
  "subllm": {
    "application": "platform",
    "function": "site-audit",
    "provider": "",
    "model": ""
  }
}
```
