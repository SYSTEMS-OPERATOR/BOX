from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from fractions import Fraction
from itertools import product
from pathlib import Path

from tools.scenarios.solve_three_body import (
    Conditions, Trial, build_bundle, classify, passive_sample, recognizes,
    threshold_bounds, verify_proof, write_bundle,
)


class ThreeBodyProofTests(unittest.TestCase):
    def setUp(self):
        self.allowed = Conditions(voluntary_a=True, voluntary_b=True)

    def test_witness_preserves_two_interpretations_and_passive_C(self):
        record, _ = build_bundle()
        inference = record["channels"]["inference"]
        self.assertTrue(inference["A"]["social_presence"])
        self.assertFalse(inference["B"]["social_presence"])
        self.assertFalse(inference["A"]["reflective_agency_belief"])
        self.assertFalse(inference["B"]["reflective_agency_belief"])
        self.assertFalse(record["claims"]["autonomous_agency_of_C"])
        self.assertEqual(record["end_state"], "social_presence_projected_by_A_only")

    def test_finite_model_admits_both_disagreement_directions(self):
        _, aggregate = build_bundle()
        states = aggregate["Boolean_model_states"]
        self.assertEqual({(s["A_social"], s["B_social"]) for s in states}, set(product((False, True), repeat=2)))
        self.assertTrue(all(s["C_agency"] is False for s in states))

    def test_countermodels_agree_on_evidence_but_disagree_on_prediction(self):
        for theta in (Fraction(7), Fraction(9)):
            self.assertFalse(recognizes(Fraction(6), theta))
        self.assertTrue(recognizes(Fraction(8), Fraction(7)))
        self.assertFalse(recognizes(Fraction(8), Fraction(9)))

    def test_exact_certificate_and_corrupted_proof_rejection(self):
        record, aggregate = build_bundle()
        certificate = aggregate["exact_mechanical_certificate"]
        self.assertEqual(certificate["residual_coefficients"], ["0", "0"])
        self.assertEqual((certificate["initial_q"], certificate["initial_v"]), ("3/5", "1/5"))
        certificate["residual_coefficients"][0] = "1/1000000000"
        with self.assertRaises(ValueError):
            verify_proof(record, aggregate)

    def test_exact_bounds_and_endpoint_semantics(self):
        trials = [Trial(Fraction(2), False), Trial(Fraction(4), False),
                  Trial(Fraction(6), True), Trial(Fraction(8), True)]
        bounds = threshold_bounds(trials)
        self.assertEqual((bounds["status"], bounds["lower"], bounds["upper"]), ("bracketed", "4", "6"))
        # Independent finite check of the interval against the original inequalities.
        for n in range(0, 101):
            theta = Fraction(n, 10)
            fits = all((trial.cue >= theta) == trial.b_report for trial in trials)
            self.assertEqual(fits, Fraction(4) < theta <= Fraction(6))

    def test_empty_and_one_sided_evidence_do_not_invent_a_crossing(self):
        self.assertEqual(threshold_bounds([])["status"], "insufficient_data")
        negative = threshold_bounds([Trial(Fraction(10), False)])
        self.assertEqual(negative["status"], "lower_bound_only")
        self.assertIsNone(negative["upper"])
        zero = threshold_bounds([Trial(Fraction(0), True)])
        self.assertTrue(zero["feasible"])
        self.assertFalse(zero["lower_open"])
        self.assertEqual(zero["upper"], "0")

    def test_nonmonotone_and_conflicting_reports_invalidate_the_model(self):
        for observations in (((2, True), (4, False)), ((4, True), (4, False))):
            bounds = threshold_bounds([Trial(Fraction(x), y) for x, y in observations])
            self.assertFalse(bounds["feasible"])
            self.assertEqual(bounds["status"], "inconsistent_with_monotone_model")

    def test_pronouns_and_discomfort_are_not_recognition_answers(self):
        ambiguous = Trial(Fraction(6), None, "it_to_she", "uncomfortable")
        self.assertEqual(threshold_bounds([ambiguous])["status"], "insufficient_data")
        neutral = Trial(Fraction(6), False)
        changed = replace(neutral, language_shift="spontaneous_name_use", affect_b="tender")
        self.assertEqual(threshold_bounds([neutral]), threshold_bounds([changed]))
        self.assertEqual(classify(True, None, self.allowed), "ambiguous_requires_retest")

    def test_every_stop_condition_overrides_a_recognition_result(self):
        changes = [{"voluntary_a": False}, {"voluntary_b": False},
                   {"distress_a": 7.1}, {"distress_b": 8},
                   {"distinction_clear": False}, {"pressure_or_conflict": True},
                   {"consent_or_recall_impaired": True}, {"new_information": False}]
        for change in changes:
            with self.subTest(change=change):
                conditions = replace(self.allowed, **change)
                self.assertEqual(classify(True, True, conditions), "stopped_for_safety")
        self.assertTrue(Conditions().stop_reasons())
        self.assertFalse(replace(self.allowed, distress_a=7).stop_reasons())

    def test_passive_solution_satisfies_equation_and_energy_law(self):
        previous = math.inf
        for n in range(81):
            sample = passive_sample(n / 10)
            self.assertLess(abs(sample["equation_residual"]), 1e-14)
            energy = sample["energy_about_loaded_equilibrium"]
            self.assertLessEqual(energy, previous)
            self.assertLessEqual(sample["energy_derivative"], 0)
            self.assertEqual(sample["actuator_input"], 0)
            self.assertFalse(sample["agency"])
            previous = energy
        # Differentiate the energy independently, rather than trusting its reported derivative.
        for t in (0.5, 1, 2, 4):
            h = 1e-5
            measured = (passive_sample(t+h)["energy_about_loaded_equilibrium"] -
                        passive_sample(t-h)["energy_about_loaded_equilibrium"]) / (2*h)
            self.assertAlmostEqual(measured, passive_sample(t)["energy_derivative"], places=9)

    def test_invalid_inputs_are_rejected(self):
        for cue in (Fraction(-1), Fraction(11), True):
            with self.assertRaises(ValueError):
                Trial(cue, False)
        with self.assertRaises(ValueError):
            Trial(Fraction(3), "yes")
        for score in (float("nan"), float("inf"), -1, 11, True):
            with self.assertRaises(ValueError):
                replace(self.allowed, distress_a=score).stop_reasons()
        with self.assertRaises(ValueError):
            replace(self.allowed, voluntary_b="yes").stop_reasons()

    def test_bundle_is_deterministic_hashed_and_explicitly_synthetic(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            write_bundle(output)
            first = {p.name: p.read_bytes() for p in output.iterdir()}
            write_bundle(output)
            self.assertEqual(first, {p.name: p.read_bytes() for p in output.iterdir()})
            for line in (output / "manifest.sha256").read_text().splitlines():
                digest, name = line.split("  ", 1)
                self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)
            record = json.loads((output / "scenario_run.json").read_text())
            self.assertEqual(record["human_trials_performed"], 0)
            self.assertEqual(record["evidence_kind"], "synthetic_constructive_witness")
            self.assertEqual(set(record["channels"]), {"observation", "inference", "affect", "fantasy"})
            self.assertEqual(record["claims"]["actual_B_threshold"], "not_estimated_no_trial_data")

    def test_cli_generates_the_four_promised_outputs(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run([sys.executable, str(root / "tools/scenarios/solve_three_body.py"),
                            "--output", folder], check=True, capture_output=True, text=True)
            self.assertEqual({p.name for p in Path(folder).iterdir()},
                             {"scenario_run.json", "scenario_run.md", "aggregate_metrics.json", "manifest.sha256"})


if __name__ == "__main__":
    unittest.main()
