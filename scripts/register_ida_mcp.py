"""Register the already-tested IDA MCP command, preserving unrelated Codex config."""
import shutil
import tomllib
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = Path.home() / ".codex/config.toml"
addition = (root / "config/ida-mcp.toml").read_text(encoding="utf-8")
desired = tomllib.loads(addition)["mcp_servers"]["ida_mcp"]
old = target.read_text(encoding="utf-8")
parsed = tomllib.loads(old)
existing = parsed.get("mcp_servers", {}).get("ida_mcp")
if existing is not None:
    if existing != desired:
        raise SystemExit("ida_mcp already has a different configuration; no changes made")
    print("IDA MCP registration already matches.")
else:
    updated = old.rstrip() + "\n\n" + addition
    after = tomllib.loads(updated)
    assert after["mcp_servers"].pop("ida_mcp") == desired
    assert after == parsed, "Unrelated configuration changed"
    backup = root / "local/ida-mcp-install/before"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup / ("codex-config-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".toml"))
    with target.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(updated)
    assert tomllib.loads(target.read_text(encoding="utf-8"))["mcp_servers"]["ida_mcp"] == desired
    print("Registered ida_mcp in user Codex config; previous configuration backed up locally.")
