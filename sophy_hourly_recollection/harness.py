"""
SOPHY Hourly Recollection Harness

This is a deterministic harness template. It runs a local digest over the
current conversation thread (last 10 turns), attempts cross-thread retrieval
(30-day window) if connector permissions allow, diffs against prior recollections,
and emits a strict JSON schema.

Failure code FT-G-01 will be emitted if the environment prevents full cross-thread
reads or persistent write access.
"""

import json
import datetime

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


def attempt_cross_thread_retrieval():
    # In this environment, cross-thread reads are not guaranteed.
    # Return None and mark FT-G-01 if not available.
    return None, {"code": "FT-G-01", "title": "limited_execution_context", "severity": "actionable"}


def diff_prior(recent, prior):
    # naive placeholder diff
    return {"added": [t for t in recent if t not in (prior or [])], "removed": [t for t in (prior or []) if t not in recent]}


def run(thread, prior_recollection=None):
    schema = dict(SCHEMA)
    schema['timestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'
    schema['thread_id'] = 'local-thread'
    schema['local_digest'] = run_local_digest(thread)

    cross, err = attempt_cross_thread_retrieval()
    if cross is None:
        schema['cross_thread_status'] = 'unavailable'
        schema['failure_modes'].append(err)
    else:
        schema['cross_thread_status'] = 'available'
        schema['cross_thread_data'] = cross

    schema['prior_diff'] = diff_prior(schema['local_digest'], prior_recollection)

    return schema
