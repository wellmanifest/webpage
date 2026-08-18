Kontynuuj z tym werdyktem. Z findings zrób listę ticketów (jeden lens = jeden ticket). Nie wymyślaj palety.

```json
{
  "schema": "wellmanifest.webpage/site-audit/v1",
  "findings": [
    {
      "code": "WEB-LLM-001",
      "severity": "error",
      "lens": "ux",
      "message": "LLM judgment skipped (--skip-llm)"
    },
    {
      "code": "GUI-VIS-COLOR-001",
      "severity": "warn",
      "message": "17 unique colors (budget 16)",
      "lens": "visual",
      "url": "http://127.0.0.1:8789/"
    },
    {
      "code": "GUI-VIS-TYPE-001",
      "severity": "warn",
      "message": "17 font sizes (budget 8)",
      "lens": "visual",
      "url": "http://127.0.0.1:8789/"
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
