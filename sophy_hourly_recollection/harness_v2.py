"""
SOPHY Hourly Recollection Harness (v2)

Writes scoped recollection JSON to `recollections/` when run.
This file is intended to be run locally or in CI. When run in GitHub Actions
(with GITHUB_TOKEN) the provided workflow will commit the generated file back
into the repository automatically.
"""

import datetime
import glob
import json
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


def _load_recollection_file(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def attempt_cross_thread_retrieval(max_entries=24):
    """
    Try to build cross-thread context from previously stored local recollections.

    Returns:
      (data, None) on success where data is a compact aggregation payload
      (None, error_dict) if no historical context can be loaded
    """
    files = sorted(glob.glob('recollections/recollection_*.json'), reverse=True)
    if not files:
        return None, {
            "code": "FT-G-01",
            "title": "limited_execution_context",
            "severity": "actionable",
            "suggested_mitigation": "Enable cross-thread read permissions or provide exports/manifests for aggregation."
        }

    loaded = []
    for path in files[:max_entries]:
        try:
            loaded.append(_load_recollection_file(path))
        except (OSError, json.JSONDecodeError):
            continue

    if not loaded:
        return None, {
            "code": "FT-G-02",
            "title": "cross_thread_artifacts_unreadable",
            "severity": "actionable",
            "suggested_mitigation": "Repair or regenerate files in recollections/ so historical context can be parsed."
        }

    unique_events = []
    seen = set()
    for entry in loaded:
        for item in entry.get('local_digest', []) or []:
            if isinstance(item, str) and item not in seen:
                unique_events.append(item)
                seen.add(item)

    latest = loaded[0]
    return {
        "source": "local-recollections",
        "sampled_recollections": len(loaded),
        "latest_timestamp": latest.get('timestamp'),
        "latest_local_digest": latest.get('local_digest', []),
        "unique_recent_events": unique_events[:50]
    }, None


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
    schema['timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    schema['thread_id'] = 'local-thread'
    schema['local_digest'] = run_local_digest(sources)

    cross, err = attempt_cross_thread_retrieval()
    if cross is None:
        schema['cross_thread_status'] = 'unavailable'
        schema['failure_modes'].append(err)
    else:
        schema['cross_thread_status'] = 'available'
        schema['cross_thread_data'] = cross

    effective_prior = prior_recollection
    if effective_prior is None and cross is not None:
        effective_prior = cross.get('latest_local_digest', [])
    schema['prior_diff'] = diff_prior(schema['local_digest'], effective_prior)

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
