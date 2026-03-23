import importlib.util
from pathlib import Path

RECOLLECT_PATH = Path(__file__).resolve().parent.parent / "tools" / "recollect.py"
SPEC = importlib.util.spec_from_file_location("recollect", RECOLLECT_PATH)
recollect = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(recollect)


def test_write_recollection_creates_file(tmp_path):
    payload = recollect.build_payload("unit-test")

    out_path = recollect.write_recollection(payload, output_dir=tmp_path)

    assert out_path.exists()
    assert out_path.parent == tmp_path
    assert "recollection_" in out_path.name
