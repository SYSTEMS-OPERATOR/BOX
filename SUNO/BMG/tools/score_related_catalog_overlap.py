#!/usr/bin/env python3
"""Score BMG-related catalog vocabulary against generated SYSOP fingerprints.

This tool never promotes catalog/release language to official BMG taxonomy. It answers a
narrower question: which BMG-distributed catalog modifiers are already characteristic of the
SYSOP corpus, and which are novel candidates worth testing?
"""
import argparse
import json
import re
from pathlib import Path

VERSION = "0.1.0"


def norm(value):
    if not isinstance(value, str):
        return ""
    value = value.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).strip().casefold()


def load_json(path):
    return json.loads(Path(path).read_text())


def term_rows(fp):
    out = {}
    for bucket in ("core_terms", "signature_terms"):
        for row in fp.get(bucket, []) or []:
            if not isinstance(row, dict) or not row.get("term"):
                continue
            key = norm(row["term"])
            prior = out.get(key)
            if prior is None or float(row.get("score", 0) or 0) > float(prior.get("score", 0) or 0):
                out[key] = row
    return out


def matches(candidate, terms):
    c = norm(candidate)
    if not c:
        return []
    rx = re.compile(rf"(?<!\w){re.escape(c)}(?!\w)", re.I)
    found = []
    for key, row in terms.items():
        if key == c or rx.search(key):
            found.append(row)
    found.sort(key=lambda x: (-(x.get("score") or 0), -(x.get("support") or 0)))
    return found


def evidence_count(block, candidate):
    c = norm(candidate)
    count = 0
    for key in ("release_title_terms", "track_title_terms"):
        for row in block.get(key, []) or []:
            text = row.get("term") if isinstance(row, dict) else row
            if c and c in norm(text):
                count += 1
    return count


def confidence_weight(conf):
    return {"high": 1.0, "moderate": 0.8, "low": 0.55, "insufficient": 0.25}.get(conf, 0.6)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fingerprints", required=True, help="Directory containing SYSOP_*_CORE.JSON")
    p.add_argument("--evidence", required=True, help="related-catalog-vocabulary.json")
    p.add_argument("--out", help="Output JSON path; defaults to stdout")
    p.add_argument("--top", type=int, default=20)
    args = p.parse_args()

    evidence = load_json(args.evidence)
    fp_dir = Path(args.fingerprints)
    fps = {}
    global_index = {}
    for path in sorted(fp_dir.glob("SYSOP_*_CORE.JSON")):
        try:
            fp = load_json(path)
        except Exception:
            continue
        map_id = fp.get("map_id")
        if not map_id:
            continue
        rows = term_rows(fp)
        fps[map_id] = (fp, rows)
        for term, row in rows.items():
            global_index.setdefault(term, []).append({
                "map_id": map_id,
                "genre": fp.get("genre"),
                "support": row.get("support"),
                "lift": row.get("lift"),
                "score": row.get("score"),
            })

    result = {
        "version": VERSION,
        "purpose": "Rank BMG-related catalog modifiers by overlap with SYSOP empirical fingerprints without treating them as official BMG taxonomy.",
        "evidence_version": evidence.get("version"),
        "maps": {},
        "novel_candidates": [],
    }

    for map_id, block in (evidence.get("maps") or {}).items():
        fp_pair = fps.get(map_id)
        fp, local_terms = fp_pair if fp_pair else ({}, {})
        conf = (fp.get("sample") or {}).get("confidence")
        ranked = []
        for candidate in block.get("candidate_modifiers", []) or []:
            local = matches(candidate, local_terms)
            global_hits = []
            for other_id, (other_fp, other_terms) in fps.items():
                hit = matches(candidate, other_terms)
                if hit:
                    best = hit[0]
                    global_hits.append({
                        "map_id": other_id,
                        "genre": other_fp.get("genre"),
                        "support": best.get("support"),
                        "lift": best.get("lift"),
                        "score": best.get("score"),
                    })
            global_hits.sort(key=lambda x: (-(x.get("score") or 0), -(x.get("support") or 0)))
            ev = evidence_count(block, candidate)
            best = local[0] if local else None
            corpus_score = float(best.get("score", 0) or 0) if best else 0.0
            support = float(best.get("support", 0) or 0) if best else 0.0
            lift = float(best.get("lift", 0) or 0) if best else 0.0
            priority = (1.0 + 0.35 * ev) * (1.0 + corpus_score) * confidence_weight(conf)
            row = {
                "term": candidate,
                "catalog_evidence_hits": ev,
                "local_overlap": bool(local),
                "local_support": round(support, 4),
                "local_lift": round(lift, 3),
                "local_score": round(corpus_score, 4),
                "fingerprint_confidence": conf,
                "other_sysop_maps": global_hits[:8],
                "test_priority": round(priority, 4),
                "status": "reinforced" if local else ("cross_genre_overlap" if global_hits else "novel_candidate"),
            }
            ranked.append(row)
            if row["status"] == "novel_candidate":
                result["novel_candidates"].append({"map_id": map_id, "term": candidate, "test_priority": row["test_priority"]})
        ranked.sort(key=lambda x: (-x["test_priority"], x["term"].casefold()))
        result["maps"][map_id] = {
            "genre": fp.get("genre") if fp else None,
            "fingerprint_confidence": conf,
            "candidates": ranked[:args.top],
        }

    result["novel_candidates"].sort(key=lambda x: (-x["test_priority"], x["map_id"], x["term"].casefold()))
    result["novel_candidates"] = result["novel_candidates"][:100]
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
