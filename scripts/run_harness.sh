#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=${DRY_RUN:-true}
OUTPUT_DIR=${OUTPUT_DIR:-outputs}

mkdir -p "$OUTPUT_DIR"

echo "Running agent.clockwork harness (dry_run=$DRY_RUN)"

# Simulate reading threads (create a sample file)
cat > "$OUTPUT_DIR/sample_threads.json" <<'JSON'
[
  {"thread_id":"t1","last_updated":"2026-03-19T12:00:00Z","summary":"Test thread 1"},
  {"thread_id":"t2","last_updated":"2026-03-20T09:00:00Z","summary":"Test thread 2"}
]
JSON

# Run recollector (if present)
if [ -x "tools/recollector/run_recollection.py" ] || [ -f "tools/recollector/run_recollection.py" ]; then
  echo "Found recollector; running"
  python tools/recollector/run_recollection.py --in "$OUTPUT_DIR/sample_threads.json" --out "$OUTPUT_DIR" --dry-run
else
  echo "No recollector found; generating sample outputs"
  cat > "$OUTPUT_DIR/recollection_summary.json" <<'JSON'
{
  "generated_at":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "threads_processed":2,
  "summary":"Sample recollection generated (dry run)"
}
JSON
  cat > "$OUTPUT_DIR/recollection_anchor.yaml" <<'YAML'
---
id: sample-anchor-$(date -u +%s)
timestamp_utc: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
root_hash: "samplehash"
summary: "Sample anchor"
signed_by: agent.clockwork
YAML
fi

if [ "$DRY_RUN" = "false" ]; then
  echo "Committing outputs to a branch and opening PR (simulated)"
  # This is a simulation in the harness; real run uses agent process
fi

echo "Harness complete. Outputs in $OUTPUT_DIR"
