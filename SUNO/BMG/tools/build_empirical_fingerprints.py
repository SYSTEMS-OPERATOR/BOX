#!/usr/bin/env python3
"""
Build empirical SYSOP genre fingerprints from a local SYSTEMS-OPERATOR/BACKUP clone.

Genre membership is matched against compact display_tags first (falling back to metadata.tags
only when display_tags are absent). Feature evidence comes from display_tags, metadata.tags,
and metadata.negative_tags. Ordinary lyric/prompt prose is ignored except explicit [RYM: ...]
blocks. Exact/reordered duplicate style profiles are collapsed for the primary support/lift
statistics so remix/variant families do not masquerade as independent evidence.
"""
import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

VERSION = "0.2.0"
RYM = re.compile(r"\[RYM\s*:\s*([^\]]+)\]", re.I)
BPM = re.compile(r"(?<!\d)(\d{2,3}(?:\.\d+)?)\s*BPM\b", re.I)
HZ = re.compile(r"(?<![\d.])(\d{1,4}(?:\.\d+)?)\s*Hz\b", re.I)
KEY = re.compile(r"(?<![A-Za-z])([A-G](?:#|b|♯|♭)?)[\s_-]*(major|minor|maj|min)\b", re.I)
CAMELOT = re.compile(r"(?<!\d)(0?[1-9]|1[0-2])([AB])\b", re.I)
HEADINGS = {"genre", "genres", "style", "styles", "mood", "moods", "vocals", "vocal", "production"}

def normalize(s):
    if not isinstance(s, str):
        return ""
    s = s.replace("♯", "#").replace("♭", "b").replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s).strip(" \t\r\n,;|")
    return s.casefold()

def boundary(term):
    return re.compile(rf"(?<!\w){re.escape(normalize(term))}(?!\w)", re.I)

def split_terms(s):
    if not isinstance(s, str):
        return []
    out = []
    for x in re.split(r"[,;\n|]+", s):
        x = re.sub(r"\s+", " ", x).strip(" .:-\t")
        if not x:
            continue
        if ":" in x:
            left, right = x.split(":", 1)
            if normalize(left) in HEADINGS and right.strip():
                x = right.strip()
        words = re.findall(r"[A-Za-z0-9#&+'/-]+", x)
        if 1 <= len(words) <= 10 and 2 <= len(x) <= 96:
            out.append(x)
    return out

def metadata(rec):
    raw = rec.get("raw_profile_record") or {}
    return raw, (raw.get("metadata") or rec.get("metadata") or {})

def genre_text(rec):
    raw, meta = metadata(rec)
    for x in (rec.get("display_tags"), raw.get("display_tags")):
        if isinstance(x, str) and x.strip():
            return x
    return meta.get("tags") or ""

def positive_text(rec):
    raw, meta = metadata(rec)
    vals = []
    for x in (rec.get("display_tags"), raw.get("display_tags"), meta.get("tags")):
        if isinstance(x, str) and x.strip() and x not in vals:
            vals.append(x)
    return " | ".join(vals)

def style_text(rec):
    raw, meta = metadata(rec)
    if isinstance(meta.get("tags"), str) and meta.get("tags").strip():
        return meta["tags"]
    return rec.get("display_tags") or raw.get("display_tags") or ""

def style_signature(rec):
    parts = sorted({normalize(x) for x in split_terms(style_text(rec)) if normalize(x)})
    return "||".join(parts) if parts else normalize(style_text(rec))

def negative_text(rec):
    _, meta = metadata(rec)
    return meta.get("negative_tags") or ""

def prompt_text(rec):
    _, meta = metadata(rec)
    return meta.get("prompt") or ""

def vocab_from_maps(maps):
    vocab = {}
    for d in maps:
        items = []
        g = d.get("genre", {})
        items += [g.get("canonical")] + g.get("aliases", []) + g.get("adjacent", [])
        tax = d.get("taxonomy", {})
        for ns in ("rym", "sysop", "bmg"):
            block = tax.get(ns, {})
            for key in ("genres", "descriptors", "seed_terms", "genre_terms", "mood_terms",
                        "instrument_terms", "production_terms", "sync_usage_terms"):
                items += block.get(key, []) or []
        for x in d.get("prompt_map", {}).get("positive", []) or []:
            if isinstance(x, dict):
                items.append(x.get("term"))
            elif isinstance(x, str):
                items.append(x)
        for x in items:
            if isinstance(x, str) and 2 <= len(x.strip()) <= 96:
                vocab.setdefault(normalize(x), x.strip())
    return vocab

def presence(text, compiled):
    hay = normalize(text)
    return {term for term, rx in compiled.items() if rx.search(hay)}

def anchors(text):
    bpms = [float(x) for x in BPM.findall(text)]
    hz = [float(x) for x in HZ.findall(text)]
    keys = []
    for note, mode in KEY.findall(text):
        mode = "minor" if mode.casefold().startswith("min") else "major"
        keys.append(f"{note.replace('♯','#').replace('♭','b')} {mode}")
    camelot = [f"{int(n):02d}{letter.upper()}" for n, letter in CAMELOT.findall(text)]
    return bpms, hz, keys, camelot

def confidence(n):
    if n < 3:
        return "insufficient"
    if n < 8:
        return "low"
    if n < 20:
        return "moderate"
    return "high"

def counter_rows(counter, total, limit=40, unit="profiles"):
    return [
        {"term": term, unit: count, "support": round(count / total, 4) if total else 0.0}
        for term, count in counter.most_common(limit)
    ]

def term_stats(profile_counter, global_profile_counter, track_counter, global_track_counter,
               profile_n, total_profiles, track_n, total_tracks, min_count):
    rows = []
    for term, count in profile_counter.items():
        if count < min_count or not profile_n or not total_profiles:
            continue
        support = count / profile_n
        global_support = global_profile_counter.get(term, 0) / total_profiles
        lift = support / max(global_support, 1 / total_profiles)
        score = support * math.log2(1 + lift) * math.log2(2 + count)
        tracks = track_counter.get(term, 0)
        rows.append({
            "term": term,
            "profiles": count,
            "support": round(support, 4),
            "global_support": round(global_support, 4),
            "lift": round(lift, 3),
            "score": round(score, 4),
            "tracks": tracks,
            "track_support": round(tracks / track_n, 4) if track_n else 0.0,
            "global_track_support": round(global_track_counter.get(term, 0) / total_tracks, 4)
                if total_tracks else 0.0,
        })
    rows.sort(key=lambda x: (-x["score"], -x["profiles"], -x["tracks"], x["term"]))
    return rows

def load_records(meta_dir):
    records = []
    for path in sorted(meta_dir.glob("*.json")):
        try:
            x = json.loads(path.read_text())
        except Exception:
            continue
        if isinstance(x, dict):
            records.append(x)
    return records

def fingerprint_name(map_id):
    return "SYSOP_" + map_id.removeprefix("BMG-").replace("-", "_") + "_CORE"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backup", required=True, help="BACKUP repo root or its metadata directory")
    p.add_argument("--maps", help="Map directory; defaults to ../maps beside this tool")
    p.add_argument("--out", help="Fingerprint output directory; defaults to ../fingerprints")
    p.add_argument("--map", action="append", dest="only_maps", help="Limit to map id; repeatable")
    p.add_argument("--top", type=int, default=40)
    p.add_argument("--core-support", type=float, default=0.20)
    p.add_argument("--signature-lift", type=float, default=1.50)
    p.add_argument("--min-count", type=int, default=2, help="Minimum unique style profiles")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    here = Path(__file__).resolve()
    maps_dir = Path(a.maps).resolve() if a.maps else here.parents[1] / "maps"
    out_dir = Path(a.out).resolve() if a.out else here.parents[1] / "fingerprints"
    meta_dir = Path(a.backup).resolve()
    if meta_dir.name != "metadata":
        meta_dir /= "metadata"

    maps = []
    only = set(a.only_maps or [])
    for path in sorted(maps_dir.glob("BMG-*.JSON")):
        if path.name == "BMG-TEMPLATE.JSON":
            continue
        try:
            d = json.loads(path.read_text())
        except Exception:
            continue
        if only and d.get("id") not in only:
            continue
        maps.append(d)

    records = load_records(meta_dir)
    if not records:
        raise SystemExit(f"No readable metadata JSON found in {meta_dir}")

    vocab = vocab_from_maps(maps)
    compiled = {term: boundary(term) for term in vocab}
    global_track_terms = Counter()
    global_track_segments = Counter()
    record_cache = []
    profiles = {}

    for rec in records:
        text = positive_text(rec)
        gtext = genre_text(rec)
        terms = presence(text, compiled)
        segs = {normalize(x) for x in split_terms(text)}
        segs.discard("")
        sig = style_signature(rec)
        global_track_terms.update(terms)
        global_track_segments.update(segs)
        item = (rec, gtext, text, terms, segs, sig)
        record_cache.append(item)
        if sig:
            profiles.setdefault(sig, item)

    global_profile_terms = Counter()
    global_profile_segments = Counter()
    for _, _, _, terms, segs, _ in profiles.values():
        global_profile_terms.update(terms)
        global_profile_segments.update(segs)

    generated_at = datetime.now(timezone.utc).isoformat()
    index = {
        "version": VERSION,
        "generated_at": generated_at,
        "source": "SYSTEMS-OPERATOR/BACKUP",
        "total_tracks_scanned": len(records),
        "total_unique_style_profiles": len(profiles),
        "fingerprints": [],
    }

    if not a.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for d in maps:
        map_id = d["id"]
        g = d["genre"]
        aliases = [g.get("canonical")] + g.get("aliases", [])
        alias_rx = [boundary(x) for x in aliases if isinstance(x, str) and x.strip()]

        matched_tracks = []
        matched_profiles = {}
        track_term_df = Counter()
        track_seg_df = Counter()
        profile_term_df = Counter()
        profile_seg_df = Counter()
        neg_profile_df = Counter()
        rym_profile_df = Counter()
        bpm_profile_df = Counter()
        hz_profile_df = Counter()
        key_profile_df = Counter()
        camelot_profile_df = Counter()
        model_track_df = Counter()

        for rec, gtext, text, terms, segs, sig in record_cache:
            hay = normalize(gtext)
            if not any(rx.search(hay) for rx in alias_rx):
                continue
            matched_tracks.append((rec, text, terms, segs, sig))
            track_term_df.update(terms)
            track_seg_df.update(segs)
            if sig:
                matched_profiles.setdefault(sig, (rec, text, terms, segs))
            raw, _ = metadata(rec)
            model = raw.get("major_model_version") or raw.get("model_name")
            if model:
                model_track_df[str(model)] += 1

        for rec, text, terms, segs in matched_profiles.values():
            profile_term_df.update(terms)
            profile_seg_df.update(segs)
            neg_profile_df.update({normalize(x) for x in split_terms(negative_text(rec)) if normalize(x)})
            for block in RYM.findall(prompt_text(rec)):
                rym_profile_df.update({normalize(x) for x in split_terms(block) if normalize(x)})
            bpms, hz, keys, camelot = anchors(text)
            bpm_profile_df.update(set(f"{x:g}" for x in bpms))
            hz_profile_df.update(set(f"{x:g}" for x in hz))
            key_profile_df.update(set(keys))
            camelot_profile_df.update(set(camelot))

        track_n = len(matched_tracks)
        profile_n = len(matched_profiles)

        controlled = term_stats(
            profile_term_df, global_profile_terms, track_term_df, global_track_terms,
            profile_n, len(profiles), track_n, len(records), a.min_count
        )
        discovered = term_stats(
            profile_seg_df, global_profile_segments, track_seg_df, global_track_segments,
            profile_n, len(profiles), track_n, len(records), a.min_count
        )
        merged = {}
        for row in controlled + discovered:
            prior = merged.get(row["term"])
            if prior is None or row["score"] > prior["score"]:
                merged[row["term"]] = row
        ranked = sorted(
            merged.values(),
            key=lambda x: (-x["score"], -x["profiles"], -x["tracks"], x["term"])
        )

        core = [x for x in ranked if x["support"] >= a.core_support][:a.top]
        signature = [x for x in ranked if x["lift"] >= a.signature_lift][:a.top]

        top_names = {x["term"] for x in ranked[:32]}
        pair_df = Counter()
        for _, _, terms, segs in matched_profiles.values():
            present = sorted((terms | segs) & top_names)
            pair_df.update(combinations(present, 2))
        pairs = [
            {"terms": list(pair), "profiles": count, "support": round(count / profile_n, 4) if profile_n else 0.0}
            for pair, count in pair_df.most_common(a.top)
        ]

        ident = fingerprint_name(map_id)
        fp = {
            "id": ident,
            "version": VERSION,
            "map_id": map_id,
            "genre": g.get("canonical"),
            "sample": {
                "matched_tracks": track_n,
                "unique_style_profiles": profile_n,
                "duplicate_style_tracks": max(0, track_n - profile_n),
                "total_tracks": len(records),
                "total_unique_style_profiles": len(profiles),
                "track_match_rate": round(track_n / len(records), 4),
                "profile_match_rate": round(profile_n / len(profiles), 4) if profiles else 0.0,
                "confidence": confidence(profile_n),
                "match_aliases": [x for x in aliases if isinstance(x, str)],
                "membership_source": "display_tags; metadata.tags only when display_tags absent",
            },
            "core_terms": core,
            "signature_terms": signature,
            "cooccurrence": pairs,
            "musical_anchors": {
                "bpm": counter_rows(bpm_profile_df, profile_n, a.top),
                "frequency_hz": counter_rows(hz_profile_df, profile_n, a.top),
                "keys": counter_rows(key_profile_df, profile_n, a.top),
                "camelot": counter_rows(camelot_profile_df, profile_n, a.top),
            },
            "rym": counter_rows(rym_profile_df, profile_n, a.top),
            "negative_terms": counter_rows(neg_profile_df, profile_n, a.top),
            "model_distribution_tracks": counter_rows(model_track_df, track_n, a.top, unit="tracks"),
            "thresholds": {
                "core_support": a.core_support,
                "signature_lift": a.signature_lift,
                "min_unique_style_profiles": a.min_count,
            },
            "provenance": {
                "generated_at": generated_at,
                "builder": "SUNO/BMG/tools/build_empirical_fingerprints.py",
                "builder_version": VERSION,
                "source_repo": "SYSTEMS-OPERATOR/BACKUP",
                "source_path": "metadata/*.json",
                "map_source": f"SUNO/BMG/maps/{map_id}.JSON",
                "policy": "Genre membership from compact display tags; primary statistics dedupe identical/reordered style profiles; ordinary lyric/prompt prose ignored except explicit [RYM: ...] blocks.",
            },
        }

        filename = f"{ident}.JSON"
        index["fingerprints"].append({
            "id": ident,
            "map_id": map_id,
            "genre": g.get("canonical"),
            "matched_tracks": track_n,
            "unique_style_profiles": profile_n,
            "confidence": confidence(profile_n),
            "file": filename,
        })
        if a.dry_run:
            print(json.dumps(fp, indent=2, ensure_ascii=False))
        else:
            (out_dir / filename).write_text(json.dumps(fp, indent=2, ensure_ascii=False) + "\n")

    if not a.dry_run:
        (out_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps(index, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
