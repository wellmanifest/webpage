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
