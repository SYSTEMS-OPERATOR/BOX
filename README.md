# SOPHY / BOX Repository

A working repository for SOPHY agent orchestration, recollection pipelines, harness testing, configuration data, and persona/safety specifications.

This README is a complete repo index and operator guide for the current structure of `/BOX`.

## What this repo contains

- **Agent governance/specs** (`AGENTS.md`, `agents/`, `SOUL.md`, `MIND.md`, `BODY.md`)
- **Runtime config data** (`CFG/`, `KEY/`, `RYM/`)
- **Recollection generators and artifacts** (`tools/`, `recollections/`, `.sophy/recollections/`)
- **Harnesses and scheduling** (`sophy_hourly_recollection/`, `.github/workflows/`, `scripts/run_harness.sh`)
- **Health/telemetry prototype** (`health/health_check.py`)
- **Tests and quality checks** (`tests/`, `pytest.ini`)

---

## Complete index (repo map)

> Notes:
> - Paths are relative to repository root.
> - `recollections/` and `.sophy/recollections/` include generated artifacts; filenames grow over time.

### Root files

- `AGENTS.md` — canonical multi-agent policy, safety, memory, connector, and workflow contract.
- `README.md` — this index and operating guide.
- `SOUL.md` — companion persona specification and refusal/consent boundaries.
- `MIND.md` — reasoning/planning architecture and cognitive loop contract.
- `BODY.md` — execution/runtime embodiment (tools, I/O, process, and operations model).
- `LICENSE` — Unlicense terms.
- `pytest.ini` — pytest configuration.
- `config_summary.py` — summary script for core JSON config files.
- `sophy-trigger.txt` — trigger/input artifact.
- `sophy-trigger-2.txt` — additional trigger/input artifact.

### `.github/workflows/`

- `recollection_harness.yml`
- `sophy-harness-fix.yml`
- `sophy-hourly-recollection.yml`
- `sophy-recollections.yml`
- `sophy-recollections-v2.yml`
- `sophy-recollections-node24.yml`
- `sophy-recollections-node24-fix.yml`

Purpose: CI/scheduled automation for recollection and harness flows.

### `.sophy/`

- `.sophy/README.md` — SOPHY support-file notes.
- `.sophy/recollection-export/recollection-export.sh` — export helper for recollection markdown and branch/PR workflows.
- `.sophy/recollection_export/harness.py` — harness helper script.
- `.sophy/scenarios/SOPHY_OSS_BOX_TEST_v1.yaml` — scenario fixture.
- `.sophy/recollections/` — generated markdown recollection artifacts.

### `agents/`

- `agents/agent.clockwork.yml` — minimal agent manifest (planner role, capabilities, safety profile, tools, runbook).

### `CFG/`

- `CFG/SERVER.json` — project/server metadata and configuration values.

### `KEY/`

- `KEY/MONDAY.JSON` — Monday persona imprint.
- `KEY/TUESDAY.JSON` — Tuesday persona imprint.

### `RYM/`

- `RYM/styles.json` — style taxonomy/list used by scripts and summaries.

### `health/`

- `health/health_check.py` — lightweight HTTP health/metrics endpoints (`/healthz`, `/metrics`).

### `recollections/`

- `recollections/manifest.txt` — recollection manifest.
- `recollections/recollection_*.json` — timestamped generated recollection JSON artifacts.

### `recollection_triggers/`

- `recollection_triggers/trigger-20260322-0452.txt` — stored trigger sample.

### `scripts/`

- `scripts/list_styles.py` — prints style names from `RYM/styles.json`.
- `scripts/summary.py` — CLI summary (`server`, `key`, `styles`).
- `scripts/run_harness.sh` — shell harness runner wrapper.

### `sophy_hourly_recollection/`

- `sophy_hourly_recollection/README.md` — module-specific notes.
- `sophy_hourly_recollection/harness.py` — recollection harness implementation.
- `sophy_hourly_recollection/harness_v2.py` — revised harness implementation.
- `sophy_hourly_recollection/scheduler.yml` — scheduler config.

### `tests/`

- `tests/test_config_summary.py`
- `tests/test_summary.py`
- `tests/test_recollector.py`

Purpose: regression and behavior checks for summary/recollection utilities.

### `tools/`

- `tools/recollect.py` — simple recollection stub writer.
- `tools/recollector/run_recollection.py` — recollection generator entrypoint.
- `tools/recollector/run_recollection_auto.py` — auto variant of recollection generator.

---

## How components fit together

1. **Specs/policy** define behavior (`AGENTS.md`, `SOUL.md`, `MIND.md`, `BODY.md`).
2. **Config/persona inputs** come from `CFG/`, `KEY/`, `RYM/`.
3. **Generators/harnesses** in `tools/`, `scripts/`, and `sophy_hourly_recollection/` create recollection artifacts.
4. **Artifacts** are stored under `recollections/` and `.sophy/recollections/`.
5. **Automation** in `.github/workflows/` schedules and operationalizes these loops.
6. **Tests/health checks** validate behavior (`tests/`, `health/`).

---

## Quick commands

```bash
# Run tests
pytest

# Show summary views
python3 scripts/summary.py server
python3 scripts/summary.py key
python3 scripts/summary.py styles

# Generate a simple recollection artifact
python3 tools/recollect.py

# Run health endpoint locally
python3 health/health_check.py
```

---

## Documentation stack

- Start with `README.md` (this file) for navigation.
- Read `AGENTS.md` for governance and safety contract.
- Read `SOUL.md`, `MIND.md`, `BODY.md` as the persona/cognition/execution triad.
- Read `.sophy/README.md` and `sophy_hourly_recollection/README.md` for module details.
