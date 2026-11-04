"""Build readable x86 compatibility assembly and prove instruction identity to 455.

No input executable is loaded or executed. Only the compiled own-source test runs.
The sole reference absolute-data operand is verified and resolved by COFF relocation.
"""
import hashlib
import json
import shutil
import struct
import subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from export_character_analysis import coff_function_records
from verify_client_coff import directives

FUNCTIONS=[('_RF455_MatrixInvert',0x8bfbc0,0x1e5),('_RF455_Vector3fTransform',0x8c0980,0x84)]


def read_va(data,va,size):
    image=pe(data)
    rva=va-image['image_base']
    section=next(s for s in image['sections'] if s['rva']<=rva and rva+size<=s['rva']+s['raw_size'])
    start=section['raw_offset']+rva-section['rva']
    if start+size>len(data): raise ValueError('Truncated reference math range')
    return data[start:start+size]


def object_relocations(data,record,size):
    if len(data)<20 or not 1<=record['section']<=struct.unpack_from('<H',data,2)[0]:
        raise ValueError('Invalid math COFF section')
    section=20+40*(record['section']-1)
    if section+40>len(data): raise ValueError('Truncated math section table')
    raw_size,raw_at=struct.unpack_from('<II',data,section+16)
    if size<0 or record['section_offset']+size>raw_size or raw_at+raw_size>len(data):
        raise ValueError('Math function exceeds stored section')
    offset=struct.unpack_from('<I',data,section+24)[0]
    count=struct.unpack_from('<H',data,section+32)[0]
    table,symbol_count=struct.unpack_from('<II',data,8)
    strings=table+18*symbol_count
    if strings+4>len(data): raise ValueError('Truncated math symbol table')
    string_size=struct.unpack_from('<I',data,strings)[0]
    if string_size<4 or strings+string_size>len(data): raise ValueError('Truncated math string table')
    found=[]
    if offset+count*10>len(data): raise ValueError('Truncated math relocations')
    for at in range(offset,offset+count*10,10):
        address,index,kind=struct.unpack_from('<IIH',data,at)
        if record['section_offset']<=address<record['section_offset']+size:
            if index>=symbol_count: raise ValueError('Invalid math relocation symbol')
            entry=table+18*index
            if data[entry:entry+4]==bytes(4):
                relative=struct.unpack_from('<I',data,entry+4)[0]
                if not 4<=relative<string_size: raise ValueError('Bad math relocation name offset')
                name_at=strings+relative
                end=data.find(b'\0',name_at,strings+string_size)
                if end<0: raise ValueError('Unterminated math relocation name')
                name=data[name_at:end].decode('ascii')
            else: name=data[entry:entry+8].split(b'\0')[0].decode('ascii')
            found.append({'offset':address-record['section_offset'],'type':kind,'symbol':name})
    return found


def main():
    verified=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    work=WS/'work/recovered/client455/x87-math'
    work.mkdir(parents=True,exist_ok=True)
    hashes={}
    for name in ['client455_x87_math.h','client455_x87_math.cpp','test_client455_x87_math.cpp']:
        source=WS/'scripts/native'/name
        shutil.copyfile(source,work/name)
        hashes[name]=hashlib.sha256(source.read_bytes()).hexdigest()
    logs=WS/'artifacts/client455-x87-math-build.txt'
    dev=Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch=work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /c client455_x87_math.cpp /Fox87-math.obj > "{logs}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455X87Math.lib x87-math.obj >> "{logs}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX test_client455_x87_math.cpp RFClient455X87Math.lib /Fex87-math-probe.exe >> "{logs}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:
        raise RuntimeError(f'Math build failed: {logs}')
    obj=(work/'x87-math.obj').read_bytes()
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj): raise ValueError('Math is not x86 /MT')
    records=coff_function_records(obj)
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    evidence=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=target[key]['sha256']: raise ValueError('Pinned math input changed')
        if read_va(raw,0xab0d60,4)!=struct.pack('<f',0.001): raise ValueError('Math epsilon changed')
        comparisons=[]
        for name,va,size in FUNCTIONS:
            record=records[name]
            reference=bytearray(read_va(raw,va,size))
            compiled=obj[record['file_offset']:record['file_offset']+size]
            relocs=object_relocations(obj,record,size)
            if name=='_RF455_MatrixInvert':
                if relocs!=[{'offset':0x21,'type':6,'symbol':'_RF455_AffineEpsilon'}]:
                    raise ValueError(f'Unexpected math relocation: {relocs}')
                if reference[0x21:0x25]!=struct.pack('<I',0xab0d60) or compiled[0x21:0x25]!=bytes(4):
                    raise ValueError('Unexpected epsilon absolute operand/addend')
                reference[0x21:0x25]=bytes(4)
            elif relocs: raise ValueError('Transform has unexpected relocations')
            if compiled!=reference:
                differing=[i for i,(a,b) in enumerate(zip(compiled,reference)) if a!=b]
                raise ValueError(f'{name}: instruction identity failed at {differing[:20]}')
            comparisons.append({'symbol':name,'va':hex(va),'rva':hex(va-0x400000),
                'size':size,'reference_code_sha256':hashlib.sha256(read_va(raw,va,size)).hexdigest(),
                'relocations':relocs,'same_all_instruction_bytes_except_verified_absolute_data_operand':True})
        evidence.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000','functions':comparisons})
    result=subprocess.run([str(work/'x87-math-probe.exe')],cwd=work,capture_output=True,timeout=20)
    (WS/'artifacts/client455-x87-math-native.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode: raise RuntimeError(f'Math native test failed: {result.stdout!r} {result.stderr!r}')
    native=json.loads(result.stdout)
    if native['failures'] or native['precision_rounding_modes']!=12 or native['checks']<330:
        raise ValueError('Incomplete math native test')
    library=work/'RFClient455X87Math.lib'
    report={'library':library.relative_to(WS).as_posix(),'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),
        'source_sha256':hashes,'object_sha256':hashlib.sha256(obj).hexdigest(),'binary_evidence':evidence,
        'native_test':native,'input_executables_loaded_or_executed':False,
        'limits':'Instruction identity for these two functions under equal x87 environment/memory; not full client equivalence or proof of matching game startup FPU state. No GPU/network behavior tested.'}
    (WS/'inventory/client455-x87-math.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: two own-source x87 functions match pinned 455 instruction bytes; {native["checks"]} native checks in 12 FP modes.')


if __name__=='__main__': main()
