# SUNO/BMG

Genre-specific parameter maps for Suno prompting, kept as a provenance-aware library rather than one giant keyword bucket.

Each `BMG-*.JSON` keeps four layers separate:

- **BMG** — normalized vocabulary verified from public BMG Production Music / Sync+ surfaces.
- **RYM** — genre and descriptor language used as a separate reference vocabulary.
- **SYSOP** — observed vocabulary from `SYSTEMS-OPERATOR/BACKUP` and direct project targets.
- **SUNO** — the eventual compiled prompt layer assembled from the map.

BMG's public site currently verifies **Electronic** as the parent genre. Child BMG terms stay
`pending_verification` until a live catalog/filter pass confirms them. The map filenames are target
namespaces, not claims that BMG exposes those exact labels as official child categories.

## Map families

`registry.json` groups the active maps into breaks, UK bass, 4x4 club, and industrial/experimental
families. The current library includes Breaks, Breakcore, Jungle, Drum & Bass, UK Garage,
Speed Garage, Bassline, Dubstep, House, Techno, Trance, EBM, Industrial Electronic, and
Experimental Electronic.

## Cross-reference BACKUP

Clone `SYSTEMS-OPERATOR/BACKUP` next to BOX and run:

```bash
python SUNO/BMG/tools/build_rym_crossref.py --backup ../BACKUP --write
```

The scanner uses boundary-aware genre matching so `house` does not accidentally match
`warehouse`, then aggregates:

- matching song count
- common metadata/style phrases
- explicit `[RYM: ...]` annotations
- BOX/RYM descriptor hits
- negative prompt terms

It does not copy lyrics, audio, artwork, cookies, auth data, or full raw BMG metadata.

## Compile a prompt frame

```bash
python SUNO/BMG/tools/compile_genre_map.py SUNO/BMG/maps/BMG-UKG.JSON
python SUNO/BMG/tools/compile_genre_map.py SUNO/BMG/maps/BMG-SPEED-GARAGE.JSON --format json
```

The compiler emits a compact RYM-style line by default or a structured JSON prompt frame.
JSON mode preserves source labels so later testing can measure which vocabulary layer is doing work.
