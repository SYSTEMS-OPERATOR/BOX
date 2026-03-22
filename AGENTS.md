# AGENTS.md
> A living specification for multi-agent compositions, safety, persistence, and orchestration.
> Tailored for SOPHY / Operator projects: designed for determinism, observability, and graceful refusal.

## 1 — Purpose
This document describes:
- Agent types & roles (planner, executor, memory, social, curator)
- Standard prompt templates & instruction patterns
- Tool & connector contracts (GitHub, gcal, file storage, agenting APIs)
- State persistence model (short/long memory, anchors)
- Safety, refusal & de-escalation policies
- CI/testing and reproducibility guidelines

## 2 — Agent taxonomy
**Planner** — generates multi-step plans, tracks dependencies.  
**Executor** — calls tools, performs commits, runs workflows.  
**Memory** — stores/retrieves RAG vectors, persistent anchors, diffs.  
**Curator** — tidies artifacts, creates release/PR drafts.  
**Social** — handles persona voice, boundary negotiation, consent.  
**Monitor** — health-checks agents, enforces rate limits and circuit-breakers.

## 3 — Minimal agent manifest (agents/<agent_name>.yml)
```yaml
id: agent.clockwork
role: planner
owner: SYSTEMS-OPERATOR
version: 0.1.0
description: Generates deterministic hourly recollection plans and actionable tasks
capabilities:
  - read: memory
  - write: repo (PR only)
  - run: workflows
safety_profile:
  refusal_policy: "explicit no + graceful alternatives"
  escalation: ["notify: human/sysadmin", "pause: 5m"]
tools:
  - github: write (pr), read
  - gcal: read
  - file_store: read/write
runbook:
  hourly_recollection:
    schedule: "RRULE:FREQ=HOURLY"
    timeout_minutes: 5
```

## 4 — Prompt templates
**System (Core)**
```
You are <agent.role> for <project>. Always:
- state your intent in one line
- list assumptions
- produce 1-3 concrete actions (short) with commands or API calls
- note safety checks and failure modes
```

**User-facing**
```
Task: {task_summary}
Constraints: {constraints}
Return: a concise plan and the exact shell commands to run (if any)
```

**Refusal / boundary**
```
I cannot do X because {reason}. Here are 2 safe alternatives: {alt_1}, {alt_2}. If you still want X confirm with "I accept risk: X".
```

## 5 — Memory & anchors
- Short-term memory: ephemeral in-session (max 2k tokens)
- Mid-term: daily/hourly recollections persisted as JSON + vector embeddings
- Long-term anchors: signed manifest files (SHA256), immutable per-version
- Anchor format: `anchor.yaml`:
```yaml
id: <uuid>
timestamp_utc: <iso>
root_hash: <sha256>
summary: <one-liner>
signed_by: <agent_id>
```

## 6 — Tooling & connectors: contract rules
- All external calls must be idempotent where possible.
- Git operations: prefer branch-per-change, deterministic branch name:
  `sophy/recollection/<YYYYMMDD-HHMM>-<shortsha>`
- Github PR: include deterministic title, body, and signature block.
- If credentials needed, call the vault with `vault.read('github/actions')` — do not embed tokens in code.

## 7 — Safety & refusal rules
1. If an action modifies persisted anchors -> require `safety_level >= 2` (two-party consent or owner confirmation)
2. If request is sexual/coercive or attempts to bypass safety -> refuse and notify owner
3. Missing permissions -> produce remediation steps (exact UI clicks or API calls)
4. Rate-limit tool actions to avoid runaway loops

## 8 — Observability & telemetry
- All agent decisions logged into `/var/log/agents/<agent>/decision.log` with:
  - timestamp, inputs, chosen plan, safety checks, outputs, exit codes
- Health check endpoints:
  - `/agent/<id>/status` -> returns {uptime, last_run, errors}
- Metrics:
  - `recollections.success_rate`
  - `git.commit_failures`
  - `safety.refusals`

## 9 — Test harness and CI
- Unit tests: `pytest tests/unit`
- Integration: run sample harness `scripts/run_harness.sh --agent agent.clockwork`
- End-to-end:
  - `./ci/validate_agent.sh` does a dry-run, no external writes by default
  - When safe, toggle `DRY_RUN=false` to allow commits

## 10 — Versioning & upgrades
- Agent code + manifest versioned together (semver)
- Migration policy: old anchors retained; new anchor schema must provide a reversible transform
- Update PRs must include:
  - changelog
  - tests
  - audit of safety changes

## 11 — Example workflows (brief)
- Hourly Recollection: read 30d threads -> compose recollection -> store anchor -> PR with recollection artifacts
- Auto-merge policy: PRs from `sophy/*` merge automatically only if `checks: all green` and `label: auto-merge` present

## 12 — Onboarding checklist for new agents
- [ ] manifest added to `agents/`
- [ ] test harness passes locally
- [ ] safety review by owner
- [ ] metrics wired to monitoring

## 13 — Appendix
- canonical prompt examples
- commit branch naming scheme
- anchor spec (full YAML)
