"""Recover a real manager constructor and test it with supplied SDK algorithms.

The test runs a newly linked component harness, never the input game executable.
Unverified exception helpers are test-only failure tripwires, not client replacements.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from export_character_analysis import WS, coff_function_records
from recover_character_layouts import operand
from verify_client_coff import directives


def main():
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    header = json.loads((WS/'inventory/character-header-recovery.json').read_text(encoding='utf-8'))
    stdio = json.loads((WS/'inventory/character-stdio-adapter.json').read_text(encoding='utf-8'))
    dx = json.loads((WS/'inventory/directx81b-sdk.json').read_text(encoding='utf-8'))
    work = WS/'work/recovered/character-legacy/managers'
    work.mkdir(parents=True, exist_ok=True)
    obj = WS/'work/character-reverse/member_06.obj'
    expected = json.loads((WS/'inventory/character-codeview.json').read_text(encoding='utf-8'))['objects'][5]['sha256']
    if hashlib.sha256(obj.read_bytes()).hexdigest() != expected:
        raise ValueError('Constructor evidence object changed')
    function = coff_function_records(obj.read_bytes())['?AddPartToMM@ChInterface@@QAEXPAD@Z']
    for at, offset in [(0x40, 4), (0x43, 8), (0x46, 12), (0x49, 16)]:
        if operand(function, at, bytes.fromhex('8970'), 1) != offset:
            raise ValueError('Inlined constructor field evidence changed')
    animation_obj = WS/'work/character-reverse/member_05.obj'
    animation_expected = json.loads((WS/'inventory/character-codeview.json').read_text(encoding='utf-8'))['objects'][4]['sha256']
    if hashlib.sha256(animation_obj.read_bytes()).hexdigest() != animation_expected:
        raise ValueError('Animation initialization evidence object changed')
    animation_init = coff_function_records(animation_obj.read_bytes())['?Init@AnimationManager@@QAEHXZ']
    if animation_init['bytes'] != bytes.fromhex('c7411000000000c7411401000000c3'):
        raise ValueError('Animation initialization instructions changed')
    includes = WS/header['header']
    if hashlib.sha256(includes.read_bytes()).hexdigest() != header['header_sha256']:
        raise ValueError('Recovered header changed')
    for key, hash_key in [('adapted_archive', 'adapted_archive_sha256'), ('adapter_library', 'adapter_library_sha256')]:
        if hashlib.sha256((WS/stdio[key]).read_bytes()).hexdigest() != stdio[hash_key]:
            raise ValueError('Stdio-adapted SDK/adapter changed')
    sources = ['character_recovered_managers.cpp', 'test_character_recovered_managers.cpp']
    hashes = {}
    for name in sources:
        source = WS/'scripts/native'/name
        shutil.copyfile(source, work/name)
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    logs = WS/'artifacts/character-managers'
    logs.mkdir(parents=True, exist_ok=True)
    log = logs/'build.txt'
    dev = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    options = f'/nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /I"{includes.parent}" /external:I"{WS/dx["include_overlay"]}" /external:W0'
    batch = work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl {options} /c character_recovered_managers.cpp /Fomanagers.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:CharacterRecoveredManagers.lib managers.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl {options} /D_CRT_SECURE_NO_WARNINGS test_character_recovered_managers.cpp CharacterRecoveredManagers.lib "{WS/stdio['adapted_archive']}" "{WS/stdio['adapter_library']}" "{Path(dx['sdk_root'])/'lib/d3dx8.lib'}" kernel32.lib user32.lib gdi32.lib advapi32.lib winmm.lib legacy_stdio_definitions.lib /Femanagers-probe.exe /link /NODEFAULTLIB:libci.lib >> "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if result.returncode:
        raise RuntimeError(f'Manager harness build failed: {log}')
    if '/DEFAULTLIB:"LIBCMT"' not in directives((work/'managers.obj').read_bytes()):
        raise ValueError('Manager constructor is not x86 /MT')
    test = subprocess.run([str(work/'managers-probe.exe')], cwd=work, capture_output=True,
                          timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    if test.returncode:
        (logs/'failure.txt').write_bytes(test.stdout+test.stderr)
        raise RuntimeError(f'Manager runtime verification failed ({test.returncode}): {logs/"failure.txt"}')
    evidence = json.loads(test.stdout)
    output = work/'CharacterRecoveredManagers.lib'
    report = {'architecture': 'x86', 'runtime': '/MT', 'library': output.relative_to(WS).as_posix(),
              'library_sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'source_sha256': hashes,
              'constructor_evidence_object_sha256': expected, 'constructor_evidence_function': '?AddPartToMM@ChInterface@@QAEXPAD@Z',
              'constructor_function_offsets': ['0x40', '0x43', '0x46', '0x49'], 'rva': None,
              'animation_initialization': {'object_sha256': animation_expected,
                  'function': '?Init@AnimationManager@@QAEHXZ', 'file_offset': hex(animation_init['file_offset']),
                  'function_bytes': animation_init['bytes'].hex(), 'rva': None,
                  'construction': 'Owned empty-vector reconstruction plus supplied Init, not recovered original inline constructor',
                  'singleton': 'No undocumented static m_AManager assignment introduced'},
              'sdk_archive_sha256': stdio['adapted_archive_sha256'], 'header_sha256': header['header_sha256'],
              'native_test': evidence, 'input_game_exe_execution': False,
              'limit': 'Ordinary object/animation manager operations on unloaded records; mesh/device/file loaders, DeleteAnimation(name), exception paths and 455 parity unverified.',
              'test_only_aliases': 'Missing _Xlen/_Xran fail the test if reached; absent from delivered manager library and client settings.'}
    (WS/'inventory/character-managers.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: reconstructed object/animation managers, {evidence["checks_passed"]} checks using real old manager routines.')


if __name__ == '__main__':
    main()
