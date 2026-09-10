# BMG repository validation — 2026-09-10

Scope: all 41 pre-existing files under `SUNO/BMG/`, plus `RYM/styles.json` as a referenced seed source, read at BOX commit `ded72e43d1f1bfc9b1311d1581f34d0b035446bc`. This is a BMG-folder audit, not a validation of the entire BOX repository. Historical external-source claims and private BACKUP outputs were not independently re-fetched or regenerated.

## Findings and repairs

| Finding | Resolution |
|---|---|
| `BMG-TEMPLATE.JSON` had dummy ID `BMG-GENRE` and zero-valued tempo defaults | Removed the unregistered template; retained all 22 real maps |
| Glitch and Rave used a taxonomy namespace and status rejected by the declared schema | Added a constrained catalog-related namespace; replaced unsupported pending statuses with evidence-backed statuses |
| Validator only checked selected keys, so schema violations passed | Full Draft 2020-12 validation, required evidence fields, cross-file integrity and regression tests |
| All map BMG arrays were empty | Populated 14 maps from selected track metadata; two maps carry exact suggestion-only evidence; six explicitly record no sampled track evidence |
| BACKUP statuses/counts lagged an existing completed aggregate scan | Linked the existing 10 September public scan summary and copied its factual track/profile counts; did not perform or imply a new scan |
| RYM seed path included an extra BOX prefix | Corrected repository-relative references to `RYM/styles.json`; retained separate seed lineage |
| README described all live values as unavailable and Glitch/Rave tags as unverified | Updated to the bounded direct harvest while preserving historical evidence layers |

Current map coverage:

- **Track-associated evidence (14):** Bassline, Big Beat, Breakcore, Breaks, DnB, Drone, Dubstep, Experimental, Glitch, House, Industrial, Rave, Techno, UKG.
- **Suggestion-only (2):** Acid, Jungle.
- **No detailed track selected (6):** EBM, Grime, Neurofunk, Riddim, Speed Garage, Trance.

Track association is not always Genre-field confirmation: Breakcore and Bassline occur in Instrumentation; Big Beat and Experimental occur in Keywords; Drone is descriptive/instrument/version language; Industrial has curated-playlist association. Each map states the limitation and retains original source-field evidence.

## Validation performed

The validation command checks **33 BMG JSON files, 22 maps, 17 sampled tracks and 1,329 exact term records**. It checks parsing, duplicate keys, exact map schemas, registry membership, local evidence references, term provenance, sample occurrence counts, relationship endpoints, and untested candidate status. Eight regression tests cover unknown schema namespaces, unsupported statuses, missing provenance, incorrect types, duplicate keys, zero-valued template tempo, a valid map and a legitimate empty evidence gap.

```bash
python -m pip install -r SUNO/BMG/tools/requirements.txt
python SUNO/BMG/tools/validate_maps.py
python -m unittest discover -s SUNO/BMG/tools -p 'test_*.py'
```

The final run passed with zero validation errors and all eight regression tests passing. Existing Python tools were syntax-checked, and all 22 map JSON compilation paths were exercised. No private fingerprint input or generation service was required for those checks. The compiler's existing default prompt construction remains seed/RYM/SYSOP-based; the harvested vocabulary is a separately ranked experimental input, not silently injected into every prompt.

## Placeholder policy and limits

No dummy map, TODO/TBD value, example URL, or unfinished substitution remains in the committed BMG deliverables. JSON nulls and empty lists remain where the source did not expose a field or the sample lacks evidence; replacing these with invented tags would corrupt the research. The Drone seed's minimum tempo of zero and empty preferred list intentionally permit absent pulse; this is documented and is not a measured catalog BPM.

Existing map aliases, genre parents, rhythmic prescriptions and prompt weights are analyst seed assumptions. They were not falsely promoted to observed BMG taxonomy or measured Suno behavior. In particular, existing 160–180 BPM DnB preferences do not overwrite literal catalog observations at 85 and 88 BPM.

The dependency `jsonschema==4.26.0` is explicit; validation fails with installation guidance if unavailable. The checks establish internal consistency and provenance linkage, not permanence of dynamic source pages, correctness of every legacy external claim, or prompt efficacy. No repository-wide agent harness was run because this change is confined to music research data and its validation tools.

No audio, lyrics, artwork, credentials, private BACKUP records, or persisted agent anchors were added or modified. The research is saved on a review branch with a pull request, following the repository's branch-per-change guidance.
