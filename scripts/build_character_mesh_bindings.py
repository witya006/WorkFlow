"""Recover four legacy CPU functions; compare SDK bodies and actual InitVertex.

455 layout/behavior differences are pinned separately; this does not certify455.
"""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from coff_source_bindings import BINDINGS,source_bindings
from export_character_analysis import coff_function_records
from verify_client_coff import directives
from build_client455_x87_math import object_relocations

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/'inventory'/name).read_text(encoding='utf-8'))

def main():
    verified=load('msvc-verification.json');stdio=load('character-stdio-adapter.json');header=load('character-header-recovery.json')
    dependencies={}
    for file,key in [('character-managers.json','managers'),('character-setters.json','setters'),('character-exceptions.json','exceptions')]:
        report=load(file);path=WS/report['library']
        if sha(path)!=report['library_sha256']:raise ValueError('Changed Character dependency:'+key)
        dependencies[key]=path
    if sha(WS/header['header'])!=header['header_sha256']:raise ValueError('Changed Character header')
    if sha(WS/stdio['adapted_archive'])!=stdio['adapted_archive_sha256'] or sha(WS/stdio['adapter_library'])!=stdio['adapter_library_sha256']:raise ValueError('Changed stdio adaptation')
    work=WS/'work/recovered/character-legacy/mesh-bindings';work.mkdir(parents=True,exist_ok=True)
    objects=[];selected=[];object_paths=[]
    for n,item in enumerate(stdio['objects'],1):
        source=WS/item['object'];raw=source.read_bytes()
        if sha(source)!=item['output_sha256']:raise ValueError('Changed adapted COFF')
        result,changes=source_bindings(raw);path=work/f'character_{n:02d}.obj';path.write_bytes(result);object_paths.append(path)
        objects.append({'object':path.relative_to(WS).as_posix(),'input_sha256':sha(source),'sha256':sha(path),'changes':changes,'instruction_bytes_unchanged':True,'rva':None})
        selected.extend(changes)
    if {c['symbol'] for c in selected}!=BINDINGS.keys():raise ValueError('Incomplete source substitution')
    init=coff_function_records((WS/stdio['objects'][8]['object']).read_bytes())['?LoadRealData@CRender@@QAE_NPAVCHARACTEROBJECT@@PAVTextureManager@@_N@Z']
    calls=[r for r in object_relocations((WS/stdio['objects'][8]['object']).read_bytes(),init,init['size']) if r['symbol']=='?InitVertex@@YAXPAVObjectData@@PAVCHARACTEROBJECT@@1PAVTextureManager@@_N@Z']
    if len(calls)!=2:raise ValueError('Expected two actual SDK LoadRealData callers')
    hashes={}
    for name in ['character_mesh_bindings.cpp','character_mesh_init.cpp','character_mesh_format.h','test_character_mesh_bindings.cpp','test_character_mesh_init.cpp']:
        source=WS/'scripts/native'/name;shutil.copyfile(source,work/name);hashes[name]=sha(source)
    dx=load('directx81b-sdk.json');dev=Path(verified['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    logs=WS/'artifacts/character-mesh-source';logs.mkdir(exist_ok=True);log=logs/'build.txt'
    options=f'/nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /I"{(WS/header["header"]).parent}" /external:I"{WS/dx["include_overlay"]}" /external:W0'
    link=' '.join(f'"{p}"' for p in [dependencies['managers'],dependencies['setters'],WS/stdio['adapter_library'],dependencies['exceptions'],Path(dx['sdk_root'])/'lib/d3dx8.lib'])
    batch=work/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl {options} /c character_mesh_bindings.cpp /Fobindings.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
cl {options} /c character_mesh_init.cpp /Foinit.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:CharacterMeshSource.lib bindings.obj init.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:CharacterMR-mesh-source.lib character_*.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl {options} test_character_mesh_bindings.cpp CharacterMeshSource.lib CharacterMR-mesh-source.lib {link} kernel32.lib user32.lib gdi32.lib advapi32.lib winmm.lib legacy_stdio_definitions.lib /Femesh-probe.exe /link /NODEFAULTLIB:libci.lib >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl {options} test_character_mesh_init.cpp CharacterMeshSource.lib CharacterMR-mesh-source.lib {link} kernel32.lib user32.lib gdi32.lib advapi32.lib winmm.lib legacy_stdio_definitions.lib /Feinit-probe.exe /link /NODEFAULTLIB:libci.lib >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:raise RuntimeError(f'Mesh source build failed:{log}')
    if '/DEFAULTLIB:"LIBCMT"' not in directives((work/'bindings.obj').read_bytes()):raise ValueError('Mesh source is not x86 /MT')
    result=subprocess.run([str(work/'mesh-probe.exe')],cwd=work,capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    (logs/'result.txt').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(f'Mesh source runtime failed:{result.returncode:#x}:{logs/"result.txt"}')
    runtime=json.loads(result.stdout)
    init_result=subprocess.run([str(work/'init-probe.exe')],cwd=work,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    (logs/'init-result.txt').write_bytes(init_result.stdout+init_result.stderr)
    if init_result.returncode:raise RuntimeError(f'InitVertex source runtime failed:{init_result.returncode:#x}:{logs/"init-result.txt"}')
    init_runtime=json.loads(init_result.stdout)
    report={'architecture':'x86','runtime':'/MT','rva':None,'library':(work/'CharacterMeshSource.lib').relative_to(WS).as_posix(),'library_sha256':sha(work/'CharacterMeshSource.lib'),
        'adapted_archive':(work/'CharacterMR-mesh-source.lib').relative_to(WS).as_posix(),'adapted_archive_sha256':sha(work/'CharacterMR-mesh-source.lib'),
        'base_archive_sha256':stdio['adapted_archive_sha256'],'source_sha256':hashes,'script_sha256':{n:sha(WS/'scripts'/n) for n in ['coff_source_bindings.py','build_character_mesh_bindings.py']},'header_sha256':header['header_sha256'],'objects':objects,
        'source_function_count':len(BINDINGS),'actual_load_real_source_calls':calls,'native_test':runtime,'native_init_test':init_runtime,'executable_sha256':sha(work/'mesh-probe.exe'),'init_executable_sha256':sha(work/'init-probe.exe'),
        'limits':['Legacy1072byte mesh/36byte vertex source prerequisite,not455renderer parity','Empty textures;0-2triangle expanded VB inputs captured by test-only COM doubles,not physical GPU','Bounded <=4legacy blend parents;unsafe overflow/OOM/invalid inputs unverified','Retained old bodies only for comparison;incoming callers select own source','Other Character functions still binary-only;455packed5803byte layout/64byte vertex/first-match/inline matrices differ']}
    (WS/'inventory/character-mesh-source.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{len(BINDINGS)}source functions,{runtime["checks_passed"]}binding+{init_runtime["checks_passed"]}InitVertex checks/{init_runtime["cases"]}cases/12FP modes;no GPU/input EXE.')

if __name__=='__main__':main()
