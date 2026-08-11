from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SHA = "f99ceb4437dadd968ab66d488e13e930ceb7c7d0"
PLUGIN_URL = "https://github.com/RomeoRaven/operator-plugin"


def _bundle() -> dict:
    return yaml.safe_load((ROOT / "protoagent.bundle.yaml").read_text())


def test_bundle_is_one_immutable_read_only_operator_member():
    bundle = _bundle()

    assert bundle["id"] == "operator-stack"
    assert bundle["name"] == "Operator Stack"
    assert bundle["verified_against"] == "0.131.3"
    assert bundle["plugins"] == [
        {
            "id": "operator_control",
            "url": PLUGIN_URL,
            "ref": PLUGIN_SHA,
        }
    ]
    assert bundle["enabled"] == ["operator_control"]


def test_bundle_starts_unbound_without_credentials_or_write_surfaces():
    bundle = _bundle()

    assert bundle["config"] == {
        "operator_control": {
            "targets": [],
            "timeout_seconds": 5,
        }
    }
    assert "secrets" not in bundle
    assert "mcp" not in bundle
    assert "archetype" not in bundle

    rendered = (ROOT / "protoagent.bundle.yaml").read_text().lower()
    for forbidden in (
        "target_tokens:",
        "api_key",
        "password",
        "allow_run: true",
        "write: true",
        "restart",
        "remediation",
    ):
        assert forbidden not in rendered


def test_canonical_grounding_and_operator_docs_preserve_incubation_boundary():
    proto = (ROOT / "PROTO.md").read_text()
    readme = (ROOT / "README.md").read_text()

    assert "single agent-grounding source" in proto
    assert "immutable commit SHA" in proto
    assert "release authorization" in proto
    assert "not_configured" in readme
    assert "plugin install https://github.com/RomeoRaven/operator-stack" in readme
    assert "/home/romeoraven" not in (ROOT / "scripts" / "verify_bundle.py").read_text()
    assert not (ROOT / "AGENTS.md").exists()
    assert not (ROOT / "CLAUDE.md").exists()
