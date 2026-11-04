"""Build own map-time/cache code; check the critical455numeric fragment and fixtures."""
import hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va,object_relocations
from export_character_analysis import coff_function_records
from build_client455_clock import sha

def main():
    work=WS/'work/recovered/client455/map-time';work.mkdir(parents=True,exist_ok=True)
    clock=json.loads((WS/'inventory/client455-clock.json').read_text(encoding='utf-8'))
    for name,digest in clock['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Clock source proof stale')
    library=WS/clock['library']
    if sha(library)!=clock['library_sha256']:raise ValueError('Clock component library changed')
    hashes={}
    for name in ['client455_clock.h','client455_map_time.h','client455_map_time.cpp','test_client455_map_time.cpp']:
        src=WS/'scripts/native'/name;shutil.copyfile(src,work/name);hashes[name]=sha(src)
    verified=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    dev=Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat';log=WS/'artifacts/client455-map-time-build.txt'
    batch=work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /c client455_map_time.cpp /Fomap-time.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455MapTime.lib map-time.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_map_time.cpp RFClient455MapTime.lib "{library}" /Femap-time-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:raise RuntimeError(f'Map time build failed:{log}')
    obj=(work/'map-time.obj').read_bytes();record=coff_function_records(obj)['_RF455_MapGameFraction']
    start,size,va=15,130,0x7c8dc4
    actual=obj[record['file_offset']+start:record['file_offset']+start+size]
    relocations=object_relocations(obj,record,start+size)
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));evidence=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if hashlib.sha256(data).hexdigest()!=target[key]['sha256']:raise ValueError('Map time reference changed')
        expected=bytearray(read_va(data,va,size));mapped=[]
        for reloc in relocations:
            offset=reloc['offset']-start
            if not 0<=offset<=size-4:raise ValueError('Unexpected map fraction relocation')
            value=struct.unpack_from('<I',expected,offset)[0]
            if reloc['type']==20:
                dest=va+offset+4+struct.unpack_from('<i',expected,offset)[0]
                if dest!=0x8b12d0 or reloc['symbol']!='_RF455_GetDayRate':raise ValueError('Map fraction rate call changed')
            elif reloc['type']==6:
                if value!=0xae8e90 or reloc['symbol']!='_RF455_SecondsPerDay':raise ValueError('Map fraction constant changed')
            else:raise ValueError('Unexpected map fraction relocation type')
            if actual[offset:offset+4]!=bytes(4):raise ValueError('Unexpected compiled relocation addend')
            expected[offset:offset+4]=bytes(4);mapped.append({**reloc,'fragment_offset':offset})
        if len(mapped)!=2 or actual!=expected:raise ValueError('Map fraction130byte sequence differs:'+str([i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:20]))
        evidence.append({'input':folder,'sha256':target[key]['sha256'],'architecture':'x86','image_base':'0x400000','va':hex(va),'rva':hex(va-0x400000),'size':size,'body_sha256':hashlib.sha256(read_va(data,va,size)).hexdigest(),'relocations':mapped,'instruction_identity_except_verified_operands':True})
    run=subprocess.run([str(work/'map-time-probe.exe')],cwd=work,capture_output=True,timeout=20)
    (WS/'artifacts/client455-map-time-native.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'Map time native failure:{run.stdout!r}:{run.stderr!r}')
    native=json.loads(run.stdout)
    if native['failures'] or native['precision_rounding_modes']!=12:raise ValueError('Incomplete map time native test')
    report={'library':(work/'RFClient455MapTime.lib').relative_to(WS).as_posix(),'library_sha256':sha(work/'RFClient455MapTime.lib'),'source_sha256':hashes,'object_sha256':sha(work/'map-time.obj'),'clock_library_sha256':clock['library_sha256'],'binary_evidence':evidence,'native_test':native,'scope':'Own module cache/packet fields and map-load arithmetic;130critical bytes equal455. Calendar uses current UCRT localtime32; complete old-CRT timezone/DST parity remains open. Client dispatcher/CLand integration tested separately.'}
    (WS/'inventory/client455-map-time.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:map-time130byte numeric fragment matches both455PE;{native["checks"]}checks/12FP modes/UTC+JST.')

if __name__=='__main__':main()
