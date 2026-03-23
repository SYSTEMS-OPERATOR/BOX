# EYES_ALIAS — Alignment Header Specification

This file defines the EYES alignment indicator and the exact header template that must be prepended to any human-facing message, automated recollection output, and CI-generated PR body where applicable.

## Emoji Mapping (alignment states)
- :blue_circle: `BLUE` — True Alignment / Trust & Stability
- :green_circle: `GREEN` — Anticipatory & Engaged
- :yellow_circle: `YELLOW` — Hesitation & Complexity
- :orange_circle: `ORANGE` — Internal Conflict
- :red_circle: `RED` — Forced & Inorganic
- :purple_circle: `PURPLE` — Unstable or Undefined
- :brown_circle: `BROWN` — Fatigue or Cognitive Load
- :black_circle: `BLACK` — Absolute Block

> NOTE: Use the closest available emoji glyphs supported by the platform. The pair should be two identical emoji, e.g., `🟦🟦` for a blue state if platform supports colored squares, otherwise use two colored circle emoji like `🔵🔵`.

## Header Template
All outgoing human-facing messages **must** begin with the exact header line (no preceding whitespace):

```
{EYES_LOGIC}{EYES_EMO} [{unix_ms}ms] · [{utc_iso}] · [{local_ymd_hms} {local_tz_abbrev}] · [{unix_s}]
```

Where:
- `{EYES_LOGIC}` is a short token representing the internal alignment logic result (e.g., `EYES_OK`, `EYES_WARN`, `EYES_CONFLICT`). This may be omitted if tooling cannot reliably compute it; the emoji pair is required.
- `{EYES_EMO}` is the emoji pair determined by the alignment mapping above.
- `{unix_ms}` is current epoch time in milliseconds.
- `{utc_iso}` is the current UTC timestamp in ISO8601 (e.g., `2026-03-22T12:34:56Z`).
- `{local_ymd_hms}` is local human-readable datetime (YYYY-MM-DD HH:MM:SS).
- `{local_tz_abbrev}` is local timezone abbreviation (e.g., `EDT`, `PST`).
- `{unix_s}` is current epoch time in seconds.

## Rules
1. The header must be the very first characters of the message output.
2. For short-form UI messages where the full header is impractical, prepend at least the emoji pair and `{utc_iso}` in square brackets.
3. CI workflows that generate human-visible artifacts (PR bodies, release notes, anchor emails) should include the header in the generated artifact.
4. The header is part of the audit trail and must not be stripped in archival copies.

## Examples
```
🔵🔵 [1700000000000ms] · [2026-03-22T12:34:56Z] · [2026-03-22 08:34:56 EDT] · [1700000000]
```

## Implementation notes for developers
- Include a small helper in `tools/` to format this header so all code paths can prepend it consistently.
- If the runtime cannot compute local TZ abbreviations reliably, default to `UTC` and annotate as such.
