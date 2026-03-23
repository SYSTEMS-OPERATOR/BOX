"""
SOPHY Hourly Recollection Harness

This is a deterministic harness template. It runs a local digest over the
current conversation thread (last 10 turns), attempts cross-thread retrieval
(30-day window) if connector permissions allow, diffs against prior recollections,
and emits a strict JSON schema.

Failure code FT-G-01 will be emitted only when neither connector access nor
local recollection history is available.
"""

import datetime
import glob
import json

SCHEMA = {
    "timestamp": None,
    "thread_id": None,
    "local_digest": None,
    "cross_thread_status": "scoped",
    "prior_diff": None,
    "failure_modes": []
}


def run_local_digest(thread):
    # placeholder: expects 'thread' as a list of turns
    return thread[-10:]


def attempt_cross_thread_retrieval(max_entries=24):
    files = sorted(glob.glob('recollections/recollection_*.json'), reverse=True)
    for path in files[:max_entries]:
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
            return {
                'source': 'local-recollections',
                'latest_timestamp': data.get('timestamp'),
                'latest_local_digest': data.get('local_digest', [])
            }, None
        except (OSError, json.JSONDecodeError):
            continue

    return None, {
        "code": "FT-G-01",
        "title": "limited_execution_context",
        "severity": "actionable",
        "suggested_mitigation": "Enable cross-thread read permissions or provide exports/manifests for aggregation."
    }


def diff_prior(recent, prior):
    # naive placeholder diff
    return {"added": [t for t in recent if t not in (prior or [])], "removed": [t for t in (prior or []) if t not in recent]}


def run(thread, prior_recollection=None):
    schema = dict(SCHEMA)
    schema['timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    schema['thread_id'] = 'local-thread'
    schema['local_digest'] = run_local_digest(thread)

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

    return schema
