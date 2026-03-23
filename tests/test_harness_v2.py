import importlib.util
import json
from pathlib import Path


HARNESS_V2_PATH = Path(__file__).resolve().parent.parent / 'sophy_hourly_recollection' / 'harness_v2.py'
SPEC = importlib.util.spec_from_file_location('harness_v2', HARNESS_V2_PATH)
harness_v2 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(harness_v2)


def test_run_marks_cross_thread_available_when_history_exists(tmp_path, monkeypatch):
    recollections = tmp_path / 'recollections'
    recollections.mkdir()
    seed = {
        'timestamp': '2026-03-23T04:06:40.013623Z',
        'thread_id': 'local-thread',
        'local_digest': [
            'user requested SOPHY_HOURLY_RECOLLECTION',
            'recent: PR merged into BOX'
        ]
    }
    (recollections / 'recollection_2026-03-23T04-06-40.013623Z.json').write_text(
        json.dumps(seed),
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    schema, outpath = harness_v2.run(['recent: PR merged into BOX'])

    assert schema['cross_thread_status'] == 'available'
    assert schema['failure_modes'] == []
    assert schema['cross_thread_data']['source'] == 'local-recollections'
    assert Path(outpath).exists()


def test_run_keeps_failure_mode_when_no_history(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    schema, _ = harness_v2.run(['just one local event'])

    assert schema['cross_thread_status'] == 'unavailable'
    assert schema['failure_modes']
    assert schema['failure_modes'][0]['code'] == 'FT-G-01'
