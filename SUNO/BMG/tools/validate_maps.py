#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ID = re.compile(r'^BMG-[A-Z0-9-]+$')
REQ = {'id','version','genre','taxonomy','parameters','prompt_map','cross_reference','provenance'}
PARAMS = {'tempo_bpm','meter','rhythm','drums','bass','harmony','texture','arrangement','mix','vocals'}
SOURCES = {'seed','bmg','rym','sysop','derived'}


def check(path):
    errors = []
    try:
        d = json.loads(path.read_text())
    except Exception as e:
        return [f'invalid JSON: {e}']
    missing = REQ - set(d)
    if missing: errors.append('missing keys: ' + ', '.join(sorted(missing)))
    if not ID.match(str(d.get('id',''))): errors.append('invalid id')
    if path.name != 'BMG-TEMPLATE.JSON' and path.stem != d.get('id'):
        errors.append(f'filename/id mismatch: {path.stem} != {d.get("id")}')
    g = d.get('genre', {})
    if not g.get('canonical') or not isinstance(g.get('aliases'), list): errors.append('genre canonical/aliases invalid')
    tax = d.get('taxonomy', {})
    if not all(k in tax for k in ('bmg','rym','sysop')): errors.append('taxonomy namespaces incomplete')
    p = d.get('parameters', {})
    missing_p = PARAMS - set(p)
    if missing_p: errors.append('missing parameters: ' + ', '.join(sorted(missing_p)))
    t = p.get('tempo_bpm', {})
    lo, hi = t.get('min'), t.get('max')
    if isinstance(lo,(int,float)) and isinstance(hi,(int,float)) and lo > hi: errors.append('tempo min > max')
    for bpm in t.get('preferred', []) or []:
        if isinstance(lo,(int,float)) and isinstance(hi,(int,float)) and not (lo <= bpm <= hi):
            errors.append(f'preferred BPM {bpm} outside range')
    for x in d.get('prompt_map', {}).get('positive', []):
        if x.get('source') not in SOURCES: errors.append(f'unknown prompt source: {x.get("source")}')
        w = x.get('weight')
        if not isinstance(w,(int,float)) or w < 0: errors.append(f'invalid weight for {x.get("term")}')
    return errors


def main():
    maps = Path(__file__).resolve().parents[1] / 'maps'
    failures = 0
    ids = {}
    for path in sorted(maps.glob('BMG-*.JSON')):
        errs = check(path)
        try:
            ident = json.loads(path.read_text()).get('id')
            if ident in ids: errs.append(f'duplicate id also in {ids[ident].name}')
            else: ids[ident] = path
        except Exception: pass
        if errs:
            failures += 1
            print(f'FAIL {path.name}')
            for e in errs: print(f'  - {e}')
        else:
            print(f'OK   {path.name}')
    if failures:
        print(f'\n{failures} map(s) failed validation.')
        return 1
    print(f'\nAll {len(ids)} map ids passed validation.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
