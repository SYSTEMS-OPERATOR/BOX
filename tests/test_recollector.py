import json
import tempfile
import os
import subprocess


def test_recollector_runs_and_outputs():
    tmpdir = tempfile.mkdtemp()
    sample = [{"thread_id":"t1","last_updated":"2026-03-01T00:00:00Z","summary":"sample thread"}]
    infile = os.path.join(tmpdir, "in.json")
    with open(infile, "w") as f:
        json.dump(sample, f)
    outdir = os.path.join(tmpdir, "out")
    os.makedirs(outdir)

    # Run the recollector in dry-run mode
    subprocess.run(["python", "tools/recollector/run_recollection.py", "--in", infile, "--out", outdir, "--dry-run"], check=True)

    summary_path = os.path.join(outdir, "recollection_summary.json")
    assert os.path.exists(summary_path), "recollection_summary.json not created"
    with open(summary_path, "r") as f:
        summary = json.load(f)
    assert summary.get("threads_processed") == 1
