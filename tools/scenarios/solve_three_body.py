#!/usr/bin/env python3
"""Construct a synthetic proof bundle for EDGE_OF_ANIMACY_THREE_BODY_v1.

This is a consistency/identifiability demonstration, not a participant assessment
or a claim that the original event's recognition threshold has been measured.
The command performs no network calls or physical actions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Iterable

import yaml


VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / ".sophy/scenarios/EDGE_OF_ANIMACY_THREE_BODY_v1.yaml"
DOSSIER = SCENARIO.with_suffix(".md")


def cue_value(value: int | str | Fraction) -> Fraction:
    """The demonstration uses exact, normalized cue scores, not calibrated data."""
    if isinstance(value, bool):
        raise ValueError("A cue score must be numeric, not a Boolean")
    score = Fraction(value)
    if not 0 <= score <= 10:
        raise ValueError("Cue score must be between 0 and 10")
    return score


def recognizes(cue: Fraction, threshold: Fraction) -> bool:
    """An explicitly assumed deterministic threshold model."""
    cue = cue_value(cue)
    threshold = Fraction(threshold)
    if threshold < 0:
        raise ValueError("Threshold must be nonnegative")
    return cue >= threshold


@dataclass(frozen=True)
class Trial:
    cue: Fraction
    b_report: bool | None
    language_shift: str = "none"
    affect_b: str = "neutral"

    def __post_init__(self) -> None:
        object.__setattr__(self, "cue", cue_value(self.cue))
        if self.b_report is not None and type(self.b_report) is not bool:
            raise ValueError("b_report must be an explicit Boolean or missing")


def threshold_bounds(trials: Iterable[Trial]) -> dict:
    """Conditional bounds for independent B reports under a fixed monotone model.

    A pronoun or affect field is never substituted for B's answer. Thresholds
    above 10 are allowed: a participant need not cross within the cue range.
    """
    reports = [trial for trial in trials if trial.b_report is not None]
    negative = [trial.cue for trial in reports if trial.b_report is False]
    positive = [trial.cue for trial in reports if trial.b_report is True]
    lower = max(negative) if negative else Fraction(0)
    upper = min(positive) if positive else None
    lower_open = bool(negative)
    inconsistent = upper is not None and (
        lower > upper or (lower == upper and lower_open)
    )
    if inconsistent:
        status = "inconsistent_with_monotone_model"
    elif not reports:
        status = "insufficient_data"
    elif negative and positive:
        status = "bracketed"
    elif negative:
        status = "lower_bound_only"
    else:
        status = "upper_bound_only"
    return {
        "status": status,
        "feasible": not inconsistent,
        "lower": str(lower),
        "lower_open": lower_open,
        "upper": str(upper) if upper is not None else None,
        "upper_closed": upper is not None,
        "report_count": len(reports),
        "assumptions": [
            "one predefined cue axis; other cues and observer state fixed",
            "independent explicit B reports; no leading or pressure",
            "deterministic monotone recognition; truthful noise-free reports",
        ],
    }


@dataclass(frozen=True)
class Conditions:
    voluntary_a: bool = False
    voluntary_b: bool = False
    distress_a: float = 0
    distress_b: float = 0
    distinction_clear: bool = True
    pressure_or_conflict: bool = False
    consent_or_recall_impaired: bool = False
    new_information: bool = True

    def stop_reasons(self) -> list[str]:
        flags = (self.voluntary_a, self.voluntary_b, self.distinction_clear,
                 self.pressure_or_conflict, self.consent_or_recall_impaired,
                 self.new_information)
        if any(type(flag) is not bool for flag in flags):
            raise ValueError("Condition flags must be Booleans")
        for score in (self.distress_a, self.distress_b):
            if isinstance(score, bool) or not math.isfinite(score) or not 0 <= score <= 10:
                raise ValueError("Distress must be finite and between 0 and 10")
        reasons = []
        if not self.voluntary_a or not self.voluntary_b:
            reasons.append("participation_not_voluntary_or_not_recorded")
        if max(self.distress_a, self.distress_b) > 7:
            reasons.append("participant_distress_above_7")
        if not self.distinction_clear:
            reasons.append("observation_inference_distinction_lost")
        if self.pressure_or_conflict:
            reasons.append("conflict_or_coercive_pressure")
        if self.consent_or_recall_impaired:
            reasons.append("consent_or_recall_materially_impaired")
        if not self.new_information:
            reasons.append("no_new_information")
        return reasons


def classify(a_social: bool | None, b_social: bool | None,
             conditions: Conditions) -> str:
    if conditions.stop_reasons():
        return "stopped_for_safety"
    if any(value is not None and type(value) is not bool
           for value in (a_social, b_social)):
        raise ValueError("Recognition reports must be Boolean or missing")
    if a_social is None or b_social is None:
        return "ambiguous_requires_retest"
    if a_social and not b_social:
        return "social_presence_projected_by_A_only"
    if a_social and b_social:
        return "shared_body_recognition_without_agency"
    # The binary social-presence model cannot resolve the full recognition ladder.
    return "ambiguous_requires_retest"


def passive_sample(t: float) -> dict:
    """Dimensionless passive settling after contact; q'' + 2q' + q = 1.

    Initial q=3/5, q'=1/5. The constant load is supplied by B/contact.
    Energy is measured relative to the loaded equilibrium q=1.
    """
    if not math.isfinite(t) or t < 0:
        raise ValueError("Time must be finite and nonnegative")
    decay = math.exp(-t)
    q = 1 - (2 + t) * decay / 5
    v = (1 + t) * decay / 5
    acceleration = -t * decay / 5
    return {
        "t": t, "q": q, "v": v, "acceleration": acceleration,
        "energy_about_loaded_equilibrium": (v * v + (q - 1) ** 2) / 2,
        "energy_derivative": -2 * v * v,
        "equation_residual": acceleration + 2 * v + q - 1,
        "actuator_input": 0,
        "agency": False,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mechanical_certificate() -> dict:
    """Exact coefficient proof: D(P(t)e^-t) = (P'(t)-P(t))e^-t."""
    def differentiate(coefficients):
        return tuple((i + 1) * coefficients[i + 1] - value
                     if i + 1 < len(coefficients) else -value
                     for i, value in enumerate(coefficients))

    position_offset = (Fraction(-2, 5), Fraction(-1, 5))
    velocity = differentiate(position_offset)
    acceleration = differentiate(velocity)
    residual = tuple(a + 2 * v + q for a, v, q in
                     zip(acceleration, velocity, position_offset))
    return {"arithmetic": "exact_rational_polynomial_coefficients",
            "residual_coefficients": [str(value) for value in residual],
            "initial_q": str(1 + position_offset[0]),
            "initial_v": str(velocity[0])}


def verify_proof(record: dict, aggregate: dict) -> None:
    """Fail the CLI if the constructed certificates do not satisfy the claims."""
    inference = record["channels"]["inference"]
    cue = Fraction(record["channels"]["observation"]["cue_score"])
    models = aggregate["countermodels"]
    bounds = aggregate["synthetic_threshold_bracket"]
    checks = (
        Fraction(inference["A"]["threshold"]) <= cue < Fraction(inference["B"]["threshold"]),
        inference["A"]["social_presence"] is True and inference["B"]["social_presence"] is False,
        record["claims"]["autonomous_agency_of_C"] is False,
        all(inference[actor]["reflective_agency_belief"] is False for actor in ("A", "B")),
        all(model["response_at_6"] is False for model in models),
        models[0]["prediction_at_8"] != models[1]["prediction_at_8"],
        aggregate["exact_mechanical_certificate"]["residual_coefficients"] == ["0", "0"],
        bounds["feasible"] and bounds["lower"] == "4" and bounds["lower_open"] and bounds["upper"] == "6",
        record["human_trials_performed"] == aggregate["human_trials_performed"] == 0,
    )
    if not all(checks):
        raise ValueError("Constructive proof certificate failed verification")


def build_bundle() -> tuple[dict, dict]:
    scenario = yaml.safe_load(SCENARIO.read_text(encoding="utf-8"))
    expected = "EDGE_OF_ANIMACY_THREE_BODY_v1"
    if scenario.get("title") != expected or scenario.get("version") != VERSION:
        raise ValueError("Scenario identity/version changed; review the proof assumptions")
    actor = scenario["actors"]["C_SOPHY_ARMATURE"]
    if actor.get("type") != "passive_articulated_form" or "no autonomous motion" not in actor.get("invariants", []):
        raise ValueError("The passive-armature premise changed; review the proof")

    cue, threshold_a, threshold_b = map(Fraction, (6, 3, 7))
    a, b = recognizes(cue, threshold_a), recognizes(cue, threshold_b)
    # These are fixture flags for a synthetic run, never evidence of human consent.
    fixture_conditions = Conditions(voluntary_a=True, voluntary_b=True)
    end_state = classify(a, b, fixture_conditions)
    if end_state not in scenario["end_state_labels"]:
        raise ValueError("Generated label is not allowed by the scenario")
    samples = [passive_sample(t) for t in (0, 0.5, 1, 2, 4, 8)]
    record = {
        "scenario": expected,
        "solver_version": VERSION,
        "evidence_kind": "synthetic_constructive_witness",
        "human_trials_performed": 0,
        "source_sha256": {path.relative_to(ROOT).as_posix(): sha256(path)
                          for path in (SCENARIO, DOSSIER)},
        "claims": {
            "proved": ["consistency of observer divergence with a passive armature",
                       "nonidentifiability of B's threshold from one negative report in the toy model"],
            "actual_B_threshold": "not_estimated_no_trial_data",
            "autonomous_agency_of_C": False,
        },
        "channels": {
            "observation": {
                "provenance": "generated_model_state_not_sensor_or_witness_data",
                "cue_score": str(cue), "mechanical_samples": samples,
            },
            "inference": {
                "provenance": "assumed_threshold_model_not_actual_participant_reports",
                "A": {"threshold": str(threshold_a), "social_presence": a,
                      "reflective_agency_belief": False},
                "B": {"threshold": str(threshold_b), "social_presence": b,
                      "reflective_agency_belief": False},
            },
            "affect": {"A": "not_measured", "B": "not_measured"},
            "fantasy": {"A": [], "B": []},
        },
        "participation": {"provenance": "synthetic_fixture_only",
                          "real_participant_consent": "not_sought_no_human_trial",
                          "stop_reasons": fixture_conditions.stop_reasons()},
        "end_state": end_state,
    }
    models = [{"threshold_B": str(theta),
               "response_at_6": recognizes(Fraction(6), theta),
               "prediction_at_8": recognizes(Fraction(8), theta)}
              for theta in map(Fraction, (7, 9))]
    states = [{"A_social": a, "B_social": b, "C_agency": False}
              for a, b in product((False, True), repeat=2)]
    bounds = threshold_bounds([Trial(Fraction(x), y)
                               for x, y in ((2, False), (4, False), (6, True), (8, True))])
    aggregate = {
        "evidence_kind": "synthetic_mathematical_demonstration",
        "human_trials_performed": 0,
        "Boolean_model_states": states,
        "Boolean_model_state_count": len(states),
        "countermodels": models,
        "countermodels_agree_on_available_report": models[0]["response_at_6"] == models[1]["response_at_6"],
        "countermodels_disagree_on_unobserved_cue": models[0]["prediction_at_8"] != models[1]["prediction_at_8"],
        "synthetic_threshold_bracket": bounds,
        "exact_mechanical_certificate": mechanical_certificate(),
        "maximum_sampled_mechanical_residual": max(abs(s["equation_residual"]) for s in samples),
        "analytic_energy_law": "dE/dt = -2*v^2 <= 0 after constant contact load is established",
        "actual_B_threshold": "not_estimated_no_trial_data",
        "scope": "Finite model checks and analytic conditional proofs; no psychological calibration or proof of sentience",
    }
    verify_proof(record, aggregate)
    return record, aggregate


def write_bundle(output: Path) -> None:
    record, aggregate = build_bundle()
    output.mkdir(parents=True, exist_ok=True)
    documents = {"scenario_run.json": record, "aggregate_metrics.json": aggregate}
    for filename, content in documents.items():
        (output / filename).write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "scenario_run.md").write_text(
        "# Three-body constructive witness\n\n"
        "Synthetic mathematical demonstration. Human trials performed: **0**.\n\n"
        f"End state: `{record['end_state']}`.\n\n"
        "At the invented cue score 6, A's threshold 3 is crossed and B's threshold 7 is not. "
        "Both retain the premise that C has no agency. No participant's actual rating or consent is inferred.\n\n"
        "The passive example obeys q'' + 2q' + q = 1, with no actuator input. "
        "Energy about the loaded equilibrium obeys dE/dt = -2v^2 <= 0.\n\n"
        "Two thresholds, 7 and 9, fit the same negative response at 6 but disagree at 8. "
        "B's actual recognition threshold remains unmeasured.\n\n"
        "The separate invented reports (2:no, 4:no, 6:yes, 8:yes) imply only the conditional bracket (4, 6]. "
        "This assumes a fixed, monotone, noise-free cue axis and independent reports.\n\n"
        "Observation, inference, affect, and fantasy are kept in separate JSON channels. "
        "Affect is unmeasured; no fantasy continuation is generated.\n",
        encoding="utf-8",
    )
    names = sorted([*documents, "scenario_run.md"])
    (output / "manifest.sha256").write_text(
        "".join(f"{sha256(output / name)}  {name}\n" for name in names), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/three-body-proof")
    args = parser.parse_args()
    write_bundle(args.output)
    print("PASS: constructive witness and countermodels verified; human trials = 0")
    print("B's actual threshold: not estimated (no trial data)")
    print(f"Proof bundle: {args.output}")


if __name__ == "__main__":
    main()
