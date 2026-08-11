# PROTO.md — Operator Stack

This is the repository's single agent-grounding source.

## Purpose and owner boundary

This standalone bundle is the durable owner for the Operator Stack tracked by RomeoRaven/protoAgent issue #2. It composes capabilities; it does not own protoAgent core or the Operator Control plugin.

The first slice installs one read-only dependency, `RomeoRaven/operator-plugin`, and starts unbound. It exists to prove that a fresh protoAgent workspace can acquire the operator evidence tool without receiving targets, credentials, or write authority.

## Simplest complete first slice

- Source artifact: `protoagent.bundle.yaml`.
- Result: an installable bundle with one enabled member and explicit empty target configuration.
- Runtime proof: a scratch protoAgent install loads exactly one `operator_snapshot` tool; invoking it returns `not_configured` without opening an HTTP client.
- Owner split: this repository owns composition and pins; `operator-plugin` owns evidence behavior; protoAgent owns bundle installation and plugin loading.

## Pin boundary

Current member pin: immutable commit SHA `f99ceb4437dadd968ab66d488e13e930ceb7c7d0`.

Accepted protoAgent bundle guidance prefers release tags. `operator-plugin` 0.5 is merged but unreleased, and work on issue #2 is not release authorization. The SHA is therefore an explicit incubation pin: deterministic and non-updating. Replace it with a release tag only after separate release approval and a passing bundle re-verification.

## Safety contract

- One member only: `operator_control`.
- The bundle starts with `targets: []` and contains no bearer token or secret declaration.
- The plugin tool remains zero-argument; only the operator may configure targets later.
- No builtin shell, filesystem, GitHub-write, scheduler, MCP, delegate, or remediation plugin is enabled.
- No archetype/persona is declared in this slice; the bundle must not imply a mature operator workflow before one is proven.
- No target discovery, enrollment, write operation, restart, update, restore, or notification behavior.
- Raw installation fetches code from the declared public repository; runtime inspection behavior remains GET-only under the plugin's own `PROTO.md` contract.

## Acceptance criteria

1. The bundle contains exactly one immutable `operator_control` member pin and enables only that member.
2. Bundle defaults contain an empty target list and timeout only; no credentials or write surfaces are present.
3. Current protoAgent installs the bundle into an isolated scratch root and records the exact requested/resolved plugin SHA.
4. The real plugin loader loads `operator_control` and contributes exactly one zero-argument `operator_snapshot` tool.
5. Invoking that tool before target enrollment returns the exact `not_configured` contract without constructing an HTTP client.
6. No `AGENTS.md` or `CLAUDE.md` is added; this file remains the sole high-authority grounding surface.

## Verification

```bash
python -m pytest -q
ruff check .
ruff format --check .
python scripts/verify_bundle.py .
```

Run the integration verifier from a current protoAgent checkout or with `PROTOAGENT_CHECKOUT` set to one. It scopes config, plugin installation, and lock state to a temporary directory.

## Files

- `protoagent.bundle.yaml` — bundle identity, immutable member pin, enable list, and empty-target defaults.
- `tests/test_bundle.py` — standalone composition/security contract.
- `scripts/verify_bundle.py` — real scratch installer/loader/tool proof against current protoAgent.
- `README.md` — operator-facing installation, behavior, and limits.

## Deferred capabilities

Persona/SOUL, health-review workflows, priority policy, plugin/upgrade readiness, incident/cost/capacity skills, notifications, and any controlled-write profile require their own evidence-backed slices. Controlled writes additionally depend on issue #3 and are not implied by this bundle.
