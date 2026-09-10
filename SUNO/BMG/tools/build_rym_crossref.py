#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RYM = re.compile(r"\[RYM\s*:\s*([^\]]+)\]", re.I)

def terms(s):
    if not isinstance(s, str):
        return []
    s = s.replace(";", ",").replace("\n", ",")
    out = []
    for x in s.split(","):
        x = re.sub(r"\s+", " ", x).strip()
        if len(x) > 1:
            out.append(x)
    return out

def alias_pattern(alias):
    parts = [re.escape(x) for x in re.split(r"[\s/_-]+", alias.strip()) if x]
    if not parts:
        return None
    body = r"[\s/_-]+".join(parts)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.I)

def matches_alias(hay, aliases):
    for alias in aliases:
        p = alias_pattern(alias)
        if p and p.search(hay):
            return True
    return False

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backup", required=True)
    p.add_argument("--top", type=int, default=40)
    p.add_argument("--write", action="store_true")
    p.add_argument("--map", dest="map_id", default=None,
                   help="Only scan one map id, e.g. BMG-UKG")
    a = p.parse_args()

    here = Path(__file__).resolve()
    maps = here.parents[1] / "maps"
    box = here.parents[3]
    meta = Path(a.backup).resolve()
    if meta.name != "metadata":
        meta /= "metadata"

    rym = []
    try:
        rym = [x["name"].casefold()
               for x in json.loads((box / "RYM/styles.json").read_text())["styles"]]
    except Exception:
        pass

    recs = []
    for f in meta.glob("*.json"):
        try:
            recs.append(json.loads(f.read_text()))
        except Exception:
            pass

    out = {}
    for f in sorted(maps.glob("BMG-*.JSON")):
        if f.name == "BMG-TEMPLATE.JSON":
            continue
        d = json.loads(f.read_text())
        if a.map_id and d.get("id") != a.map_id:
            continue

        aliases = list(dict.fromkeys([d["genre"]["canonical"]] + d["genre"].get("aliases", [])))
        c, rc, nc, dc = Counter(), Counter(), Counter(), Counter()
        ids = set()

        for x in recs:
            raw = x.get("raw_profile_record") or {}
            m = raw.get("metadata") or {}
            disp = x.get("display_tags") or raw.get("display_tags") or ""
            style = m.get("tags") or ""
            hay = disp + " | " + style
            if not matches_alias(hay, aliases):
                continue

            if x.get("id"):
                ids.add(x["id"])
            for t in terms(disp) + terms(style):
                c[t] += 1
                lt = t.casefold()
                for q in rym:
                    if re.search(rf"(?<!\w){re.escape(q)}(?!\w)", lt):
                        dc[q] += 1
            for block in RYM.findall(m.get("prompt") or ""):
                for t in terms(block):
                    rc[t] += 1
            for t in terms(m.get("negative_tags") or ""):
                nc[t] += 1

        z = d.setdefault("cross_reference", {}).setdefault("backup", {})
        z.update({
            "status": "scanned",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "matched_tracks": len(ids),
            "top_terms": [{"term": k, "count": v} for k, v in c.most_common(a.top)],
            "rym_terms": [{"term": k, "count": v} for k, v in rc.most_common(a.top)],
            "rym_descriptor_hits": [{"term": k, "count": v} for k, v in dc.most_common(a.top)],
            "negative_terms": [{"term": k, "count": v} for k, v in nc.most_common(a.top)]
        })
        out[d["id"]] = {
            "matched_tracks": len(ids),
            "top_terms": z["top_terms"][:10],
            "rym_terms": z["rym_terms"][:10],
            "rym_descriptor_hits": z["rym_descriptor_hits"][:10]
        }
        if a.write:
            f.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
