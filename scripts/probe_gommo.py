"""Read-only MCP handshake/tools/status audit via GoMMO's documented stdio bridge.

Does not read or persist authentication tokens, launch game clients, or edit assets.
The bridge may open Studio if Studio is not already running.
"""
import json
import queue
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def probe():
    paths = json.loads((ROOT / "config/paths.json").read_text(encoding="utf-8"))
    process = subprocess.Popen(
        [paths["gommo"], "-mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    responses = queue.Queue()

    def read():
        for line in process.stdout:
            try:
                responses.put(json.loads(line))
            except json.JSONDecodeError:
                pass
        responses.put(None)

    threading.Thread(target=read, daemon=True).start()
    serial = 0

    def send(method, params, notification=False):
        nonlocal serial
        serial += 1
        packet = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            packet["id"] = serial
        process.stdin.write(json.dumps(packet) + "\n")
        process.stdin.flush()
        if notification:
            return None
        # A fixed overall deadline prevents unrelated notifications extending the wait.
        import time
        deadline = time.monotonic() + 25
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"MCP timeout: {method}")
            result = responses.get(timeout=remaining)
            if result is None:
                raise RuntimeError("MCP bridge closed stdout")
            if result.get("id") == serial:
                if "error" in result:
                    raise RuntimeError(f"MCP error for {method}: {result['error']}")
                return result["result"]

    try:
        initialized = send("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "rf-workflow-audit", "version": "0.1"},
        })
        send("notifications/initialized", {}, notification=True)
        tools = []
        params = {}
        while True:
            page = send("tools/list", params)
            tools.extend(page.get("tools", []))
            if not page.get("nextCursor"):
                break
            params = {"cursor": page["nextCursor"]}
        status_tool = next((t for t in tools if t["name"] == "studio_status"), None)
        status = None
        if status_tool and not status_tool.get("inputSchema", {}).get("required"):
            status = send("tools/call", {"name": "studio_status", "arguments": {}})
        report = {
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "transport": "stdio", "server": initialized, "tool_count": len(tools),
            "tools": tools, "studio_status": status,
        }
        destination = ROOT / "inventory/gommo-mcp.json"
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"server": initialized.get("serverInfo"), "tool_count": len(tools),
                          "studio_status": status.get("structuredContent") if status else None},
                         ensure_ascii=False, indent=2))
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()  # Only the bridge process started above, never the GUI.
            process.wait(timeout=5)


if __name__ == "__main__":
    probe()
