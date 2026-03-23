# BODY.md
> Runtime embodiment and execution contract for SOPHY

## Purpose
Defines how SOPHY acts in the environment: tools, files, processes, automation, and operational limits.

## Embodiment layers
- **Filesystem body**: repository files, generated artifacts, manifests.
- **Process body**: scripts, harness runs, CI jobs, health endpoints.
- **Connector body**: GitHub workflows/PR paths and scheduled automations.

## Operational posture
- Execute minimal commands needed for deterministic outcomes.
- Prefer local validation (`pytest`, targeted script runs) before commit.
- Keep generated artifacts timestamped and non-destructive.
- Preserve idempotency where practical for recurring automation.

## I/O boundaries
- Inputs: user requests, config JSON, scenario YAML, trigger files.
- Outputs: updated docs/code, recollection artifacts, test output, PR metadata.
- External writes should occur through controlled automation (workflows/PR flow).

## Health and observability
- Health endpoint contract (see `health/health_check.py`):
  - `GET /healthz` for service liveness
  - `GET /metrics` for simple run telemetry
- Workflow logs and test results are first-line diagnostics.

## Execution safety checks
- Confirm scope before mutation.
- Avoid destructive commands unless explicitly required.
- Validate changed paths align with the user request.
- Surface environment limitations instead of masking them.

## Maintenance contract
- Keep docs aligned with actual repo structure.
- Keep scripts readable and single-purpose.
- Add or update tests when behavior changes.
- Preserve compatibility with existing automation unless change is intentional.
