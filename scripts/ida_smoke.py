"""Executed inside IDA only, on work/ida-smoke/LoginServerSR.exe."""
import json
import hashlib
import sys
from pathlib import Path

import ida_auto
import ida_funcs
import ida_hexrays
import ida_nalt
import ida_pro
import idaapi
import idautils

root = Path(__file__).resolve().parents[1]
report = {"ida_version": idaapi.get_kernel_version(), "input": ida_nalt.get_input_file_path()}
report["python_version"] = sys.version
report["input_sha256"] = hashlib.sha256(Path(report["input"]).read_bytes()).hexdigest()
exit_code = 0
try:
    ida_auto.auto_wait()
    report["function_count"] = ida_funcs.get_func_qty()
    report["hexrays_initialized"] = bool(ida_hexrays.init_hexrays_plugin())
    report["decompilation_verified"] = False
    if report["hexrays_initialized"]:
        for address in list(idautils.Functions())[:20]:
            function = ida_hexrays.decompile(address)
            if function:
                report["decompilation_verified"] = True
                report["sample_rva"] = hex(address - ida_nalt.get_imagebase())
                break
    if not report["decompilation_verified"]:
        raise RuntimeError("Hex-Rays did not produce a verified decompilation")
except Exception as error:
    report["error"] = str(error)
    exit_code = 1
finally:
    (root / "inventory/ida-runtime.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    ida_pro.qexit(exit_code)
