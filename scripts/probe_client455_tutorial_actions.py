"""Build/test source-owned QBI execution core; the production host is still open."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from compare_client_binaries import WS, pe
from coff_references import parse
from probe_client455_tutorial_scripts import fixture


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ref_path = WS / 'inventory/client455-tutorial-actions-reference.json'
    reference = json.loads(ref_path.read_text())
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_tutorial_actions.py'):
        raise ValueError('Refresh runtime reference first')
    root = WS / 'work/client455-port/tutorial-actions-probe'
    root.mkdir(parents=True, exist_ok=True)
    native = WS / 'scripts/native'
    names = ['client455_tutorial_script.cpp', 'client455_tutorial_runtime.cpp', 'client455_tutorial_spatial.cpp', 'client455_tutorial_actions.cpp']
    probe = native / 'client455_tutorial_actions_probe.cpp'
    library, exe = root / 'RF455TutorialActions.lib', root / 'tutorial-actions-probe.exe'
    log, map_file = root / 'build.txt', exe.with_suffix('.map')
    info = json.loads((WS / 'inventory/msvc-verification.json').read_text())
    dev = Path(info['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    batch = root / 'build.cmd'
    lines = ['@echo off', f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1',
             'if errorlevel 1 exit /b 1']
    objects = []
    for index, name in enumerate(names + [probe.name]):
        obj = root / (Path(name).stem + '.obj')
        lines += [f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /I"{native}" "{native/name}" /Fo"{obj}" {">" if index==0 else ">>"} "{log}" 2>&1',
                  'if errorlevel 1 exit /b 1']
        objects.append(obj)
    lines += [f'lib /nologo /OUT:"{library}" ' + ' '.join(f'"{p}"' for p in objects[:-1]) + f' >> "{log}" 2>&1',
              'if errorlevel 1 exit /b 1',
              f'link /nologo /SUBSYSTEM:CONSOLE /MACHINE:X86 /OUT:"{exe}" /MAP:"{map_file}" "{objects[-1]}" "{library}" kernel32.lib >> "{log}" 2>&1',
              'exit /b %errorlevel%']
    batch.write_text('\n'.join(lines) + '\n', encoding='ascii')
    result = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=root,
                            creationflags=subprocess.CREATE_NO_WINDOW, timeout=90)
    if result.returncode:
        raise ValueError('QBI native build: ' + str(log))
    for obj in objects:
        parse(obj.read_bytes())
    parent = WS / 'work/m9' / sha(exe)[:8]
    parent.mkdir(parents=True, exist_ok=True)
    index = 1
    while (parent / f'tutorial-actions-{index:03d}').exists():
        index += 1
    run = parent / f'tutorial-actions-{index:03d}'
    run.mkdir()
    target = run / exe.name
    shutil.copyfile(exe, target)
    inputs = []
    for row in reference['inputs']:
        original = Path(row['file'])
        if sha(original) != row['sha256']:
            raise ValueError('Changed real tutorial file')
        dest = run / row['name']
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, dest)
        inputs.append({'file': dest.relative_to(WS).as_posix(), 'sha256': sha(dest)})
    (run/'inputs.txt').write_text(''.join(row['name']+'\n' for row in reference['inputs']),encoding='ascii')
    (run/'all47.scp').write_bytes(fixture())
    result = subprocess.run([str(target)], cwd=run, capture_output=True, timeout=25,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    (run / 'console.txt').write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError(f'QBI native runtime {result.returncode}: {run}: {result.stderr.decode(errors="replace")}')
    output = run / 'result.json'
    category_map = run / 'equip-map.bin'
    expected_map = next(row for row in reference['references'][0]['data'] if row['role'] == 'equip_slot_map')
    if category_map.read_bytes().hex() != expected_map['hex']:
        raise ValueError('Source item mapping differs from pinned 455 bytes')
    report = {'scope': 'QBI19to46 action rules and complete processor preparation with a recording host; actual UI/world Tutorial OPEN',
              'architecture': 'x86', 'entry_rva': hex(pe(exe.read_bytes())['entry_rva']),
              'sources': {name: sha(native/name) for name in names + [probe.name, 'client455_tutorial_script.h', 'client455_tutorial_runtime.h', 'client455_tutorial_spatial.h', 'client455_tutorial_actions.h', 'testing/client455_tutorial_recording_host.h', 'testing/client455_tutorial_actions_host.h']},
              'script_sha256': sha(Path(__file__)), 'reference_sha256': sha(ref_path),
              'library': library.relative_to(WS).as_posix(), 'library_sha256': sha(library),
              'objects': [{'file': p.relative_to(WS).as_posix(), 'sha256': sha(p)} for p in objects],
              'exe': {'file': target.relative_to(WS).as_posix(), 'sha256': sha(target)},
              'map': {'file': map_file.relative_to(WS).as_posix(), 'sha256': sha(map_file)},
              'build_log': {'file': log.relative_to(WS).as_posix(), 'sha256': sha(log)},
              'output': {'file': output.relative_to(WS).as_posix(), 'sha256': sha(output)},
              'inputs': inputs, 'equip_map': {'file': category_map.relative_to(WS).as_posix(), 'sha256': sha(category_map)},
              'fixtures': [{'file': p.relative_to(WS).as_posix(), 'sha256': sha(p)} for p in [run/'inputs.txt', run/'all47.scp']],
              'native': json.loads(output.read_text()), 'natural_exit': result.returncode,
              'normal_client_relinked': False, 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS/'inventory/client455-tutorial-actions-native.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['native']))


if __name__ == '__main__':
    main()
