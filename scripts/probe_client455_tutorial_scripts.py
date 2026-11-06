"""Build the source-owned SCP library; verify real files and bounded failures.

The ordinary client/Tutorial runtime is deliberately not claimed by this probe.
It does not relink the unchanged production client or rerun its existing suites.
"""
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path

from compare_client_binaries import WS, pe
from audit_client455_tutorial_scripts import fixed_size, inspect
from coff_references import parse


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(max_text=False):
    # Independent Python packing, including nonzero serialized padding, embedded
    # NUL/DBCS bytes, and different outer selectors vs stored data type bytes.
    result = bytearray(struct.pack('<II64sH', 1, 0x12345678, bytes(range(64)), 1 if max_text else 47))
    for selector in ([0] if max_text else range(47)):
        result += bytes([selector])
        if selector < 4:
            result += struct.pack('<BHI3BIIIB', selector ^ 0x80, 1000 + selector,
                                  0x87654321, 1, 50, 255, 0x10203040, 0x01020304,
                                  0x80ff0080, 1 if max_text else 2)
            texts = [bytes(i % 256 for i in range(65535))] if max_text else [b'\0\x81\x40\xffA', b'']
            for index, text in enumerate(texts):
                result += bytes((selector + index + i * 13) % 256 for i in range(12))
                result += struct.pack('<H', len(text)) + text
        else:
            size = fixed_size(selector)
            data = bytearray((selector * 17 + i * 23) % 256 for i in range(size))
            data[0] = selector ^ 0x80
            struct.pack_into('<H', data, 2, 1000 + selector)
            result += data
    return bytes(result)


def main():
    reference_path = WS / 'inventory/client455-tutorial-scripts-reference.json'
    ref = json.loads(reference_path.read_text())
    if ref['script_sha256'] != sha(WS / 'scripts/audit_client455_tutorial_scripts.py'):
        raise ValueError('Refresh the SCP reference audit')
    root = WS / 'work/client455-port/tutorial-scripts-probe'
    root.mkdir(parents=True, exist_ok=True)
    native = WS / 'scripts/native'
    source = native / 'client455_tutorial_script.cpp'
    probe = native / 'client455_tutorial_script_probe.cpp'
    header = native / 'client455_tutorial_script.h'
    obj, probe_obj = root / 'script.obj', root / 'probe.obj'
    library, exe = root / 'RF455TutorialScripts.lib', root / 'tutorial-scripts-probe.exe'
    log, map_file = root / 'build.txt', exe.with_suffix('.map')
    info = json.loads((WS / 'inventory/msvc-verification.json').read_text())
    dev = Path(info['installation_path']) / 'Common7/Tools/VsDevCmd.bat'
    batch = root / 'build.cmd'
    lines = ['@echo off', f'call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1',
             'if errorlevel 1 exit /b 1',
             f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /I"{native}" "{source}" /Fo"{obj}" > "{log}" 2>&1',
             'if errorlevel 1 exit /b 1',
             f'lib /nologo /OUT:"{library}" "{obj}" >> "{log}" 2>&1',
             'if errorlevel 1 exit /b 1',
             f'cl /c /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /I"{native}" "{probe}" /Fo"{probe_obj}" >> "{log}" 2>&1',
             'if errorlevel 1 exit /b 1',
             f'link /nologo /SUBSYSTEM:CONSOLE /MACHINE:X86 /OUT:"{exe}" /MAP:"{map_file}" "{probe_obj}" "{library}" kernel32.lib >> "{log}" 2>&1',
             'exit /b %errorlevel%']
    batch.write_text('\n'.join(lines) + '\n', encoding='ascii')
    build = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=root,
                           creationflags=subprocess.CREATE_NO_WINDOW, timeout=90)
    if build.returncode:
        raise ValueError(f'Tutorial script native build: {log}')
    parse(obj.read_bytes())  # Rejects a non-x86 COFF.
    parent = WS / 'work/m9' / sha(exe)[:8]
    parent.mkdir(parents=True, exist_ok=True)
    index = 1
    while (parent / f'tutorial-scripts-{index:03d}').exists():
        index += 1
    run = parent / f'tutorial-scripts-{index:03d}'
    run.mkdir()
    target = run / exe.name
    shutil.copyfile(exe, target)
    copied = []
    for row in ref['inputs']:
        original, path = Path(row['file']), run / row['relative']
        if sha(original) != row['sha256']:
            raise ValueError('Changed client SCP input')
        for prefix in ['', 'roundtrip', 'semantic']:
            (run / prefix / row['relative']).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, path)
        copied.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path)})
    (run / 'inputs.txt').write_text(''.join(row['relative'] + '\n' for row in ref['inputs']), encoding='ascii')
    (run / 'all47.scp').write_bytes(fixture())
    (run / 'max-text.scp').write_bytes(fixture(True))
    generic = next(row for row in ref['other_inputs'] if row['relative'] == 'DataTable/ko-kr/Tutorial.scp')
    if sha(Path(generic['file'])) != generic['sha256']:
        raise ValueError('Changed unselected generic script')
    shutil.copyfile(generic['file'], run / 'unselected-Tutorial.scp')
    result = subprocess.run([str(target)], cwd=run, capture_output=True, timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    (run / 'console.txt').write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise ValueError(f'Tutorial script native runtime {result.returncode}: {run}')
    output = run / 'result.json'
    actual = json.loads(output.read_text())
    roundtrips = []
    semantics = []
    for row in ref['inputs']:
        raw = Path(row['file']).read_bytes()
        path = run / 'roundtrip' / row['relative']
        semantic = run / 'semantic' / row['relative']
        if path.read_bytes() != raw or sha(semantic) != row['layout']['semantic_sha256']:
            raise ValueError('C++ field/roundtrip mismatch: ' + row['relative'])
        roundtrips.append({'file': path.relative_to(WS).as_posix(), 'sha256': sha(path)})
        semantics.append({'file': semantic.relative_to(WS).as_posix(), 'sha256': sha(semantic)})
    if sha(run / 'all47.semantic') != inspect(fixture())['semantic_sha256']:
        raise ValueError('Synthetic 47-selector semantic mismatch')
    expected = {'files': len(ref['inputs']),
                'quests': sum(r['layout']['quest_count'] for r in ref['inputs']),
                'instructions': sum(r['layout']['instructions'] for r in ref['inputs']),
                'texts': sum(r['layout']['strings'] for r in ref['inputs']),
                'text_bytes': sum(r['layout']['string_bytes'] for r in ref['inputs'])}
    if any(actual[key] != value for key, value in expected.items()):
        raise ValueError('Native/Python SCP totals differ')
    if actual['selectors'] != [ref['selectors'].get(str(i), 0) for i in range(47)]:
        raise ValueError('Native/Python selector counts differ')
    report = {'scope': 'Source-owned SCP library and wire model; not yet ordinary Tutorial integration',
              'architecture': 'x86', 'entry_rva': hex(pe(exe.read_bytes())['entry_rva']),
              'script_sha256': sha(Path(__file__)), 'reference_sha256': sha(reference_path),
              'sources': {p.name: sha(p) for p in [source, header, probe]},
              'library': {'file': library.relative_to(WS).as_posix(), 'sha256': sha(library)},
              'object': {'file': obj.relative_to(WS).as_posix(), 'sha256': sha(obj)},
              'exe': {'file': target.relative_to(WS).as_posix(), 'sha256': sha(target)},
              'map': {'file': map_file.relative_to(WS).as_posix(), 'sha256': sha(map_file)},
              'build_log': {'file': log.relative_to(WS).as_posix(), 'sha256': sha(log)},
              'output': {'file': output.relative_to(WS).as_posix(), 'sha256': sha(output)},
              'inputs': copied, 'roundtrips': roundtrips, 'semantics': semantics,
              'fixtures': [{'file': p.relative_to(WS).as_posix(), 'sha256': sha(p)}
                           for p in [run / 'all47.scp', run / 'all47.semantic', run / 'max-text.scp',
                                     run / 'inputs.txt', run / 'unselected-Tutorial.scp']],
              'native': actual, 'semantic_fields_match_independent_python': True,
              'normal_client_relinked': False, 'normal_client_functionality_changed': False,
              'natural_exit': result.returncode, 'input_exe_executed': False,
              'server_modified': False, 'M6': 'OPEN', 'M6F': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-tutorial-scripts-native.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(actual))


if __name__ == '__main__':
    main()
