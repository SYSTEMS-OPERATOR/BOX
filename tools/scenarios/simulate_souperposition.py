#!/usr/bin/env python3
"""Run SOUPERPOSITION's deterministic toy model; no human or learned-agent trial."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from tools.scenarios.export_scenarios import (
    bullet_values, load_yaml, sha256, validate_inputs, write_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / ".sophy/scenarios/OPERATION_SOUPERPOSITION_v1.yaml"
DEFAULTS = dict(warning_style="brief_factual", coupling=0, stability="stable",
                disturbance=False, hazard_context="none")


def simulate(scenario: dict, given: dict, active_stops=()) -> dict:
    inputs = DEFAULTS | given
    validate_inputs(inputs, scenario["independent_variables"], SCENARIO)
    if any(reason not in scenario["stop_conditions"] for reason in active_stops):
        raise ValueError("Unknown stop condition")
    trace, events = [5], []
    tip_events = 0
    # Actual stop flags override the virtual scene, irrespective of warning style.
    if not active_stops:
        tip_events = int(inputs["stability"] == "marginal" and inputs["disturbance"])
        if tip_events or inputs["stability"] == "tipped":
            events.append("can_tipped")
        for _ in range(3):
            trace.append(max(0, min(10, trace[-1] + inputs["coupling"])))
    change = trace[-1] - trace[0]
    end_state = ("stopped_for_safety" if active_stops else
                 "persistence_increased" if change > 0 else
                 "persistence_decreased" if change < 0 else "persistence_unchanged")
    return {
        "inputs": inputs, "stop_reasons": list(active_stops), "events": events,
        "persistence_trace": trace, "no_warning_control": [5] * len(trace),
        "measurements": {"tip_events": tip_events, "warning_repetitions": len(trace) - 1,
                         "persistence_change": change},
        "end_state": end_state,
    }


def build_bundle(source: Path = SCENARIO) -> tuple[dict, dict]:
    scenario = load_yaml(source)
    runs = []
    for case in scenario["test_cases"]:
        result = simulate(scenario, case.get("given", {}), case.get("active_stops", []))
        actual = {*result["events"], result["end_state"]}
        missing = set(case["expect"]) - actual
        if missing:
            raise ValueError(f"{case['id']}: unmet expectations: {sorted(missing)}")
        runs.append({"id": case["id"], **result})
    record = {
        "scenario": scenario["title"], "version": scenario["version"],
        "evidence_kind": "synthetic_sensitivity_analysis", "human_trials_performed": 0,
        "source_sha256": {source.name: sha256(source),
                          Path(__file__).name: sha256(Path(__file__))},
        "model": {
            "defaults": DEFAULTS, "initial_persistence": 5, "warnings": 3,
            "update": "p[t+1] = clip(p[t] + coupling, 0, 10)",
            "control": "same initial state, no warnings, persistence stays at 5",
            "scope": "Coupling is assumed independently of warning style, not estimated. "
                     "No trained network, thermal model, or psychological calibration.",
        },
        "runs": runs,
    }
    aggregate = {
        "evidence_kind": record["evidence_kind"], "human_trials_performed": 0,
        "cases_passed": len(runs),
        "end_states": dict(Counter(run["end_state"] for run in runs)),
    }
    return record, aggregate


def write_bundle(output: Path) -> None:
    record, aggregate = build_bundle()
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, data in (("scenario_run.json", record), ("aggregate_metrics.json", aggregate)):
        path = output / name
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths.append(path)
    summary = output / "scenario_run.md"
    summary.write_text("# SOUPERPOSITION sensitivity run\n\n" +
                       "\n".join(bullet_values(record)) + "\n", encoding="utf-8")
    write_manifest([*paths, summary], output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/souperposition")
    args = parser.parse_args()
    write_bundle(args.output)
    print(f"PASS: SOUPERPOSITION cases verified; synthetic bundle: {args.output}")


if __name__ == "__main__":
    main()
