"""Verify 455 setter code and legacy consumed fields; build real leaf methods.

No input EXE executes. The native probe runs own methods on guarded ABI storage.
"""
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS, pe
from export_character_analysis import coff_function_records
from recover_character_layouts import operand
from verify_client_coff import directives


def verify_evidence():
    pinned = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    facts = []
    for folder, key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data = (WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != pinned[key]['sha256']:
            raise ValueError('Pinned client changed')
        image = pe(data)

        def check(va, wanted):
            rva = va-image['image_base']
            s = next(s for s in image['sections'] if s['rva'] <= rva < s['rva']+s['raw_size'])
            offset = s['raw_offset']+rva-s['rva']
            if data[offset:offset+len(wanted)] != wanted:
                raise ValueError(f'Setter evidence changed at {va:x}')
            return {'va':hex(va),'rva':hex(rva),'file_offset':hex(offset),'bytes':wanted.hex()}

        checks = [check(0x60814c,bytes.fromhex('837d0c00741b')),
            check(0x608152,bytes.fromhex('68ff000000')),
            check(0x60815e,bytes.fromhex('81c114010000')),
            check(0x608165,b'\xe8'+struct.pack('<i',0x8797a0-0x60816a)),
            check(0x540123,bytes.fromhex('81c1e8200000')),
            check(0x540129,b'\xe8'+struct.pack('<i',0x540140-0x54012e)),
            check(0x540152,bytes.fromhex('89881c010000'))]
        facts.append({'input':folder,'sha256':digest,'architecture':'x86','instructions':checks})
    manifest = json.loads((WS/'inventory/character-codeview.json').read_text(encoding='utf-8'))
    for index, symbol, offset, prefix, value in [
            (7,'?InitVertex@@YAXPAVObjectData@@PAVCHARACTEROBJECT@@1PAVTextureManager@@_N@Z',0x1b7,'8a8a',272),
            (8,'?AddTexture@TextureManager@@QAE_NPBD0@Z',0x15b,'8b83',156),
            (3,'?LoadEffectFileList@EffectList@@QAEXPAD@Z',0x49,'81ff',500),
            (3,'?LoadEffectFileList@EffectList@@QAEXPAD@Z',0xd0,'8984ab',2000)]:
        entry = manifest['objects'][index-1]
        data = (WS/entry['working_object']).read_bytes()
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('Legacy field evidence object changed')
        record = coff_function_records(data)[symbol]
        if operand(record,offset,bytes.fromhex(prefix)) != value:
            raise ValueError('Legacy consumed field offset changed')
        facts.append({'object_sha256':entry['sha256'],'symbol':symbol,'architecture':'x86',
            'function_offset':hex(offset),'file_offset':hex(record['file_offset']+offset),
            'rva':None,'verified_operand':value})
    return facts


def main():
    facts = verify_evidence()
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    header = json.loads((WS/'inventory/character-header-recovery.json').read_text(encoding='utf-8'))
    include = WS/header['header']
    if hashlib.sha256(include.read_bytes()).hexdigest() != header['header_sha256']:
        raise ValueError('Recovered header changed')
    dx = WS/'local/directx81b/include-overlay'
    work = WS/'work/recovered/character-legacy/setters'
    work.mkdir(parents=True,exist_ok=True)
    hashes = {}
    for name in ['character_recovered_setters.cpp','character_recovered_effect_setter.cpp','test_character_recovered_setters.cpp']:
        source = WS/'scripts/native'/name
        shutil.copyfile(source,work/name)
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    log = WS/'artifacts/character-setters-build.txt'
    dev = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    opts = f'/nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /I"{include.parent}" /external:I"{dx}" /external:W0'
    batch = work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl {opts} /c character_recovered_setters.cpp /Fosetters.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl {opts} /c character_recovered_effect_setter.cpp /Foeffect_setter.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:CharacterRecoveredSetters.lib setters.obj effect_setter.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl {opts} test_character_recovered_setters.cpp CharacterRecoveredSetters.lib /Fesetters-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:
        raise RuntimeError(f'Setter build failed: {log}')
    obj = (work/'setters.obj').read_bytes()
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj):
        raise ValueError('Expected /MT setter object')
    definitions = coff_function_records(obj)
    if not {'?SetMipMap@CRender@@QAEXK@Z','?SetTexPath@ChInterface@@QAEXPAVCHARACTEROBJECT@@PAD@Z'} <= definitions.keys():
        raise ValueError('Setter symbol contract mismatch')
    effect_obj = (work/'effect_setter.obj').read_bytes()
    if '/DEFAULTLIB:"LIBCMT"' not in directives(effect_obj) or '?SetEffect@EffectList@@QAEXPAVCHARACTEROBJECT@@K@Z' not in coff_function_records(effect_obj):
        raise ValueError('Effect setter x86 /MT symbol contract mismatch')
    run = subprocess.run([str(work/'setters-probe.exe')],cwd=work,capture_output=True,
        timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:
        (WS/'artifacts/character-setters-failure.txt').write_bytes(run.stdout+run.stderr)
        raise RuntimeError(f'Setter ABI test failed ({run.returncode})')
    result = json.loads(run.stdout)
    library = work/'CharacterRecoveredSetters.lib'
    report = {'architecture':'x86','runtime':'/MT','library':library.relative_to(WS).as_posix(),
        'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'source_sha256':hashes,
        'header_sha256':header['header_sha256'],'binary_evidence':facts,'native_test':result,
        'effect_bridge_runtime_verification':'Separate inventory/character-effect-loaders.json, not covered by the leaf setter probe',
        'input_game_exe_execution':False,
        'correspondence':'455 source/call-sequence correspondence inferred; instruction effects confirmed. Legacy storage adapted using checked consumers.',
        'limit':'Leaf method ABI/byte effects only; full C++ renderer construction and loaded textures not tested. Source length >=255 deliberately does not force the last byte to NUL, matching the reference.'}
    (WS/'inventory/character-setters.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: reconstructed SetTexPath/SetMipMap, {result["checks_passed"]} guarded machine-ABI checks.')


if __name__=='__main__':
    main()
