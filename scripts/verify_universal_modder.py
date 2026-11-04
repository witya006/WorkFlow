"""Validate installed skills and exercise offline CLI discovery.

Run with the universal-modder uv tool interpreter and -X utf8.
Use --scan to also repeat the read-only RF client scan.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_PROFILE = Path.home()
parser = argparse.ArgumentParser()
parser.add_argument("--scan", action="store_true")
args = parser.parse_args()
revision = (ROOT / "local/universal-modder-install/commit.txt").read_text().strip()
source = ROOT / "local/universal-modder-install" / ("universal-modder-" + revision)
validator_path = USER_PROFILE / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"
spec = importlib.util.spec_from_file_location("skill_validation", validator_path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
skills = []
for skill in sorted((source / "skills").iterdir()):
    if not skill.is_dir():
        continue
    installed = USER_PROFILE / ".codex/skills" / skill.name
    valid, message = validator.validate_skill(installed)
    assert valid, f"{skill.name}: {message}"
    files = [p for p in skill.rglob("*") if p.is_file()]
    for path in files:
        relative = path.relative_to(skill)
        actual = installed / relative
        if skill.name == "game-recon" and relative.as_posix() == "SKILL.md":
            parts = path.read_text(encoding="utf-8").split("---", 2)
            parts[1] = parts[1].replace("<game>", "this game")
            assert actual.read_text(encoding="utf-8") == "---".join(parts)
        else:
            assert actual.read_bytes() == path.read_bytes(), str(actual)
    skills.append({"name": skill.name, "valid": True, "files_verified": len(files),
                   "skill_sha256": hashlib.sha256((installed / "SKILL.md").read_bytes()).hexdigest()})
um = USER_PROFILE / ".local/bin/um.exe"


def run(*arguments):
    result = subprocess.run([str(um), *arguments], capture_output=True, text=True,
                            encoding="utf-8", timeout=90, check=True)
    return result.stdout


cli_version = run("--version").strip()
assert "scan" in run("--help")
native_hits = json.loads(run("kb", "search", "native", "--limit", "2", "--json"))
assert native_hits, "Knowledge base query returned no results"
scan_path = ROOT / "inventory/universal-modder-rf-scan.json"
if args.scan:
    scan_path.write_text(run("scan", "E:/RFOnlineTrash/RFOnline", "--json"), encoding="utf-8")
scan = json.loads(scan_path.read_text(encoding="utf-8-sig"))
assert scan["name"] == "RFOnline" and scan["files_indexed"] > 0
report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "revision": revision,
          "source": str(source), "cli": str(um), "cli_version": cli_version,
          "source_archive_sha256": hashlib.sha256((source.parent / "source.zip").read_bytes()).hexdigest(),
          "packages": {name: version(name) for name in ("universal-modder", "numpy", "pillow", "pyyaml")},
          "skills": skills, "skill_count": len(skills), "all_valid": True,
          "local_adaptation": "game-recon description only: <game> -> this game",
          "kb_query_success": True, "scan_repeated_this_run": args.scan,
          "scan_report": str(scan_path.relative_to(ROOT)), "scan_files_indexed": scan["files_indexed"],
          "not_tested": ["paid asset generation", "game control", "video capture", "3D rendering", "publishing"]}
(ROOT / "inventory/universal-modder-installation.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"skills_valid": len(skills), "cli_version": cli_version,
                  "knowledge_base": "ok", "scan_files_indexed": scan["files_indexed"]}, indent=2))
