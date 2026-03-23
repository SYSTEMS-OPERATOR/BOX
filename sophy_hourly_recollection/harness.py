"""SOPHY Hourly Recollection Harness.

This deterministic harness computes a local digest, attempts to enrich context
from previous recollection artifacts, and returns a strict schema payload.
"""

from __future__ import annotations

import datetime
import glob
import json
from typing import Any

SCHEMA = {
    "timestamp": None,
    "thread_id": None,
    "local_digest": None,
    "cross_thread_status": "scoped",
    "prior_diff": None,
    "failure_modes": [],
}


def _normalize_event(event: Any) -> str:
    """Normalize an event into a single-line string for deterministic diffs."""
    if isinstance(event, str):
        return event.strip()
    if isinstance(event, dict):
        try:
            return json.dumps(event, sort_keys=True)
        except TypeError:
            return str(event)
    return str(event)


def run_local_digest(thread: list[Any], limit: int = 10) -> list[str]:
    """Return a compact digest from the latest thread items.

    Dev Agent Breadcrumb: Normalize and trim turns so downstream diff logic
    stays stable even if thread events are mixed types.
    """
    normalized = [_normalize_event(event) for event in thread]
    return [item for item in normalized if item][-limit:]


def attempt_cross_thread_retrieval(max_entries: int = 24) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    """Load recent recollection files and return latest digest context.

    Dev Agent Breadcrumb: We scan newest-first and stop at the first readable
    file to keep this call fast and deterministic in CI.
    """
    files = sorted(glob.glob("recollections/recollection_*.json"), reverse=True)
    for path in files[:max_entries]:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return {
                "source": "local-recollections",
                "latest_timestamp": data.get("timestamp") or data.get("recollection_time"),
                "latest_local_digest": data.get("local_digest", []),
            }, None
        except (OSError, json.JSONDecodeError):
            continue

    return None, {
        "code": "FT-G-01",
        "title": "limited_execution_context",
        "severity": "actionable",
        "suggested_mitigation": (
            "Enable cross-thread read permissions or provide exports/manifests "
            "for aggregation."
        ),
    }


def diff_prior(recent: list[str], prior: list[str] | None) -> dict[str, list[str]]:
    """Return deterministic added/removed entries between recent and prior."""
    prior = prior or []

    # Dev Agent Breadcrumb: set-based membership avoids O(n^2) behavior.
    prior_set = set(prior)
    recent_set = set(recent)
    return {
        "added": [item for item in recent if item not in prior_set],
        "removed": [item for item in prior if item not in recent_set],
    }


def run(thread: list[Any], prior_recollection: list[str] | None = None) -> dict[str, Any]:
    """Execute recollection workflow and return the schema payload."""
    schema = dict(SCHEMA)
    schema["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )
    schema["thread_id"] = "local-thread"
    schema["local_digest"] = run_local_digest(thread)

    cross, err = attempt_cross_thread_retrieval()
    if cross is None:
        schema["cross_thread_status"] = "unavailable"
        schema["failure_modes"].append(err)
    else:
        schema["cross_thread_status"] = "available"
        schema["cross_thread_data"] = cross

    effective_prior = prior_recollection
    if effective_prior is None and cross is not None:
        effective_prior = cross.get("latest_local_digest", [])
    schema["prior_diff"] = diff_prior(schema["local_digest"], effective_prior)

    return schema
