# SOPHY Hourly Recollection

This branch contains the SOPHY_HOURLY_RECOLLECTION harness and scheduler config.

## Purpose
- Deterministic hourly recollection pass
- Cross-thread retrieval (30d) — scoped: limited by execution context access
- Local thread digest (last 10 turns)
- Prior recollection diffing
- Strict output schema with timestamps and explicit failure modes

## Notes
- Some operations require cross-thread read and persistent write access; if unavailable, the harness will record failure code `FT-G-01` and proceed with scoped recollections.
