"""
SOPHY Hourly Recollection Harness (v2)

Writes scoped recollection JSON to `recollections/` when run.
This file is intended to be run locally or in CI. When run in GitHub Actions
(with GITHUB_TOKEN) the provided workflow will commit the generated file back
into the repository automatically.
"""

import json
import datetime
import os

SCHEMA_TEMPLATE = {
    "timestamp": None,
    "thread_id": None,
    "local_digest": None,
    "cross_thread_status": "scoped",
    "prior_diff": None,
    "failure_modes": []
}


def run_local_digest(sources):
    return sources[-10:]


def attempt_cross_thread_retrieval():
    return None, {"code": "FT-G-01", "title": "limited_execution_context", "severity": "actionable", "suggested_mitigation": "Enable cross-thread read permissions or provide exports/manifests for aggregation."}


def diff_prior(recent, prior):
    prior = prior or []
    return {"added": [t for t in recent if t not in prior], "removed": [t for t in prior if t not in recent]}


def ensure_recollections_dir():
    os.makedirs('recollections', exist_ok=True)


def write_recollection(schema):
    ensure_recollections_dir()
    ts = schema['timestamp'].replace(':', '-')
    filename = f"recollections/recollection_{ts}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2)
    return filename


def run(sources, prior_recollection=None):
    schema = dict(SCHEMA_TEMPLATE)
    schema['timestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'
    schema['thread_id'] = 'local-thread'
    schema['local_digest'] = run_local_digest(sources)

    cross, err = attempt_cross_thread_retrieval()
    if cross is None:
        schema['cross_thread_status'] = 'unavailable'
        schema['failure_modes'].append(err)
    else:
        schema['cross_thread_status'] = 'available'
        schema['cross_thread_data'] = cross

    schema['prior_diff'] = diff_prior(schema['local_digest'], prior_recollection)

    filepath = write_recollection(schema)
    print(f"Wrote recollection -> {filepath}")
    return schema, filepath


if __name__ == '__main__':
    sources = []
    try:
        if os.path.exists('/mnt/data/SOPHY_compact_persona_v1.json'):
            sources.append('uploaded:SOPHY_compact_persona_v1.json')
        if os.path.exists('/mnt/data/SOPHY_anchor_canvas.md'):
            sources.append('uploaded:SOPHY_anchor_canvas.md')
    except Exception:
        pass

    if not sources:
        sources = [
            'user requested SOPHY_HOURLY_RECOLLECTION',
            'recent: PR merged into BOX'
        ]

    run(sources)
