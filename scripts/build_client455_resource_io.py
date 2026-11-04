"""Compile recovered RPK code; verify actual members, ordering and FILE semantics."""
import ctypes
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from verify_client_coff import directives
from rpk455 import Rpk
from test_map455 import archive
from build_client455_x87_math import read_va
from ctypes import wintypes


def sha(b):return hashlib.sha256(b).hexdigest()


def windows_inventory(pattern):
    class FindData(ctypes.Structure):
        _fields_=[('attributes',wintypes.DWORD),('creation',wintypes.FILETIME),('access',wintypes.FILETIME),
                  ('write',wintypes.FILETIME),('sizeHigh',wintypes.DWORD),('sizeLow',wintypes.DWORD),
                  ('reserved0',wintypes.DWORD),('reserved1',wintypes.DWORD),('name',ctypes.c_char*260),('alternate',ctypes.c_char*14)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.FindFirstFileA.argtypes=[ctypes.c_char_p,ctypes.POINTER(FindData)];kernel.FindFirstFileA.restype=wintypes.HANDLE
    kernel.FindNextFileA.argtypes=[wintypes.HANDLE,ctypes.POINTER(FindData)];kernel.FindNextFileA.restype=wintypes.BOOL
    kernel.FindClose.argtypes=[wintypes.HANDLE];kernel.FindClose.restype=wintypes.BOOL
    found=FindData();handle=kernel.FindFirstFileA(str(pattern).encode('ascii'),ctypes.byref(found));rows=[]
    if handle==ctypes.c_void_p(-1).value:raise OSError('Fixture enumeration failed')
    try:
        while True:
            rows.append((bytes(found.name).decode('ascii'),found.attributes))
            if not kernel.FindNextFileA(handle,ctypes.byref(found)):break
    finally:kernel.FindClose(handle)
    return rows


def main():
    evidence=json.loads((WS/'inventory/client455-map-resources.json').read_text(encoding='utf-8'))
    extra=[];first_bodies=None
    for item in evidence['binary_evidence']:
        data=(WS/f'work/client-reference/{item["input"]}/RF_Online.bin').read_bytes()
        if sha(data)!=item['sha256']:raise ValueError('Resource PE changed')
        functions=[];bodies=[]
        for name,va,size in [('rpk_release',0x8e6d60,0x36),('group_release',0x8e7440,0x65),
                             ('group_exists',0x8e7510,0x60),('set_active',0x8e75d0,0xa),
                             ('resource_exists',0x8e75f0,0x48),('file_exists',0x8e7130,0x19),
                             ('material_binary',0x90b1c0,0x1ad)]:
            body=read_va(data,va,size);bodies.append(body)
            functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':sha(body)})
        if first_bodies is not None and bodies!=first_bodies:raise ValueError('Resource helper bodies differ')
        first_bodies=bodies
        extra.append({'input':item['input'],'sha256':item['sha256'],'architecture':'x86','image_base':'0x400000','functions':functions})
    root=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455'])
    work=WS/'work/recovered/client455/resource-io';work.mkdir(parents=True,exist_ok=True)
    sources=['client455_resource_io.h','client455_resource_io.cpp','test_client455_resource_io.cpp']
    hashes={}
    for name in sources:
        source=WS/'scripts/native'/name;shutil.copyfile(source,work/name);hashes[name]=sha(source.read_bytes())
    verified=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dev=Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    includes=WS/'work/client-build/source/R3Engine/common'
    log=WS/'artifacts/client455-resource-io-build.txt'
    batch=work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /I"{includes}" /c client455_resource_io.cpp /Foresource-io.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_resource_io.cpp resource-io.obj bcrypt.lib /Feresource-io-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:raise ValueError(f'Resource build failed: {log}')
    exe=work/'resource-io-probe.exe'
    pe(exe.read_bytes())
    if '/DEFAULTLIB:"LIBCMT"' not in directives((work/'resource-io.obj').read_bytes()):raise ValueError('Expected x86 /MT')
    cases=[];checks=0
    for no,record in enumerate(evidence['archives']):
        data=(root/record['path']).read_bytes()
        if sha(data)!=record['sha256']:raise ValueError('Audited archive changed')
        rpk=Rpk(data);keys=sorted(rpk.files)
        folder=work/f'archives/{no:03}';folder.mkdir(parents=True,exist_ok=True)
        request=folder/'requests.bin';output=folder/'result.bin'
        request.write_bytes(b'RFPRQ455'+struct.pack('<I',len(keys))+b''.join(key.ljust(256,b'\0')+struct.pack('<I',rpk.extents[rpk.files[key]]) for key in keys))
        result=subprocess.run([str(exe),'members',str(root/record['path']),str(request),str(output)],cwd=folder,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:raise ValueError(f'Native archive read failed {record["path"]}: {result.returncode}')
        result=output.read_bytes()
        if result[:12]!=b'RFPOS455'+struct.pack('<I',len(keys)) or len(result)!=12+48*len(keys):raise ValueError('Bad native read report')
        for i,key in enumerate(keys):
            opened,position,consumed,digest,after=struct.unpack_from('<III32si',result,12+48*i)
            node=rpk.files[key];raw=rpk.read(key);end=rpk.offsets[node]+len(raw)
            expected_after=rpk.payload[end] if end<len(rpk.payload) else -1
            if (opened,position,consumed,digest.hex(),after)!=(1,rpk.base+rpk.offsets[node],len(raw),sha(raw),expected_after):
                raise ValueError(f'Native member differs: {key!r}')
            checks+=5
        cases.append({'path':record['path'],'sha256':record['sha256'],'files_checked':len(keys),'output_sha256':sha(result)})
    # Controlled duplicates in distinct archives plus a loose fallback/override.
    fixture=work/'group';packs=fixture/'packs';packs.mkdir(parents=True,exist_ok=True)
    (packs/'first.rpk').write_bytes(archive())
    second=bytearray(archive());second[-6:]=b'xxxYYY';(packs/'second.rpk').write_bytes(second)
    (packs/'oddXrpk').write_bytes(archive())
    (fixture/'dir').mkdir(exist_ok=True);(fixture/'dir/a.spt').write_bytes(b'LOOSE')
    (packs/'fallback.txt').write_bytes(b'FALLBACK')
    (packs/'ignored.rpk').mkdir(exist_ok=True)
    queries=[(b'PACKS\\DIR\\A.SPT',1),(b'packs\\fallback.txt',1),(b'packs\\missing.spt',1),
             (b'DIR\\A.SPT',0),(b'DIR\\A.SPT',1),(b'XXXXXXDIR\\A.SPT',1)]
    request=fixture/'request.bin';output=fixture/'result.bin'
    request.write_bytes(b'RFGRQ455'+struct.pack('<I',len(queries))+b''.join(q.ljust(256,b'\0')+struct.pack('<I',active) for q,active in queries))
    result=subprocess.run([str(exe),'group','packs\\',str(request),str(output)],cwd=fixture,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise ValueError(f'Native group read failed: {result.returncode}')
    raw=output.read_bytes();count,prefix=struct.unpack_from('<II',raw,8)
    if raw[:8]!=b'RFGOS455' or count!=3 or prefix!=6:raise ValueError('Group fixture inventory differs')
    names=[raw[16+256*i:16+256*(i+1)].split(b'\0')[0].decode('ascii') for i in range(count)]
    os_rows=windows_inventory(packs/'*.*')
    expected_names=['packs\\'+name.lower() for name,attr in os_rows[1:] if not attr&16 and len(name)>=4 and name.lower().endswith('rpk')]
    if names!=expected_names:raise ValueError('Group order differs from independent Win32 enumeration')
    first=ord('x') if names[0].endswith('second.rpk') else ord('o')
    values=[]
    for i,(query,active) in enumerate(queries):
        at=16+256*count+264*i;name=raw[at:at+256].split(b'\0')[0];value,exists=struct.unpack_from('<ii',raw,at+256)
        expected=[first,ord('F'),-2,ord('L'),ord('L'),first][i]
        if value!=expected or exists!=(value!=-2) or name!=(query.lower() if active else query):raise ValueError(f'Group query differs:{query!r} ->{name!r}/{value}')
        checks+=3;values.append({'query':query.decode('ascii'),'active':bool(active),'mutated':name.decode('ascii'),'first_byte':value,'exists':bool(exists)})
    leaks,warnings=struct.unpack_from('<II',raw,len(raw)-8)
    if leaks or warnings:raise ValueError('Unexpected group ownership/warnings')
    checks+=2
    boundaries=[]
    for label,expected_count,expected_warnings in [('missing',0,0),('empty',0,0),('wrong-version',1,1),('limit256',0,1)]:
        case=work/'boundaries'/label;directory=case/'packs'
        case.mkdir(parents=True,exist_ok=True)
        if label!='missing':directory.mkdir(exist_ok=True)
        if label=='wrong-version':(directory/'bad.rpk').write_bytes(struct.pack('<f',2.0))
        if label=='limit256':
            for i in range(256):(directory/f'{i:03}.rpk').write_bytes(archive())
        query_file=case/'requests.bin';out_file=case/'result.bin'
        query_file.write_bytes(b'RFGRQ455'+struct.pack('<I',0))
        run=subprocess.run([str(exe),'group','packs\\',str(query_file),str(out_file)],cwd=case,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
        if run.returncode:raise ValueError(f'Group boundary failed:{label}/{run.returncode}')
        result=out_file.read_bytes();actual_count=struct.unpack_from('<I',result,8)[0]
        balance,warning_count=struct.unpack_from('<II',result,len(result)-8)
        if (actual_count,balance,warning_count)!=(expected_count,0,expected_warnings):raise ValueError(f'Group boundary result differs:{label}')
        checks+=3;boundaries.append({'case':label,'archive_count':actual_count,'allocation_balance':balance,'warnings':warning_count})
    report={'source_sha256':hashes,'exe':exe.relative_to(WS).as_posix(),'exe_sha256':sha(exe.read_bytes()),
            'object_sha256':sha((work/'resource-io.obj').read_bytes()),'architecture':'x86','runtime':'/MT',
            'binary_evidence':extra,'native_checks':checks,'archives':cases,'group':{'archive_order':names,'independent_windows_enumeration':os_rows,'queries':values,'allocation_balance':leaks},'group_boundaries':boundaries,
            'limits':['Own native module execution, no input game EXE/DLL.',
                      'Valid metadata and explicit safe version/missing/count-limit cases; unsafe tables, >256archive overrun, repeated successful load leak/OOM not exercised.',
                      'Group ordering compared with independent Win32 enumeration on the controlled fixture; other filesystems/locales remain unverified.',
                      'This standalone report covers the resource module only; full-client integration has separate reports. Normal map/GPU remains outside this check.']}
    (WS/'inventory/client455-resource-io.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: native RPK read {sum(c["files_checked"] for c in cases)}members/{len(cases)}archives, {checks}checks; source x86 /MT.')


if __name__=='__main__':main()
