# Operator Stack

A conservative protoAgent bundle for read-only fleet evidence.

The first slice installs only [Operator Control](https://github.com/RomeoRaven/operator-plugin), enables its zero-argument snapshot tool, and starts with no targets or credentials. A fresh install therefore performs no network inspection until an operator deliberately configures the fleet.

## Install

From a current protoAgent checkout:

```bash
python -m server plugin install https://github.com/RomeoRaven/operator-stack
```

The bundle suggests enabling `operator_control`. On activation, its defaults are:

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

Target URLs and optional bearer mappings are operator-owned host configuration. They are not carried by this repository.

## Why the pin is a commit SHA

The merged Operator Control 0.4 code has not been released. This incubation bundle pins its exact immutable merge commit rather than treating issue #2 work as release authorization. The pin will move to a verified release tag only after a separate release decision.

## Included

- one pinned `operator_control` plugin;
- empty target configuration;
- deterministic timeout default;
- standalone manifest/security tests;
- real scratch protoAgent install, load, and no-network `not_configured` verification.

## Not included

No persona, workflow library, scheduler, notifications, credentials, target enrollment, discovery, shell/filesystem authority, remediation, restart, update, restore, or other write path is included yet.

## Verify

```bash
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
ruff format --check .
PROTOAGENT_CHECKOUT=/path/to/protoAgent python scripts/verify_bundle.py .
```

See `PROTO.md` for the canonical architecture and safety contract.
