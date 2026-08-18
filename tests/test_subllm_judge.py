import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from subllm_judge import parse_judgment


def test_fixture_is_valid_judgment() -> None:
    raw = Path(__file__).resolve().parents[1] / "examples/fixtures/llm-judgment.v1.json"
    parsed = parse_judgment(raw.read_text())
    assert parsed["schema"] == "wellmanifest.webpage/llm-judgment/v1"


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
