#!/usr/bin/env python3
"""Generate a deterministic recollection artifact in ``recollections/``."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path("recollections")


def build_payload(summary: str = "Automated recollection run") -> dict[str, str]:
    """Build a recollection payload using an RFC3339 UTC timestamp."""
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "recollection_time": timestamp,
        "summary": summary,
    }


def write_recollection(payload: dict[str, str], output_dir: Path = OUTPUT_DIR) -> Path:
    """Write payload to ``output_dir`` and return created path.

    Dev Agent Breadcrumb: Filename is timestamp-derived to keep generated files
    sortable and easy to diff in follow-up recollection runs.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_timestamp = payload["recollection_time"].replace(":", "-")
    out_path = output_dir / f"recollection_{safe_timestamp}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    """CLI entrypoint for local/manual recollection generation."""
    payload = build_payload()
    out_path = write_recollection(payload)
    print(f"wrote recollection {payload['recollection_time']} -> {out_path}")


if __name__ == "__main__":
    main()
