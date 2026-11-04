"""Compile the reconstructed declarations and diagnose a real client translation unit.

No link, loading or execution; unresolved inline implementations remain explicit.
"""
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def declaration_probe(contracts):
    lines = ['#include "Character.h"']
    expected = set()
    for entry in contracts:
        if entry['declaration'].startswith(('private:', 'protected:')):
            continue  # Not addressable by a client; access is preserved in the header.
        declaration = re.sub(r'^(public|private|protected): ', '', entry['declaration'])
        if '`' in declaration:
            continue
        static = declaration.startswith('static ')
        declaration = declaration.removeprefix('static ')
        match = re.fullmatch(r'(.*?)\b(__thiscall|__cdecl)\s+([A-Za-z_]\w*(?:::(?:~?\w+|operator=))?)\((.*)\)', declaration)
        if not match or not match[1].strip():
            continue  # Constructors/destructors cannot be addressed in C++ source.
        result, convention, name, arguments = match.groups()
        owner = name.split('::')[0] if '::' in name else None
        if owner and not static:
            pointer = f'{result} (__thiscall {owner}::*)({arguments})'
        else:
            pointer = f'{result} ({convention}*)({arguments})'
        lines.append(f'auto contract_{len(expected)} = static_cast<{pointer}>(&{name});')
        expected.add(entry['mangled'].encode('ascii'))
    return '\n'.join(lines)+'\n', expected


def main():
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    work = WS/'work/recovered/character-legacy'
    header = work/'include/Character.h'
    manifest_path = WS/'inventory/character-header-recovery.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if hashlib.sha256(header.read_bytes()).hexdigest() != manifest['header_sha256']:
        raise ValueError('Header differs from generated manifest')
    probe = work/'header_probe.cpp'
    contracts = json.loads((WS/'inventory/character-public-contracts.json').read_text(encoding='utf-8'))['contracts']
    probe_source, expected = declaration_probe(contracts)
    probe_source += 'CRender& render() { return CRender::GetRender(); }\n'
    probe.write_text(probe_source, encoding='ascii')
    dx = WS/'local/directx81b/include-overlay'
    batch = work/'header_probe.cmd'
    log = WS/'artifacts/character-header-compile.txt'
    env = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch.write_text(f'''@echo off
call "{env}" -no_logo -arch=x86 -host_arch=x64 > header-env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /c /std:c++14 /W4 /WX /EHsc /MT /I"{work/'include'}" /external:I"{dx}" /external:W0 "{probe}" /Foheader_probe.obj > "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    run = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if run.returncode:
        print(log.read_text(encoding='utf-8', errors='replace')[:6500])
        raise RuntimeError('Header compile failed')
    dumpbin = Path(verified['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    symbols = subprocess.check_output([str(dumpbin), '/symbols', str(work/'header_probe.obj')])
    refs = set(re.findall(rb'UNDEF[^\r\n]+\| (\?[^\s]+)', symbols))
    if not expected <= refs:
        raise ValueError(f'Native decorated signatures differ: {expected-refs}')
    manifest['native_verification'] = {'compile_exit': 0, 'architecture': 'x86',
        'decorated_references_matched': sorted(x.decode('ascii') for x in expected),
        'probe_obj_sha256': hashlib.sha256((work/'header_probe.obj').read_bytes()).hexdigest(),
        'executed': False}
    # This compile uses the real, unchanged working client file. It is diagnostic only.
    rf = WS/'work/client-build/source/RF_Client'
    engine = WS/'work/client-build/source/R3Engine'
    includes = [work/'include', dx, rf, engine, *[engine/x for x in ['extension','1stclass','2ndclass','common','d3d/include']]]
    options = ' '.join(f'/I"{p}"' for p in includes)
    # Keep source-migration diagnostics separate from recovered binary declarations.
    shim = work/'diagnostic_std.hpp'
    shim.write_text('#include <winsock2.h>\n#include <windows.h>\n#include <tchar.h>\n#include "dxutil.h"\n#include <list>\n#include <queue>\n#include <map>\n#include <vector>\n#include <string>\nusing namespace std;\n', encoding='ascii')
    client_log = WS/'artifacts/character-global-compile.txt'
    batch.write_text(f'''@echo off
call "{env}" -no_logo -arch=x86 -host_arch=x64 > header-env.txt 2>&1
if errorlevel 1 exit /b 1
set VSLANG=1033
cl /nologo /c /std:c++14 /W3 /EHsc /MT /Zc:forScope- /DWIN32 /DNDEBUG /D_WINDOWS /D_MBCS /D_NEW_UI_ /FI"{shim}" {options} "{rf/'global.cpp'}" /Foglobal_probe.obj > "{client_log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    text = client_log.read_text(encoding='utf-8', errors='replace')
    manifest['client_global_diagnostic'] = {'compile_exit': result.returncode,
        'error_counts': dict(collections.Counter(re.findall(r'(?:fatal )?error (C\d+)', text))),
        'missing_Character_h': 'C1083' in text and 'Character.h' in text,
        'source_sha256': hashlib.sha256((rf/'global.cpp').read_bytes()).hexdigest(),
        'forced_std_compatibility': 'Diagnostic only: legacy unqualified STL names exposed in separate forced header',
        'diagnostic_std_sha256': hashlib.sha256(shim.read_bytes()).hexdigest(),
        'new_ui': 'Enabled for this diagnostic: present in original Debug flags; current item classes are guarded by it',
        'log': client_log.relative_to(WS).as_posix()}
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: header/layout compile and {len(expected)} decorated symbol references match supplied library.')
    print(json.dumps(manifest['client_global_diagnostic'], indent=2))
    print('\n'.join(x for x in text.splitlines() if 'error C' in x)[:4200])


if __name__ == '__main__':
    main()
