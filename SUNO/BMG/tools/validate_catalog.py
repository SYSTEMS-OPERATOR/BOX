#!/usr/bin/env python3
"""Validate BMG schemas, provenance and cross-file integrity; fail closed.

Nulls and empty arrays are allowed for documented missing evidence.
"""
import json
import re
from pathlib import Path
try:
    from jsonschema import Draft202012Validator
except ImportError:
    raise SystemExit('Install dependency: python -m pip install -r SUNO/BMG/tools/requirements.txt')

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(r'^(?:TODO|TBD|FIXME|PLACEHOLDER|BMG-GENRE|YOUR[_ -].*|INSERT HERE|\.\.\.)$', re.I)

def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=no_duplicate_keys)

def strings(value):
    if isinstance(value, str): yield value
    elif isinstance(value, dict):
        for child in value.values(): yield from strings(child)
    elif isinstance(value, list):
        for child in value: yield from strings(child)

def check_document(d, schema):
    errors = [f'{"/".join(map(str,e.path))}: {e.message}' for e in Draft202012Validator(schema).iter_errors(d)]
    if errors: return errors
    bmg = d['taxonomy']['bmg']
    for group in ('genre_terms','mood_terms','instrument_terms','production_terms','sync_usage_terms','suggestion_terms'):
        for term in bmg.get(group, []):
            if not bmg.get('term_evidence', {}).get(term): errors.append(f'missing BMG provenance: {term}')
    if bmg['status'] == 'not_observed_in_sample' and bmg['term_evidence']:
        errors.append('unobserved status contradicts term evidence')
    if bmg['status'] == 'partially_verified' and not bmg['track_urls']:
        errors.append('partially_verified requires sampled track URLs')
    tempo = d['parameters']['tempo_bpm']
    lo, hi = tempo['min'], tempo['max']
    if lo < 0 or hi <= 0 or lo > hi: errors.append('invalid or placeholder tempo range')
    for bpm in tempo['preferred']:
        if bpm <= 0 or not lo <= bpm <= hi: errors.append('preferred BPM outside range')
    for text in strings(d):
        if PLACEHOLDER.fullmatch(text.strip()) or 'example.com' in text:
            errors.append(f'placeholder value: {text}')
    return errors

def check(path):
    try:
        d = read(path)
        errors = check_document(d, read(ROOT/'genre-map.schema.json'))
        if path.stem != d.get('id'): errors.append('filename/id mismatch')
        return errors
    except (ValueError, OSError) as exc: return [str(exc)]

def validate(root=ROOT):
    errors=[]
    files=[p for p in root.rglob('*') if p.suffix.lower()=='.json']
    parsed={}
    for path in files:
        try:
            parsed[path]=read(path)
            for value in strings(parsed[path]):
                if PLACEHOLDER.fullmatch(value.strip()) or 'example.com' in value:
                    errors.append(f'{path.name}: placeholder {value}')
        except (ValueError,OSError) as exc: errors.append(f'{path.name}: {exc}')
    if errors: return errors, {'json_files':len(files)}
    schema=parsed[root/'genre-map.schema.json']
    Draft202012Validator.check_schema(schema)
    maps={}
    for path in sorted((root/'maps').glob('BMG-*.JSON')):
        d=parsed[path]
        if path.stem!=d.get('id'): errors.append(f'{path.name}: filename/id mismatch')
        if d['id'] in maps: errors.append(f'duplicate map id {d["id"]}')
        maps[d['id']]=d
        errors.extend(f'{path.name}: {e}' for e in check_document(d,schema))
    if (root/'maps/BMG-TEMPLATE.JSON').exists(): errors.append('template map remains')
    registry=parsed[root/'registry.json']
    registered=registry['active']+list(registry['candidate_families'])
    if len(set(registered))!=len(registered): errors.append('duplicate registry ID')
    if set(registered)!=set(maps): errors.append('registry and map IDs differ')
    for family,ids in registry['families'].items():
        if not set(ids)<=set(maps): errors.append(f'unknown ID in family {family}')
    repo=root.parents[1]
    for path,d in parsed.items():
        for text in strings(d):
            if re.fullmatch(r'(?:SUNO/BMG/|RYM/)[^\s]+\.(?:json|JSON|md|py)',text) and not (repo/text).is_file():
                errors.append(f'{path.name}: missing local reference {text}')
    dataset=parsed[root/'bmg_sync_electronic_taxonomy.json']
    ui=parsed[root/'evidence/public-ui-harvest-2026-09-10.json']
    tracks=dataset['tracks_sampled'];terms={t['term']:t for t in dataset['terms']}
    if tracks!=ui['track_observations']: errors.append('track evidence and dataset differ')
    if len(terms)!=len(dataset['terms']): errors.append('duplicate exact term')
    urls={t['url'] for t in tracks}
    if len(urls)!=len(tracks): errors.append('duplicate sampled track URL')
    for term,t in terms.items():
        if not t['sources'] or t['evidence_status']!='observed' or t['canonical_display']!=term:
            errors.append(f'invalid observed term {term}')
        if t['occurrence_count']!=len({s['url'] for s in t['sources']}): errors.append(f'bad occurrence count {term}')
        expected=[x for x in tracks if any(term in x['source_fields'].get(f,[]) for f in ['GENRE','KEYWORDS','INSTRUMENTATION','KEY','TEMPO'])]
        if t['track_occurrence_count']!=len(expected): errors.append(f'bad track count {term}')
        for s in t['sources']:
            if s['page_type']=='track' and s['source_field']!='ALBUM':
                match=next((x for x in tracks if x['url']==s['url']),None)
                if not match or term not in match['source_fields'].get(s['source_field'],[]): errors.append(f'unsupported track term {term}')
    for d in maps.values():
        b=d['taxonomy']['bmg']
        if not set(b['track_urls'])<=urls: errors.append(f'{d["id"]}: unknown sampled URL')
        for term,sources in b['term_evidence'].items():
            if term not in terms or any(s not in terms[term]['sources'] for s in sources): errors.append(f'{d["id"]}: unsupported term evidence {term}')
    for relation in dataset['relationships']:
        if relation['source_term'] not in terms or relation['target_term'] not in terms: errors.append('relationship endpoint missing')
        if relation['evidence_status'] not in ['observed','derived','hypothesis']: errors.append('bad relationship evidence status')
    for tier,candidates in dataset['v6_candidate_vocabulary'].items():
        for candidate in candidates:
            t=terms.get(candidate['term'])
            if not t or not candidate['source_urls']: errors.append('candidate lacks term/provenance')
            if tier=='high_confidence' and (t['track_occurrence_count']<2 or t['label_count']<2): errors.append('high-confidence candidate lacks independent repetition')
            if candidate['suno_control_status']!='untested': errors.append('unsupported Suno-control claim')
    return errors,dict(json_files=len(files),maps=len(maps),tracks=len(tracks),terms=len(terms))

def main():
    errors,counts=validate()
    for error in errors: print('FAIL',error)
    print(json.dumps({'status':'FAIL' if errors else 'PASS',**counts,'errors':len(errors)}))
    return bool(errors)

if __name__=='__main__': raise SystemExit(main())
