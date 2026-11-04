"""Read-only inventory: hash all legacy files and selected reference binaries.

Game/server trees get metadata summaries only, not a claim of complete hash backup.
"""
import hashlib
import json
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def describe(path, base):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    result = {"path": path.relative_to(base).as_posix(), "bytes": path.stat().st_size,
              "sha256": digest.hexdigest()}
    with path.open("rb") as stream:
        if stream.read(2) == b"MZ":
            stream.seek(0x3C)
            offset_data = stream.read(4)
            if len(offset_data) == 4:
                stream.seek(struct.unpack("<I", offset_data)[0])
                if stream.read(4) == b"PE\0\0":
                    machine = struct.unpack("<H", stream.read(2))[0]
                    result["pe_machine"] = hex(machine)
                    result["architecture"] = {0x14C: "x86", 0x8664: "x64"}.get(machine, "other")
    return result


def main():
    paths = json.loads((ROOT / "config/paths.json").read_text(encoding="utf-8"))
    output = ROOT / "inventory"
    output.mkdir(exist_ok=True)
    summary = {"observed_at_utc": datetime.now(timezone.utc).isoformat(), "roots": {}}
    for name in ("legacy_source", "client_455", "server_bundle"):
        base = Path(paths[name])
        files = sorted(p for p in base.rglob("*") if p.is_file() and ".git" not in p.parts)
        summary["roots"][name] = {"path": str(base), "file_count": len(files),
            "bytes": sum(p.stat().st_size for p in files),
            "extensions": dict(Counter(p.suffix.lower() for p in files).most_common())}
        if name == "legacy_source":
            records = [describe(p, base) for p in files]
            (output / "legacy-files.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    selected = {
        "client_455": ["RF_Online.bin", "RF_Online.bin.2026-10-18_12-15-42.backup", "RF.exe"],
        "server_bundle": ["server/windows/gameserver.exe", "client/rflauncher.exe"],
    }
    binaries = []
    for name, relatives in selected.items():
        for relative in relatives:
            path = Path(paths[name]) / relative
            if path.is_file():
                binaries.append({"root": name, **describe(path, Path(paths[name]))})
            else:
                binaries.append({"root": name, "path": relative, "missing": True})
    for filename, data in (("roots.json", summary), ("reference-binaries.json", binaries)):
        (output / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
