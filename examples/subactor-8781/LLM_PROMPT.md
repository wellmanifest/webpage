Kontynuuj z tym werdyktem. Z findings zrób listę ticketów (jeden lens = jeden ticket). Nie wymyślaj palety.

```json
{
  "schema": "wellmanifest.webpage/site-audit/v1",
  "findings": [
    {
      "code": "WEB-UX-001",
      "severity": "error",
      "lens": "ux",
      "message": "Contact path /?action=contact has no form (advertised in nav/footer)",
      "url": "/?action=contact"
    },
    {
      "code": "WEB-LLM-001",
      "severity": "error",
      "lens": "ux",
      "message": "LLM judgment skipped (--skip-llm)"
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
