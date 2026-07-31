#!/usr/bin/env python3
"""Validate and export SOPHY scenario YAML files.

Produces a self-contained export bundle containing source YAML, normalized JSON,
human-readable Markdown, and a portable SHA-256 manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml


REQUIRED_KEYS = {"title", "purpose", "mode", "actors", "constraints"}
STRING_FIELDS = ("title", "purpose", "mode")
STRING_LIST_FIELDS = {
    "constraints",
    "research_questions",
    "scene_sequence",
    "stop_conditions",
    "end_state_labels",
}
META_KEYS = {"title", "version", "mode", "purpose"}
PREFERRED_SECTIONS = [
    "status",
    "tone",
    "privacy",
    "constraints",
    "core_premise",
    "assumptions",
    "actors",
    "system_model",
    "interaction_rules",
    "research_questions",
    "independent_variables",
    "recommended_scene_sequence",
    "scene_sequence",
    "measurements",
    "evaluation_metrics",
    "success_conditions",
    "failure_modes",
    "stop_conditions",
    "outputs",
    "end_state_labels",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_scenario(data: dict[str, Any], path: Path) -> None:
    missing = REQUIRED_KEYS - set(data)
    if missing:
        raise ValueError(f"{path}: missing required keys: {sorted(missing)}")

    for key in STRING_FIELDS:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{path}: {key!r} must be a non-empty string")

    if not isinstance(data.get("actors"), dict) or not data["actors"]:
        raise ValueError(f"{path}: 'actors' must be a non-empty mapping")

    for key in STRING_LIST_FIELDS:
        if key not in data:
            continue
        value = data[key]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"{path}: {key!r} must be a list of strings")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    validate_scenario(data, path)
    return data


def scalar_text(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def bullet_values(value: Any, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                lines.append(f"{prefix}- **{key}:**")
                lines.extend(bullet_values(child, indent + 1))
            else:
                lines.append(f"{prefix}- **{key}:** {scalar_text(child)}")
        return lines

    if isinstance(value, list):
        lines: list[str] = []
        for child in value:
            if isinstance(child, dict):
                # Render mappings directly so list items never become blank dashes.
                lines.extend(bullet_values(child, indent))
            elif isinstance(child, list):
                lines.extend(bullet_values(child, indent + 1))
            else:
                lines.append(f"{prefix}- {scalar_text(child)}")
        return lines

    return [f"{prefix}- {scalar_text(value)}"]


def ordered_sections(data: dict[str, Any]) -> list[str]:
    preferred = [key for key in PREFERRED_SECTIONS if key in data]
    remaining = sorted(key for key in data if key not in META_KEYS and key not in preferred)
    return preferred + remaining


def render_markdown(data: dict[str, Any], source: Path) -> str:
    lines = [
        f"# {data['title']}",
        "",
        f"- **Version:** {data.get('version', 'legacy/unspecified')}",
        f"- **Mode:** {data['mode']}",
        f"- **Source:** `source/{source.name}`",
        "",
        "## Purpose",
        "",
        data["purpose"],
    ]

    for key in ordered_sections(data):
        heading = key.replace("_", " ").title()
        lines.extend(["", f"## {heading}", ""])
        value = data[key]
        if isinstance(value, (dict, list)):
            lines.extend(bullet_values(value))
        else:
            lines.append(scalar_text(value))

    lines.append("")
    return "\n".join(lines)


def export_one(source: Path, out_dir: Path) -> list[Path]:
    data = load_yaml(source)
    stem = source.stem
    source_dir = out_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_copy = source_dir / source.name
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"

    shutil.copy2(source, source_copy)
    json_path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(data, source), encoding="utf-8")
    return [source_copy, json_path, md_path]


def write_manifest(paths: list[Path], out_dir: Path) -> Path:
    manifest = out_dir / "manifest.sha256"
    unique_paths = sorted(set(paths), key=lambda path: path.relative_to(out_dir).as_posix())
    manifest.write_text(
        "".join(
            f"{sha256(path)}  {path.relative_to(out_dir).as_posix()}\n"
            for path in unique_paths
        ),
        encoding="utf-8",
    )
    return manifest


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

    out_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []
    for path in scenario_paths:
        exported.extend(export_one(path, out_dir))
    write_manifest(exported, out_dir)
    print(f"Exported {len(scenario_paths)} scenario(s) to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
