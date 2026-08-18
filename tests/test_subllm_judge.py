import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from subllm_judge import parse_judgment


def test_fixture_is_valid_judgment() -> None:
    raw = Path(__file__).resolve().parents[1] / "examples/fixtures/llm-judgment.v1.json"
    parsed = parse_judgment(raw.read_text())
    assert parsed["schema"] == "wellmanifest.webpage/llm-judgment/v1"


def test_observation_keeps_gui_kind() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import observation_page

    raw = {
        "title": "EU legal information",
        "structure": {
            "landmarks": {"main": True, "footer": True, "h1": "Legal", "form": False, "article": True, "listing": False, "headingOutline": [{"tag": "H1", "text": "Legal"}]},
            "chrome": {},
        },
        "tokens": {"fontFamilyCount": 1, "colorCount": 6, "fontSizeCount": 3, "fontFamilies": [], "colors": [], "fontSizes": []},
    }
    item = observation_page("http://127.0.0.1:8781/legal", raw, {"title": "EU legal information"})
    assert item["intentKind"] == "article"
    assert item["page"]["page"]["kind"] == "article"
    assert item["page"]["visual"]["budgets"]["fontSizes"] >= 3


def test_article_kind_without_article_landmark() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import observation_page

    raw = {
        "title": "Compare",
        "structure": {
            "landmarks": {
                "main": True,
                "footer": True,
                "h1": "Compare",
                "form": False,
                "article": False,
                "listing": True,
                "headingOutline": [{"tag": "H1", "text": "Compare"}],
            },
            "chrome": {},
        },
        "tokens": {"fontFamilyCount": 1, "colorCount": 4, "fontSizeCount": 3, "fontFamilies": [], "colors": [], "fontSizes": []},
    }
    item = observation_page("http://127.0.0.1:8789/compare", raw, {"title": "Compare"})
    assert item["page"]["page"]["kind"] == "article"
    assert any(d["code"] == "GUI-VIS-STRUCT-005" for d in item["page"]["defects"])
    assert item["lenses"]["structure"][0]["code"] == "GUI-VIS-STRUCT-005"


def test_article_heading_outline_without_h2() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import observation_page

    raw = {
        "title": "Compare",
        "structure": {
            "landmarks": {
                "main": True,
                "footer": True,
                "h1": "Compare",
                "form": False,
                "article": True,
                "listing": True,
                "headingOutline": [{"tag": "H1", "text": "Compare"}],
            },
            "chrome": {},
        },
        "tokens": {"fontFamilyCount": 1, "colorCount": 4, "fontSizeCount": 3, "fontFamilies": [], "colors": [], "fontSizes": []},
    }
    item = observation_page("http://127.0.0.1:8789/compare", raw, {"title": "Compare"})
    assert any(d["code"] == "GUI-VIS-STRUCT-006" for d in item["page"]["defects"])


def test_contact_url_with_form_is_form_despite_long_outline() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import observation_page

    raw = {
        "title": "Subactor — platforma",
        "structure": {
            "landmarks": {
                "main": True,
                "footer": True,
                "h1": "Wybierz pakiet",
                "form": True,
                "article": False,
                "listing": False,
                "headingOutline": [
                    {"tag": "H1", "text": "Wybierz pakiet"},
                    {"tag": "H2", "text": "Integracje"},
                    {"tag": "H2", "text": "Panel"},
                    {"tag": "H3", "text": "Dziennik"},
                    {"tag": "H2", "text": "Kontakt"},
                ],
            },
            "chrome": {},
        },
        "tokens": {"fontFamilyCount": 1, "colorCount": 6, "fontSizeCount": 3, "fontFamilies": [], "colors": [], "fontSizes": []},
    }
    item = observation_page(
        "http://127.0.0.1:8789/?action=contact",
        raw,
        {"title": "Subactor — platforma", "formCount": 1},
    )
    assert item["intentKind"] == "form"
    assert item["page"]["page"]["kind"] == "form"


def test_observation_findings_flag_canonical_contact_and_lang() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import observation_findings

    pages = [
        {
            "url": "http://127.0.0.1:8789/",
            "signals": {
                "lang": "pl",
                "canonical": "",
                "viewport": True,
                "formCount": 0,
                "footerLinks": ["/?action=contact"],
                "navLinks": ["/?action=contact"],
            },
            "lenses": {"seo": [], "ux": [], "a11y": []},
        },
        {
            "url": "http://127.0.0.1:8789/compare",
            "signals": {
                "lang": "en",
                "canonical": "http://127.0.0.1:8789/compare",
                "viewport": True,
                "formCount": 0,
                "footerLinks": ["/?action=contact"],
                "navLinks": [],
            },
            "lenses": {"seo": [], "ux": [], "a11y": []},
        },
    ]
    codes = {row["code"] for row in observation_findings(pages)}
    assert "WEB-SEO-001" in codes
    assert "WEB-UX-001" in codes
    assert "WEB-CONS-003" in codes
    assert pages[0]["lenses"]["seo"][0]["code"] == "WEB-SEO-001"


def test_observation_findings_flag_form_reusing_other_h1() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import observation_findings

    pages = [
        {
            "url": "http://127.0.0.1:8789/",
            "intentKind": "landing",
            "page": {
                "page": {"kind": "landing"},
                "structure": {"landmarks": {"h1": "Wybierz pakiet"}},
            },
            "signals": {
                "lang": "pl",
                "canonical": "http://127.0.0.1:8789/",
                "viewport": True,
                "formCount": 0,
                "footerLinks": ["/?action=contact"],
                "navLinks": ["/?action=contact"],
            },
            "lenses": {},
        },
        {
            "url": "http://127.0.0.1:8789/?action=contact",
            "intentKind": "form",
            "page": {
                "page": {"kind": "form"},
                "structure": {"landmarks": {"h1": "Wybierz pakiet"}},
            },
            "signals": {
                "lang": "pl",
                "canonical": "http://127.0.0.1:8789/",
                "viewport": True,
                "formCount": 1,
                "footerLinks": ["/?action=contact"],
                "navLinks": [],
            },
            "lenses": {},
        },
    ]
    codes = {row["code"] for row in observation_findings(pages)}
    assert "WEB-UX-001" not in codes
    assert "WEB-UX-002" in codes


def test_observation_findings_skip_contact_when_form_observed() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import advertised_contact_targets, observation_findings

    home = {
        "url": "http://127.0.0.1:8789/",
        "signals": {
            "lang": "pl",
            "canonical": "http://127.0.0.1:8789/",
            "viewport": True,
            "formCount": 0,
            "footerLinks": ["/?action=contact"],
            "navLinks": ["/?action=contact"],
        },
        "lenses": {"seo": [], "ux": [], "a11y": []},
    }
    contact = {
        "url": "http://127.0.0.1:8789/?action=contact",
        "signals": {
            "lang": "pl",
            "canonical": "http://127.0.0.1:8789/",
            "viewport": True,
            "formCount": 1,
            "footerLinks": ["/?action=contact"],
            "navLinks": [],
        },
        "lenses": {"seo": [], "ux": [], "a11y": []},
    }
    codes = {row["code"] for row in observation_findings([home, contact])}
    assert "WEB-UX-001" not in codes
    assert advertised_contact_targets([home], "http://127.0.0.1:8789/") == [
        "http://127.0.0.1:8789/?action=contact"
    ]


def test_observation_findings_flag_footer_and_family_drift() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from audit_site import observation_findings

    pages = [
        {
            "url": "http://127.0.0.1:8789/compare",
            "page": {
                "page": {"family": "content"},
                "visual": {
                    "counts": {"colors": 6},
                    "tokens": {"fontFamilies": [{"value": "Inter"}]},
                },
            },
            "signals": {
                "lang": "pl",
                "canonical": "http://127.0.0.1:8789/compare",
                "viewport": True,
                "formCount": 0,
                "footerLinks": ["/compare", "/legal"],
                "navLinks": ["/compare", "/legal"],
            },
            "lenses": {},
        },
        {
            "url": "http://127.0.0.1:8789/legal",
            "page": {
                "page": {"family": "content"},
                "visual": {
                    "counts": {"colors": 11},
                    "tokens": {"fontFamilies": [{"value": "Arial"}]},
                },
            },
            "signals": {
                "lang": "pl",
                "canonical": "http://127.0.0.1:8789/legal",
                "viewport": True,
                "formCount": 0,
                "footerLinks": ["/compare", "/legal", "/"],
                "navLinks": ["/compare", "/legal", "/"],
            },
            "lenses": {},
        },
    ]
    codes = {row["code"] for row in observation_findings(pages)}
    assert "WEB-NAV-001" in codes
    assert "WEB-NAV-002" in codes
    assert "WEB-CONS-001" in codes
    assert "WEB-CONS-002" in codes


def test_parse_judgment_normalizes_live_wrapper() -> None:
    raw = {
        "meta": {"application": "platform", "function": "site-audit", "provider": "openrouter", "model": "glm-5.2"},
        "judgment": {
            "schema": "wellmanifest.webpage/llm-judgment/v1",
            "pages": [
                {
                    "url": "http://127.0.0.1:8789/",
                    "page": {"kind": "landing.pricing", "intentKind": "evaluate"},
                    "visualBudget": {"colors": 6, "fontSizes": 4, "fontFamilies": 1},
                    "findings": [
                        {
                            "id": "GUI-VIS-001",
                            "lens": "visual",
                            "severity": "medium",
                            "message": "Color count 10 exceeds invented budget 6.",
                        },
                        {
                            "id": "WEB-SEO-001",
                            "lens": "seo",
                            "severity": "low",
                            "message": "Missing rel=canonical",
                            "url": "http://127.0.0.1:8789/",
                        },
                    ],
                }
            ],
            "findings": [
                {
                    "id": "UX-STRUCTURE-001",
                    "lens": "ux",
                    "severity": "high",
                    "message": "Contact form is embedded in the landing template.",
                }
            ],
            "poaHints": [
                {"target": "pages[/?action=contact].structure", "hint": "Isolate the contact form."}
            ],
        },
    }
    parsed = parse_judgment(json.dumps(raw))
    assert parsed["pages"][0]["kind"] == "landing"
    assert parsed["pages"][0]["intentKind"] == "unknown"
    assert parsed["pages"][0]["budgets"]["colors"] == 6
    codes = {row["code"] for row in parsed["pages"][0]["findings"]}
    assert codes == {"WEB-SEO-001"}
    assert parsed["pages"][0]["findings"][0]["severity"] == "info"
    assert parsed["siteFindings"] == []
    assert any("GUI-VIS-001" in hint for hint in parsed["hints"])
    assert any("UX-STRUCTURE-001" in hint for hint in parsed["hints"])
    assert any("Isolate the contact form" in hint for hint in parsed["hints"])


def test_apply_judgment_keeps_observed_kind_and_budgets() -> None:
    from audit_site import apply_judgment

    pages = [
        {
            "url": "http://127.0.0.1:8789/",
            "intentKind": "landing",
            "page": {
                "page": {"kind": "landing", "family": "marketing"},
                "visual": {"budgets": {"fontFamilies": 3, "colors": 16, "fontSizes": 8}},
            },
            "lenses": {"seo": [], "visual": []},
        }
    ]
    apply_judgment(
        pages,
        {
            "pages": [
                {
                    "url": "http://127.0.0.1:8789/",
                    "kind": "landing",
                    "intentKind": "unknown",
                    "budgets": {"fontFamilies": 1, "colors": 6, "fontSizes": 4},
                    "findings": [
                        {
                            "code": "WEB-SEO-001",
                            "severity": "info",
                            "lens": "seo",
                            "message": "Missing rel=canonical",
                        }
                    ],
                }
            ]
        },
    )
    assert pages[0]["intentKind"] == "landing"
    assert pages[0]["page"]["page"]["kind"] == "landing"
    assert pages[0]["page"]["visual"]["budgets"]["colors"] == 16
    assert pages[0]["lenses"]["seo"][0]["code"] == "WEB-SEO-001"


def test_parse_judgment_accepts_fenced_json() -> None:
    raw = {
        "schema": "wellmanifest.webpage/llm-judgment/v1",
        "pages": [
            {
                "url": "http://127.0.0.1:8781/",
                "kind": "landing",
                "intentKind": "landing",
                "budgets": {"fontFamilies": 3, "colors": 16, "fontSizes": 8},
                "findings": [],
            }
        ],
        "siteFindings": [],
        "hints": ["Add sitemap.xml"],
    }
    parsed = parse_judgment("```json\n" + json.dumps(raw) + "\n```")
    assert parsed["pages"][0]["kind"] == "landing"
