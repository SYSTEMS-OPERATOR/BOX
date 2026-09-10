# SUNO/BMG

Genre-specific parameter maps for Suno prompting, kept as a provenance-aware library rather than one giant keyword bucket.

## Evidence layers

Never flatten these sources together:

- **BMG** — values verified directly on current BMG-owned search/filter/metadata surfaces.
- **BMG_CATALOG_RELATED** — vocabulary from BMG Production Music-distributed release/track titles and historical SYNC+ descriptive copy. Useful candidate language, not automatically an official tag.
- **BMG_EDITORIAL** — BMG-owned `Music For` / background-music facets such as Drama, Documentary & History, News & Journalism, Nature & Landscapes, Inspired By, and era pages.
- **BMG_DISTRIBUTOR_EXTERNAL** — structured-looking BMG Production Music metadata exposed by third-party distributors; corroborative only.
- **RYM** — independent genre and descriptor language.
- **SYSOP** — direct project vocabulary and observed BACKUP terms.
- **SYSOP_EMPIRICAL** — corpus-derived fingerprints measuring what actually recurs in BACKUP.
- **SUNO** — compiled prompt output.

## Direct public-UI harvest — 10 September 2026

- [Analysis-ready taxonomy](bmg_sync_electronic_taxonomy.json): 1,329 exact displayed strings, 17 detailed tracks, source fields, counts, relationships and untested Suno candidates.
- [Research summary](bmg_sync_electronic_taxonomy_summary.md): findings, uncertainties and controlled experiments.
- [Compact UI evidence](evidence/public-ui-harvest-2026-09-10.json): public navigation and metadata observations; no media or catalog prose.
- [Validation report](validation_report.md): existing-file audit, repairs, test results and scope limits.

The current harvest is from BMG Production Music. Sync+ required login with no existing authenticated catalog access. Track panels expose Genre, Keywords, Instrumentation, optional Key, BPM and optional Tempo. Analytical mood/production/use-case buckets do not imply separate source fields.

Fourteen maps have bounded track evidence, two have suggestion-only evidence and six are explicitly unsampled. `active` is a project registry designation, not BMG verification. Existing map `genre` relationships, aliases, parameter ranges and prompt weights remain seed assumptions; only `taxonomy.bmg` carries the new direct evidence. Every populated BMG term links to its original source field and URL. Nulls and empty arrays with documented evidence gaps are intentional.

## Advertised BMG search model

The current public BMG MusicSpace surface explicitly advertises automatic keyword suggestions and A.I.-enhanced track tagging across five search axes:

`genre | mood | instrument | key | tempo`

It also exposes similarity search. `evidence/official-tag-axes.json` records those verified axes. The direct UI harvest now supplies observed values, including 852 distinct nonempty suggestions for a UK Garage result set. This is not a complete enumerable vocabulary or proof that every suggestion is a controlled tag. Source fields remain distinct from advertised search axes.

## Catalog-related vocabulary

`evidence/related-catalog-vocabulary.json` records terms found in BMG Production Music-distributed release/track titles. Examples now include:

- DnB: `anthemic`, `essential`, `liquid`
- UKG: `2-step`, `revival`, `reloaded`
- Dubstep: `melodic`, `post`, `devastating`, `metal`, `orchestral`, `hard hitting`, `electro`
- Jungle: `atmos`, `electric`, `mania`
- House: `deep`, `French`, `melodic`, `positive`, `vocal dance`
- Techno: `abstract`, `Berlin`, `afterparty`
- Acid: `pressure`, `groove`, `trax`, `test`
- Drone: `dark`, `tension`, `investigation`

Two catalog families retain candidate-map placement. The direct harvest now observes `Glitch` and `Rave` in Genre fields; the longer release-title phrases below remain catalog-related evidence:

`BMG-GLITCH.JSON` — Glitched Electronica / Hyper Glitch / Glitch Hop / Lofi Glitch Hop

`BMG-RAVE.JSON` — Future Rave and related catalog language

Historical BMG SYNC+ promotional copy is stored separately and includes phrases such as `full on electro`, `French house`, `glitch house`, `pounding EDM`, `electronic hybrid`, `filmic elements`, `retro synths`, and `huge beats`.

## Background-music / editorial facets

`evidence/official-editorial-facets.json` keeps project/use-case facets separate from genre tags. Confirmed BMG-owned examples include Drama, Documentary & History, News & Journalism, Nature & Landscapes, Inspired By, and 1950s/era material. These are useful as a separate BGM/use-case prompt layer rather than genre taxonomy.

## External distributor metadata

`evidence/distributor-tag-samples.json` captures BMG Production Music tracks surfaced through an external production-music distributor. Its filter axes include Genre, Instrument, Vocals, Mood, BPM Range and Musical Key. Sample BMG-associated vocabulary includes `Electro Pop`, `Breakbeat`, `Synth Pop`, `energetic`, `frantic`, `playful`, `groovy`, `raw`, `cinematic`, `ethereal`, `driving`, `synthesizer`, `synth drums`, `drones`, `female vocal`, and `instrumental`.

This layer is evidence for reconstruction/testing, not a claim that every value is a current canonical BMG tag.

## Map library

`registry.json` indexes twenty active maps plus candidate Glitch and Rave maps across breaks, UK bass, 4x4 club, and industrial/experimental families.

## Cross-reference BACKUP

```bash
python SUNO/BMG/tools/build_rym_crossref.py --backup ../BACKUP --write
```

The scanner uses boundary-aware genre matching and aggregates metadata/style phrases, explicit `[RYM: ...]` annotations, BOX/RYM descriptor hits, and negative prompt terms.

## Build empirical fingerprints

```bash
python SUNO/BMG/tools/build_empirical_fingerprints.py --backup ../BACKUP
```

The empirical pass matches compact style metadata first and collapses duplicate/reordered style profiles before computing support and lift. The current private BACKUP scan covers **441 tracks / 325 unique style profiles**. Full `SYSOP_*_CORE.JSON` objects remain in private BACKUP.

## Score BMG-catalog overlap

```bash
python SUNO/BMG/tools/score_related_catalog_overlap.py \
  --fingerprints ../BACKUP/analysis/fingerprints \
  --evidence SUNO/BMG/evidence/related-catalog-vocabulary.json \
  --out ../BACKUP/analysis/bmg_related_overlap.json
```

The scorer classifies each candidate modifier as `reinforced`, `cross_genre_overlap`, or `novel_candidate` against the SYSOP corpus. This makes BMG-related language testable without laundering catalog titles into official taxonomy.

## Compare fingerprints

```bash
python SUNO/BMG/tools/compare_fingerprints.py \
  ../BACKUP/analysis/fingerprints/SYSOP_NEUROFUNK_CORE.JSON \
  ../BACKUP/analysis/fingerprints/SYSOP_SPEED_GARAGE_CORE.JSON
```

## Compile one map

```bash
python SUNO/BMG/tools/compile_genre_map.py \
  SUNO/BMG/maps/BMG-NEUROFUNK.JSON \
  --fingerprint ../BACKUP/analysis/fingerprints/SYSOP_NEUROFUNK_CORE.JSON \
  --empirical-min-lift 1.5
```

## Blend maps

```bash
python SUNO/BMG/tools/blend_maps.py \
  SUNO/BMG/maps/BMG-SPEED-GARAGE.JSON \
  SUNO/BMG/maps/BMG-BASSLINE.JSON \
  --weights 1,0.8
```

## Validate

```bash
python -m pip install -r SUNO/BMG/tools/requirements.txt
python SUNO/BMG/tools/validate_maps.py
python -m unittest discover -s SUNO/BMG/tools -p 'test_*.py'
```

Validation enforces Draft 2020-12 map schemas, JSON duplicate-key checks, registry integrity, local evidence references, per-term provenance, track/count consistency, relationship endpoints, candidate ranking rules and explicit dummy values. Missing dependencies fail closed. Historical external evidence receives structural checks; its source contents were not all re-fetched during this harvest.

