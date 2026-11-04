"""Link-only ABI experiment for one recovered symbol from the supplied VC6 library.

The output is not loaded or executed. It does not substitute a Character header.
"""
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def main():
    verified = json.loads((WS / 'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    work = WS / 'work/character-reverse/link-probe'
    work.mkdir(parents=True, exist_ok=True)
    library = WS / 'work/client-build/source/RF_Client/CharacterMR.lib'
    source = work / 'probe.cpp'
    source.write_text('''class CHARACTEROBJECT;
class ChInterface {
public:
    float GetAlpha(CHARACTEROBJECT*);
};
extern "C" __declspec(dllexport) float call_alpha(ChInterface* iface, CHARACTEROBJECT* object) {
    return iface->GetAlpha(object);
}
''', encoding='ascii')
    devcmd = Path(verified['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    batch = work / 'probe.cmd'
    log = WS / 'artifacts/character-link-probe.txt'
    batch.write_text(f'''@echo off
call "{devcmd}" -no_logo -arch=x86 -host_arch=x64 > env-init.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /LD /MT /EHsc probe.cpp "{library}" kernel32.lib user32.lib gdi32.lib advapi32.lib winmm.lib libucrt.lib libvcruntime.lib legacy_stdio_definitions.lib "{WS / 'local/directx81b/extracted/DX8.1b SDK/DXF/DXSDK/lib/d3dx8.lib'}" /link /NOENTRY /MACHINE:X86 /OPT:REF /NODEFAULTLIB:libci.lib /OUT:probe.dll > "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    run = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    text = log.read_bytes().decode('utf-8', errors='replace')
    errors = collections.Counter(re.findall(r'(?:error|fatal error) (LNK\d+|C\d+)', text))
    unresolved = []
    for line in text.splitlines():
        if 'error LNK2019:' not in line and 'error LNK2001:' not in line:
            continue
        decorated = re.search(r'\((\?[A-Za-z0-9_?$@]+)\)', line)
        if decorated:
            unresolved.append(decorated[1])
        else:
            match = re.search(r'error LNK(?:2019|2001):.*? ([?_][A-Za-z0-9_?$@]+)(?=[\s.,])', line)
            if match:
                unresolved.append(match[1])
    unresolved = sorted(set(unresolved))
    report = {'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(), 'architecture': 'x86',
              'symbol': '?GetAlpha@ChInterface@@QAEMPAVCHARACTEROBJECT@@@Z', 'link_exit': run.returncode,
              'loaded_or_executed': False, 'error_counts': dict(errors), 'unresolved_identifiers': unresolved,
              'diagnostic_switch': 'Excluded missing SDK default libci.lib only in this link probe; explicit modern CRT supplied. No unresolved-symbol errors suppressed.',
              'limit': 'One prototype-only link probe, no layout or runtime compatibility established.'}
    output = work / 'probe.dll'
    if run.returncode == 0:
        report['output_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    (WS / 'inventory/character-link-probe.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
