"""Bounded static IDA smoke test. Never executes the input game/server binary."""
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = json.loads((ROOT / "config/paths.json").read_text(encoding="utf-8"))
work = ROOT / "work/ida-smoke"
work.mkdir(parents=True, exist_ok=True)
source = Path(paths["legacy_source"]) / "RF Server Side/RF_Server/RF_Bin/LoginServerSR.exe"
copy = work / source.name
shutil.copy2(source, copy)
runtime_report = ROOT / "inventory/ida-runtime.json"
if runtime_report.exists():
    # Do not let an earlier successful report hide a failed new run.
    runtime_report.unlink()
log_path = work / "ida.log"
if log_path.exists():
    log_path.unlink()
command = [paths["idat"], "-A", "-c", f"-o{work / 'smoke.i64'}",
           f"-L{work / 'ida.log'}", f"-S{ROOT / 'scripts/ida_smoke.py'}", str(copy)]
report = {"observed_at_utc": datetime.now(timezone.utc).isoformat(),
          "input_copy": str(copy), "timeout_seconds": 45}
with (work / "console.log").open("wb") as output:
    try:
        completed = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                                   timeout=45, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        report["exit_code"] = completed.returncode
    except subprocess.TimeoutExpired:
        report["timed_out"] = True
report["runtime_report_created"] = runtime_report.exists()
if log_path.exists():
    log = log_path.read_text(encoding="utf-8", errors="replace")
    report["python_runtime_load_failed"] = "failed to load Python runtime" in log
    report["hexrays_plugin_loaded"] = "Hex-Rays Decompiler plugin has been loaded" in log
    report["input_loaded"] = "has been successfully loaded into the database" in log
report["success"] = report.get("exit_code") == 0 and runtime_report.exists()
(ROOT / "inventory/ida-probe.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
if runtime_report.exists():
    print(runtime_report.read_text(encoding="utf-8"))
raise SystemExit(0 if report["success"] else 1)
