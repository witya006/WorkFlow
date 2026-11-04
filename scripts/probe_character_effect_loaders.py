"""Exercise actual old pattern/item parsers with isolated FILE adaptation.

No original game executable is run. No test-only exception substitutions.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from compare_client_binaries import WS
from recover_character_effect_defaults import verify_default_evidence


def main():
    facts = verify_default_evidence()
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    stdio = json.loads((WS/'inventory/character-stdio-adapter.json').read_text(encoding='utf-8'))
    exceptions = json.loads((WS/'inventory/character-exceptions.json').read_text(encoding='utf-8'))
    exception_library = WS/exceptions['library']
    if hashlib.sha256(exception_library.read_bytes()).hexdigest() != exceptions['library_sha256']:
        raise ValueError('Exception support changed since verification')
    header = json.loads((WS/'inventory/character-header-recovery.json').read_text(encoding='utf-8'))
    dx = json.loads((WS/'inventory/directx81b-sdk.json').read_text(encoding='utf-8'))
    includes = WS/header['header']
    if hashlib.sha256(includes.read_bytes()).hexdigest() != header['header_sha256']:
        raise ValueError('Header changed since preflight')
    for file, digest in [('adapted_archive', 'adapted_archive_sha256'), ('adapter_library', 'adapter_library_sha256')]:
        if hashlib.sha256((WS/stdio[file]).read_bytes()).hexdigest() != stdio[digest]:
            raise ValueError('SDK/stdio adapter changed')
    work = WS/'work/recovered/character-legacy/effect-loaders'
    work.mkdir(parents=True, exist_ok=True)
    fixtures = {'patterns.txt': b'1 1 0 2 0 3 0 4 0 5\r\n2 0 0 0 0 0 0 0 0 0\r\n',
        'items.txt': b'10203040 1 2 2 2 2 2\r\nABCDEF01 1 2 2 2 2 2\r\n'}
    for name, data in fixtures.items():
        (work/name).write_bytes(data)
    source = WS/'scripts/native/test_character_effect_loaders.cpp'
    shutil.copyfile(source, work/source.name)
    logs = WS/'artifacts/character-effect-loaders'
    logs.mkdir(parents=True, exist_ok=True)
    log = logs/'build.txt'
    dev = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch = work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /I"{includes.parent}" /external:I"{WS/dx['include_overlay']}" /external:W0 "{source.name}" "{WS/stdio['adapted_archive']}" "{WS/stdio['adapter_library']}" "{exception_library}" "{Path(dx['sdk_root'])/'lib/d3dx8.lib'}" kernel32.lib user32.lib gdi32.lib advapi32.lib winmm.lib legacy_stdio_definitions.lib /Feeffect-loaders.exe /link /NODEFAULTLIB:libci.lib > "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    build = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if build.returncode:
        raise RuntimeError(f'Effect-loader test build failed: {log}')
    run = subprocess.run([str(work/'effect-loaders.exe')], cwd=work,
        capture_output=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    (logs/'result.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:
        raise RuntimeError(f'Effect-loader test failed ({run.returncode}): {logs/"result.txt"}')
    result = json.loads(run.stdout)
    report = {'architecture': 'x86', 'runtime': '/MT', 'native_test': result,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'executable_sha256': hashlib.sha256((work/'effect-loaders.exe').read_bytes()).hexdigest(),
        'header_sha256': header['header_sha256'], 'sdk_archive_sha256': stdio['adapted_archive_sha256'],
        'adapter_library_sha256': stdio['adapter_library_sha256'],
        'exception_library_sha256': exceptions['library_sha256'], 'test_only_aliases': False,
        'fixtures': {name: hashlib.sha256(data).hexdigest() for name, data in fixtures.items()},
        'default_argument_facts': facts, 'input_game_exe_execution': False,
        'limit': 'Valid bounded synthetic pattern/item inputs; malformed old-loader inputs, effect-file loading, rendering and 455 behavior parity unverified.'}
    (WS/'inventory/character-effect-loaders.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: two actual SDK text loaders, {result["checks_passed"]} effect-query/default checks.')


if __name__ == '__main__':
    main()
