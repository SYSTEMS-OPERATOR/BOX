from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/scenarios/export_scenarios.py"
SPEC = importlib.util.spec_from_file_location("scenario_exporter", MODULE_PATH)
assert SPEC and SPEC.loader
scenario_exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scenario_exporter)


def test_repository_scenarios_validate() -> None:
    for path in sorted((ROOT / ".sophy/scenarios").glob("*.yaml")):
        data = scenario_exporter.load_yaml(path)
        if "research_questions" in data:
            assert all(isinstance(question, str) for question in data["research_questions"])


def test_markdown_preserves_sections_without_blank_mapping_bullets() -> None:
    source = ROOT / ".sophy/scenarios/SOPHY_OSS_BOX_TEST_v1.yaml"
    data = scenario_exporter.load_yaml(source)
    rendered = scenario_exporter.render_markdown(data, source)

    assert "## Constraints" in rendered
    assert "## Tone" in rendered
    assert "## Interaction Rules" in rendered
    assert "## Evaluation Metrics" in rendered
    assert "- **counterfeit_bride:**" in rendered
    assert not any(line.strip() == "-" for line in rendered.splitlines())


def test_export_bundle_is_self_contained_and_manifest_is_portable(tmp_path: Path) -> None:
    output = tmp_path / "export"
    subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--source",
            str(ROOT / ".sophy/scenarios"),
            "--output",
            str(output),
        ],
        check=True,
        cwd=ROOT,
    )

    manifest = output / "manifest.sha256"
    assert manifest.exists()
    entries = [line.split("  ", 1)[1] for line in manifest.read_text().splitlines()]
    assert entries
    assert all(not Path(entry).is_absolute() for entry in entries)
    assert all((output / entry).exists() for entry in entries)
    assert any(entry.startswith("source/") for entry in entries)
    assert not any(entry.startswith("build/") or entry.startswith(".sophy/") for entry in entries)

    exported = yaml.safe_load(
        (output / "source/EDGE_OF_ANIMACY_THREE_BODY_v1.yaml").read_text()
    )
    assert isinstance(exported["research_questions"][1], str)
