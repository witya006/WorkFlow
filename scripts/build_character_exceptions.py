"""Reconstruct two VC6 string error helpers using observed exception contracts.

Compare own native functions to genuine installed classic DLL exports by type,
message and reference catches/rethrow. Complete old SDK unwinding is still open.
"""
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS, pe
from export_character_analysis import coff_function_records


def main():
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    provider = Path('C:/Windows/SysWOW64/msvcp60.dll')
    data = provider.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != '8d024f35eead1e0942aad24ecbf86cf72e3237f7c94eebb5a6a3a41f498dd139':
        raise ValueError('Inspected classic C++ provider changed; recheck exports and code')
    image = pe(data)

    def at(rva, size):
        section = next(s for s in image['sections'] if s['rva'] <= rva < s['rva']+s['raw_size'])
        offset = section['raw_offset']+rva-section['rva']
        return data[offset:offset+size]

    facts = []
    for name, rva, message_rva, text, ctor, throwinfo, throwcall in [
            ('_Xlen', 0x27010, 0x615c, b'string too long', 0xc0b0, 0x3bc98, 0x27046),
            ('_Xran', 0x27060, 0x616c, b'invalid string position', 0xc270, 0x3bcd4, 0x27096)]:
        if at(message_rva, len(text)+1) != text+b'\0':
            raise ValueError('Legacy error message changed')
        if at(rva+0x10, 5) != b'\x68'+struct.pack('<I', image['image_base']+message_rva):
            raise ValueError('Helper no longer references the inspected message')
        instruction = at(rva+0x28, 5)
        if instruction[0] != 0xe8 or rva+0x2d+struct.unpack_from('<i', instruction, 1)[0] != ctor:
            raise ValueError('Exception class constructor call changed')
        if at(rva+0x2d, 5) != b'\x68'+struct.pack('<I', image['image_base']+throwinfo):
            raise ValueError('Legacy throw descriptor changed')
        instruction = at(throwcall, 5)
        if instruction[0] != 0xe8 or throwcall+5+struct.unpack_from('<i', instruction, 1)[0] != 0x32680:
            raise ValueError('Legacy throw call changed')
        facts.append({'symbol': f'?{name}@std@@YAXXZ', 'rva': hex(rva),
            'exception_constructor_rva': hex(ctor), 'throwinfo_rva': hex(throwinfo),
            'throw_call_rva': hex(throwcall), 'message_rva': hex(message_rva), 'message': text.decode('ascii')})
    work = WS/'work/recovered/character-legacy/exceptions'
    work.mkdir(parents=True, exist_ok=True)
    sources = ['character_legacy_exceptions.cpp', 'test_character_legacy_exceptions.cpp']
    hashes = {}
    for name in sources:
        source = WS/'scripts/native'/name
        shutil.copyfile(source, work/name)
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    logs = WS/'artifacts/character-exceptions'
    logs.mkdir(parents=True, exist_ok=True)
    log = logs/'build.txt'
    dev = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch = work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /c character_legacy_exceptions.cpp /Foexceptions.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:CharacterLegacyExceptions.lib exceptions.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX test_character_legacy_exceptions.cpp CharacterLegacyExceptions.lib /Feexceptions-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''', encoding='ascii')
    if subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=work).returncode:
        raise RuntimeError(f'Exception helper build failed: {log}')
    definitions = coff_function_records((work/'exceptions.obj').read_bytes())
    if not {'?_Xlen@std@@YAXXZ', '?_Xran@std@@YAXXZ'} <= definitions.keys():
        raise ValueError('Required helper symbols not defined')
    if any('basic_string' in name for name in definitions):
        raise ValueError('Modern string COMDAT definitions could collide with old SDK')
    run = subprocess.run([str(work/'exceptions-probe.exe')], cwd=work, timeout=20,
        capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    (logs/'result.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:
        raise RuntimeError(f'Exception contract test failed ({run.returncode}): {logs/"result.txt"}')
    result = json.loads(run.stdout)
    pe_at = struct.unpack_from('<I', data, 0x3c)[0]
    if (result['provider_timestamp'], result['provider_image_size']) != (
            struct.unpack_from('<I', data, pe_at+8)[0], struct.unpack_from('<I', data, pe_at+24+56)[0]):
        raise ValueError('Loaded 32-bit provider metadata differs from the hashed SysWOW64 provider')
    library = work/'CharacterLegacyExceptions.lib'
    report = {'architecture': 'x86', 'runtime': '/MT', 'library': library.relative_to(WS).as_posix(),
        'library_sha256': hashlib.sha256(library.read_bytes()).hexdigest(), 'source_sha256': hashes,
        'comparison_provider': str(provider), 'provider_sha256': digest, 'image_base': hex(image['image_base']),
        'binary_facts': facts, 'native_test': result, 'input_game_exe_execution': False,
        'limit': 'Type/message/reference catch/rethrow contracts checked against installed compatible classic provider, not exact SDK-linked historical libci. Old Character exception unwind paths and copied old exception layouts unverified.'}
    (WS/'inventory/character-exceptions.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(f'PASS: real exception helpers and classic export comparison, {result["checks_passed"]} checks.')


if __name__ == '__main__':
    main()
