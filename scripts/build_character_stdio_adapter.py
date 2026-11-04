"""Build/test classic FILE adapter and retarget only eight undefined COFF symbols.

Input archive/objects and their instruction/relocation bytes are not modified.
Only new ignored copies receive symbol table edits; no game EXE is run.
"""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from export_character_analysis import WS, coff_function_records
from verify_client_coff import directives

STREAMS = ('fopen', 'fclose', 'fgets', 'fread', 'fwrite', 'fscanf', 'fseek', 'ftell')
RENAMES = {'_'+name: '_rf_vc6_'+name for name in STREAMS}


def retarget_stdio(data):
    defined = coff_function_records(data)
    table, count = struct.unpack_from('<II', data, 8)
    strings = table+18*count
    length = struct.unpack_from('<I', data, strings)[0]
    if strings+length != len(data):
        raise ValueError('Expected a terminal, bounded COFF string table')
    result = bytearray(data)
    added = bytearray()
    changes = []
    index = 0
    while index < count:
        at = table+18*index
        section, _, storage, aux = struct.unpack_from('<hHBB', data, at+12)
        if data[at:at+4] == b'\0'*4:
            offset = struct.unpack_from('<I', data, at+4)[0]
            if not 4 <= offset < length:
                raise ValueError('Invalid external symbol string offset')
            end = data.find(b'\0', strings+offset, strings+length)
            if end < 0:
                raise ValueError('Unterminated external symbol name')
            name = data[strings+offset:end].decode('ascii')
        else:
            name = data[at:at+8].split(b'\0', 1)[0].decode('ascii')
        if section == 0 and storage == 2 and name in RENAMES:
            replacement = RENAMES[name]
            struct.pack_into('<II', result, at, 0, length+len(added))
            added.extend(replacement.encode('ascii')+b'\0')
            changes.append({'symbol_index': index, 'before': name, 'after': replacement})
        index += 1+aux
    result.extend(added)
    struct.pack_into('<I', result, strings, length+len(added))
    result = bytes(result)
    if result[:table] != data[:table]:
        raise ValueError('Header/sections/relocations changed')
    after = coff_function_records(result)
    if defined.keys() != after.keys() or any(x['bytes'] != after[name]['bytes'] for name, x in defined.items()):
        raise ValueError('Public definition or function bytes changed')
    return result, changes


def main():
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    inputs = json.loads((WS/'inventory/character-codeview.json').read_text(encoding='utf-8'))
    work = WS/'work/recovered/character-legacy/stdio-adapter'
    work.mkdir(parents=True, exist_ok=True)
    files = ['character_legacy_stdio.h', 'character_legacy_stdio.cpp', 'test_character_legacy_stdio.cpp']
    source_hashes = {}
    for name in files:
        original = WS/'scripts/native'/name
        data = original.read_bytes()
        (work/name).write_bytes(data)
        source_hashes[name] = hashlib.sha256(data).hexdigest()
    (work/'malformed.txt').write_bytes(b'name nope\n')
    if (work/'missing-does-not-exist.bin').exists():
        raise ValueError('Unexpected missing-file test fixture')
    objects = []
    all_renamed = set()
    for index, item in enumerate(inputs['objects'], 1):
        raw = (WS/item['working_object']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('Original COFF digest changed')
        output, changes = retarget_stdio(raw)
        path = work/f'character_{index:02d}.obj'
        path.write_bytes(output)
        all_renamed.update(x['before'] for x in changes)
        objects.append({'input_sha256': item['sha256'], 'output_sha256': hashlib.sha256(output).hexdigest(),
                        'object': path.relative_to(WS).as_posix(), 'renames': changes,
                        'instructions_and_relocations_unchanged': True})
    if all_renamed != RENAMES.keys():
        raise ValueError('Observed stdio surface differs from the eight inspected APIs')
    dev = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    logs = WS/'artifacts/character-stdio-adapter'
    logs.mkdir(parents=True, exist_ok=True)
    log = logs/'build.txt'
    batch = work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /c /MT /O2 /EHsc /W4 /WX character_legacy_stdio.cpp /Foadapter.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:CharacterLegacyStdio.lib adapter.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:CharacterMR-stdio.lib character_*.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_character_legacy_stdio.cpp CharacterLegacyStdio.lib /Festdio-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    run = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work)
    if run.returncode:
        raise RuntimeError(f'Adapter build failed: {log}')
    if '/DEFAULTLIB:"LIBCMT"' not in directives((work/'adapter.obj').read_bytes()):
        raise ValueError('Adapter is not x86 /MT')
    test = subprocess.run([str(work/'stdio-probe.exe')], cwd=work, capture_output=True)
    if test.returncode:
        (logs/'test-failure.txt').write_bytes(test.stdout+test.stderr)
        raise RuntimeError(f'Adapter test failed ({test.returncode}): {logs/"test-failure.txt"}')
    evidence = json.loads(test.stdout)
    original = WS/'work/client-build/source/RF_Client/CharacterMR.lib'
    if hashlib.sha256(original.read_bytes()).hexdigest() != inputs['sha256']:
        raise ValueError('Original archive changed')
    provider = json.loads((WS/'inventory/vc6-stdio-probe.json').read_text(encoding='utf-8'))
    report = {'architecture': 'x86', 'runtime': '/MT', 'rva': None,
        'original_archive_sha256': inputs['sha256'], 'source_sha256': source_hashes,
        'adapted_archive': (work/'CharacterMR-stdio.lib').relative_to(WS).as_posix(),
        'adapted_archive_sha256': hashlib.sha256((work/'CharacterMR-stdio.lib').read_bytes()).hexdigest(),
        'adapter_library': (work/'CharacterLegacyStdio.lib').relative_to(WS).as_posix(),
        'adapter_library_sha256': hashlib.sha256((work/'CharacterLegacyStdio.lib').read_bytes()).hexdigest(),
        'objects': objects, 'stream_api_surface': list(STREAMS), 'native_test': evidence,
        'classic_provider_hash_file': provider['classic_hash_file'],
        'classic_provider_sha256': hashlib.sha256(Path(provider['classic_hash_file']).read_bytes()).hexdigest(),
        'input_game_exe_execution': False,
        'limits': ['Adapter API and COFF edits verified; no original game execution.',
                   'Old Character loaders/containers/constructors/exceptions are not runtime-verified by these tests.']}
    (WS/'inventory/character-stdio-adapter.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: eight stream APIs; {evidence["checks_passed"]} native checks; ten COFF objects preserve instructions/relocations.')


if __name__ == '__main__':
    main()
