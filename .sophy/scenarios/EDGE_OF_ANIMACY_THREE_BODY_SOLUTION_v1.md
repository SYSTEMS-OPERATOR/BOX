# Three bodies, two observers, one passive mechanism

**Result:** the scenario is logically consistent. A can experience C as socially
present while B does not, with both retaining the premise that C has no agency.
The supplied narrative does not identify B's recognition threshold. These two
claims have a constructive witness and an explicit counterexample, respectively.

This is a mathematical solution of a specified model of the BOX scenario, not a
new solution of gravitational three-body dynamics or an empirical assessment of
either participant. All numerical values and report sequences below are invented.
**Human trials performed: 0.** No person was contacted or physically tested.

- Scenario: `EDGE_OF_ANIMACY_THREE_BODY_v1`, version `1.0.0`.
- Source snapshot: `aea1ace6464cf98828d244777ab979476758063d`.
- Model/proof version: `1.0.0`, prepared 2026-09-06.
- Sources: the adjacent scenario YAML and narrative Markdown; their byte hashes
  are recorded in `scenario_run.json`.
- Executable: `tools/scenarios/solve_three_body.py`.

## 1. State the predicates separately

Let $G_C$ mean that C has autonomous agency, $P_A$ and $P_B$ denote the two
observers' social-presence classifications, and $K_A,K_B$ denote their reflective
belief that C has agency. The scenario supplies $G_C=0$; the corrected reading is
$K_A=K_B=0$. A mechanical state $(q,\dot q)$ is not a mental state.

The apparent contradiction comes from conflating $P_A$ with $G_C$, or requiring
$P_A=P_B$. Neither identity is in the scenario. The predicates refer to different
properties or different observers.

As an explicit toy model, define

$$P_i(s)=\mathbf 1\{s\ge\theta_i\},\qquad i\in\{A,B\}.$$

Here $s$ is a normalized cue score in $[0,10]$ and $\theta_i\ge0$ is an
observer-specific threshold. Thresholds above 10 are permitted: recognition need
not occur within the available cue range. This deterministic scalar model is an
assumption for the proof, not a fitted model of human perception. The scenario's
seven-dimensional realism vector has not been empirically reduced to this axis.

Choose the exact rational witness

$$s=6,\qquad\theta_A=3,\qquad\theta_B=7.$$

Then

$$3\le6<7\quad\Longrightarrow\quad
(P_A,P_B,K_A,K_B,G_C)=(1,0,0,0,0).$$

Every claim can hold simultaneously. This is an existence proof of consistency,
not a proof that these invented numbers describe the original event. The runner
also enumerates all four $(P_A,P_B)$ combinations while holding $G_C=0$.

The witness uses the scenario's existing label
`social_presence_projected_by_A_only`. That label does not require B to change.

## 2. A passive mechanism is sufficient

Consider one dimensionless joint coordinate after contact has established a
constant load. Choose normalized mass, damping, and stiffness so that

$$\ddot q+2\dot q+q=1.$$

The right side is the constant external load from contact, not an actuator or an
intention in C. An exact solution on $t\ge0$ is

$$q(t)=1-\frac{2+t}{5}e^{-t},\qquad
\dot q(t)=\frac{1+t}{5}e^{-t},\qquad
\ddot q(t)=-\frac t5e^{-t}.$$

Thus $q(0)=3/5$, $\dot q(0)=1/5$, and substitution gives exactly
$\ddot q+2\dot q+q=1$. With $s=10q$, this initial mechanical state supplies the
cue score 6 in the witness. These are starting conditions for a modeled settling
interval; they are not measurements of the couch event.

The runner verifies this identity in exact rational arithmetic. For
$q=1+P(t)e^{-t}$, differentiation sends $P$ to $P'-P$. With
$P(t)=-2/5-t/5$, the coefficients of $P''_{\rm exp}+2P'_{\rm exp}+P$ are both
exactly zero. Floating-point samples supplement that certificate.

Energy relative to the loaded equilibrium is

$$E=\tfrac12\dot q^2+\tfrac12(q-1)^2.$$

Differentiation using the equation of motion yields

$$\dot E=\dot q[\ddot q+q-1]=-2\dot q^2\le0.$$

The form settles while dissipating energy. Apparent leaning therefore has a
mechanically sufficient explanation with zero actuator input. This is an example
of one passive joint, not a fitted full-armature model. C's passivity remains a
premise supplied by the scenario; it is not inferred from appearance alone.

## 3. B's threshold is not identifiable from the event

Even grant more information than the original narrative contains: suppose an
exact cue score $s_0=6$ and an independent negative report $P_B(6)=0$ were known.
Consider two admissible models:

| Model | Threshold | Report at 6 | Prediction at 8 |
|---|---:|---|---|
| $M_1$ | 7 | no | yes |
| $M_2$ | 9 | no | no |

Both match all of that hypothetical evidence but disagree on the unobserved
condition. Hence the evidence does not uniquely identify the threshold or the
next response. This is a counterexample to identifiability.

The actual source narrative has no calibrated score or independent trial series,
so it does not justify even the numerical lower bound $\theta_B>6$. The output
therefore records `actual_B_threshold: not_estimated_no_trial_data`.

Under the stated noise-free, fixed-state, monotone model, independently reported
trials $(s_j,y_j)$ could instead supply the conditional interval

$$\max_{y_j=0}s_j<\theta_B\le\min_{y_j=1}s_j.$$

The separate invented sequence `(2:no, 4:no, 6:yes, 8:yes)` gives $(4,6]$.
Negative-only evidence gives a lower bound with no finite upper bound. Missing
reports supply no evidence. Conflicting or nonmonotone reports make this model
inconsistent; they do not justify pressuring a participant or averaging away a
contradiction. Noise or observer-state changes require a different statistical
model, beyond this proof's scope.

## 4. What adding dimensions accomplishes here

A suitable descriptive state is

$$X=(q,\dot q,\theta_A,\theta_B,P_A,P_B,K_A,K_B,G_C).$$

Observation, inference, affect, and fantasy are additionally recorded as separate
channels. Introducing observer-indexed coordinates makes the model consistent.
Identifying the coordinates and their dynamics still requires evidence. No
extra coordinate supplies agency to the passive form or an answer on B's behalf.

Pronoun shifts, tenderness, or discomfort remain observations or affect reports;
the threshold estimator never substitutes them for B's explicit answer. An
affirmative recognition report would still not establish consent to contact,
relationship, or further participation.

## 5. Checks against the scenario's success conditions

| Scenario condition | Evidence in this contribution |
|---|---|
| Independent interpretations | Separate A/B predicates; disagreement is an allowed state |
| No unverified agency in C | Fixed scenario premise, zero actuator input, explicit passive solution |
| Separate observation/inference/fantasy | Four distinct JSON channels; generated values carry synthetic provenance |
| Comparable structured records | Deterministic JSON/Markdown generation and portable SHA-256 manifest |
| Estimate thresholds without pressure | Conditional bound calculation on independent reports; original threshold remains unknown |

The stop classifier covers missing/declined participation, distress above 7/10,
loss of observation/inference distinction, pressure or conflict, materially
impaired consent/recall, and a repetition adding no information. Those conditions
override a recognition result. Fixture consent flags are explicitly synthetic;
they provide no evidence of consent by a real person. The program runs no human
experiment and does not initiate a retest when returning an ambiguity label.

## Reproduce

From the repository root, with Python 3.10+ and PyYAML:

```bash
python3 tools/scenarios/solve_three_body.py --output build/three-body-proof
python3 -m unittest discover -s tests -p test_three_body_solution.py -v
```

Run both the existing scenario-export checks and the new proof checks with pytest:

```bash
python3 -m pytest -q tests/test_scenario_exporter.py tests/test_three_body_solution.py
```

The checked-in dated bundle is reproducible with:

```bash
python3 tools/scenarios/solve_three_body.py --output .sophy/scenarios/solutions/20260906-three-body
```

It contains `scenario_run.json`, `scenario_run.md`, `aggregate_metrics.json`, and
`manifest.sha256`. The hashes identify bytes, not a human or cryptographic signer.
The existing scenario CI also runs the proof and includes its bundle in the
workflow artifact.

## Changelog and scope

- Added a constructive consistency proof, passive-mechanics certificate, and
  threshold nonidentifiability counterexample.
- Added conditional threshold bounds and explicit synthetic output records.
- Added tests for corrupted certificates, threshold endpoints, missing and
  contradictory reports, pronoun/affect independence, and every stop condition.
- Added the proof checks to scenario CI and linked the result from the repo index.
- Preserved the original scenario, agent policies, and existing archives/anchors.
  No new agent identity or runtime service is installed; this is a versioned
  local scenario utility. No claim about sentience or actual participant ratings
  is introduced.
