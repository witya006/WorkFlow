"""Compile recovered GPU declarations and compare their native representation."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    verified = json.loads((WS / 'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    work = WS / 'work/recovered/character455'
    devcmd = Path(verified['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    log = WS / 'artifacts/recovered-vertex-build.txt'
    batch = work / 'probe.cmd'
    batch.write_text(f'''@echo off
call "{devcmd}" -no_logo -arch=x86 -host_arch=x64 > env-init.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /EHsc /std:c++17 /W4 probe.cpp /Feprobe.exe > "{log}" 2>&1
if errorlevel 1 exit /b 1
probe.exe > observed.bin
exit /b %errorlevel%
''', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if result.returncode:
        raise RuntimeError(f'Native build/probe failed; see {log}')
    observed = (work / 'observed.bin').read_bytes()
    expected = (work / 'expected.bin').read_bytes()
    if observed != expected:
        raise ValueError('Native vertex declaration bytes differ from recovered records')
    exe = (work / 'probe.exe').read_bytes()
    pe = struct.unpack_from('<I', exe, 0x3c)[0]
    if struct.unpack_from('<H', exe, pe+4)[0] != 0x14c:
        raise ValueError('Expected x86 probe')
    report_path = WS / 'inventory/character455-vertex-layouts.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    report['native_verification'] = {'exit_code': result.returncode, 'declaration_bytes_compared': len(observed),
                                     'equal': True, 'header_sha256': hashlib.sha256((work / 'vertex_declarations.hpp').read_bytes()).hexdigest(),
                                     'probe_sha256': hashlib.sha256(exe).hexdigest(), 'probe_architecture': 'x86',
                                     'probe_entry_rva': hex(struct.unpack_from('<I', exe, pe+24+16)[0])}
    report_path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('PASS: x86 native structures and 96 declaration bytes match recovered records.')


if __name__ == '__main__':
    main()
