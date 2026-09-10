#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_weights(raw, n):
    if not raw:
        return [1.0] * n
    vals = [float(x) for x in raw.split(',')]
    if len(vals) != n:
        raise SystemExit(f'--weights needs {n} comma-separated values')
    return vals


def main():
    p = argparse.ArgumentParser(description='Blend multiple genre maps without flattening provenance.')
    p.add_argument('maps', nargs='+')
    p.add_argument('--weights', help='Comma-separated map weights in path order')
    p.add_argument('--format', choices=['rym', 'json'], default='rym')
    p.add_argument('--max-terms', type=int, default=36)
    a = p.parse_args()

    docs = [json.loads(Path(x).read_text()) for x in a.maps]
    weights = parse_weights(a.weights, len(docs))
    scores = defaultdict(float)
    origins = defaultdict(list)
    negatives = []
    mins, maxs, preferred = [], [], []

    for d, mw in zip(docs, weights):
        gid = d['id']
        t = d.get('parameters', {}).get('tempo_bpm', {})
        if isinstance(t.get('min'), (int, float)): mins.append(t['min'])
        if isinstance(t.get('max'), (int, float)): maxs.append(t['max'])
        preferred.extend(t.get('preferred') or [])

        base = [(d['genre']['canonical'], 1.0, 'genre')]
        base += [(x, 0.82, 'rym.genre') for x in d['taxonomy'].get('rym', {}).get('genres', [])]
        base += [(x, 0.55, 'rym.descriptor') for x in d['taxonomy'].get('rym', {}).get('descriptors', [])]
        base += [(x, 0.58, 'sysop.seed') for x in d['taxonomy'].get('sysop', {}).get('seed_terms', [])]
        base += [(x.get('term'), float(x.get('weight', 0)), x.get('source', 'prompt'))
                 for x in d.get('prompt_map', {}).get('positive', []) if x.get('term')]

        for term, tw, source in base:
            key = term.casefold()
            scores[key] += mw * tw
            origins[key].append({'map': gid, 'source': source, 'map_weight': mw, 'term_weight': tw})
        negatives.extend(d.get('prompt_map', {}).get('negative', []))

    ranked = sorted(scores, key=lambda k: (-scores[k], k))[:a.max_terms]
    names = {k: origins[k][0] for k in ranked}
    # Recover original casing from first matching map/source occurrence.
    display = {}
    for d in docs:
        candidates = [d['genre']['canonical']]
        candidates += d['taxonomy'].get('rym', {}).get('genres', [])
        candidates += d['taxonomy'].get('rym', {}).get('descriptors', [])
        candidates += d['taxonomy'].get('sysop', {}).get('seed_terms', [])
        candidates += [x.get('term') for x in d.get('prompt_map', {}).get('positive', []) if x.get('term')]
        for x in candidates:
            display.setdefault(x.casefold(), x)

    tempo_intersection = None
    if mins and maxs:
        lo, hi = max(mins), min(maxs)
        if lo <= hi:
            tempo_intersection = {'min': lo, 'max': hi}

    if a.format == 'rym':
        print(', '.join(display[k] for k in ranked))
        return

    out = {
        'maps': [{'id': d['id'], 'weight': w} for d, w in zip(docs, weights)],
        'tempo': {
            'intersection': tempo_intersection,
            'preferred_candidates': sorted(set(preferred))
        },
        'terms': [
            {'term': display[k], 'score': round(scores[k], 4), 'origins': origins[k]}
            for k in ranked
        ],
        'negative': list(dict.fromkeys(negatives))
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
