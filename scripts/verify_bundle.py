from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

PLUGIN_SHA = "f99ceb4437dadd968ab66d488e13e930ceb7c7d0"
POLICY_SHA = "f6b1953023b0039d05ae9e52aedc12b39554d894"


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
        assert summary["enabled"] == ["operator_control", "operator_policy"]
        assert summary["config"] == {"operator_control": {"targets": [], "timeout_seconds": 5}}
        assert len(summary["installed"]) == 2
        installed_by_id = {plugin["id"]: plugin for plugin in summary["installed"]}
        assert installed_by_id["operator_control"]["requested_ref"] == PLUGIN_SHA
        assert installed_by_id["operator_control"]["resolved_sha"] == PLUGIN_SHA
        assert installed_by_id["operator_policy"]["requested_ref"] == POLICY_SHA
        assert installed_by_id["operator_policy"]["resolved_sha"] == POLICY_SHA

        cfg_path = config_dir / "langgraph-config.yaml"
        cfg_path.write_text(
            "plugins:\n"
            "  enabled: [operator_control, operator_policy]\n"
            f"  plugins_dir: {plugins_dir}\n"
            "operator_control:\n"
            "  targets: []\n"
            "  timeout_seconds: 5\n"
        )
        loaded = load_plugins(LangGraphConfig.from_yaml(str(cfg_path)))
        meta_by_id = {meta["id"]: meta for meta in loaded.meta}
        assert meta_by_id["operator_control"]["loaded"] is True
        assert meta_by_id["operator_control"]["incomplete"] is False
        assert meta_by_id["operator_policy"]["loaded"] is True
        assert meta_by_id["operator_policy"]["incomplete"] is False

        expected_tools = {"operator_snapshot", "operator_select_attention"}
        tools = {tool.name: tool for tool in loaded.tools if tool.name in expected_tools}
        assert set(tools) == expected_tools
        assert tools["operator_snapshot"].args == {}
        assert set(tools["operator_select_attention"].args) == {"snapshot"}
        with patch(
            "httpx.AsyncClient",
            side_effect=AssertionError("unconfigured stack attempted network access"),
        ):
            snapshot_result = json.loads(asyncio.run(tools["operator_snapshot"].ainvoke({})))
        assert snapshot_result == {
            "schema_version": "operator.fleet_snapshot.v1",
            "status": "not_configured",
            "error": "Configure operator_control.targets before inspecting the fleet.",
        }
        policy_result = json.loads(
            tools["operator_select_attention"].invoke(
                {
                    "snapshot": {
                        "schema_version": "operator.fleet_snapshot.v1",
                        "observed_at": "2026-08-12T02:30:00Z",
                        "status": "ready",
                        "findings": [],
                    }
                }
            )
        )
        assert policy_result["status"] == "no_attention_required"
        assert policy_result["selected_finding"] is None

        lock = json.loads((scratch / "plugins.lock").read_text())
        locked_by_id = {plugin["id"]: plugin for plugin in lock["plugins"]}
        assert locked_by_id["operator_control"]["requested_ref"] == PLUGIN_SHA
        assert locked_by_id["operator_control"]["resolved_sha"] == PLUGIN_SHA
        assert locked_by_id["operator_policy"]["requested_ref"] == POLICY_SHA
        assert locked_by_id["operator_policy"]["resolved_sha"] == POLICY_SHA

        print(
            json.dumps(
                {
                    "bundle": summary["bundle"],
                    "plugins": sorted(installed_by_id),
                    "resolved_shas": {
                        plugin_id: plugin["resolved_sha"] for plugin_id, plugin in sorted(installed_by_id.items())
                    },
                    "tools": sorted(tools),
                    "snapshot_result": snapshot_result["status"],
                    "policy_result": policy_result["status"],
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
