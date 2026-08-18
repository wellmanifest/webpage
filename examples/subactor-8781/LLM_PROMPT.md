Kontynuuj z tym werdyktem. Z findings zrób listę ticketów (jeden lens = jeden ticket). Nie wymyślaj palety.

```json
{
  "schema": "wellmanifest.webpage/site-audit/v1",
  "findings": [],
  "hints": [
    "UX-STRUCTURE-001: Contact page renders full home page content (integrations, panel preview, full access sections) alongside the form. The form is not the primary focus. Isolate the contact form on its own page template.",
    "MODULARITY-001: Contact form is injected into home page via ?action=contact query param rather than having a dedicated route/template. This couples form rendering to landing content and prevents independent maintenance.",
    "UX-STRUCTURE-001: Contact form is embedded within full home page content, reducing form focus and creating cognitive overload.",
    "MODULARITY-001: Contact route uses query param ?action=contact on home URL instead of a dedicated /contact path. This couples form and landing templates."
  ],
  "subllm": {
    "application": "platform",
    "function": "site-audit",
    "provider": "openrouter",
    "model": "glm-5.2"
  }
}
```
