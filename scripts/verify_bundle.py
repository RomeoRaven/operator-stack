from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

PLUGIN_SHA = "b4ffc439ecdab57169990309edc0805c66bf4588"


def main(bundle_source: str) -> int:
    checkout = Path(os.environ.get("PROTOAGENT_CHECKOUT", os.getcwd())).resolve()
    if not (checkout / "graph" / "plugins" / "installer.py").is_file():
        print(f"FAIL: protoAgent checkout not found at {checkout}")
        return 2

    sys.path.insert(0, str(checkout))
    source = Path(bundle_source).resolve()

    with tempfile.TemporaryDirectory(prefix="operator-stack-verify-") as tmp:
        scratch = Path(tmp)
        config_dir = scratch / "config"
        plugins_dir = config_dir / "plugins"
        config_dir.mkdir()
        os.environ["PROTOAGENT_CONFIG_DIR"] = str(config_dir)
        os.environ["PROTOAGENT_PLUGINS_DIR"] = str(plugins_dir)
        os.environ["PROTOAGENT_PLUGINS_LOCK"] = str(scratch / "plugins.lock")

        from graph.config import LangGraphConfig
        from graph.plugins import installer
        from graph.plugins.loader import load_plugins

        summary = installer.install(str(source), by="operator-stack-verifier")
        assert summary["bundle"] == "operator-stack"
        assert summary["enabled"] == ["operator_control"]
        assert summary["config"] == {"operator_control": {"targets": [], "timeout_seconds": 5}}
        assert len(summary["installed"]) == 1
        installed = summary["installed"][0]
        assert installed["id"] == "operator_control"
        assert installed["requested_ref"] == PLUGIN_SHA
        assert installed["resolved_sha"] == PLUGIN_SHA

        cfg_path = config_dir / "langgraph-config.yaml"
        cfg_path.write_text(
            "plugins:\n"
            "  enabled: [operator_control]\n"
            f"  plugins_dir: {plugins_dir}\n"
            "operator_control:\n"
            "  targets: []\n"
            "  timeout_seconds: 5\n"
        )
        loaded = load_plugins(LangGraphConfig.from_yaml(str(cfg_path)))
        plugin_meta = next(m for m in loaded.meta if m["id"] == "operator_control")
        assert plugin_meta["loaded"] is True
        assert plugin_meta["incomplete"] is False

        tools = [tool for tool in loaded.tools if tool.name == "operator_snapshot"]
        assert len(tools) == 1
        assert tools[0].args == {}
        with patch(
            "httpx.AsyncClient",
            side_effect=AssertionError("unconfigured stack attempted network access"),
        ):
            result = json.loads(asyncio.run(tools[0].ainvoke({})))
        assert result == {
            "schema_version": "operator.fleet_snapshot.v1",
            "status": "not_configured",
            "error": "Configure operator_control.targets before inspecting the fleet.",
        }

        lock = json.loads((scratch / "plugins.lock").read_text())
        locked = next(p for p in lock["plugins"] if p["id"] == "operator_control")
        assert locked["requested_ref"] == PLUGIN_SHA
        assert locked["resolved_sha"] == PLUGIN_SHA

        print(
            json.dumps(
                {
                    "bundle": summary["bundle"],
                    "plugin": installed["id"],
                    "resolved_sha": installed["resolved_sha"],
                    "tool": tools[0].name,
                    "result": result["status"],
                    "network_attempted": False,
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: verify_bundle.py BUNDLE_REPOSITORY")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
