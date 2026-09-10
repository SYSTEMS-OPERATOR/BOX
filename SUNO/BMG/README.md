# SUNO/BMG

Genre-specific parameter maps for Suno prompting.

Each `BMG-*.JSON` keeps four layers separate: **BMG** (public catalog vocabulary),
**RYM** (genre/descriptors), **SYSOP** (observed vocabulary from private `BACKUP`),
and **SUNO** (compiled prompt terms). Useful overlap is preserved without erasing provenance.

BMG's public site currently verifies **Electronic** as the parent genre. Child BMG terms
stay `pending_verification` until a live catalog/filter pass confirms them.

Initial maps: `BMG-BREAKCORE.JSON`, `BMG-DNB.JSON`, `BMG-BREAKS.JSON`.
Next targets are listed in `registry.json`; clone a map or use `BMG-TEMPLATE.JSON`.

To cross-reference a local clone of `SYSTEMS-OPERATOR/BACKUP`:

```bash
python SUNO/BMG/tools/build_rym_crossref.py --backup ../BACKUP --write
```

The tool aggregates metadata vocabulary and explicit `[RYM: ...]` annotations only.
It does not copy lyrics, audio, artwork, cookies, auth data, or full raw records.
