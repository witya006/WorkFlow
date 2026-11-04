"""Verify installed IDA MCP on a copy; --catalog-only skips binary analysis."""
import argparse
import hashlib
import json
import shutil
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from mcp_stdio import StdioMCP

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--catalog-only", action="store_true")
parser.add_argument("--configured", action="store_true", help="Use the registered user Codex MCP command")
args = parser.parse_args()
verification_path = ROOT / "inventory/ida-mcp-verification.json"
if not args.catalog_only and verification_path.exists():
    verification_path.unlink()  # A failed new run must not leave stale success evidence.
python = ROOT / "local/ida-mcp-venv/Scripts/python.exe"
command = [str(python), "-m", "ida_pro_mcp.idalib_supervisor", "--stdio"]
if args.configured:
    config = tomllib.loads((Path.home() / ".codex/config.toml").read_text(encoding="utf-8"))
    registered = config["mcp_servers"]["ida_mcp"]
    command = [registered["command"], *registered.get("args", [])]
client = StdioMCP(command,
                  ROOT / "local/ida-mcp-probe.log")
database = None
try:
    server = client.request("initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "rf-workflow-audit", "version": "0.2"},
    })
    client.request("notifications/initialized", notification=True)
    tools = client.request("tools/list")["tools"]
    report = {"observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "transport": "stdio", "server": server,
              "tool_count": len(tools), "tools": tools}
    (ROOT / "inventory/ida-mcp-tools.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"server": server.get("serverInfo"), "tool_count": len(tools)}, indent=2), flush=True)
    if not args.catalog_only:
        target=json.loads((ROOT/'config/client-target.json').read_text(encoding='utf-8'))
        source=ROOT/'work/client-reference/reference-backup/RF_Online.bin'
        source_idb=source.with_suffix('.bin.i64')
        work = ROOT / "work/ida-mcp-smoke/client455"
        work.mkdir(parents=True, exist_ok=True)
        binary = work / source.name
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest!=target['secondary_reference']['sha256']:raise RuntimeError('Pinned455 smoke input changed')
        if binary.exists() and hashlib.sha256(binary.read_bytes()).hexdigest() != digest:
            raise RuntimeError("Existing smoke input differs; refusing to overwrite it")
        if not binary.exists():
            shutil.copy2(source, binary)
        cached=binary.with_suffix('.bin.i64')
        if not cached.exists():shutil.copyfile(source_idb,cached)
        print("Opening working copy through MCP...", flush=True)
        opened = client.call("idb_open", {"input_path": str(cached), "mode": "force_headless", "run_auto_analysis":False,"build_caches":False,"init_hexrays":True})
        if not opened.get("success"):
            raise RuntimeError(opened)
        database = opened["session"]["session_id"]
        health = client.call("server_health", {"database": database})
        listed = client.call("list_funcs", {"database": database, "queries": {"count": 10}})
        pages = listed["result"] if isinstance(listed, dict) else listed
        functions = pages[0]["data"]
        if not functions:
            raise RuntimeError("Function listing is empty")
        sample = None
        for function in functions:
            size = function.get("size", 0)
            size = int(size, 0) if isinstance(size, str) else size
            if 64 <= size <= 1024:
                candidate = client.call("decompile", {"database": database, "addr": function["addr"], "max_lines": 100})
                if candidate.get("code"):
                    sample = {"function": function, "decompilation": candidate}
                    break
        if sample is None:
            raise RuntimeError("No nontrivial function was decompiled")
        result = {"observed_at_utc": datetime.now(timezone.utc).isoformat(), "success": True,
                  "input_path": str(binary), "input_sha256": digest,
                  "used_registered_codex_config": args.configured,
                  "open": opened, "health": health, "listed_function_count": len(functions),
                  "function_listing_scope":"first10,page only;not total function count","next_offset":pages[0].get('next_offset'),
                  "functions": functions, "sample": sample,
                  "sample_rva": hex(int(sample["function"]["addr"], 0) - int(health["imagebase"], 0))}
        closed = client.call("idb_close", {"database": database, "save": True})
        result["close"] = closed
        if not closed.get("success"):
            raise RuntimeError(closed)
        database = None
        verification_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"success": True, "functions": len(functions), "health": health,
                          "sample": sample, "close": closed}, ensure_ascii=False, indent=2), flush=True)
finally:
    if database:
        try:
            client.call("idb_close", {"database": database, "save": False})
        except Exception:
            pass
    client.close()
