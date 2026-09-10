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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("map")
    p.add_argument("--format", choices=["rym", "json"], default="rym")
    p.add_argument("--max-terms", type=int, default=28)
    a = p.parse_args()

    d = json.loads(Path(a.map).read_text())
    g = d["genre"]
    tax = d["taxonomy"]
    pm = d["prompt_map"]

    weighted = sorted(pm.get("positive", []), key=lambda x: float(x.get("weight", 0)), reverse=True)
    terms = [g["canonical"]]
    terms += tax.get("rym", {}).get("genres", [])
    terms += [x.get("term") for x in weighted if x.get("term")]
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
        "negative": pm.get("negative", [])
    }
    print(json.dumps(frame, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
