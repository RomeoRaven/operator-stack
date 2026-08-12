# Operator Stack

A conservative protoAgent bundle that separates read-only fleet evidence from deterministic attention policy.

It installs two pinned plugins:

- [Operator Control](https://github.com/RomeoRaven/operator-plugin) collects normalized findings from operator-configured targets using GET-only health and runtime reads.
- [Operator Attention Policy](https://github.com/RomeoRaven/operator-policy-plugin) chooses the one existing finding that needs attention first—or reports all clear.

The bundle starts with no targets or credentials, so a fresh install performs no network inspection until an operator deliberately configures the fleet.

## Install

From a current protoAgent checkout:

```bash
python -m server plugin install https://github.com/RomeoRaven/operator-stack
```

The bundle suggests enabling `operator_control` and `operator_policy`. Its only configuration is:

```yaml
operator_control:
  targets: []
  timeout_seconds: 5
```

Before targets are configured, `operator_snapshot` returns:

```json
{
  "schema_version": "operator.fleet_snapshot.v1",
  "status": "not_configured",
  "error": "Configure operator_control.targets before inspecting the fleet."
}
```

For a valid snapshot with no findings, `operator_select_attention(snapshot)` returns:

```json
{
  "schema_version": "operator.attention_selection.v1",
  "policy_version": "operator.attention_policy.v1",
  "status": "no_attention_required",
  "selected_finding": null
}
```

When findings exist, the policy returns exactly one unchanged finding, including its existing source evidence and safe next inspection. Loss of target visibility ranks before incomplete-plugin configuration and fleet version mismatch; ties are stable rather than input-order dependent.

Target URLs and optional bearer mappings remain operator-owned host configuration. They are not carried by this repository. The policy member has no configuration or secrets.

## Why the pins are commit SHAs

The merged Operator Control 0.5 code and the initial Operator Policy 0.1 code have not been released. This incubation bundle pins exact immutable commits rather than treating issue #2 work as release authorization. Each pin moves to a verified release tag only after a separate release decision.

## Included

- pinned `operator_control` evidence plugin;
- pinned `operator_policy` deterministic policy plugin;
- target readiness, version-skew, and incomplete-plugin findings supplied by Operator Control;
- explicit selection of one finding or `no_attention_required` supplied by Operator Policy;
- empty target configuration and deterministic timeout default;
- standalone manifest/security/documentation tests;
- real scratch protoAgent installation, loading, exact-lock, two-tool, and no-network unconfigured verification.

## Not included

No persona, dashboard, telemetry aggregator, fleet roster/proxy, generic operating runbooks, scheduler, notifications, credentials, target enrollment, discovery, shell/filesystem authority, incident mutation, remediation, restart, update, restore, or other write path is included.

## Verify

```bash
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
ruff format --check .
PROTOAGENT_CHECKOUT=/path/to/protoAgent /path/to/protoAgent/.venv/bin/python scripts/verify_bundle.py .
```

See `PROTO.md` for the canonical architecture and safety contract.
