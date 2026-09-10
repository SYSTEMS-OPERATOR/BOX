#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def unique(seq):
    out = []
    seen = set()
    for x in seq:
        key = x.casefold() if isinstance(x, str) else json.dumps(x, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out


def load_fingerprint(path, map_id):
    if not path:
        return None
    fp = json.loads(Path(path).read_text())
    if fp.get("map_id") != map_id:
        raise SystemExit(f"fingerprint map mismatch: {fp.get('map_id')} != {map_id}")
    return fp


def empirical_terms(fp, limit, min_lift):
    if not fp:
        return []
    rows = []
    seen = set()
    for key in ("core_terms", "signature_terms"):
        for x in fp.get(key, []) or []:
            term = x.get("term") if isinstance(x, dict) else None
            if not term:
                continue
            k = term.casefold()
            if k in seen:
                continue
            if float(x.get("lift", 0)) < min_lift:
                continue
            seen.add(k)
            rows.append({
                "term": term,
                "support": x.get("support"),
                "lift": x.get("lift"),
                "score": x.get("score"),
                "profiles": x.get("profiles"),
                "tracks": x.get("tracks"),
                "source": "sysop_empirical",
            })
    rows.sort(key=lambda x: (-(x.get("score") or 0), -(x.get("support") or 0), x["term"]))
    return rows[:limit]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("map")
    p.add_argument("--format", choices=["rym", "json"], default="rym")
    p.add_argument("--max-terms", type=int, default=28)
    p.add_argument("--fingerprint", help="Optional SYSOP_*_CORE.JSON generated from BACKUP")
    p.add_argument("--empirical-limit", type=int, default=10)
    p.add_argument("--empirical-min-lift", type=float, default=1.5)
    a = p.parse_args()

    d = json.loads(Path(a.map).read_text())
    g = d["genre"]
    tax = d["taxonomy"]
    pm = d["prompt_map"]
    fp = load_fingerprint(a.fingerprint, d["id"])
    empirical = empirical_terms(fp, a.empirical_limit, a.empirical_min_lift)

    weighted = sorted(pm.get("positive", []), key=lambda x: float(x.get("weight", 0)), reverse=True)
    terms = [g["canonical"]]
    terms += tax.get("rym", {}).get("genres", [])
    terms += [x.get("term") for x in weighted if x.get("term")]
    terms += [x["term"] for x in empirical]
    terms += tax.get("rym", {}).get("descriptors", [])
    terms += tax.get("sysop", {}).get("seed_terms", [])
    terms = unique([x for x in terms if isinstance(x, str) and x.strip()])[:a.max_terms]

    tempo = d.get("parameters", {}).get("tempo_bpm", {})
    preferred = tempo.get("preferred") or []
    bpm = preferred[0] if preferred else None

    if a.format == "rym":
        if bpm:
            terms.append(f"{bpm} BPM")
        print(", ".join(unique(terms)))
        return

    frame = {
        "id": d["id"],
        "genre": g["canonical"],
        "tempo_bpm": {
            "preferred": preferred,
            "min": tempo.get("min"),
            "max": tempo.get("max")
        },
        "terms": [
            {"term": x.get("term"), "weight": x.get("weight"), "source": x.get("source")}
            for x in weighted
        ],
        "rym": {
            "genres": tax.get("rym", {}).get("genres", []),
            "descriptors": tax.get("rym", {}).get("descriptors", [])
        },
        "sysop_seed_terms": tax.get("sysop", {}).get("seed_terms", []),
        "sysop_empirical": {
            "fingerprint_id": fp.get("id") if fp else None,
            "sample": fp.get("sample") if fp else None,
            "terms": empirical
        },
        "negative": pm.get("negative", [])
    }
    print(json.dumps(frame, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
