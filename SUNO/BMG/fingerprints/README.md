# SYSOP empirical fingerprints

This directory is the generated evidence layer for `SUNO/BMG`.

`BMG-*.JSON` files describe target genre parameter maps. `SYSOP_*_CORE.JSON` files are learned from the
actual `SYSTEMS-OPERATOR/BACKUP/metadata` corpus and answer a different question: **what repeatedly
co-occurs in this catalog when that genre is present?**

The builder measures document-frequency support, global support, lift, a ranking score, top
co-occurrences, BPM, explicit Hz anchors, key/Camelot cues, explicit `[RYM: ...]` annotations,
negative terms, and model-version distribution.

The fingerprint layer never claims that a frequent SYSOP token is an official BMG term. Provenance
stays split.

Generate all fingerprints:

```bash
python SUNO/BMG/tools/build_empirical_fingerprints.py --backup ../BACKUP
```

Generate selected fingerprints:

```bash
python SUNO/BMG/tools/build_empirical_fingerprints.py \
  --backup ../BACKUP \
  --map BMG-NEUROFUNK \
  --map BMG-SPEED-GARAGE
```

Compare two generated cores:

```bash
python SUNO/BMG/tools/compare_fingerprints.py \
  SUNO/BMG/fingerprints/SYSOP_NEUROFUNK_CORE.JSON \
  SUNO/BMG/fingerprints/SYSOP_SPEED_GARAGE_CORE.JSON
```

Default core threshold is `support >= 0.20`; default signature threshold is `lift >= 1.50`,
with at least two supporting tracks. Tune these on the builder CLI when a genre has a very small
or very large sample.

The scanner ignores ordinary lyric/prompt prose. Only explicit `[RYM: ...]` blocks are read from
the prompt field; all other evidence comes from style/display/negative metadata.
