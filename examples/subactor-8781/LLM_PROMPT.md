Kontynuuj z tym werdyktem. Z findings zrób listę ticketów (jeden lens = jeden ticket). Nie wymyślaj palety.

```json
{
  "schema": "wellmanifest.webpage/site-audit/v1",
  "findings": [],
  "hints": [
    "pages[/legal].structure: Add in-page table of contents with anchor links to each of the 12 H2 sections for improved navigation.",
    "SEO-TITLE-002: Page title 'Subactor — platforma autonomizacji procesów biznesowych' is brand-generic while H1 'Wybierz pakiet dla swojej organizacji' is package-specific. Align title to reflect pricing intent.",
    "UX-NAV-001: 12 H2 sections with no in-page table of contents or anchor navigation. Add a sticky TOC or section anchors for findability in long legal content.",
    "UX-STRUCTURE-001: Contact page renders full home page content (integrations, panel preview, full access sections) alongside the form. The form is not the primary focus. Isolate the contact form on its own page template.",
    "MODULARITY-001: Contact form is injected into home page via ?action=contact query param rather than having a dedicated route/template. This couples form rendering to landing content and prevents independent maintenance.",
    "UX-STRUCTURE-001: Contact form is embedded within full home page content, reducing form focus and creating cognitive overload.",
    "MODULARITY-001: Contact route uses query param ?action=contact on home URL instead of a dedicated /contact path. This couples form and landing templates.",
    "UX-NAV-001: Legal page has 12 H2 sections with no in-page navigation. Add a table of contents or section anchors."
  ],
  "subllm": {
    "application": "platform",
    "function": "site-audit",
    "provider": "openrouter",
    "model": "glm-5.2"
  }
}
```
