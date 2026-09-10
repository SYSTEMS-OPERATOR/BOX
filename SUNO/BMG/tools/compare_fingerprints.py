#!/usr/bin/env python3
"""Compare two empirical SYSOP fingerprint JSON files."""
import argparse
import json
from pathlib import Path

def terms(d, key):
    return {x["term"]: x for x in d.get(key, []) if isinstance(x, dict) and x.get("term")}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("left")
    p.add_argument("right")
    p.add_argument("--top", type=int, default=20)
    a = p.parse_args()

    left = json.loads(Path(a.left).read_text())
    right = json.loads(Path(a.right).read_text())
    lc = terms(left, "core_terms")
    rc = terms(right, "core_terms")
    ls = terms(left, "signature_terms")
    rs = terms(right, "signature_terms")

    shared = sorted(
        set(lc) & set(rc),
        key=lambda t: -((lc[t].get("support", 0) + rc[t].get("support", 0)) / 2),
    )[:a.top]
    left_only = sorted(
        set(ls) - set(rs),
        key=lambda t: -ls[t].get("score", 0),
    )[:a.top]
    right_only = sorted(
        set(rs) - set(ls),
        key=lambda t: -rs[t].get("score", 0),
    )[:a.top]

    out = {
        "left": {"id": left.get("id"), "genre": left.get("genre")},
        "right": {"id": right.get("id"), "genre": right.get("genre")},
        "shared_core": [
            {
                "term": t,
                "left_support": lc[t].get("support"),
                "right_support": rc[t].get("support"),
                "left_lift": lc[t].get("lift"),
                "right_lift": rc[t].get("lift"),
            }
            for t in shared
        ],
        "left_signature_only": [ls[t] for t in left_only],
        "right_signature_only": [rs[t] for t in right_only],
        "tempo": {
            "left": left.get("musical_anchors", {}).get("bpm", [])[:10],
            "right": right.get("musical_anchors", {}).get("bpm", [])[:10],
        },
        "frequency_hz": {
            "left": left.get("musical_anchors", {}).get("frequency_hz", [])[:10],
            "right": right.get("musical_anchors", {}).get("frequency_hz", [])[:10],
        },
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
