"""Small synchronous JSON-lines MCP client for reproducible local checks."""
import json
import queue
import subprocess
import threading
import time


class StdioMCP:
    def __init__(self, command, log, env=None):
        self.stderr = open(log, "ab")
        self.process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.stderr,
            text=True, encoding="utf-8", env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        self.responses = queue.Queue()
        self.serial = 0
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.process.stdout:
            try:
                packet = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(packet, dict):
                self.responses.put(packet)
        self.responses.put(None)

    def request(self, method, params=None, timeout=120, notification=False):
        self.serial += 1
        packet = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if not notification:
            packet["id"] = self.serial
        self.process.stdin.write(json.dumps(packet) + "\n")
        self.process.stdin.flush()
        if notification:
            return
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(method)
            try:
                result = self.responses.get(timeout=remaining)
            except queue.Empty as error:
                raise TimeoutError(method) from error
            if result is None:
                raise RuntimeError(f"MCP exited during {method}; see local stderr log")
            if result.get("id") == self.serial:
                if "error" in result:
                    raise RuntimeError(result["error"])
                return result["result"]

    def call(self, name, arguments):
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise RuntimeError(result)
        content = result.get("structuredContent")
        if content is None:
            for block in result.get("content", []):
                if block.get("type") == "text":
                    try:
                        content = json.loads(block["text"])
                    except json.JSONDecodeError:
                        continue
                    break
        if isinstance(content, dict) and content.get("error"):
            raise RuntimeError(content["error"])
        return content if content is not None else result

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=5)
        self.stderr.close()
