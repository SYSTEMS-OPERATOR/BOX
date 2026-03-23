#!/usr/bin/env python3
import argparse
import json
from datetime import UTC, datetime
import os


def utc_iso_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def write_simple_yaml(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for key, value in payload.items():
            rendered = str(value).replace("'", "''")
            f.write(f"{key}: '{rendered}'\n")

parser = argparse.ArgumentParser()
parser.add_argument('--in', dest='infile', required=True)
parser.add_argument('--out', dest='outdir', required=True)
parser.add_argument('--dry-run', dest='dry', action='store_true')
args = parser.parse_args()

with open(args.infile, 'r') as f:
    threads = json.load(f)

summary = {
    'generated_at': utc_iso_now(),
    'threads_processed': len(threads),
    'threads': threads,
    'summary': 'Auto-generated recollection (dry run: %s)' % args.dry
}

os.makedirs(args.outdir, exist_ok=True)
with open(os.path.join(args.outdir, 'recollection_summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)

anchor = {
    'id': 'anchor-' + datetime.now(UTC).strftime('%Y%m%d%H%M%S'),
    'timestamp_utc': utc_iso_now(),
    'root_hash': 'deadbeef',
    'summary': 'Recollection anchor (dry run: %s)' % args.dry,
    'signed_by': 'agent.clockwork'
}
write_simple_yaml(os.path.join(args.outdir, 'recollection_anchor.yaml'), anchor)

print('Recollection written to', args.outdir)
