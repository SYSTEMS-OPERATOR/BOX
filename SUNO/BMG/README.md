# SUNO/BMG

Genre-specific parameter maps for Suno prompting, kept as a provenance-aware library rather than one giant keyword bucket.

Each `BMG-*.JSON` keeps four source layers separate:

- **BMG** — normalized vocabulary verified from public BMG Production Music / Sync+ surfaces.
- **RYM** — genre and descriptor language used as a separate reference vocabulary.
- **SYSOP** — observed vocabulary from `SYSTEMS-OPERATOR/BACKUP` and direct project targets.
- **SUNO** — the compiled prompt layer assembled from the map.

A fifth generated layer, **SYSOP_EMPIRICAL**, lives under `fingerprints/`. It measures what actually
recurs in BACKUP for each map instead of treating every historically used token as equally important.

BMG's public site currently verifies **Electronic** as the parent genre. Child BMG terms stay
`pending_verification` until a live catalog/filter pass confirms them. `evidence/catalog-genre-terms.json`
separately records genre language observed in BMG Production Music-distributed releases; that evidence
is useful, but is deliberately **not** treated as proof of the official BMG filter hierarchy.

## Map library

`registry.json` indexes twenty maps across breaks, UK bass, 4x4 club, and industrial/experimental
families: Breaks, Big Beat, Breakcore, Jungle, Drum & Bass, UK Garage, Speed Garage, Bassline, Grime,
Dubstep, Riddim Dubstep, Neurofunk, House, Techno, Acid, Trance, EBM, Industrial Electronic,
Experimental Electronic, and Drone Electronic.

## Cross-reference BACKUP

Clone `SYSTEMS-OPERATOR/BACKUP` next to BOX and run:

```bash
python SUNO/BMG/tools/build_rym_crossref.py --backup ../BACKUP --write
python SUNO/BMG/tools/build_rym_crossref.py --backup ../BACKUP --map BMG-NEUROFUNK
```

The scanner uses boundary-aware genre matching so `house` does not accidentally match `warehouse`.
It aggregates matching-song count, common metadata/style phrases, explicit `[RYM: ...]` annotations,
BOX/RYM descriptor hits, and negative prompt terms.

## Build empirical fingerprints

```bash
python SUNO/BMG/tools/build_empirical_fingerprints.py --backup ../BACKUP
```

This writes one `SYSOP_<GENRE>_CORE.JSON` per active map plus `fingerprints/index.json`.
Each fingerprint contains corpus support, global support, lift, ranked core/signature terms,
co-occurrence pairs, BPM/Hz/key/Camelot anchors, explicit RYM annotations, negative terms, and
model distribution. Ordinary lyric/prompt prose is ignored.

Useful focused pass:

```bash
python SUNO/BMG/tools/build_empirical_fingerprints.py \
  --backup ../BACKUP \
  --map BMG-NEUROFUNK \
  --map BMG-SPEED-GARAGE
```

Compare fingerprints:

```bash
python SUNO/BMG/tools/compare_fingerprints.py \
  SUNO/BMG/fingerprints/SYSOP_NEUROFUNK_CORE.JSON \
  SUNO/BMG/fingerprints/SYSOP_SPEED_GARAGE_CORE.JSON
```

## Compile one map

```bash
python SUNO/BMG/tools/compile_genre_map.py SUNO/BMG/maps/BMG-UKG.JSON
python SUNO/BMG/tools/compile_genre_map.py SUNO/BMG/maps/BMG-SPEED-GARAGE.JSON --format json
```

## Blend maps

```bash
python SUNO/BMG/tools/blend_maps.py \
  SUNO/BMG/maps/BMG-SPEED-GARAGE.JSON \
  SUNO/BMG/maps/BMG-BASSLINE.JSON \
  --weights 1,0.8

python SUNO/BMG/tools/blend_maps.py \
  SUNO/BMG/maps/BMG-NEUROFUNK.JSON \
  SUNO/BMG/maps/BMG-BREAKCORE.JSON \
  --weights 1,0.55 --format json
```

The blender sums term scores while preserving every contributing map/source in JSON mode and reports
the tempo-range intersection when one exists.

## Validate

```bash
python SUNO/BMG/tools/validate_maps.py
```

This catches malformed JSON, duplicate IDs, filename/ID mismatches, missing parameter groups,
out-of-range preferred BPM values, and invalid prompt-source labels before the library is used.
