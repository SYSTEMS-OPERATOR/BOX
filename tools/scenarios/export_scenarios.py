#!/usr/bin/env python3
"""Validate and export SOPHY scenario YAML files.

Creates normalized JSON, Markdown summaries, and a SHA-256 manifest without
copying private legal identities into generated output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_KEYS = {"title", "purpose", "mode", "actors", "constraints"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    missing = REQUIRED_KEYS - set(data)
    if missing:
        raise ValueError(f"{path}: missing required keys: {sorted(missing)}")
    return data


def bullet_values(value: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                lines.append(f"{prefix}- **{key}**")
                lines.extend(bullet_values(child, indent + 1))
            else:
                lines.append(f"{prefix}- **{key}:** {child}")
        return lines
    if isinstance(value, list):
        lines = []
        for child in value:
            if isinstance(child, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(bullet_values(child, indent + 1))
            else:
                lines.append(f"{prefix}- {child}")
        return lines
    return [f"{prefix}- {value}"]


def render_markdown(data: dict[str, Any], source: Path) -> str:
    title = str(data["title"])
    lines = [
        f"# {title}",
        "",
        f"- **Version:** {data.get('version', 'legacy/unspecified')}",
        f"- **Mode:** {data.get('mode', 'unspecified')}",
        f"- **Source:** `{source.as_posix()}`",
        "",
        "## Purpose",
        "",
        str(data.get("purpose", "")),
    ]
    preferred = [
        "core_premise",
        "actors",
        "system_model",
        "research_questions",
        "independent_variables",
        "scene_sequence",
        "measurements",
        "success_conditions",
        "failure_modes",
        "stop_conditions",
        "outputs",
        "end_state_labels",
    ]
    for key in preferred:
        if key not in data:
            continue
        heading = key.replace("_", " ").title()
        lines.extend(["", f"## {heading}", ""])
        lines.extend(bullet_values(data[key]))
    lines.append("")
    return "\n".join(lines)


def export_one(source: Path, out_dir: Path) -> list[Path]:
    data = load_yaml(source)
    stem = source.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"
    json_path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(data, source), encoding="utf-8")
    return [source, json_path, md_path]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=".sophy/scenarios")
    parser.add_argument("--output", default="build/scenario-export")
    args = parser.parse_args()

    source_dir = Path(args.source)
    out_dir = Path(args.output)
    scenario_paths = sorted(source_dir.glob("*.yaml"))
    if not scenario_paths:
        raise SystemExit(f"No scenario YAML files found in {source_dir}")

    exported: list[Path] = []
    for path in scenario_paths:
        exported.extend(export_one(path, out_dir))

    manifest = out_dir / "manifest.sha256"
    unique_paths = sorted(set(exported), key=lambda p: p.as_posix())
    manifest.write_text(
        "".join(f"{sha256(path)}  {path.as_posix()}\n" for path in unique_paths),
        encoding="utf-8",
    )
    print(f"Exported {len(scenario_paths)} scenario(s) to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
