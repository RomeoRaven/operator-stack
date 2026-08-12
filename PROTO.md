# PROTO.md — Operator Stack

This is the repository's single agent-grounding source.

## Purpose and owner boundary

This standalone bundle is the durable composition owner for the Operator Stack tracked by RomeoRaven/protoAgent issue #2. It composes capabilities; it does not own protoAgent core, fleet evidence collection, or policy implementation.

The current slice installs two disabled-by-default external plugins:

- `RomeoRaven/operator-plugin` owns bounded GET-only fleet collection, normalized findings, source attribution, stable ordering, and secret filtering.
- `RomeoRaven/operator-policy-plugin` owns validation and deterministic selection of one existing finding or an explicit all-clear result.

protoAgent core owns fleet telemetry aggregation/UI and generic fleet-operating guidance. Do not reproduce those surfaces here.

## Runtime shape

- Source artifact: `protoagent.bundle.yaml`.
- Two immutable commit SHAs, both enabled by the bundle.
- Explicit empty target configuration; no credentials.
- Tools after installation:
  - `operator_snapshot()` — collect configured read-only evidence; unconfigured returns `not_configured` without network access.
  - `operator_select_attention(snapshot)` — choose one finding from that existing snapshot or return `no_attention_required`.
- The policy tool is intentionally explicit-input rather than secretly invoking the collector. Evidence acquisition and policy remain inspectable separate steps.

## Pin boundary

Current pins:

- Operator Control: `f99ceb4437dadd968ab66d488e13e930ceb7c7d0`
- Operator Attention Policy: `f6b1953023b0039d05ae9e52aedc12b39554d894`

Both are incubation pins. Neither issue #2 nor this integration is release authorization. Replace a pin with a release tag only after separate release approval and passing bundle re-verification.

## Safety contract

- Exactly two members: `operator_control` and `operator_policy`.
- The bundle starts with `targets: []` and contains no bearer token or secret declaration.
- Only the operator may configure targets; the model cannot enroll or redirect the fleet.
- Operator Control interaction remains its declared GET-only health/runtime reads.
- Operator Policy declares no network, filesystem, configuration, secrets, scheduler, notification, or write surface.
- No builtin shell, filesystem, GitHub-write, scheduler, MCP, delegate, remediation, or dashboard plugin is enabled.
- No archetype/persona is declared; this slice proves deterministic policy, not a mature autonomous operator.
- No fleet roster/proxy, telemetry rollup/UI, generic operating runbooks, target discovery, enrollment, restart, update, restore, incident mutation, or remediation.

## Acceptance criteria

1. The bundle contains exactly the two immutable external member pins and enables only those members.
2. Bundle defaults contain an empty target list and timeout only; no credentials or write surfaces are present.
3. Current protoAgent installs both members into an isolated scratch root and records each exact requested/resolved SHA.
4. The real plugin loader loads both members and contributes `operator_snapshot` plus `operator_select_attention` with their intended argument contracts.
5. Invoking the collector before target enrollment returns `not_configured` without constructing an HTTP client.
6. Invoking the policy tool with a valid healthy synthetic snapshot returns `no_attention_required`.
7. No `AGENTS.md` or `CLAUDE.md` is added; this file remains the sole high-authority grounding surface.

## Verification

```bash
python -m pytest -q
ruff check .
ruff format --check .
PROTOAGENT_CHECKOUT=/path/to/protoAgent /path/to/protoAgent/.venv/bin/python scripts/verify_bundle.py .
```

For an uncommitted candidate, pass a temporary Git repository containing the exact candidate files. A Git-backed working checkout resolves to its committed branch state, so dirty working-tree changes are intentionally not installation evidence.

The integration verifier scopes config, plugin installation, and lock state to a temporary directory.

## Files

- `protoagent.bundle.yaml` — bundle identity, immutable member pins, enable list, and empty-target defaults.
- `tests/test_bundle.py` — standalone composition/security/documentation contract.
- `scripts/verify_bundle.py` — real scratch installer/loader/two-tool proof against current protoAgent.
- `README.md` — operator-facing installation, behavior, and limits.

## Deferred capabilities

Persona/SOUL, notification composition, and any controlled-write profile require separate evidence-backed slices. Controlled writes additionally depend on issue #3 and are not implied by this bundle.
