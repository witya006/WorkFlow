"""Reconstruct reference effect logging and exercise synthetic file boundaries.

Only the own component test runs, in isolated fixture working directories.
No automatic lifecycle is invented for the reference's unreferenced clear routine.
"""
import ctypes
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives


def binary_evidence():
    target = json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    facts = []
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data = (WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != target[key]['sha256']:
            raise ValueError('Pinned reference changed')
        image = pe(data)

        def check(va,wanted):
            rva = va-image['image_base']
            s = next(s for s in image['sections'] if s['rva']<=rva<s['rva']+s['raw_size'])
            at = s['raw_offset']+rva-s['rva']
            if data[at:at+len(wanted)] != wanted:
                raise ValueError(f'Logging instruction changed at {va:x}')
            return {'va':hex(va),'rva':hex(rva),'file_offset':hex(at),'bytes':wanted.hex()}

        checks = [check(0x7df294,bytes.fromhex('3d809698007e23')),
            check(0x7df2c4,bytes.fromhex('3d404b4c007e0a')),
            check(0x7df2cb,bytes.fromhex('c7055ce4130101000000')),
            check(0x7df1bc,bytes.fromhex('833d5ce4130100')),
            check(0x7df1c5,bytes.fromhex('c7055ce4130100000000')),
            check(0xaedc70,b'.\\NetLog\\EffectLog.log\0'),
            check(0xaedc88,b'wt\0'),check(0xaedc8c,b'rt+\0')]
        for va,destination in [(0x7df213,0x874a43),(0x7df22e,0x874a43),
                (0x7df248,0x87a2c4),(0x7df25b,0x87a3b9),(0x7df267,0x87a2c4),
                (0x7df27a,0x87f3c8),(0x7df286,0x874903),(0x7df2a5,0x874a43),
                (0x7df2b4,0x874903),(0x7df1d9,0x874a43),(0x7df1e8,0x874903)]:
            checks.append(check(va,b'\xe8'+struct.pack('<i',destination-va-5)))
        facts.append({'input':folder,'sha256':digest,'architecture':'x86','instructions':checks})
    return facts


def main():
    evidence = binary_evidence()
    verified = json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    work = WS/'work/recovered/client455/effect-log'
    work.mkdir(parents=True,exist_ok=True)
    sources = ['client455_effect_log.h','client455_effect_log.cpp','test_client455_effect_log.cpp']
    hashes = {}
    for name in sources:
        source = WS/'scripts/native'/name
        shutil.copyfile(source,work/name)
        hashes[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    log = WS/'artifacts/client455-effect-log-build.txt'
    dev = Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    options = '/nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS'
    batch = work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl {options} /c client455_effect_log.cpp /Foeffect-log.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455EffectLog.lib effect-log.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl {options} test_client455_effect_log.cpp RFClient455EffectLog.lib /Feeffect-log-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:
        raise RuntimeError(f'Logging build failed: {log}')
    if '/DEFAULTLIB:"LIBCMT"' not in directives((work/'effect-log.obj').read_bytes()):
        raise ValueError('Logging object is not x86 /MT')
    # (initial bytes, mode, first size, final size, directory exists, read-only)
    specs = [(None,'none',5,5,True,False),(None,'none',-1,-1,False,False),
        (0,'clear',5,5,True,False),(4999999,'none',5000004,5000004,True,False),
        (5000000,'clear',5000005,5000005,True,False),
        (5000001,'none',5000006,5000006,True,False),(5000001,'clear',5000006,0,True,False),
        (10000000,'none',10000005,10000005,True,False),(10000000,'clear',10000005,0,True,False),
        (10000001,'none',0,0,True,False),(10000001,'clear',0,0,True,False),
        (5000000,'repeatclear',5000005,0,True,False),
        (5000001,'shrinkclear',5000006,0,True,False),(10,'none',10,10,True,True)]
    cases = []
    checks = 0
    for index,(length,mode,first,final,directory,readonly) in enumerate(specs):
        case = work/f'cases/{index:02}'
        case.mkdir(parents=True,exist_ok=True)
        folder = case/'NetLog'
        path = folder/'EffectLog.log'
        if directory:
            folder.mkdir(exist_ok=True)
        elif folder.exists():
            raise ValueError('Missing-directory fixture unexpectedly contains NetLog')
        if path.exists():
            # Only this exact owned fixture file; no recursive cleanup.
            ctypes.windll.kernel32.SetFileAttributesW(str(path),0x80)
            path.unlink()
        if length is not None:
            path.write_bytes(b'x'*length)
        if readonly and not ctypes.windll.kernel32.SetFileAttributesW(str(path),1):
            raise OSError('Cannot prepare own read-only fixture')
        run = subprocess.run([str(work/'effect-log-probe.exe'),mode],cwd=case,
            capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
        if run.returncode:
            raise RuntimeError(f'Logging case {index} failed: {run.returncode} {run.stderr!r}')
        result = json.loads(run.stdout)
        assert result['first_size']==first,(index,result)
        assert result['final_size']==final,(index,result)
        actual = path.stat().st_size if path.exists() else -1
        assert actual==final,(index,actual) # Includes normal process shutdown.
        checks += 4
        if actual>0:
            with path.open('rb') as stream:
                prefix = stream.read(min(16,actual))
                stream.seek(max(0,actual-5))
                tail = stream.read()
            if length and length>=16:
                assert prefix==b'x'*16
                checks += 1
            if not readonly:
                assert tail==b'log\r\n'
                checks += 1
        cases.append({'initial_bytes':length,'mode':mode,'read_only':readonly,
            'directory_exists':directory,'first_bytes':first,'after_exit_bytes':actual})
    library = work/'RFClient455EffectLog.lib'
    report = {'architecture':'x86','runtime':'/MT','library':library.relative_to(WS).as_posix(),
        'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'source_sha256':hashes,
        'binary_evidence':evidence,'native_checks':checks,'cases':cases,'input_game_exe_execution':False,
        'lifecycle':'No automatic clear/atexit; original clear routine reachability unproven. Explicit clear tested separately.',
        'limits':'Static reference contract plus own native file tests; null buffers, >2GB/ftell errors, concurrent calls and truncate-open failure behavior unverified.'}
    (WS/'inventory/client455-effect-log.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: 455 logging, {len(cases)} isolated cases / {checks} checks; no input executable execution.')


if __name__=='__main__':
    main()
