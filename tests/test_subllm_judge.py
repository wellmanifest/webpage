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
