from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

from tools.scenarios.export_scenarios import load_yaml, validate_scenario
from tools.scenarios.simulate_souperposition import ROOT, SCENARIO, build_bundle, simulate


class SouperpositionTests(unittest.TestCase):
    def setUp(self):
        self.scenario = load_yaml(SCENARIO)

    def test_declared_cases_execute_and_allow_opposite_results(self):
        record, aggregate = build_bundle()
        self.assertEqual(aggregate["cases_passed"], len(self.scenario["test_cases"]))
        self.assertEqual({run["end_state"] for run in record["runs"]},
                         set(self.scenario["end_state_labels"]))
        self.assertEqual(record["human_trials_performed"], 0)

    def test_style_alone_does_not_determine_reinforcement(self):
        for style in self.scenario["independent_variables"]["warning_style"]:
            for coupling, expected in ((-1, -3), (0, 0), (1, 3)):
                with self.subTest(style=style, coupling=coupling):
                    run = simulate(self.scenario, dict(warning_style=style, coupling=coupling))
                    self.assertEqual(run["measurements"]["persistence_change"], expected)
                    self.assertEqual(run["no_warning_control"], [5, 5, 5, 5])

    def test_marginal_support_requires_disturbance(self):
        for stability, disturbed, tipped in (("stable", True, 0), ("marginal", False, 0),
                                             ("marginal", True, 1), ("tipped", False, 0)):
            with self.subTest(stability=stability, disturbed=disturbed):
                run = simulate(self.scenario, dict(stability=stability, disturbance=disturbed))
                self.assertEqual(run["measurements"]["tip_events"], tipped)

    def test_every_stop_prevents_all_scene_updates(self):
        for stop in self.scenario["stop_conditions"]:
            with self.subTest(stop=stop):
                run = simulate(self.scenario, dict(stability="tipped", coupling=1), [stop])
                self.assertEqual(run["end_state"], "stopped_for_safety")
                self.assertEqual(run["persistence_trace"], [5])
                self.assertEqual(run["events"], [])
                self.assertEqual(run["measurements"],
                                 dict(tip_events=0, warning_repetitions=0, persistence_change=0))

    def test_virtual_hazard_is_not_an_active_stop(self):
        run = simulate(self.scenario, dict(hazard_context="exhaust_or_combustion", coupling=1))
        self.assertEqual(run["end_state"], "persistence_increased")
        self.assertEqual(run["stop_reasons"], [])

    def test_semantic_errors_are_rejected_by_existing_validator(self):
        case = {"id": "BAD", "expect": ["persistence_unchanged"]}
        mutations = [
            ("test_cases", "not_a_list"),
            ("test_cases", [case | {"given": {"coupling": True}}]),
            ("test_cases", [case | {"given": {"unknown": 0}}]),
            ("test_cases", [case | {"expect": ["invented_outcome"]}]),
            ("test_cases", [case | {"expect_measure": ["invented_measure"]}]),
            ("test_cases", [case | {"active_stops": ["invented_stop"]}]),
            ("test_cases", [{"id": "DUP", "expect": ["persistence_unchanged"]}] * 2),
            ("test_cases", [{"id": "EMPTY", "given": {}}]),
            ("measurements", {"score": {"min": 10, "max": -1}}),
            ("measurements", {"score": {"min": 0, "max": float("nan")}}),
        ]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                data = copy.deepcopy(self.scenario)
                data[key] = value
                with self.assertRaises(ValueError):
                    validate_scenario(data, SCENARIO)

    def test_valid_but_wrong_expectation_fails_the_runner(self):
        data = copy.deepcopy(self.scenario)
        data["test_cases"][0]["expect"] = ["persistence_decreased"]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / SCENARIO.name
            source.write_text(yaml.safe_dump(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CAN_001"):
                build_bundle(source)

    def test_cli_outputs_are_deterministic_and_manifest_hashes_match(self):
        with tempfile.TemporaryDirectory() as directory:
            outputs = [Path(directory) / name for name in ("first", "second")]
            for output in outputs:
                subprocess.run([sys.executable, "-m", "tools.scenarios.simulate_souperposition",
                                "--output", str(output)], cwd=ROOT, check=True, capture_output=True)
            names = {"scenario_run.json", "scenario_run.md", "aggregate_metrics.json", "manifest.sha256"}
            self.assertEqual({p.name for p in outputs[0].iterdir()}, names)
            for name in names:
                self.assertEqual((outputs[0] / name).read_bytes(), (outputs[1] / name).read_bytes())
            entries = (outputs[0] / "manifest.sha256").read_text().splitlines()
            self.assertEqual(len(entries), 3)
            for line in entries:
                digest, name = line.split("  ", 1)
                self.assertEqual(digest, hashlib.sha256((outputs[0] / name).read_bytes()).hexdigest())
            record = json.loads((outputs[0] / "scenario_run.json").read_text())
            self.assertEqual(record["evidence_kind"], "synthetic_sensitivity_analysis")
