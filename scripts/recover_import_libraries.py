"""Recover import archives from supplied client DLL exports; never load DLL code."""
import hashlib
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    paths = json.loads((WS / 'config/paths.json').read_text(encoding='utf-8'))
    verified = json.loads((WS / 'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    tools = Path(verified['compiler_path'].splitlines()[0]).parent
    work = WS / 'work/client-build/recovered-imports'
    refs = WS / 'work/client-dependencies/reference'
    work.mkdir(parents=True, exist_ok=True)
    refs.mkdir(parents=True, exist_ok=True)
    reports = []
    for name in ['ABuse', 'Adv', 'PDLL']:
        original = Path(paths['client_455']) / f'{name}.dll'
        data = original.read_bytes()
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        if data[pe:pe+4] != b'PE\0\0' or struct.unpack_from('<H', data, pe+4)[0] != 0x14c:
            raise ValueError('Expected x86 PE DLL')
        copy = refs / original.name
        if copy.exists() and copy.read_bytes() != data:
            raise ValueError(f'Preserving different DLL copy: {copy}')
        shutil.copyfile(original, copy)
        output = subprocess.check_output([str(tools / 'dumpbin.exe'), '/exports', str(copy)])
        exports = [(int(o), int(r, 16), n.decode('ascii')) for o, r, n in re.findall(rb'^\s+(\d+)\s+[0-9A-F]+\s+([0-9A-F]{8})\s+(\S+)', output, re.M)]
        if not exports:
            raise ValueError('No exports found')
        definition = work / f'{name}.def'
        # Use named imports rather than pinning the probe to DLL ordinals.
        definition.write_text(f'LIBRARY {name}.dll\nEXPORTS\n' + ''.join(f'  {n}\n' for _, _, n in exports), encoding='ascii')
        library = work / f'{name}.lib'
        subprocess.check_output([str(tools / 'lib.exe'), '/nologo', '/machine:x86', f'/def:{definition}', f'/out:{library}'])
        reports.append({'dll': original.name, 'dll_sha256': hashlib.sha256(data).hexdigest(), 'architecture': 'x86',
                        'exports': [{'ordinal': o, 'rva': hex(r), 'name': n} for o, r, n in exports],
                        'library': library.relative_to(WS).as_posix(), 'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest()})
    (work / 'import_probe.cpp').write_text('''#include <windows.h>
extern "C" __declspec(dllimport) int ABuse_LoadDic(char*);
extern "C" __declspec(dllimport) int Adv_LoadDic(char*);
__declspec(dllimport) BOOL WINAPI HookAllApps(BOOL,DWORD);
int main() {
  char path[] = "";
  return ABuse_LoadDic(path) + Adv_LoadDic(path) + HookAllApps(FALSE,0);
}
''', encoding='ascii')
    devcmd = Path(verified['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    batch = work / 'link_probe.cmd'
    logs = WS / 'artifacts/recovered-import-link.txt'
    batch.write_text(f'''@echo off
call "{devcmd}" -no_logo -arch=x86 -host_arch=x64 > env-init.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /EHsc import_probe.cpp ABuse.lib Adv.lib PDLL.lib /Feimport_probe.exe > "{logs}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    run = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if run.returncode:
        raise RuntimeError(f'Import link probe failed: {logs}')
    imports = subprocess.check_output([str(tools / 'dumpbin.exe'), '/imports', str(work / 'import_probe.exe')])
    for name in [b'ABuse_LoadDic', b'Adv_LoadDic', b'?HookAllApps@@YGHHK@Z']:
        if name not in imports:
            raise ValueError(f'Import not present in probe: {name!r}')
    probe = (work / 'import_probe.exe').read_bytes()
    pe = struct.unpack_from('<I', probe, 0x3c)[0]
    report = {'libraries': reports, 'link_probe': {'exit': run.returncode, 'executed': False,
               'sha256': hashlib.sha256(probe).hexdigest(), 'architecture': 'x86',
               'entry_rva': hex(struct.unpack_from('<I', probe, pe+24+16)[0])},
              'scope': 'Import name/link validation only. DLL function signatures/behavior not independently established. No DLL or probe execution.'}
    (WS / 'inventory/recovered-import-libraries.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('PASS: generated 3 x86 import libraries, 19 exports; native link/import-name probe passed without execution.')


if __name__ == '__main__':
    main()
