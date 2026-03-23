import importlib.util
import json
from pathlib import Path

HARNESS_PATH = Path(__file__).resolve().parent.parent / "sophy_hourly_recollection" / "harness.py"
SPEC = importlib.util.spec_from_file_location("harness", HARNESS_PATH)
harness = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(harness)


def test_run_local_digest_normalizes_and_limits():
    thread = [
        " a ",
        {"b": 1, "a": 2},
        3,
    ] * 4
    digest = harness.run_local_digest(thread, limit=3)

    assert len(digest) == 3
    assert digest[0] == "a"
    assert digest[1] == '{"a": 2, "b": 1}'
    assert digest[2] == "3"


def test_run_uses_recollection_time_fallback(tmp_path, monkeypatch):
    recollections = tmp_path / "recollections"
    recollections.mkdir()
    seed = {
        "recollection_time": "2026-03-23T10:00:00Z",
        "local_digest": ["historic"],
    }
    (recollections / "recollection_2026-03-23T10-00-00Z.json").write_text(
        json.dumps(seed),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    schema = harness.run(["historic", "new"])

    assert schema["cross_thread_status"] == "available"
    assert schema["cross_thread_data"]["latest_timestamp"] == "2026-03-23T10:00:00Z"
    assert schema["prior_diff"]["added"] == ["new"]
