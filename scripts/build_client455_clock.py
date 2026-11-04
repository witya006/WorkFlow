"""Build the own-source clock; prove bounded instruction identity and native ABI."""
import hashlib,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va,object_relocations
from export_character_analysis import coff_function_records
from verify_client_coff import directives

FUNCTIONS=[('_RF455_SetDayRate',0x8b12c0,11),('_RF455_GetDayRate',0x8b12d0,7),
           ('_RF455_SetDayTime',0x8b12e0,0xcc),('_RF455_GetDayTime',0x8b13b0,0x75),
           ('_RF455_GetDayFraction',0x8b1430,7),('_RF455_SetDayFraction',0x8b1440,0x55),
           ('_RF455_GetRealDayFraction',0x8b15c0,7),('_RF455_SetRealDayFraction',0x8b15d0,0x4f),
           ('_RF455_AdvanceDayClock',0x8b1f20,0x100)]
OPERANDS={0xbf7348:'_RF455_DayRate',0x1154dec:'_RF455_DayFraction',0x1154df0:'_RF455_DayBase',
          0x1154de0:'_RF455_RealDayFraction',0x1154de4:'_RF455_RealDayBase',0xaa4214:'_RF455_ClockTickSource',
          0xae8e90:'_RF455_SecondsPerDay',0xaa9890:'_RF455_MillisecondsPerSecond',0xb369b0:'_RF455_UInt32Bias'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    verified=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'))
    work=WS/'work/recovered/client455/clock';work.mkdir(parents=True,exist_ok=True)
    sources=['client455_clock.h','client455_clock.cpp','test_client455_clock.cpp'];hashes={}
    for name in sources:
        src=WS/'scripts/native'/name;shutil.copyfile(src,work/name);hashes[name]=sha(src)
    log=WS/'artifacts/client455-clock-build.txt';dev=Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch=work/'build.cmd'
    batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /c client455_clock.cpp /Foclock.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455Clock.lib clock.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX test_client455_clock.cpp RFClient455Clock.lib /Feclock-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:raise RuntimeError(f'Clock build failed:{log}')
    obj=(work/'clock.obj').read_bytes();records=coff_function_records(obj)
    if '/DEFAULTLIB:"LIBCMT"' not in directives(obj):raise ValueError('Clock CRT must be /MT')
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));evidence=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=target[key]['sha256']:raise ValueError('Clock reference changed')
        for addr,value in [(0xae8e90,struct.pack('<d',86400)),(0xaa9890,struct.pack('<d',1000)),(0xb369b0,struct.pack('<f',2**32)),(0xbf7348,struct.pack('<f',3))]:
            if read_va(raw,addr,len(value))!=value:raise ValueError('Clock constant changed')
        comparisons=[]
        for name,va,size in FUNCTIONS:
            record=records[name];ref=bytearray(read_va(raw,va,size));compiled=obj[record['file_offset']:record['file_offset']+size]
            relocations=object_relocations(obj,record,size)
            for reloc in relocations:
                at=reloc['offset'];original=struct.unpack_from('<I',ref,at)[0]
                if reloc['type']!=6 or OPERANDS.get(original)!=reloc['symbol'] or compiled[at:at+4]!=bytes(4):raise ValueError(f'Unproved clock relocation:{name}:{reloc}:{original:x}')
                ref[at:at+4]=bytes(4)
            if compiled!=ref:
                differences=[i for i,(a,b) in enumerate(zip(compiled,ref)) if a!=b]
                raise ValueError(f'Clock instruction difference:{name}:{differences[:20]}')
            comparisons.append({'symbol':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'reference_body_sha256':hashlib.sha256(read_va(raw,va,size)).hexdigest(),'relocations':relocations,'identity_except_verified_absolute_operands':True,'prefix_only':name=='_RF455_AdvanceDayClock'})
        evidence.append({'input':folder,'sha256':target[key]['sha256'],'architecture':'x86','image_base':'0x400000','functions':comparisons})
    run=subprocess.run([str(work/'clock-probe.exe')],cwd=work,capture_output=True,timeout=15)
    (WS/'artifacts/client455-clock-native.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'Clock native failure:{run.stdout!r}:{run.stderr!r}')
    native=json.loads(run.stdout)
    if native['failures'] or native['precision_rounding_modes']!=12:raise ValueError('Incomplete native clock test')
    report={'library':(work/'RFClient455Clock.lib').relative_to(WS).as_posix(),'library_sha256':sha(work/'RFClient455Clock.lib'),
            'source_sha256':hashes,'object_sha256':sha(work/'clock.obj'),'binary_evidence':evidence,'native_test':native,
            'reference_executables_executed':False,'scope':'Eight scalar clock routines and256byte two-clock update prefix. Not full lighting, map caller, console commands, network synchronization or M9.'}
    (WS/'inventory/client455-clock.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:8clock functions+256byte frame prefix match both455PE;{native["checks"]}native checks/12FP modes.')

if __name__=='__main__':main()
