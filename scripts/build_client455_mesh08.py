"""Build/test bounded source MESH08 reader/writer on pinned real-model fixtures."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from compare_client_binaries import WS
from verify_client_coff import directives

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    corpus=json.loads((WS/'inventory/character-mesh08-corpus.json').read_text(encoding='utf-8'))
    if corpus['framing_errors'] or sha(WS/'scripts/mesh08.py')!=corpus['python_parser_sha256'] or sha(WS/corpus['native_golden'])!=corpus['native_golden_sha256']:raise ValueError('MESH08 fixtures/parser changed')
    for sample in corpus['samples']:
        if sha(WS/sample['copy'])!=sample['sha256']:raise ValueError('MESH08 native input changed')
    work=WS/'work/recovered/client455/mesh08';work.mkdir(parents=True,exist_ok=True);hashes={}
    for name in ['client455_mesh08.cpp','client455_mesh08.h','test_client455_mesh08.cpp']:
        source=WS/'scripts/native'/name;shutil.copyfile(source,work/name);hashes[name]=sha(source)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text(encoding='utf-8'));dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat';log=WS/'artifacts/character-mesh08/build.txt'
    batch=work/'build.cmd';batch.write_text(f'''@echo off
call "{dev}" -no_logo -arch=x86 -host_arch=x64 > env.txt 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /Gy /EHsc /std:c++14 /W4 /WX /c client455_mesh08.cpp /Fomesh08.obj > "{log}" 2>&1
if errorlevel 1 exit /b 1
lib /nologo /machine:x86 /out:RFClient455Mesh08.lib mesh08.obj >> "{log}" 2>&1
if errorlevel 1 exit /b 1
cl /nologo /MT /O2 /EHsc /std:c++14 /W4 /WX /D_CRT_SECURE_NO_WARNINGS test_client455_mesh08.cpp RFClient455Mesh08.lib /Femesh08-probe.exe >> "{log}" 2>&1
exit /b %errorlevel%
''',encoding='ascii')
    if subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=work).returncode:raise RuntimeError(f'MESH08 build failed:{log}')
    if '/DEFAULTLIB:"LIBCMT"' not in directives((work/'mesh08.obj').read_bytes()):raise ValueError('MESH08 source is not x86/MT')
    run=subprocess.run([str(work/'mesh08-probe.exe'),str(WS/corpus['native_golden'])],cwd=work,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    (WS/'artifacts/character-mesh08/native-result.txt').write_bytes(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'MESH08 source runtime failed:{run.returncode:#x}')
    native=json.loads(run.stdout)
    if native['failures'] or native['real_files']!=len(corpus['samples']) or native['boundary_cases']!=1309:raise ValueError('MESH08 native fixtures incomplete')
    report={'architecture':'x86','runtime':'/MT','library':(work/'RFClient455Mesh08.lib').relative_to(WS).as_posix(),'library_sha256':sha(work/'RFClient455Mesh08.lib'),'source_sha256':hashes,
        'object_sha256':sha(work/'mesh08.obj'),'executable_sha256':sha(work/'mesh08-probe.exe'),'native_test':native,'corpus_report_sha256':sha(WS/'inventory/character-mesh08-corpus.json'),
        'limits':['Owned byte views andlossless framing;not455ObjectMesh ABI','Runtime materials/textures/bone resolution/shared GPU buffers/load publication not implemented bythis module','Explicit bounded length/capacity errors differ from unchecked reference AV/OOM/debugbreak behavior','No input EXE orphysicalGPU/network/game DLL execution']}
    (WS/'inventory/client455-mesh08.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:MESH08 source reader/writer,{native["checks"]}checks/{native["real_files"]}real files/{native["parts"]}parts,1309guarded truncations;x86/MT.')

if __name__=='__main__':main()
